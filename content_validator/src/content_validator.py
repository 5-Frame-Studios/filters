"""
Content validation for Add-Ons Guidelines compliance.
"""

import os
import glob
from typing import Dict, List, Any
from .models import ValidationResult, ValidationLevel
from .utils import logger, find_pack_directories, get_first_existing_path, safe_file_read, safe_json_load


class ContentValidator:
    """Validate content compliance with Add-Ons Guidelines."""
    
    def __init__(self, settings: dict):
        self.settings = settings
    
    def validate_addon_guidelines(self, report) -> None:
        """Validate compliance with Add-Ons Guidelines."""
        logger.info("Validating Add-Ons Guidelines compliance...")
        
        # Check for prohibited content and features
        self._check_prohibited_content(report)
        self._check_vanilla_file_modifications(report)
        self._check_experimental_features(report)
        self._check_ui_modifications(report)
        self._check_player_character_modifications(report)
        self._check_dimension_modifications(report)
        self._check_weapons_policy(report)
        self._check_dependencies(report)
        self._check_size_requirements(report)
    
    def _check_prohibited_content(self, report) -> None:
        """Check for prohibited content types."""
        logger.info("Checking for prohibited content...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        prohibited_patterns = {
            'mod_terminology': ['mod', 'modded', 'modification'],
            'cheat_patterns': [
                'invincibility', 'invulnerability', 'instakill', 'auto_break', 'auto_mine',
                'clipping', 'aura', 'aimbot', 'console_command', 'keep_inventory',
                'fire_tick', 'grief_mobs', 'player_locator', 'inventory_locator'
            ],
            'disallowed_genres': [
                'one_block', 'skyblock', 'lucky_block', 'random_op', 'x_ray', 'xray',
                'dance_creator', 'skin_generator', 'resource_generator', 'cape_generator'
            ],
            'forbidden_items': [
                'horse_armor', 'ender_pearl', 'saddle', 'portal_frame', 'written_book'
            ]
        }
        
        for path in bp_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            self._check_prohibited_patterns_in_file(file_path, prohibited_patterns, report)
                break  # Found the first valid path
    
    def _check_prohibited_patterns_in_file(self, file_path: str, prohibited_patterns: Dict[str, List[str]], report) -> None:
        """Check for prohibited patterns in a specific file."""
        content = safe_file_read(file_path)
        if not content:
            return
        
        content_lower = content.lower()
        
        # Check for mod terminology (but exclude common technical terms)
        for pattern in prohibited_patterns['mod_terminology']:
            if pattern in content_lower:
                # Skip if it's part of common technical terms
                technical_terms = ['modules', 'modular', 'modification', 'modify']
                if any(term in content_lower for term in technical_terms):
                    continue
                
                # Check if it's standalone "mod" terminology
                if pattern == 'mod' and 'modules' in content_lower:
                    continue
                
                report.add_result(ValidationResult(
                    ValidationLevel.POSSIBLE_ISSUE,
                    f"Possible prohibited terminology '{pattern}' found - Add-Ons should avoid 'mod' terminology (manual review recommended)",
                    file_path,
                    context={'prohibited_term': pattern}
                ))
        
        # Check for cheat patterns
        for pattern in prohibited_patterns['cheat_patterns']:
            if pattern in content_lower:
                report.add_result(ValidationResult(
                    ValidationLevel.POSSIBLE_ISSUE,
                    f"Possible cheat pattern '{pattern}' found - cheats/hacks are not allowed (manual review recommended)",
                    file_path,
                    context={'prohibited_pattern': pattern}
                ))
        
        # Check for disallowed genres
        for pattern in prohibited_patterns['disallowed_genres']:
            if pattern in content_lower:
                report.add_result(ValidationResult(
                    ValidationLevel.POSSIBLE_ISSUE,
                    f"Possible disallowed genre '{pattern}' found - this content type may not be allowed as Add-On (manual review recommended)",
                    file_path,
                    context={'disallowed_genre': pattern}
                ))
        
        # Check for forbidden items only in recipe outputs (not ingredients)
        if 'recipe.json' in file_path:
            self._check_forbidden_items_in_recipe(file_path, prohibited_patterns['forbidden_items'], report)
        else:
            # For non-recipe files, only check for forbidden items in specific contexts
            self._check_forbidden_items_in_context(file_path, content_lower, prohibited_patterns['forbidden_items'], report)
    
    def _check_forbidden_items_in_recipe(self, file_path: str, forbidden_items: List[str], report) -> None:
        """Check for forbidden items only in recipe outputs, not ingredients."""
        try:
            content = safe_file_read(file_path)
            if not content:
                return
            
            data = safe_json_load(content)
            if not data:
                return
            
            # Check recipe result/output
            if 'result' in data:
                result = data['result']
                if isinstance(result, dict) and 'item' in result:
                    item_id = result['item']
                    for forbidden_item in forbidden_items:
                        if forbidden_item in item_id:
                            report.add_result(ValidationResult(
                                ValidationLevel.WARNING,
                                f"Forbidden item '{forbidden_item}' found in recipe output - crafting traditionally uncraftable items requires justification",
                                file_path,
                                context={'forbidden_item': forbidden_item, 'output_item': item_id}
                            ))
            
            # Check for multiple results in tags array
            if 'tags' in data and isinstance(data['tags'], list):
                for tag in data['tags']:
                    if 'result' in tag and isinstance(tag['result'], dict) and 'item' in tag['result']:
                        item_id = tag['result']['item']
                        for forbidden_item in forbidden_items:
                            if forbidden_item in item_id:
                                report.add_result(ValidationResult(
                                    ValidationLevel.WARNING,
                                    f"Forbidden item '{forbidden_item}' found in recipe output - crafting traditionally uncraftable items requires justification",
                                    file_path,
                                    context={'forbidden_item': forbidden_item, 'output_item': item_id}
                                ))
                                
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            pass
    
    def _check_forbidden_items_in_context(self, file_path: str, content_lower: str, forbidden_items: List[str], report) -> None:
        """Check for forbidden items in non-recipe contexts where they might be inappropriate."""
        # Only flag forbidden items in item definition files (where new items are being created)
        if 'item.json' in file_path and any(path in file_path for path in ['items/', 'item/']):
            for forbidden_item in forbidden_items:
                if forbidden_item in content_lower:
                    report.add_result(ValidationResult(
                        ValidationLevel.WARNING,
                        f"Forbidden item '{forbidden_item}' found in item definition - creating traditionally uncraftable items requires justification",
                        file_path,
                        context={'forbidden_item': forbidden_item}
                    ))
    
    def _check_vanilla_file_modifications(self, report) -> None:
        """Check for vanilla file modifications."""
        logger.info("Checking for vanilla file modifications...")
        
        pack_dirs = find_pack_directories()
        vanilla_namespaces = ['minecraft']
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._check_vanilla_modifications_in_file(file_path, vanilla_namespaces, report)
                    break  # Found the first valid path for this pack type
    
    def _check_vanilla_modifications_in_file(self, file_path: str, vanilla_namespaces: List[str], report) -> None:
        """Check for vanilla file modifications in a specific file."""
        data = safe_json_load(file_path)
        if not data:
            return
        
        # Check for vanilla namespace usage in identifiers
        self._check_vanilla_identifiers_recursive(data, vanilla_namespaces, file_path, report)
    
    def _check_vanilla_identifiers_recursive(self, data: Any, vanilla_namespaces: List[str], file_path: str, report, path: str = "") -> None:
        """Recursively check for vanilla identifier usage."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self._check_vanilla_identifiers_recursive(value, vanilla_namespaces, file_path, report, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_vanilla_identifiers_recursive(item, vanilla_namespaces, file_path, report, current_path)
        elif isinstance(data, str):
            # Check for vanilla namespace in identifiers
            if ':' in data:
                namespace = data.split(':')[0]
                if namespace in vanilla_namespaces:
                    # Only flag vanilla namespace usage for NEW entity/block/item identifiers
                    # Skip legitimate references like recipe ingredients, loot table items, etc.
                    if self._is_identifier_definition_legacy(path, file_path):
                        report.add_result(ValidationResult(
                            ValidationLevel.ERROR,
                            f"Vanilla namespace '{namespace}' should not be modified in Add-Ons",
                            file_path,
                            context={'value': data, 'path': path}
                        ))
    
    def _is_identifier_definition_legacy(self, path: str, file_path: str) -> bool:
        """Check if this path represents a new identifier definition (not a reference)."""
        # These are legitimate references, not new definitions
        legitimate_reference_paths = [
            'result.item', 'key.item', 'tags.item', 'item', 'input', 'output', 
            'ingredient', 'materials', 'drops', 'pools.entries.name', 'give', 
            'item_name', 'spawn_item'
        ]
        
        # File types that commonly have legitimate minecraft: references
        legitimate_reference_files = [
            'recipe.json', 'loot_table.json', 'trade.json', 
            'crafting_item_catalog.json', 'trading.json'
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
    
    def _check_experimental_features(self, report) -> None:
        """Check for experimental features."""
        logger.info("Checking for experimental features...")
        
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(root, file)
                                self._check_experimental_in_json_file(file_path, report)
                            elif file.endswith(('.js', '.mcfunction')):
                                # For script files, still check content but be more specific
                                file_path = os.path.join(root, file)
                                self._check_experimental_in_script_file(file_path, report)
                    break  # Found the first valid path for this pack type
    
    def _check_experimental_in_json_file(self, file_path: str, report) -> None:
        """Check for experimental features in JSON files with proper context awareness."""
        try:
            content = safe_file_read(file_path)
            if not content:
                return
            
            data = safe_json_load(content)
            if not data:
                return
            
            # Check for experimental features in manifest files
            if 'manifest.json' in file_path:
                if 'dependencies' in data:
                    for dep in data['dependencies']:
                        if isinstance(dep, dict) and dep.get('module_name') in ['@minecraft/server-gametest', '@minecraft/server-admin']:
                            report.add_result(ValidationResult(
                                ValidationLevel.ERROR,
                                f"Experimental module '{dep.get('module_name')}' detected - experimental features are not allowed",
                                file_path,
                                context={'module': dep.get('module_name')}
                            ))
            
            # Check for is_experimental: true and other experimental flags
            self._check_experimental_json_recursive(data, file_path, report)
            
        except (FileNotFoundError, OSError):
            pass
    
    def _check_experimental_json_recursive(self, data: Any, file_path: str, report, path: str = "") -> None:
        """Recursively check for experimental features in JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Only flag is_experimental: true, not is_experimental: false
                if key == 'is_experimental' and value is True:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Experimental feature indicator 'experimental' found - experimental features are not allowed",
                        file_path,
                        context={'experimental_indicator': 'experimental', 'path': current_path}
                    ))
                
                # Check for experimental feature flags that are enabled
                if key in ['enable_experimental', 'experimental_features'] and value:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Experimental feature flag '{key}' enabled - experimental features are not allowed",
                        file_path,
                        context={'experimental_flag': key, 'path': current_path}
                    ))
                
                # Recurse into nested structures
                self._check_experimental_json_recursive(value, file_path, report, current_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._check_experimental_json_recursive(item, file_path, report, current_path)
    
    def _check_experimental_in_script_file(self, file_path: str, report) -> None:
        """Check for experimental features in script files (.js, .mcfunction)."""
        try:
            content = safe_file_read(file_path)
            if not content:
                return
            
            content_lower = content.lower()
            
            # Be more specific for script files - look for actual experimental APIs
            experimental_apis = [
                'server-gametest', 'server-admin', 'experimental_features',
                '@minecraft/server-gametest', '@minecraft/server-admin'
            ]
            
            for api in experimental_apis:
                if api in content_lower:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Experimental API '{api}' found - experimental features are not allowed",
                        file_path,
                        context={'experimental_api': api}
                    ))
            
        except (FileNotFoundError, OSError):
            pass
    
    def _check_ui_modifications(self, report) -> None:
        """Check for UI modifications."""
        logger.info("Checking for UI modifications...")
        
        pack_dirs = find_pack_directories()
        rp_paths = pack_dirs.get('RP', [])
        
        for path in rp_paths:
            if os.path.exists(path):
                # Check for UI folder
                ui_path = f"{path}/UI"
                if os.path.exists(ui_path):
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"UI folder found at {ui_path} - Add-Ons cannot modify game UI",
                        ui_path
                    ))
                
                # Check for font folder
                font_path = f"{path}/font"
                if os.path.exists(font_path):
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Font folder found at {font_path} - Add-Ons cannot override fonts/glyphs",
                        font_path
                    ))
                break  # Found the first valid path
    
    def _check_player_character_modifications(self, report) -> None:
        """Check for player character modifications."""
        logger.info("Checking for player character modifications...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        player_indicators = [
            'player_character', 'player_model', 'player_skin', 'player_entity',
            'minecraft:player', 'player_modification'
        ]
        
        for path in bp_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            content = safe_file_read(file_path)
                            if content:
                                content_lower = content.lower()
                                for indicator in player_indicators:
                                    if indicator in content_lower:
                                        report.add_result(ValidationResult(
                                            ValidationLevel.POSSIBLE_ISSUE,
                                            f"Possible player character modification indicator '{indicator}' found - direct player modifications are not allowed (manual review recommended)",
                                            file_path,
                                            context={'player_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
    def _check_dimension_modifications(self, report) -> None:
        """Check for dimension modifications."""
        logger.info("Checking for dimension modifications...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        for path in bp_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            self._check_dimension_modifications_in_json(file_path, report)
                        elif file.endswith(('.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            self._check_dimension_modifications_in_script(file_path, report)
                break  # Found the first valid path
    
    def _check_dimension_modifications_in_json(self, file_path: str, report) -> None:
        """Check for actual dimension modifications in JSON files, not just references."""
        try:
            content = safe_file_read(file_path)
            if not content:
                return
            
            data = safe_json_load(content)
            if not data:
                return
            
            # Only flag files that actually define new dimensions
            # Check for dimension definitions (these would be problematic)
            if self._is_dimension_definition_file(file_path, data):
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Dimension definition found - Add-Ons cannot add/subtract dimensions",
                    file_path,
                    context={'file_type': 'dimension_definition'}
                ))
            
            # Check for dimension modification APIs in data
            if isinstance(data, dict):
                self._check_dimension_modification_apis(data, file_path, report)
            
        except (FileNotFoundError, OSError):
            pass
    
    def _is_dimension_definition_file(self, file_path: str, data: Any) -> bool:
        """Check if this file actually defines a new dimension."""
        # Check file path patterns that indicate dimension definitions
        dimension_definition_paths = [
            'dimensions/', 'dimension_types/', 'dimension/'
        ]
        
        file_path_lower = file_path.lower()
        for dim_path in dimension_definition_paths:
            if dim_path in file_path_lower:
                return True
        
        # Check JSON structure for dimension definitions
        if isinstance(data, dict):
            # Look for dimension definition structures
            if 'minecraft:dimension_type' in data or 'minecraft:dimension' in data:
                return True
            
            if 'description' in data and isinstance(data['description'], dict):
                desc = data['description']
                if 'identifier' in desc and any(keyword in str(desc['identifier']).lower() 
                                              for keyword in ['dimension', 'world']):
                    # But allow existing dimension references
                    identifier = str(desc['identifier']).lower()
                    if not any(existing in identifier for existing in ['overworld', 'nether', 'the_end']):
                        return True
        
        return False
    
    def _check_dimension_modification_apis(self, data: Any, file_path: str, report, path: str = "") -> None:
        """Recursively check for dimension modification APIs."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for dimension modification methods/properties
                if key in ['createDimension', 'removeDimension', 'addDimension', 'deleteDimension']:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Dimension modification API '{key}' found - Add-Ons cannot add/subtract dimensions",
                        file_path,
                        context={'api_method': key, 'path': current_path}
                    ))
                
                # Recurse into nested structures
                self._check_dimension_modification_apis(value, file_path, report, current_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._check_dimension_modification_apis(item, file_path, report, current_path)
    
    def _check_dimension_modifications_in_script(self, file_path: str, report) -> None:
        """Check for dimension modifications in script files."""
        try:
            content = safe_file_read(file_path)
            if not content:
                return
            
            content_lower = content.lower()
            
            # Look for actual dimension modification APIs/methods
            dimension_modification_apis = [
                'createdimension', 'removedimension', 'adddimension', 'deletedimension',
                'dimension.create', 'dimension.add', 'dimension.remove', 'dimension.delete',
                'new dimension', 'custom_dimension_type'
            ]
            
            for api in dimension_modification_apis:
                if api in content_lower:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Dimension modification API '{api}' found - Add-Ons cannot add/subtract dimensions",
                        file_path,
                        context={'modification_api': api}
                    ))
            
        except (FileNotFoundError, OSError):
            pass
    
    def _check_weapons_policy(self, report) -> None:
        """Check weapons policy compliance."""
        logger.info("Checking weapons policy...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        weapon_indicators = [
            'gun', 'firearm', 'rifle', 'pistol', 'shotgun', 'sniper',
            'trigger', 'ammo', 'bullet', 'projectile_weapon'
        ]
        
        for path in bp_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.mcfunction')):
                            file_path = os.path.join(root, file)
                            content = safe_file_read(file_path)
                            if content:
                                content_lower = content.lower()
                                for indicator in weapon_indicators:
                                    if indicator in content_lower:
                                        report.add_result(ValidationResult(
                                            ValidationLevel.POSSIBLE_ISSUE,
                                            f"Possible weapon indicator '{indicator}' found - projectile weapons require additional scrutiny (manual review recommended)",
                                            file_path,
                                            context={'weapon_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
    def _check_dependencies(self, report) -> None:
        """Check for external dependencies."""
        logger.info("Checking for external dependencies...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        dependency_indicators = [
            'external', 'patreon', 'discord', 'website', 'download',
            'external_requirement', 'external_dependency'
        ]
        
        for path in bp_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.mcfunction', '.txt', '.md')):
                            file_path = os.path.join(root, file)
                            content = safe_file_read(file_path)
                            if content:
                                content_lower = content.lower()
                                for indicator in dependency_indicators:
                                    if indicator in content_lower:
                                        report.add_result(ValidationResult(
                                            ValidationLevel.POSSIBLE_ISSUE,
                                            f"Possible external dependency indicator '{indicator}' found - Add-Ons cannot require external sources (manual review recommended)",
                                            file_path,
                                            context={'dependency_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
    def _check_size_requirements(self, report) -> None:
        """Check size requirements using compressed size."""
        logger.info("Checking size requirements...")
        
        import zipfile
        import io
        
        total_files = 0
        pack_dirs = find_pack_directories()
        
        # Get actual compressed size by creating a zip in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
            for pack_type, possible_paths in pack_dirs.items():
                for path in possible_paths:
                    if os.path.exists(path):
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    # Create relative path for zip
                                    rel_path = os.path.relpath(file_path, os.path.dirname(path))
                                    zip_file.write(file_path, rel_path)
                                    total_files += 1
                                except (OSError, ValueError):
                                    # Skip files that can't be read or have invalid paths
                                    pass
                        break  # Found the first valid path for this pack type
        
        # Get the compressed size
        compressed_size = zip_buffer.tell()
        zip_buffer.close()
        
        # Check 25MB limit (compressed)
        size_limit_bytes = 25 * 1024 * 1024
        if compressed_size > size_limit_bytes:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Compressed add-on size ({compressed_size / (1024*1024):.2f}MB) exceeds 25MB limit",
                context={'compressed_size_mb': compressed_size / (1024*1024), 'limit_mb': 25}
            ))
        
        # Check minimum content requirement
        if total_files < 5:
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Add-On has very few files ({total_files}) - ensure sufficient content for approval",
                context={'total_files': total_files}
            ))
