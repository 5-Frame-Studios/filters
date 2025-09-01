#!/usr/bin/env python3
"""
Test script for content validator filter.
This script runs the content validator and checks the results.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_regolith_test():
    """Run the Regolith test with content validator."""
    print("🧪 Running Content Validator Test")
    print("=" * 50)
    
    # Check if we're in the test directory
    if not os.path.exists("config.json"):
        print("❌ Error: Must run from test directory")
        sys.exit(1)
    
    # Run Regolith
    print("📦 Running Regolith with content validator...")
    try:
        result = subprocess.run(['regolith', 'run'], 
                              capture_output=True, text=True, timeout=60)
        
        print("📋 Regolith Output:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Regolith Errors:")
            print("-" * 30)
            print(result.stderr)
        
        # Check if validation report was generated in Regolith temp directory
        report_path = ".regolith/tmp/data/content_validator_report.json"
        # Fallback to regular path for non-Regolith runs
        if not os.path.exists(report_path):
            report_path = "data/content_validator_report.json"
        if os.path.exists(report_path):
            print("\n📊 Validation Report Found!")
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            print(f"✅ Total Files Checked: {report['summary']['total_files_checked']}")
            print(f"❌ Errors: {report['summary']['total_errors']}")
            print(f"⚠️  Warnings: {report['summary']['total_warnings']}")
            print(f"ℹ️  Info: {report['summary']['total_info']}")
            print(f"🎯 Valid: {report['summary']['is_valid']}")
            
            if report['summary']['total_errors'] > 0:
                print("\n🚨 Validation Errors Found:")
                for result in report['results']:
                    if result['level'] == 'error':
                        print(f"  - {result['message']}")
                        if result.get('file_path'):
                            print(f"    File: {result['file_path']}")
            
            if report['summary']['total_warnings'] > 0:
                print("\n⚠️  Validation Warnings Found:")
                for result in report['results']:
                    if result['level'] == 'warning':
                        print(f"  - {result['message']}")
                        if result.get('file_path'):
                            print(f"    File: {result['file_path']}")
            
            return report['summary']['is_valid']
        else:
            print("❌ No validation report found")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Regolith test timed out")
        return False
    except FileNotFoundError:
        print("❌ Regolith not found. Make sure it's installed and in PATH")
        return False
    except Exception as e:
        print(f"❌ Error running Regolith: {e}")
        return False

def main():
    """Main test function."""
    success = run_regolith_test()
    
    if success:
        print("\n✅ Content Validator Test Passed!")
        print("The filter is working correctly.")
    else:
        print("\n❌ Content Validator Test Failed!")
        print("Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
