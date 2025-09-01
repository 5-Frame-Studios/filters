"""
Minecraft Creator Tools validation test.
Wrapper for the MCT validator module.
"""

from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationReport
from ..mct_validator import MCTValidator


class MCTTest(BaseValidatorTest):
    """Test for validating with Minecraft Creator Tools."""
    
    def get_test_name(self) -> str:
        return "Minecraft Creator Tools"
    
    def get_test_description(self) -> str:
        return "Validates content using Minecraft Creator Tools"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate with Minecraft Creator Tools."""
        self.log_info("Validating with Minecraft Creator Tools...")
        
        # Create MCT validator instance
        mct_validator = MCTValidator(self.settings)
        
        # Run MCT validation
        mct_validator.validate_with_minecraft_creator_tools(self.report)
        
        return self.report
