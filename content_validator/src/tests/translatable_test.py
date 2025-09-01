"""
Translatable text validation test.
Validates that user-facing text is translatable and not hardcoded.
"""

import os
import json
from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import find_pack_directories


class TranslatableTest(BaseValidatorTest):
    """Test for validating translatable text."""
    
    def get_test_name(self) -> str:
        return "Translatable Text"
    
    def get_test_description(self) -> str:
        return "Validates that user-facing text is translatable and not hardcoded"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate that user-facing text is translatable."""
        self.log_info("Validating translatable text...")
        
        pack_dirs = find_pack_directories()
        
        # Check for hardcoded text in various file types
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    # Check for hardcoded text in JSON files
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._check_hardcoded_text_in_json(file_path)
                    break  # Found the first valid path for this pack type
        
        return self.report
    
    def _check_hardcoded_text_in_json(self, file_path: str):
        """Check for hardcoded text in JSON files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._check_hardcoded_text_recursive(data, file_path)
        
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    
    def _check_hardcoded_text_recursive(self, data: Any, file_path: str, path: str = ""):
        """Recursively check for hardcoded text."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self._check_hardcoded_text_recursive(value, file_path, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_hardcoded_text_recursive(item, file_path, current_path)
        elif isinstance(data, str):
            # Check for potential user-facing text
            if len(data) > 3 and not data.startswith('minecraft:') and not data.startswith(self.namespace_info.namespace or ''):
                # Look for common user-facing text patterns
                if any(word in data.lower() for word in ['welcome', 'hello', 'goodbye', 'error', 'success', 'failed']):
                    self.add_result(
                        ValidationLevel.WARNING,
                        f"Potential hardcoded user-facing text found",
                        file_path,
                        context={'text': data, 'path': path}
                    )
