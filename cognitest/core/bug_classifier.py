"""
CogniTest Framework - Bug Classifier
Author: Çağrı Temel
Description: Automated bug severity classification using LLM
"""

import json
import re
from typing import Dict, Optional, List
import logging
from enum import Enum

from cognitest.core.llm_engine import LLMEngine
from cognitest.utils.prompt_templates import PromptTemplates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """Bug severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class BugClassifier:
    """
    Classifies bug severity using LLM-based analysis.
    """

    def __init__(self, llm_engine: Optional[LLMEngine] = None):
        """
        Initialize bug classifier.

        Args:
            llm_engine: LLM engine instance (creates new if None)
        """
        self.llm_engine = llm_engine or LLMEngine()
        self.templates = PromptTemplates()
        self.classification_history = []

    def classify(
            self,
            error_message: str,
            test_context: str,
            endpoint: str
    ) -> Dict:
        """
        Classify bug severity.

        Args:
            error_message: Error message or stack trace
            test_context: Context of the failed test
            endpoint: Affected API endpoint

        Returns:
            Classification result with severity, scores, and reasoning
        """
        logger.info(f"Classifying bug for endpoint: {endpoint}")

        # Create prompt
        prompt = self.templates.bug_classification_prompt(
            error_message=error_message,
            test_context=test_context,
            endpoint=endpoint
        )

        # Generate classification
        response = self.llm_engine.generate(prompt, temperature=0.2)

        # Parse JSON response
        classification = self._parse_classification(response)

        # Validate and adjust if needed
        classification = self._validate_classification(classification)

        # Store in history
        self.classification_history.append({
            "endpoint": endpoint,
            "classification": classification
        })

        logger.info(f"Classification: {classification['severity']} (score: {classification['weighted_score']:.2f})")
        return classification

    def classify_batch(
            self,
            bugs: List[Dict]
    ) -> List[Dict]:
        """
        Classify multiple bugs in batch.

        Args:
            bugs: List of bug dictionaries with error_message, test_context, endpoint

        Returns:
            List of classification results
        """
        results = []

        for bug in bugs:
            classification = self.classify(
                error_message=bug['error_message'],
                test_context=bug.get('test_context', ''),
                endpoint=bug['endpoint']
            )
            results.append({
                **bug,
                "classification": classification
            })

        return results

    def _parse_classification(self, response: str) -> Dict:
        """Parse LLM response into structured classification"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                classification = json.loads(json_str)
            else:
                # Fallback parsing
                classification = self._fallback_parse(response)

            # Calculate weighted score if not present
            if 'weighted_score' not in classification:
                classification['weighted_score'] = (
                        0.5 * classification.get('impact_score', 5) +
                        0.3 * classification.get('frequency_score', 5) +
                        0.2 * classification.get('recovery_score', 5)
                )

            return classification

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification: {e}")
            return self._default_classification()

    def _fallback_parse(self, response: str) -> Dict:
        """Fallback parsing when JSON extraction fails"""
        severity = Severity.MEDIUM.value

        # Try to extract severity from text
        if "critical" in response.lower():
            severity = Severity.CRITICAL.value
        elif "high" in response.lower():
            severity = Severity.HIGH.value
        elif "low" in response.lower():
            severity = Severity.LOW.value

        return {
            "severity": severity,
            "impact_score": 5,
            "frequency_score": 5,
            "recovery_score": 5,
            "weighted_score": 5.0,
            "reasoning": "Parsed from unstructured response"
        }

    def _default_classification(self) -> Dict:
        """Default classification when parsing fails"""
        return {
            "severity": Severity.MEDIUM.value,
            "impact_score": 5,
            "frequency_score": 5,
            "recovery_score": 5,
            "weighted_score": 5.0,
            "reasoning": "Default classification due to parsing error"
        }

    def _validate_classification(self, classification: Dict) -> Dict:
        """Validate and adjust classification if needed"""
        # Ensure severity is valid
        valid_severities = [s.value for s in Severity]
        if classification.get('severity') not in valid_severities:
            classification['severity'] = Severity.MEDIUM.value

        # Ensure scores are in range 0-10
        for score_key in ['impact_score', 'frequency_score', 'recovery_score']:
            if score_key in classification:
                classification[score_key] = max(0, min(10, classification[score_key]))

        # Recalculate weighted score
        classification['weighted_score'] = (
                0.5 * classification.get('impact_score', 5) +
                0.3 * classification.get('frequency_score', 5) +
                0.2 * classification.get('recovery_score', 5)
        )

        return classification

    def get_statistics(self) -> Dict:
        """Get classification statistics"""
        if not self.classification_history:
            return {
                "total_classifications": 0,
                "severity_distribution": {},
                "average_weighted_score": 0.0
            }

        severity_counts = {}
        total_score = 0

        for item in self.classification_history:
            severity = item['classification']['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            total_score += item['classification']['weighted_score']

        return {
            "total_classifications": len(self.classification_history),
            "severity_distribution": severity_counts,
            "average_weighted_score": total_score / len(self.classification_history)
        }


if __name__ == "__main__":
    # Example usage
    classifier = BugClassifier()

    result = classifier.classify(
        error_message="AssertionError: assert 500 == 200",
        test_context="Test user registration with invalid email format",
        endpoint="/api/users/register"
    )

    print("Classification Result:")
    print(json.dumps(result, indent=2))
    print("\nStatistics:", classifier.get_statistics())