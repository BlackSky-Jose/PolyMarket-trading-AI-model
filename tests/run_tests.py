"""
Test runner script for the PolyMarket Trading AI Model project.
Run this script to test all components.
"""
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Run all test suites."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test modules
    test_modules = [
        "tests.test",
        "tests.test_imports",
        "tests.test_mongodb",
        "tests.test_basic_functionality",
    ]

    for module_name in test_modules:
        try:
            tests = loader.loadTestsFromName(module_name)
            suite.addTests(tests)
            print(f"✓ Loaded tests from {module_name}")
        except Exception as e:
            print(f"✗ Failed to load {module_name}: {e}")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
