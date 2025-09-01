"""
File structure validation test.
Wrapper for the file validator module.
"""

from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationReport
from ..file_validator import FileValidator


class FileStructureTest(BaseValidatorTest):
    """Test for validating file structure."""
    
    def get_test_name(self) -> str:
        return "File Structure"
    
    def get_test_description(self) -> str:
        return "Validates file structure, size limits, and organization requirements"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate file structure."""
        self.log_info("Validating file structure...")
        
        # Create file validator instance with namespace info
        file_validator = FileValidator(self.settings, self.namespace_info)
        
        # Run file structure validation
        file_validator.validate_file_structure(self.report)
        file_validator.validate_size_limits(self.report)
        file_validator.validate_block_permutations(self.report)
        file_validator.validate_guidebook_requirements(self.report)
        file_validator.validate_folder_depth(self.report)
        file_validator.validate_subcategory_limits(self.report)
        
        return self.report
