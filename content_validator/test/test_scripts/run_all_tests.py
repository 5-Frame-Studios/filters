#!/usr/bin/env python3
"""
Script to run all individual validation tests.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, '../../src')

from tests.test_registry import test_registry
from utils import parse_settings, get_regolith_environment, logger


def run_individual_test(test_name: str) -> bool:
    """Run an individual test script."""
    test_script = f"test_{test_name.lower().replace(' ', '_')}.py"
    test_path = Path(__file__).parent / test_script
    
    if not test_path.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    print(f"\n🧪 Running {test_name} Test...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, str(test_path)], 
                               capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running {test_name} test: {e}")
        return False


def main():
    """Run all individual tests."""
    print("🧪 Running All Individual Tests")
    print("=" * 60)
    
    # Get list of available tests
    available_tests = test_registry.list_tests()
    execution_order = test_registry.get_execution_order()
    
    print(f"📋 Found {len(available_tests)} tests:")
    for i, test_name in enumerate(execution_order, 1):
        print(f"  {i}. {test_name}")
    
    print(f"\n🔄 Running tests in execution order...")
    
    # Track results
    passed_tests = []
    failed_tests = []
    
    # Run each test
    for test_name in execution_order:
        success = run_individual_test(test_name)
        if success:
            passed_tests.append(test_name)
        else:
            failed_tests.append(test_name)
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {len(passed_tests)}/{len(available_tests)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(available_tests)}")
    
    if passed_tests:
        print(f"\n✅ Passed Tests:")
        for test_name in passed_tests:
            print(f"  - {test_name}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    
    # Exit with appropriate code
    if failed_tests:
        print(f"\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
