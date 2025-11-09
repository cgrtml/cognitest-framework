"""
CogniTest Framework - Test Generator
Author: Çağrı Temel
Description: Automated test case generation from natural language requirements
"""

import re
import os
from typing import List, Dict, Optional
import logging
from pathlib import Path

from cognitest.core.llm_engine import LLMEngine
from cognitest.utils.prompt_templates import PromptTemplates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGenerator:
    """
    Generates pytest test cases from natural language requirements using LLM.
    """

    def __init__(self, llm_engine: Optional[LLMEngine] = None):
        """
        Initialize test generator.

        Args:
            llm_engine: LLM engine instance (creates new if None)
        """
        self.llm_engine = llm_engine or LLMEngine()
        self.templates = PromptTemplates()
        self.generated_tests = []

    def generate_from_requirement(
            self,
            requirement: str,
            api_endpoint: str,
            http_method: str = "POST",
            output_file: Optional[str] = None
    ) -> str:
        """
        Generate test cases from a single requirement.

        Args:
            requirement: Natural language requirement description
            api_endpoint: API endpoint to test
            http_method: HTTP method (GET, POST, PUT, DELETE)
            output_file: Optional file path to save generated tests

        Returns:
            Generated test code as string
        """
        logger.info(f"Generating tests for: {requirement[:50]}...")

        # Create prompt
        prompt = self.templates.test_generation_prompt(
            requirement=requirement,
            api_endpoint=api_endpoint,
            http_method=http_method
        )

        # Generate test code
        test_code = self.llm_engine.generate(prompt, temperature=0.3)

        # Clean up generated code
        test_code = self._clean_generated_code(test_code)

        # Validate syntax
        if not self._validate_syntax(test_code):
            logger.warning("Generated code has syntax errors, attempting to fix...")
            test_code = self._attempt_fix(test_code)

        # Save to file if specified
        if output_file:
            self._save_test_file(test_code, output_file)

        self.generated_tests.append({
            "requirement": requirement,
            "endpoint": api_endpoint,
            "code": test_code
        })

        logger.info("Test generation completed successfully")
        return test_code

    def generate_from_requirements_file(
            self,
            requirements_file: str,
            output_dir: str = "tests/generated"
    ) -> List[str]:
        """
        Generate tests from a requirements file.

        Args:
            requirements_file: Path to requirements file
            output_dir: Directory to save generated tests

        Returns:
            List of generated test file paths
        """
        logger.info(f"Reading requirements from: {requirements_file}")

        # Parse requirements file
        requirements = self._parse_requirements_file(requirements_file)

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        generated_files = []

        for idx, req in enumerate(requirements):
            output_file = os.path.join(
                output_dir,
                f"test_generated_{idx + 1}_{req['name']}.py"
            )

            test_code = self.generate_from_requirement(
                requirement=req['description'],
                api_endpoint=req['endpoint'],
                http_method=req['method'],
                output_file=output_file
            )

            generated_files.append(output_file)

        logger.info(f"Generated {len(generated_files)} test files")
        return generated_files

    def _clean_generated_code(self, code: str) -> str:
        """Remove markdown formatting and extra whitespace"""
        # Remove markdown code blocks
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```\n?', '', code)

        # Remove any leading/trailing whitespace
        code = code.strip()

        # Ensure proper imports at the top
        if 'import pytest' not in code:
            code = 'import pytest\n' + code
        if 'import requests' not in code and 'requests.' in code:
            code = code.replace('import pytest\n', 'import pytest\nimport requests\n')

        return code

    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            return False

    def _attempt_fix(self, code: str) -> str:
        """Attempt to fix common syntax errors"""
        # Fix common issues
        lines = code.split('\n')
        fixed_lines = []

        for line in lines:
            # Fix indentation issues
            if line.strip().startswith('def ') and not line.startswith('def '):
                line = line.lstrip()

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _save_test_file(self, code: str, filepath: str):
        """Save generated test code to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        logger.info(f"Test file saved: {filepath}")

    def _parse_requirements_file(self, filepath: str) -> List[Dict]:
        """
        Parse requirements file into structured format.

        Expected format:
        [Requirement Name]
        Endpoint: /api/endpoint
        Method: POST
        Description: Requirement description here
        ---
        """
        requirements = []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by separator
        sections = content.split('---')

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.split('\n')
            req = {
                'name': '',
                'endpoint': '',
                'method': 'POST',
                'description': ''
            }

            # Parse section
            for i, line in enumerate(lines):
                line = line.strip()

                if i == 0 and line.startswith('[') and line.endswith(']'):
                    req['name'] = line[1:-1].lower().replace(' ', '_')
                elif line.startswith('Endpoint:'):
                    req['endpoint'] = line.split(':', 1)[1].strip()
                elif line.startswith('Method:'):
                    req['method'] = line.split(':', 1)[1].strip()
                elif line.startswith('Description:'):
                    req['description'] = line.split(':', 1)[1].strip()
                elif req['description'] and line:
                    req['description'] += ' ' + line

            if req['endpoint'] and req['description']:
                requirements.append(req)

        return requirements

    def get_generation_stats(self) -> Dict:
        """Get statistics about generated tests"""
        return {
            "total_tests": len(self.generated_tests),
            "total_lines": sum(len(t['code'].split('\n')) for t in self.generated_tests),
            "average_lines_per_test": (
                sum(len(t['code'].split('\n')) for t in self.generated_tests) / len(self.generated_tests)
                if self.generated_tests else 0
            )
        }


if __name__ == "__main__":
    # Example usage
    generator = TestGenerator()

    requirement = """
    Users must be able to register with email and password.
    Email must be unique and in valid format.
    Password must be at least 8 characters with one uppercase, one lowercase, and one number.
    """

    test_code = generator.generate_from_requirement(
        requirement=requirement,
        api_endpoint="http://localhost:8000/api/users/register",
        http_method="POST",
        output_file="tests/generated/test_user_registration.py"
    )

    print("Generated Test Code:")
    print(test_code)
    print("\nStats:", generator.get_generation_stats())