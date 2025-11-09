"""
Bug Classification Experiment
Author: Cagri Temel
Description: Evaluate bug severity classification accuracy
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cognitest.core.bug_classifier import BugClassifier, Severity
from cognitest.utils.metrics import MetricsCollector


def load_ground_truth_bugs() -> List[Dict]:
    """
    Load sample bugs with ground truth severity labels
    These would typically come from expert SDET ratings
    """
    bugs = [
        {
            "id": 1,
            "error_message": "Database connection timeout after 30 seconds",
            "test_context": "test_user_registration - User cannot complete registration",
            "endpoint": "/api/users/register",
            "ground_truth": "Critical"
        },
        {
            "id": 2,
            "error_message": "AssertionError: assert 500 == 200",
            "test_context": "test_create_order - Internal server error on order creation",
            "endpoint": "/api/orders",
            "ground_truth": "High"
        },
        {
            "id": 3,
            "error_message": "ValidationError: Email format invalid",
            "test_context": "test_user_registration - Email validation not working",
            "endpoint": "/api/users/register",
            "ground_truth": "Medium"
        },
        {
            "id": 4,
            "error_message": "Typo in error message: 'Pasword' instead of 'Password'",
            "test_context": "test_user_login - Error message has spelling mistake",
            "endpoint": "/api/users/login",
            "ground_truth": "Low"
        },
        {
            "id": 5,
            "error_message": "SQL Injection vulnerability: unescaped user input in query",
            "test_context": "test_search_products - Security vulnerability detected",
            "endpoint": "/api/products/search",
            "ground_truth": "Critical"
        },
        {
            "id": 6,
            "error_message": "Payment gateway returns 500 error for valid card",
            "test_context": "test_process_payment - Payment fails with valid data",
            "endpoint": "/api/payments",
            "ground_truth": "Critical"
        },
        {
            "id": 7,
            "error_message": "Order status not updating after payment confirmation",
            "test_context": "test_order_workflow - Status remains 'pending'",
            "endpoint": "/api/orders",
            "ground_truth": "High"
        },
        {
            "id": 8,
            "error_message": "Pagination returns incorrect total count",
            "test_context": "test_list_orders - Total count shows 105 instead of 100",
            "endpoint": "/api/orders",
            "ground_truth": "Medium"
        },
        {
            "id": 9,
            "error_message": "Response time exceeds 3 seconds for simple query",
            "test_context": "test_get_user_profile - Performance degradation",
            "endpoint": "/api/users/profile",
            "ground_truth": "Medium"
        },
        {
            "id": 10,
            "error_message": "Button color slightly off brand guidelines",
            "test_context": "test_ui_consistency - Visual inconsistency",
            "endpoint": "/ui/checkout",
            "ground_truth": "Low"
        },
        {
            "id": 11,
            "error_message": "Race condition: Concurrent orders create duplicate entries",
            "test_context": "test_concurrent_orders - Data integrity issue",
            "endpoint": "/api/orders",
            "ground_truth": "Critical"
        },
        {
            "id": 12,
            "error_message": "Password reset token expires after 10 minutes instead of 60",
            "test_context": "test_password_reset - Token expiration too short",
            "endpoint": "/api/users/reset-password",
            "ground_truth": "High"
        },
        {
            "id": 13,
            "error_message": "Search returns results even with empty query",
            "test_context": "test_search_validation - Should return empty for blank search",
            "endpoint": "/api/search",
            "ground_truth": "Low"
        },
        {
            "id": 14,
            "error_message": "Session timeout not working, user stays logged in indefinitely",
            "test_context": "test_session_management - Security concern",
            "endpoint": "/api/auth/session",
            "ground_truth": "High"
        },
        {
            "id": 15,
            "error_message": "Loading spinner disappears before data loads",
            "test_context": "test_ui_loading_state - UX issue",
            "endpoint": "/ui/dashboard",
            "ground_truth": "Medium"
        }
    ]

    return bugs


def calculate_accuracy_metrics(predictions: List[str], ground_truth: List[str]) -> Dict:
    """
    Calculate precision, recall, F1-score for each severity class
    """
    from collections import defaultdict

    # Initialize counters
    tp = defaultdict(int)  # True positives
    fp = defaultdict(int)  # False positives
    fn = defaultdict(int)  # False negatives

    severity_classes = ["Critical", "High", "Medium", "Low"]

    # Calculate TP, FP, FN for each class
    for pred, truth in zip(predictions, ground_truth):
        if pred == truth:
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[truth] += 1

    # Calculate metrics for each class
    metrics = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for severity in severity_classes:
        precision = tp[severity] / (tp[severity] + fp[severity]) if (tp[severity] + fp[severity]) > 0 else 0
        recall = tp[severity] / (tp[severity] + fn[severity]) if (tp[severity] + fn[severity]) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics[severity] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "support": tp[severity] + fn[severity]
        }

        total_tp += tp[severity]
        total_fp += fp[severity]
        total_fn += fn[severity]

    # Calculate overall accuracy
    total_predictions = len(predictions)
    correct_predictions = sum(1 for p, t in zip(predictions, ground_truth) if p == t)
    overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0

    # Calculate weighted averages
    total_samples = sum(m["support"] for m in metrics.values())
    weighted_precision = sum(
        m["precision"] * m["support"] for m in metrics.values()) / total_samples if total_samples > 0 else 0
    weighted_recall = sum(
        m["recall"] * m["support"] for m in metrics.values()) / total_samples if total_samples > 0 else 0
    weighted_f1 = sum(
        m["f1_score"] * m["support"] for m in metrics.values()) / total_samples if total_samples > 0 else 0

    metrics["weighted_avg"] = {
        "precision": round(weighted_precision, 3),
        "recall": round(weighted_recall, 3),
        "f1_score": round(weighted_f1, 3)
    }

    metrics["overall_accuracy"] = round(overall_accuracy, 3)

    return metrics


def main():
    """Run bug classification experiment"""
    print("\n" + "=" * 60)
    print("BUG CLASSIFICATION EXPERIMENT - CogniTest Framework")
    print("=" * 60)

    collector = MetricsCollector()

    # Load sample bugs
    bugs = load_ground_truth_bugs()

    print("\nLoaded {} bugs with ground truth labels".format(len(bugs)))
    print("Initializing Bug Classifier...\n")

    try:
        classifier = BugClassifier()
    except Exception as e:
        print("ERROR: Failed to initialize BugClassifier")
        print("Error message: {}".format(str(e)))
        print("\nNote: LLM model loading requires significant memory.")
        return

    # Classify all bugs
    predictions = []
    ground_truths = []
    classification_results = []

    collector.start_timer("bug_classification")

    for idx, bug in enumerate(bugs, 1):
        print("  [{}/{}] Classifying bug ID {}...".format(idx, len(bugs), bug['id']))

        try:
            classification = classifier.classify(
                error_message=bug['error_message'],
                test_context=bug['test_context'],
                endpoint=bug['endpoint']
            )

            predictions.append(classification['severity'])
            ground_truths.append(bug['ground_truth'])

            classification_results.append({
                "bug_id": bug['id'],
                "endpoint": bug['endpoint'],
                "predicted": classification['severity'],
                "ground_truth": bug['ground_truth'],
                "correct": classification['severity'] == bug['ground_truth'],
                "weighted_score": classification['weighted_score'],
                "reasoning": classification.get('reasoning', '')
            })

            status = "CORRECT" if classification['severity'] == bug['ground_truth'] else "INCORRECT"
            print("    Predicted: {} | Ground Truth: {} | {}".format(
                classification['severity'],
                bug['ground_truth'],
                status
            ))

        except Exception as e:
            print("    ERROR: {}".format(str(e)))
            continue

    classification_time = collector.stop_timer()

    # Calculate accuracy metrics
    print("\nCalculating accuracy metrics...")
    metrics = calculate_accuracy_metrics(predictions, ground_truths)

    # Count bugs by severity
    severity_counts = {
        "Critical": sum(1 for p in predictions if p == "Critical"),
        "High": sum(1 for p in predictions if p == "High"),
        "Medium": sum(1 for p in predictions if p == "Medium"),
        "Low": sum(1 for p in predictions if p == "Low")
    }

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    print("\nClassification Distribution:")
    for severity, count in severity_counts.items():
        print("  {}: {}".format(severity, count))

    print("\nOverall Accuracy: {:.1f}%".format(metrics['overall_accuracy'] * 100))

    print("\nPer-Class Metrics:")
    print("-" * 60)
    print("{:<12} {:<12} {:<12} {:<12}".format("Severity", "Precision", "Recall", "F1-Score"))
    print("-" * 60)

    for severity in ["Critical", "High", "Medium", "Low"]:
        if severity in metrics:
            m = metrics[severity]
            print("{:<12} {:<12.3f} {:<12.3f} {:<12.3f}".format(
                severity, m['precision'], m['recall'], m['f1_score']
            ))

    print("-" * 60)
    print("{:<12} {:<12.3f} {:<12.3f} {:<12.3f}".format(
        "Weighted Avg",
        metrics['weighted_avg']['precision'],
        metrics['weighted_avg']['recall'],
        metrics['weighted_avg']['f1_score']
    ))

    print("\nClassification Time: {:.2f} seconds".format(classification_time))
    print("Average Time per Bug: {:.2f} seconds".format(classification_time / len(bugs)))

    # Record metrics
    collector.record_classification(
        total=len(bugs),
        critical=severity_counts["Critical"],
        high=severity_counts["High"],
        medium=severity_counts["Medium"],
        low=severity_counts["Low"],
        time_taken=classification_time,
        accuracy=metrics['overall_accuracy'] * 100
    )

    # Save results
    results = {
        "total_bugs": len(bugs),
        "classification_time_seconds": classification_time,
        "overall_accuracy": metrics['overall_accuracy'],
        "severity_distribution": severity_counts,
        "per_class_metrics": {
            k: v for k, v in metrics.items()
            if k not in ['weighted_avg', 'overall_accuracy']
        },
        "weighted_averages": metrics['weighted_avg'],
        "detailed_results": classification_results
    }

    # Create results directory
    results_dir = Path("data/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save results
    with open(results_dir / "classification_experiment.json", 'w') as f:
        json.dump(results, f, indent=2)

    collector.save_metrics(str(results_dir / "classification_metrics.json"))

    print("\nResults saved to: data/results/classification_experiment.json")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()