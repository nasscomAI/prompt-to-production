"""
Master Integration and Verification Test Suite
Discovers and runs all unit & integration tests across all four problems.
"""
import unittest
import sys
import os

def run_suite():
    # Setup PYTHONPATH so that modules can be discovered properly
    repo_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(repo_root, "uc-0a"))
    sys.path.insert(0, os.path.join(repo_root, "uc-0b"))
    sys.path.insert(0, os.path.join(repo_root, "uc-0c"))
    sys.path.insert(0, os.path.join(repo_root, "uc-x"))

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add tests from each subdirectory
    print("Discovering tests for P1 (UC-0A)...")
    p1_tests = loader.discover(start_dir=os.path.join(repo_root, "uc-0a"), pattern="test_*.py")
    suite.addTests(p1_tests)

    print("Discovering tests for P2 (UC-0B)...")
    p2_tests = loader.discover(start_dir=os.path.join(repo_root, "uc-0b"), pattern="test_*.py")
    suite.addTests(p2_tests)

    print("Discovering tests for P3 (UC-0C)...")
    p3_tests = loader.discover(start_dir=os.path.join(repo_root, "uc-0c"), pattern="test_*.py")
    suite.addTests(p3_tests)

    print("Discovering tests for P4 (UC-X)...")
    p4_tests = loader.discover(start_dir=os.path.join(repo_root, "uc-x"), pattern="test_*.py")
    suite.addTests(p4_tests)

    print("\nRunning all test suites...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print("\nTest Run FAILED!")
        sys.exit(1)
    else:
        print("\nAll Test Suites Passed Successfully! (100% PASS)")
        sys.exit(0)

if __name__ == "__main__":
    run_suite()
