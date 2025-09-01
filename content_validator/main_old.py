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
"""

import sys
from src.validator import MainValidator
from src.utils import parse_settings, get_regolith_environment, logger


def main():
    """Main entry point."""
    try:
        logger.info("Content Validator Filter - Starting")
        
        # Parse settings
        settings = parse_settings()
        
        # Get Regolith environment info
        env_info = get_regolith_environment()
        logger.info(f"Working directory: {env_info['WORKING_DIR']}")
        
        # Set log level
        log_level = settings.get('log_level', 'INFO')
        logger.setLevel(getattr(logger, log_level.upper()))
        
        # Create validator
        validator = MainValidator(settings)
        
        # Run validation
        report = validator.validate_addon()
        
        # Exit with appropriate code
        if report.is_valid():
            logger.info("✅ Add-On validation passed!")
            sys.exit(0)
        else:
            logger.error("❌ Add-On validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
