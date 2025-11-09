"""
CogniTest Framework - Metrics
Author: Çağrı Temel
Description: Metrics collection and reporting utilities
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TestMetrics:
    """Metrics for test execution"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    execution_time: float = 0.0
    coverage_percentage: float = 0.0
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    edge_cases_found: int = 0

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "pass_rate": round(self.pass_rate, 2),
            "execution_time": round(self.execution_time, 2),
            "coverage_percentage": round(self.coverage_percentage, 2),
            "line_coverage": round(self.line_coverage, 2),
            "branch_coverage": round(self.branch_coverage, 2),
            "edge_cases_found": self.edge_cases_found
        }


@dataclass
class GenerationMetrics:
    """Metrics for test generation"""
    requirements_processed: int = 0
    tests_generated: int = 0
    generation_time: float = 0.0
    average_time_per_test: float = 0.0
    total_lines_generated: int = 0
    syntax_errors: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "requirements_processed": self.requirements_processed,
            "tests_generated": self.tests_generated,
            "generation_time": round(self.generation_time, 2),
            "average_time_per_test": round(self.average_time_per_test, 2),
            "total_lines_generated": self.total_lines_generated,
            "syntax_errors": self.syntax_errors
        }


@dataclass
class ClassificationMetrics:
    """Metrics for bug classification"""
    total_classifications: int = 0
    critical_bugs: int = 0
    high_bugs: int = 0
    medium_bugs: int = 0
    low_bugs: int = 0
    classification_time: float = 0.0
    accuracy: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "total_classifications": self.total_classifications,
            "severity_distribution": {
                "critical": self.critical_bugs,
                "high": self.high_bugs,
                "medium": self.medium_bugs,
                "low": self.low_bugs
            },
            "classification_time": round(self.classification_time, 2),
            "accuracy": round(self.accuracy, 2)
        }


class MetricsCollector:
    """Collects and aggregates metrics from CogniTest framework"""

    def __init__(self):
        self.test_metrics = TestMetrics()
        self.generation_metrics = GenerationMetrics()
        self.classification_metrics = ClassificationMetrics()
        self.start_time: Optional[float] = None
        self.timestamps: List[Dict] = []

    def start_timer(self, label: str = "operation"):
        """Start timing an operation"""
        self.start_time = time.time()
        self.timestamps.append({
            "label": label,
            "start": datetime.now().isoformat(),
            "start_time": self.start_time
        })

    def stop_timer(self) -> float:
        """Stop timer and return elapsed time"""
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time

        if self.timestamps:
            self.timestamps[-1]["end"] = datetime.now().isoformat()
            self.timestamps[-1]["duration"] = elapsed

        self.start_time = None
        return elapsed

    def record_test_execution(
            self,
            total: int,
            passed: int,
            failed: int,
            skipped: int = 0,
            execution_time: float = 0.0,
            coverage: float = 0.0,
            line_cov: float = 0.0,
            branch_cov: float = 0.0
    ):
        """Record test execution metrics"""
        self.test_metrics.total_tests = total
        self.test_metrics.passed_tests = passed
        self.test_metrics.failed_tests = failed
        self.test_metrics.skipped_tests = skipped
        self.test_metrics.execution_time = execution_time
        self.test_metrics.coverage_percentage = coverage
        self.test_metrics.line_coverage = line_cov
        self.test_metrics.branch_coverage = branch_cov

    def record_generation(
            self,
            requirements: int,
            tests: int,
            time_taken: float,
            lines: int,
            errors: int = 0
    ):
        """Record test generation metrics"""
        self.generation_metrics.requirements_processed = requirements
        self.generation_metrics.tests_generated = tests
        self.generation_metrics.generation_time = time_taken
        self.generation_metrics.total_lines_generated = lines
        self.generation_metrics.syntax_errors = errors

        if tests > 0:
            self.generation_metrics.average_time_per_test = time_taken / tests

    def record_classification(
            self,
            total: int,
            critical: int,
            high: int,
            medium: int,
            low: int,
            time_taken: float,
            accuracy: float = 0.0
    ):
        """Record bug classification metrics"""
        self.classification_metrics.total_classifications = total
        self.classification_metrics.critical_bugs = critical
        self.classification_metrics.high_bugs = high
        self.classification_metrics.medium_bugs = medium
        self.classification_metrics.low_bugs = low
        self.classification_metrics.classification_time = time_taken
        self.classification_metrics.accuracy = accuracy

    def get_all_metrics(self) -> Dict:
        """Get all metrics as dictionary"""
        return {
            "test_execution": self.test_metrics.to_dict(),
            "test_generation": self.generation_metrics.to_dict(),
            "bug_classification": self.classification_metrics.to_dict(),
            "timestamps": self.timestamps
        }

    def save_metrics(self, filepath: str):
        """Save metrics to JSON file"""
        metrics = self.get_all_metrics()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

    def generate_report(self) -> str:
        """Generate human-readable metrics report"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    COGNITEST METRICS REPORT                   ║
╚══════════════════════════════════════════════════════════════╝

TEST EXECUTION METRICS
──────────────────────────────────────────────────────────────
  Total Tests:           {self.test_metrics.total_tests}
  Passed:                {self.test_metrics.passed_tests}
  Failed:                {self.test_metrics.failed_tests}
  Skipped:               {self.test_metrics.skipped_tests}
  Pass Rate:             {self.test_metrics.pass_rate:.2f}%
  Execution Time:        {self.test_metrics.execution_time:.2f}s

COVERAGE METRICS
──────────────────────────────────────────────────────────────
  Overall Coverage:      {self.test_metrics.coverage_percentage:.2f}%
  Line Coverage:         {self.test_metrics.line_coverage:.2f}%
  Branch Coverage:       {self.test_metrics.branch_coverage:.2f}%
  Edge Cases Found:      {self.test_metrics.edge_cases_found}

TEST GENERATION METRICS
──────────────────────────────────────────────────────────────
  Requirements:          {self.generation_metrics.requirements_processed}
  Tests Generated:       {self.generation_metrics.tests_generated}
  Generation Time:       {self.generation_metrics.generation_time:.2f}s
  Avg Time/Test:         {self.generation_metrics.average_time_per_test:.2f}s
  Lines Generated:       {self.generation_metrics.total_lines_generated}
  Syntax Errors:         {self.generation_metrics.syntax_errors}

BUG CLASSIFICATION METRICS
──────────────────────────────────────────────────────────────
  Total Classified:      {self.classification_metrics.total_classifications}
  Critical:              {self.classification_metrics.critical_bugs}
  High:                  {self.classification_metrics.high_bugs}
  Medium:                {self.classification_metrics.medium_bugs}
  Low:                   {self.classification_metrics.low_bugs}
  Classification Time:   {self.classification_metrics.classification_time:.2f}s
  Accuracy:              {self.classification_metrics.accuracy:.2f}%

═════════════════════════════════════════════════════════════════
"""
        return report


if __name__ == "__main__":
    # Example usage
    collector = MetricsCollector()

    # Record test execution
    collector.record_test_execution(
        total=100,
        passed=95,
        failed=5,
        execution_time=45.3,
        coverage=91.2,
        line_cov=91.2,
        branch_cov=84.9
    )

    # Record generation
    collector.record_generation(
        requirements=5,
        tests=30,
        time_taken=16.5,
        lines=450
    )

    # Record classification
    collector.record_classification(
        total=156,
        critical=12,
        high=34,
        medium=78,
        low=32,
        time_taken=89.2,
        accuracy=91.7
    )

    print(collector.generate_report())