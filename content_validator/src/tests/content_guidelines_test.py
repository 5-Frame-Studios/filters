"""
Content guidelines validation test.
Wrapper for the content validator module.
"""

from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationReport
from ..content_validator import ContentValidator


class ContentGuidelinesTest(BaseValidatorTest):
    """Test for validating content guidelines."""
    
    def get_test_name(self) -> str:
        return "Content Guidelines"
    
    def get_test_description(self) -> str:
        return "Validates Add-On guidelines compliance"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate content guidelines."""
        self.log_info("Validating content guidelines...")
        
        # Create content validator instance
        content_validator = ContentValidator(self.settings)
        
        # Run content guidelines validation
        content_validator.validate_addon_guidelines(self.report)
        
        return self.report
