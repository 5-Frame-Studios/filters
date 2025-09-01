"""
Manifest validation test.
Wrapper for the manifest validator module.
"""

from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationReport
from ..manifest_validator import ManifestValidator


class ManifestTest(BaseValidatorTest):
    """Test for validating manifests."""
    
    def get_test_name(self) -> str:
        return "Manifest Validation"
    
    def get_test_description(self) -> str:
        return "Validates manifest requirements and format"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate manifests."""
        self.log_info("Validating manifests...")
        
        # Create manifest validator instance
        manifest_validator = ManifestValidator(self.settings)
        
        # Run manifest validation
        manifest_validator.validate_manifests(self.report)
        manifest_validator.validate_version_format(self.report)
        
        return self.report
