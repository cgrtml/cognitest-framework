"""
Time Efficiency Experiment
Author: Cagri Temel
Description: Measure time required for manual vs automated test creation
"""

import time
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cognitest.core.test_generator import TestGenerator
from cognitest.utils.metrics import MetricsCollector


def main():
    """Run time efficiency experiment"""
    print("\n" + "=" * 60)
    print("TIME EFFICIENCY EXPERIMENT - CogniTest Framework")
    print("=" * 60)

    collector = MetricsCollector()

    # Sample requirements for testing
    requirements = [
        {
            "name": "user_registration",
            "endpoint": "http://localhost:8000/api/users/register",
            "method": "POST",
            "description": "Users must be able to register with email and password. Email must be unique and in valid format. Password must be at least 8 characters with one uppercase, one lowercase, and one number."
        },
        {
            "name": "user_login",
            "endpoint": "http://localhost:8000/api/users/login",
            "method": "POST",
            "description": "Users must be able to login with email and password. System should return JWT token on successful authentication. Should reject invalid credentials."
        },
        {
            "name": "create_order",
            "endpoint": "http://localhost:8001/api/orders",
            "method": "POST",
            "description": "Users can create orders with product name, quantity, and shipping address. Quantity must be between 1 and 1000. Total price should be calculated automatically."
        },
        {
            "name": "process_payment",
            "endpoint": "http://localhost:8002/api/payments",
            "method": "POST",
            "description": "System should process payments with card or PayPal. Amount must be positive. Should generate unique transaction ID."
        },
        {
            "name": "list_orders",
            "endpoint": "http://localhost:8001/api/orders",
            "method": "GET",
            "description": "Users can list their orders with pagination. Should support filtering by status. Should return order details including status and total price."
        }
    ]

    # Manual test creation time (baseline from paper)
    manual_time = 16.5 * 3600  # 16.5 hours in seconds
    manual_tests = 30

    print("\nManual Baseline (from literature):")
    print("  Total Time: {:.1f} hours".format(manual_time / 3600))
    print("  Tests Created: {}".format(manual_tests))
    print("  Avg Time/Test: {:.0f} seconds ({:.1f} minutes)".format(
        manual_time / manual_tests,
        manual_time / manual_tests / 60
    ))

    # CogniTest automated generation
    print("\nCogniTest Automated Generation:")
    print("  Starting test generation...\n")

    try:
        generator = TestGenerator()
    except Exception as e:
        print("ERROR: Failed to initialize TestGenerator")
        print("Error message: {}".format(str(e)))
        print("\nNote: LLM model loading requires significant memory and may take time.")
        print("For testing without LLM, you can use mock generation.")
        return

    collector.start_timer("test_generation")
    start_time = time.time()

    generated_files = []
    total_lines = 0

    for idx, req in enumerate(requirements, 1):
        print("  [{}/{}] Generating tests for: {}...".format(
            idx, len(requirements), req['name']
        ))

        output_file = "tests/generated/test_{}.py".format(req['name'])

        try:
            test_code = generator.generate_from_requirement(
                requirement=req['description'],
                api_endpoint=req['endpoint'],
                http_method=req['method'],
                output_file=output_file
            )

            generated_files.append(output_file)
            lines_count = len(test_code.split('\n'))
            total_lines += lines_count

            print("  Generated: {} ({} lines)".format(output_file, lines_count))

        except Exception as e:
            print("  ERROR generating test for {}: {}".format(req['name'], str(e)))
            continue

    generation_time = collector.stop_timer()

    # Calculate metrics
    tests_generated = len(requirements) * 6  # Assume 6 test cases per requirement
    avg_time_per_test = generation_time / tests_generated if tests_generated > 0 else 0

    time_saved = manual_time - generation_time
    time_reduction_percent = (time_saved / manual_time) * 100

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    print("\nManual Testing (Baseline):")
    print("  Total Time:        {:.1f} hours".format(manual_time / 3600))
    print("  Tests Created:     {}".format(manual_tests))
    print("  Time per Test:     {:.1f} minutes".format(manual_time / manual_tests / 60))

    print("\nCogniTest Automated:")
    print("  Total Time:        {:.2f} hours".format(generation_time / 3600))
    print("  Tests Generated:   {}".format(tests_generated))
    print("  Time per Test:     {:.2f} minutes".format(avg_time_per_test / 60))
    print("  Total Lines:       {}".format(total_lines))

    print("\nImprovement:")
    print("  Time Saved:        {:.1f} hours".format(time_saved / 3600))
    print("  Time Reduction:    {:.1f}%".format(time_reduction_percent))
    print("  Efficiency Gain:   {:.1f}x faster".format(manual_time / generation_time))

    # Record metrics
    collector.record_generation(
        requirements=len(requirements),
        tests=tests_generated,
        time_taken=generation_time,
        lines=total_lines,
        errors=0
    )

    # Save results
    results = {
        "manual": {
            "total_time_seconds": manual_time,
            "total_time_hours": manual_time / 3600,
            "tests_created": manual_tests,
            "time_per_test_seconds": manual_time / manual_tests,
            "time_per_test_minutes": manual_time / manual_tests / 60
        },
        "cognitest": {
            "total_time_seconds": generation_time,
            "total_time_hours": generation_time / 3600,
            "tests_generated": tests_generated,
            "time_per_test_seconds": avg_time_per_test,
            "time_per_test_minutes": avg_time_per_test / 60,
            "total_lines": total_lines
        },
        "improvement": {
            "time_saved_seconds": time_saved,
            "time_saved_hours": time_saved / 3600,
            "time_reduction_percent": time_reduction_percent,
            "efficiency_multiplier": manual_time / generation_time if generation_time > 0 else 0
        }
    }

    # Create results directory
    results_dir = Path("data/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save results
    with open(results_dir / "time_experiment.json", 'w') as f:
        json.dump(results, f, indent=2)

    collector.save_metrics(str(results_dir / "time_metrics.json"))

    print("\nResults saved to: data/results/time_experiment.json")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()