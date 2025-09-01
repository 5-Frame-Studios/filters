"""
Organization-specific requirements validation test.
Wrapper for organization-specific validation requirements.
"""

from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationReport
from ..namespace_extractor import NamespaceExtractor


class OrganizationTest(BaseValidatorTest):
    """Test for validating organization-specific requirements."""
    
    def get_test_name(self) -> str:
        return "Organization Requirements"
    
    def get_test_description(self) -> str:
        return "Validates organization-specific requirements like namespace prefix"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate organization-specific requirements."""
        self.log_info("Validating organization-specific requirements...")
        
        # Create namespace extractor instance
        namespace_extractor = NamespaceExtractor(self.settings)
        
        # Validate namespace prefix
        namespace_extractor.validate_namespace_prefix(self.report)
        
        return self.report
