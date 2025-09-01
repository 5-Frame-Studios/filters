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
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._check_experimental_in_file(file_path)
                    break  # Found the first valid path for this pack type
    
    def _check_experimental_in_file(self, file_path: str):
        """Check for actual experimental features usage in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for experimental features in manifest files
            if 'manifest.json' in file_path:
                if 'dependencies' in data:
                    for dep in data['dependencies']:
                        if isinstance(dep, dict) and dep.get('module_name') in ['@minecraft/server-gametest', '@minecraft/server-admin']:
                            self.add_result(
                                ValidationLevel.ERROR,
                                f"Experimental module '{dep.get('module_name')}' detected - experimental features are not allowed",
                                file_path,
                                context={'module': dep.get('module_name')}
                            )
            
            # Check for is_experimental: true in any JSON
            self._check_experimental_recursive(data, file_path)
            
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            pass
    
    def _check_experimental_recursive(self, data: Any, file_path: str, path: str = ""):
        """Recursively check for experimental features in JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for is_experimental: true
                if key == 'is_experimental' and value is True:
                    self.add_result(
                        ValidationLevel.ERROR,
                        f"Experimental feature indicator 'experimental' found - experimental features are not allowed",
                        file_path,
                        context={'experimental_indicator': 'experimental', 'path': current_path}
                    )
                
                # Check for experimental feature flags
                if key in ['enable_experimental', 'experimental_features'] and value:
                    self.add_result(
                        ValidationLevel.ERROR,
                        f"Experimental feature flag '{key}' enabled - experimental features are not allowed",
                        file_path,
                        context={'experimental_flag': key, 'path': current_path}
                    )
                
                # Recurse into nested structures
                self._check_experimental_recursive(value, file_path, current_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._check_experimental_recursive(item, file_path, current_path)
    
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
                    # Only flag vanilla namespace usage for NEW entity/block/item identifiers
                    # Skip legitimate references like recipe ingredients, loot table items, etc.
                    if self._is_identifier_definition(path, file_path):
                        self.add_result(
                            ValidationLevel.ERROR,
                            f"Vanilla namespace '{namespace}' should not be overridden in Add-Ons",
                            file_path,
                            context={'value': data, 'path': path}
                        )
    
    def _is_identifier_definition(self, path: str, file_path: str) -> bool:
        """Check if this path represents a new identifier definition (not a reference)."""
        # These are legitimate references, not new definitions
        legitimate_reference_paths = [
            'result.item',           # Recipe results can use minecraft: items
            'key.item',             # Recipe ingredients can use minecraft: items  
            'tags.item',            # Recipe tags can reference minecraft: items
            'item',                 # General item references
            'input',                # Recipe inputs
            'output',               # Recipe outputs
            'ingredient',           # Recipe ingredients
            'materials',            # Crafting materials
            'drops',                # Loot table drops
            'pools.entries.name',   # Loot table entries
            'give',                 # Give commands
            'item_name',            # Item name references
            'spawn_item',           # Spawn item references
        ]
        
        # File types that commonly have legitimate minecraft: references
        legitimate_reference_files = [
            'recipe.json',
            'loot_table.json',
            'trade.json',
            'crafting_item_catalog.json',
            'trading.json'
        ]
        
        # Check if this is a legitimate reference context
        path_lower = path.lower()
        for ref_path in legitimate_reference_paths:
            if ref_path in path_lower:
                return False
        
        # Check if this is a file type that commonly has references
        file_name = file_path.split('\\')[-1].split('/')[-1]
        for ref_file in legitimate_reference_files:
            if ref_file in file_name:
                return False
        
        # Check for entity/block/item identifier definitions (these should be flagged)
        identifier_definition_paths = [
            'minecraft:entity.description.identifier',
            'minecraft:block.description.identifier', 
            'minecraft:item.description.identifier',
            'description.identifier',
            'identifier'
        ]
        
        for def_path in identifier_definition_paths:
            if def_path in path_lower:
                return True
        
        # Default to not flagging unless we're sure it's a new definition
        return False
    
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
            
            ticking_patterns = ['ticking', 'tickarea', 'tick_area', 'tickingarea']
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
