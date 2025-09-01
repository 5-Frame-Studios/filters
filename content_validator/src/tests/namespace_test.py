"""
Namespace validation test.
Validates namespace usage across all files and checks for forbidden namespaces.
"""

import os
import json
from typing import Dict, Any, List
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import find_pack_directories


class NamespaceTest(BaseValidatorTest):
    """Test for validating namespace usage."""
    
    def get_test_name(self) -> str:
        return "Namespace Usage"
    
    def get_test_description(self) -> str:
        return "Validates namespace usage across all files and checks for forbidden namespaces"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate namespace usage."""
        self.log_info("Validating namespace usage...")
        
        if not self.namespace_info or not self.namespace_info.namespace:
            self.add_result(
                ValidationLevel.ERROR,
                "No valid namespace detected"
            )
            return self.report
        
        # Check for forbidden namespace usage
        forbidden_namespaces = self.settings.get('forbidden_namespaces', [])
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._validate_namespace_in_file(file_path, forbidden_namespaces)
                    break  # Found the first valid path for this pack type
        
        return self.report
    
    def _validate_namespace_in_file(self, file_path: str, forbidden_namespaces: List[str]):
        """Validate namespace usage in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._check_namespace_recursive(data, forbidden_namespaces, file_path)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # Skip invalid JSON files
    
    def _check_namespace_recursive(self, data: Any, forbidden_namespaces: List[str], file_path: str, path: str = ""):
        """Recursively check for forbidden namespace usage."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self._check_namespace_recursive(value, forbidden_namespaces, file_path, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_namespace_recursive(item, forbidden_namespaces, file_path, current_path)
        elif isinstance(data, str):
            # Check for namespace patterns
            if ':' in data:
                namespace = data.split(':')[0]
                if namespace in forbidden_namespaces:
                    self.add_result(
                        ValidationLevel.ERROR,
                        f"Forbidden namespace '{namespace}' used in {path}",
                        file_path,
                        context={'value': data, 'path': path}
                    )
