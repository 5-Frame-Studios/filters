#!/usr/bin/env python3
"""
Individual test script for namespace validation.
"""

import sys
import os
sys.path.insert(0, '../../src')

from tests.namespace_test import NamespaceTest
from utils import parse_settings, get_regolith_environment, logger
from namespace_extractor import NamespaceExtractor


def main():
    """Run namespace test."""
    try:
        logger.info("Namespace Test - Starting")
        
        # Parse settings
        settings = parse_settings()
        
        # Get Regolith environment info
        env_info = get_regolith_environment()
        logger.info(f"Working directory: {env_info['WORKING_DIR']}")
        
        # Extract namespace info first
        namespace_extractor = NamespaceExtractor(settings)
        namespace_info = namespace_extractor.extract_namespace_info()
        
        # Create test instance
        test = NamespaceTest(settings, namespace_info)
        
        # Get pack paths (Regolith standard)
        pack_paths = {}
        bp_path = "packs/BP"
        rp_path = "packs/RP"
        
        if os.path.exists(bp_path):
            pack_paths['BP'] = bp_path
        if os.path.exists(rp_path):
            pack_paths['RP'] = rp_path
        
        # Run test
        report = test.validate(pack_paths)
        
        # Print results
        print(f"\n📊 {test.get_test_name()} Test Results:")
        print(f"Description: {test.get_test_description()}")
        print(f"✅ Total Files Checked: {report.summary['total_files_checked']}")
        print(f"❌ Errors: {report.summary['total_errors']}")
        print(f"⚠️  Warnings: {report.summary['total_warnings']}")
        print(f"ℹ️  Info: {report.summary['total_info']}")
        print(f"🎯 Valid: {report.summary['is_valid']}")
        
        if report.summary['total_errors'] > 0:
            print("\n🚨 Validation Errors Found:")
            for result in report.results:
                if result.level == 'error':
                    print(f"  - {result.message}")
                    if result.file_path:
                        print(f"    File: {result.file_path}")
        
        if report.summary['total_warnings'] > 0:
            print("\n⚠️  Validation Warnings Found:")
            for result in report.results:
                if result.level == 'warning':
                    print(f"  - {result.message}")
                    if result.file_path:
                        print(f"    File: {result.file_path}")
        
        # Exit with appropriate code
        if report.is_valid():
            logger.info("✅ Namespace Test Passed!")
            sys.exit(0)
        else:
            logger.error("❌ Namespace Test Failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error during namespace test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
