"""
CogniTest Framework - Prompt Templates
Author: Çağrı Temel
Description: Structured prompts for test generation, bug classification, and log interpretation
"""


class PromptTemplates:
    """Collection of prompt templates for different CogniTest tasks"""

    @staticmethod
    def test_generation_prompt(requirement: str, api_endpoint: str, http_method: str = "POST") -> str:
        """
        Generate prompt for test case generation from requirements.

        Args:
            requirement: Natural language requirement description
            api_endpoint: API endpoint to test
            http_method: HTTP method (GET, POST, PUT, DELETE)

        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""You are an expert Software Development Engineer in Test (SDET). Generate comprehensive pytest test cases based on the following requirement.

**Requirement:**
{requirement}

**API Endpoint:** {api_endpoint}
**HTTP Method:** {http_method}

**Instructions:**
1. Generate pytest test functions with proper fixtures
2. Include parametrize decorators for multiple test scenarios
3. Test both success cases and error cases
4. Include edge cases and boundary conditions
5. Use descriptive test function names
6. Add assertions for status codes and response data
7. Use the 'requests' library for HTTP calls

**Output Format:**
Provide ONLY valid Python code with pytest test functions. Do not include any markdown formatting or explanations outside the code. Start directly with imports.

**Example Structure:**
```python
import pytest
import requests

@pytest.mark.parametrize("input,expected", [...])
def test_scenario_name(input, expected):
    response = requests.{http_method.lower()}("{api_endpoint}", json=input)
    assert response.status_code == expected
```

Generate the complete test code now:"""

        return prompt

    @staticmethod
    def bug_classification_prompt(error_message: str, test_context: str, endpoint: str) -> str:
        """
        Generate prompt for bug severity classification.

        Args:
            error_message: Error message or stack trace
            test_context: Context of the failed test
            endpoint: Affected API endpoint

        Returns:
            Formatted prompt for severity classification
        """
        prompt = f"""You are a senior QA engineer analyzing a software bug. Classify the severity of this bug based on business impact, frequency, and recovery difficulty.

**Failed Test Context:**
{test_context}

**Error Message:**
{error_message}

**Affected Endpoint:**
{endpoint}

**Classification Criteria:**
- **Critical**: Data loss, security vulnerabilities, system crashes, complete feature failure
- **High**: Major functionality broken, significant user impact, no workaround
- **Medium**: Partial functionality broken, moderate user impact, workaround available
- **Low**: Minor issues, cosmetic problems, negligible user impact

**Scoring Factors:**
1. **Impact** (0-10): Business criticality and data integrity
2. **Frequency** (0-10): How often users encounter this
3. **Recovery** (0-10): Difficulty of workaround or fix

**Output Format:**
Provide your analysis in EXACTLY this JSON format (no additional text):
{{
    "severity": "Critical|High|Medium|Low",
    "impact_score": <0-10>,
    "frequency_score": <0-10>,
    "recovery_score": <0-10>,
    "weighted_score": <calculated using weights 0.5, 0.3, 0.2>,
    "reasoning": "Brief explanation of classification"
}}

Analyze and classify now:"""

        return prompt

    @staticmethod
    def log_interpretation_prompt(error_log: str, service_name: str) -> str:
        """
        Generate prompt for log interpretation and root cause analysis.

        Args:
            error_log: Raw error log or stack trace
            service_name: Name of the service that failed

        Returns:
            Formatted prompt for log interpretation
        """
        prompt = f"""You are a debugging expert analyzing a system failure. Provide a clear, human-readable explanation of what went wrong and how to fix it.

**Service:** {service_name}

**Error Log:**
{error_log}

**Your Task:**
1. Identify the root cause of the failure
2. Explain what components are affected
3. Provide actionable remediation steps
4. Suggest preventive measures

**Output Format:**
Provide your analysis in this structure:

**Root Cause:**
<One clear sentence explaining what caused the failure>

**Affected Components:**
<List the impacted services, endpoints, or data>

**Recommended Fix:**
<Step-by-step remediation instructions>

**Prevention:**
<Suggestions to prevent similar issues>

Analyze this error now:"""

        return prompt

    @staticmethod
    def edge_case_generation_prompt(function_spec: str) -> str:
        """
        Generate prompt for edge case identification.

        Args:
            function_spec: Specification of the function to test

        Returns:
            Formatted prompt for edge case generation
        """
        prompt = f"""You are a security-focused SDET specializing in edge case discovery. Identify all possible edge cases for the following function specification.

**Function Specification:**
{function_spec}

**Edge Case Categories to Consider:**
1. **Boundary Values**: Min/max limits, empty inputs, very large inputs
2. **Invalid Input**: Wrong types, malformed data, SQL injection attempts
3. **Concurrency**: Race conditions, simultaneous requests
4. **State Issues**: Duplicate operations, out-of-order operations
5. **Security**: Authentication bypass, privilege escalation
6. **Performance**: Timeout scenarios, resource exhaustion

**Output Format:**
List each edge case with:
- Description of the scenario
- Expected system behavior
- Test data example

Provide at least 8-10 edge cases. Be creative and thorough.

Generate edge cases now:"""

        return prompt


if __name__ == "__main__":
    # Example usage
    templates = PromptTemplates()

    requirement = "Users must register with valid email and strong password (8+ chars, 1 uppercase, 1 lowercase, 1 number)"
    prompt = templates.test_generation_prompt(
        requirement=requirement,
        api_endpoint="http://localhost:8000/api/users/register",
        http_method="POST"
    )

    print(prompt)