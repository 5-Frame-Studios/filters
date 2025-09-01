#!/usr/bin/env python3
"""
Content Validator Filter for Regolith

Comprehensive validation filter for Minecraft Bedrock Add-Ons.
Validates compliance with marketplace guidelines including:
- Namespace requirements and conflicts
- File structure and organization
- Manifest requirements
- Naming conventions
- Technical restrictions
- File size and count limits
- Block permutation limits

Regolith Integration:
- Works in temporary directory with RP/, BP/, and data/ subdirectories
- Non-destructive validation - only reports issues
- Uses environment variables for external file access if needed
- Generates comprehensive validation reports

New Features:
- Modular test system with individual test execution
- Standard API for all validation tests
- Test registry for managing test execution order
"""

import sys
import argparse
from src.validator import MainValidator
from src.utils import parse_settings, get_regolith_environment, logger


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Content Validator for Minecraft Bedrock Add-Ons')
    parser.add_argument('--test', '-t', help='Run a specific test by name')
    parser.add_argument('--list-tests', '-l', action='store_true', help='List all available tests')
    parser.add_argument('--execution-order', '-e', action='store_true', help='Show test execution order')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        logger.info("Content Validator Filter - Starting")
        
        # Parse settings
        settings = parse_settings()
        
        # Get Regolith environment info
        env_info = get_regolith_environment()
        logger.info(f"Working directory: {env_info['WORKING_DIR']}")
        
        # Set log level
        log_level = settings.get('log_level', 'INFO')
        if args.verbose:
            log_level = 'DEBUG'
        import logging
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        # Create validator
        validator = MainValidator(settings)
        
        # Handle different modes
        if args.list_tests:
            print("📋 Available Tests:")
            for i, test_name in enumerate(validator.list_available_tests(), 1):
                print(f"  {i}. {test_name}")
            sys.exit(0)
        
        if args.execution_order:
            print("🔄 Test Execution Order:")
            for i, test_name in enumerate(validator.get_test_execution_order(), 1):
                print(f"  {i}. {test_name}")
            sys.exit(0)
        
        if args.test:
            # Run specific test
            logger.info(f"Running specific test: {args.test}")
            report = validator.run_specific_test(args.test)
            
            if report.is_valid():
                logger.info(f"✅ {args.test} test passed!")
                sys.exit(0)
            else:
                logger.error(f"❌ {args.test} test failed!")
                sys.exit(1)
        
        # Run all tests (default behavior)
        logger.info("Running all validation tests...")
        report = validator.validate_addon()
        
        # Check if we should exit on error
        exit_on_error = settings.get('exit_on_error', True)
        
        # Exit with appropriate code
        if report.is_valid():
            logger.info("✅ Add-On validation passed!")
            sys.exit(0)
        else:
            if exit_on_error:
                logger.error("❌ Add-On validation failed!")
                sys.exit(1)
            else:
                logger.error("❌ Add-On validation failed!")
                logger.info("📊 Continuing due to exit_on_error=false setting")
                sys.exit(0)
            
    except Exception as e:
        logger.error(f"Fatal error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
