"""
Debug statement validation test.
Validates that debug statements are removed from the final content.
"""

import os
from typing import Dict, Any, List
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import find_pack_directories


class DebugTest(BaseValidatorTest):
    """Test for validating debug statements."""
    
    def get_test_name(self) -> str:
        return "Debug Statements"
    
    def get_test_description(self) -> str:
        return "Validates that debug statements are removed from the final content"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate that debug statements are removed."""
        self.log_info("Validating debug statements...")
        
        debug_patterns = self.settings.get('organization_specific', {}).get('debug_statement_patterns', [])
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith(('.json', '.js', '.mcfunction')):
                                file_path = os.path.join(root, file)
                                self._check_debug_statements_in_file(file_path, debug_patterns)
                    break  # Found the first valid path for this pack type
        
        return self.report
    
    def _check_debug_statements_in_file(self, file_path: str, debug_patterns: List[str]):
        """Check for debug statements in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in debug_patterns:
                if pattern.lower() in content.lower():
                    self.add_result(
                        ValidationLevel.WARNING,
                        f"Debug statement found: '{pattern}'",
                        file_path,
                        context={'pattern': pattern}
                    )
        
        except (UnicodeDecodeError, OSError):
            pass
