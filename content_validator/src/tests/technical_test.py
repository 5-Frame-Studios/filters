"""
Technical restrictions validation test.
Validates various technical restrictions like runtime_identifier, experimental features, vanilla overrides, etc.
"""

import os
import json
import glob
from typing import Dict, Any, List
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import find_pack_directories


class TechnicalTest(BaseValidatorTest):
    """Test for validating technical restrictions."""
    
    def get_test_name(self) -> str:
        return "Technical Restrictions"
    
    def get_test_description(self) -> str:
        return "Validates technical restrictions like runtime_identifier, experimental features, vanilla overrides"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate technical restrictions."""
        self.log_info("Validating technical restrictions...")
        
        # Check for runtime_identifier usage
        self._check_runtime_identifier_usage(pack_paths)
        
        # Check for experimental features
        self._check_experimental_features(pack_paths)
        
        # Check for vanilla overrides
        self._check_vanilla_overrides(pack_paths)
        
        # Check for setLore restrictions
        self._check_setlore_restrictions(pack_paths)
        
        # Check for ticking areas
        self._check_ticking_areas(pack_paths)
        
        return self.report
    
    def _check_runtime_identifier_usage(self, pack_paths: Dict[str, str]):
        """Check for forbidden runtime_identifier usage."""
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        for path in bp_paths:
            if os.path.exists(path):
                entity_files = glob.glob(f"{path}/entities/*.json")
                
                for file_path in entity_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'minecraft:entity' in data:
                            entity_data = data['minecraft:entity']
                            if 'runtime_identifier' in entity_data:
                                self.add_result(
                                    ValidationLevel.ERROR,
                                    "runtime_identifier is not allowed in Add-On entities",
                                    file_path,
                                    context={'entity_id': entity_data.get('description', {}).get('identifier', 'unknown')}
                                )
                    
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
                break  # Found the first valid path
    
    def _check_experimental_features(self, pack_paths: Dict[str, str]):
        """Check for experimental features usage."""
        experimental_indicators = ['experimental', 'beta', 'preview']
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read().lower()
                                    
                                    for indicator in experimental_indicators:
                                        if indicator in content:
                                            self.add_result(
                                                ValidationLevel.WARNING,
                                                f"Potential experimental feature usage detected: '{indicator}'",
                                                file_path
                                            )
                                
                                except (UnicodeDecodeError):
                                    pass
                    break  # Found the first valid path for this pack type
    
    def _check_vanilla_overrides(self, pack_paths: Dict[str, str]):
        """Check for vanilla content overrides."""
        vanilla_namespaces = ['minecraft']
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._check_vanilla_override_in_file(file_path, vanilla_namespaces)
                    break  # Found the first valid path for this pack type
    
    def _check_vanilla_override_in_file(self, file_path: str, vanilla_namespaces: List[str]):
        """Check for vanilla overrides in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for vanilla namespace usage in identifiers
            self._check_vanilla_identifiers(data, vanilla_namespaces, file_path)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    
    def _check_vanilla_identifiers(self, data: Any, vanilla_namespaces: List[str], file_path: str, path: str = ""):
        """Recursively check for vanilla identifier usage."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self._check_vanilla_identifiers(value, vanilla_namespaces, file_path, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_vanilla_identifiers(item, vanilla_namespaces, file_path, current_path)
        elif isinstance(data, str):
            # Check for vanilla namespace in identifiers
            if ':' in data:
                namespace = data.split(':')[0]
                if namespace in vanilla_namespaces:
                    self.add_result(
                        ValidationLevel.ERROR,
                        f"Vanilla namespace '{namespace}' should not be overridden in Add-Ons",
                        file_path,
                        context={'value': data, 'path': path}
                    )
    
    def _check_setlore_restrictions(self, pack_paths: Dict[str, str]):
        """Check for setLore API restrictions."""
        forbidden_patterns = self.settings.get('organization_specific', {}).get('forbidden_text_patterns', [])
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        for path in bp_paths:
            if os.path.exists(path):
                # Check for setLore usage on forbidden items
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            self._check_setlore_in_file(file_path, forbidden_patterns)
                break  # Found the first valid path
    
    def _check_setlore_in_file(self, file_path: str, forbidden_patterns: List[str]):
        """Check for setLore usage on forbidden items."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for setLore usage
            if 'setLore' in content:
                for pattern in forbidden_patterns:
                    if pattern in content:
                        self.add_result(
                            ValidationLevel.ERROR,
                            f"setLore API cannot be used on '{pattern}'",
                            file_path,
                            context={'forbidden_item': pattern}
                        )
        
        except (UnicodeDecodeError, OSError):
            pass
    
    def _check_ticking_areas(self, pack_paths: Dict[str, str]):
        """Check for ticking area usage."""
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        for path in bp_paths:
            if os.path.exists(path):
                # Check for ticking area usage in various file types
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            self._check_ticking_areas_in_file(file_path)
                break  # Found the first valid path
    
    def _check_ticking_areas_in_file(self, file_path: str):
        """Check for ticking area usage in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ticking_patterns = ['ticking', 'tickarea', 'tick_area']
            for pattern in ticking_patterns:
                if pattern in content.lower():
                    self.add_result(
                        ValidationLevel.ERROR,
                        f"Ticking areas are not allowed in Add-Ons",
                        file_path,
                        context={'pattern_found': pattern}
                    )
        
        except (UnicodeDecodeError, OSError):
            pass
