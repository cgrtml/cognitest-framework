"""
CogniTest Framework - Log Interpreter
Author: Çağrı Temel
Description: Automated log interpretation and root cause analysis using LLM
"""

import re
from typing import Dict, Optional, List
import logging

from cognitest.core.llm_engine import LLMEngine
from cognitest.utils.prompt_templates import PromptTemplates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogInterpreter:
    """
    Interprets error logs and provides human-readable explanations using LLM.
    """

    def __init__(self, llm_engine: Optional[LLMEngine] = None):
        """
        Initialize log interpreter.

        Args:
            llm_engine: LLM engine instance (creates new if None)
        """
        self.llm_engine = llm_engine or LLMEngine()
        self.templates = PromptTemplates()
        self.interpretation_history = []

    def interpret(
            self,
            error_log: str,
            service_name: str
    ) -> Dict:
        """
        Interpret error log and provide root cause analysis.

        Args:
            error_log: Raw error log or stack trace
            service_name: Name of the service that failed

        Returns:
            Interpretation with root cause, affected components, fix, and prevention
        """
        logger.info(f"Interpreting log for service: {service_name}")

        # Create prompt
        prompt = self.templates.log_interpretation_prompt(
            error_log=error_log,
            service_name=service_name
        )

        # Generate interpretation
        response = self.llm_engine.generate(prompt, temperature=0.3)

        # Parse structured response
        interpretation = self._parse_interpretation(response)

        # Add metadata
        interpretation['service_name'] = service_name
        interpretation['original_log'] = error_log[:500]  # First 500 chars

        # Store in history
        self.interpretation_history.append({
            "service": service_name,
            "interpretation": interpretation
        })

        logger.info("Log interpretation completed")
        return interpretation

    def interpret_batch(
            self,
            logs: List[Dict]
    ) -> List[Dict]:
        """
        Interpret multiple error logs in batch.

        Args:
            logs: List of log dictionaries with error_log and service_name

        Returns:
            List of interpretation results
        """
        results = []

        for log_entry in logs:
            interpretation = self.interpret(
                error_log=log_entry['error_log'],
                service_name=log_entry['service_name']
            )
            results.append({
                **log_entry,
                "interpretation": interpretation
            })

        return results

    def _parse_interpretation(self, response: str) -> Dict:
        """Parse LLM response into structured interpretation"""
        interpretation = {
            "root_cause": "",
            "affected_components": "",
            "recommended_fix": "",
            "prevention": "",
            "raw_response": response
        }

        # Extract sections
        sections = {
            "root_cause": r"\*\*Root Cause:\*\*\s*(.*?)(?=\*\*|$)",
            "affected_components": r"\*\*Affected Components:\*\*\s*(.*?)(?=\*\*|$)",
            "recommended_fix": r"\*\*Recommended Fix:\*\*\s*(.*?)(?=\*\*|$)",
            "prevention": r"\*\*Prevention:\*\*\s*(.*?)(?=\*\*|$)"
        }

        for key, pattern in sections.items():
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                interpretation[key] = match.group(1).strip()
            else:
                # Fallback: try without asterisks
                pattern_simple = pattern.replace(r"\*\*", "").replace(r"\*", "")
                match = re.search(pattern_simple, response, re.DOTALL | re.IGNORECASE)
                if match:
                    interpretation[key] = match.group(1).strip()

        # If parsing failed, try to extract any useful information
        if not interpretation["root_cause"]:
            interpretation = self._fallback_parse(response)

        return interpretation

    def _fallback_parse(self, response: str) -> Dict:
        """Fallback parsing when structured parsing fails"""
        # Split by paragraphs
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]

        return {
            "root_cause": paragraphs[0] if len(paragraphs) > 0 else "Unable to determine root cause",
            "affected_components": paragraphs[1] if len(paragraphs) > 1 else "Unknown",
            "recommended_fix": paragraphs[2] if len(paragraphs) > 2 else "Manual investigation required",
            "prevention": paragraphs[3] if len(paragraphs) > 3 else "N/A",
            "raw_response": response
        }

    def generate_report(self, interpretation: Dict) -> str:
        """
        Generate a formatted report from interpretation.

        Args:
            interpretation: Interpretation dictionary

        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    LOG INTERPRETATION REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

Service: {interpretation.get('service_name', 'Unknown')}

─────────────────────────────────────────────────────────────────
ROOT CAUSE
─────────────────────────────────────────────────────────────────
{interpretation.get('root_cause', 'N/A')}

─────────────────────────────────────────────────────────────────
AFFECTED COMPONENTS
─────────────────────────────────────────────────────────────────
{interpretation.get('affected_components', 'N/A')}

─────────────────────────────────────────────────────────────────
RECOMMENDED FIX
─────────────────────────────────────────────────────────────────
{interpretation.get('recommended_fix', 'N/A')}

─────────────────────────────────────────────────────────────────
PREVENTION
─────────────────────────────────────────────────────────────────
{interpretation.get('prevention', 'N/A')}

═════════════════════════════════════════════════════════════════
"""
        return report

    def get_statistics(self) -> Dict:
        """Get interpretation statistics"""
        if not self.interpretation_history:
            return {
                "total_interpretations": 0,
                "services_analyzed": []
            }

        services = set()
        for item in self.interpretation_history:
            services.add(item['service'])

        return {
            "total_interpretations": len(self.interpretation_history),
            "services_analyzed": list(services),
            "unique_services": len(services)
        }


if __name__ == "__main__":
    # Example usage
    interpreter = LogInterpreter()

    error_log = """
    AssertionError: assert 500 == 200
    Full URL: POST http://localhost:8001/api/orders
    Response: {"detail":"Internal Server Error"}
    Traceback (most recent call last):
      File "test_orders.py", line 45, in test_create_order
        assert response.status_code == 200
    """

    result = interpreter.interpret(
        error_log=error_log,
        service_name="Order Service"
    )

    print(interpreter.generate_report(result))
    print("\nStatistics:", interpreter.get_statistics())