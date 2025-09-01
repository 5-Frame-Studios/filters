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
                    ValidationLevel.ERROR,
                    f"Prohibited terminology '{pattern}' found - Add-Ons cannot use 'mod' terminology",
                    file_path,
                    context={'prohibited_term': pattern}
                ))
        
        # Check for cheat patterns
        for pattern in prohibited_patterns['cheat_patterns']:
            if pattern in content_lower:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Prohibited cheat pattern '{pattern}' found - cheats/hacks are not allowed",
                    file_path,
                    context={'prohibited_pattern': pattern}
                ))
        
        # Check for disallowed genres
        for pattern in prohibited_patterns['disallowed_genres']:
            if pattern in content_lower:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Disallowed genre '{pattern}' found - this content type is not allowed as Add-On",
                    file_path,
                    context={'disallowed_genre': pattern}
                ))
        
        # Check for forbidden items
        for pattern in prohibited_patterns['forbidden_items']:
            if pattern in content_lower:
                report.add_result(ValidationResult(
                    ValidationLevel.WARNING,
                    f"Forbidden item '{pattern}' found - crafting traditionally uncraftable items requires justification",
                    file_path,
                    context={'forbidden_item': pattern}
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
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Vanilla namespace '{namespace}' should not be modified in Add-Ons",
                        file_path,
                        context={'value': data, 'path': path}
                    ))
    
    def _check_experimental_features(self, report) -> None:
        """Check for experimental features."""
        logger.info("Checking for experimental features...")
        
        experimental_indicators = [
            'experimental', 'beta', 'preview', 'unreleased', 'upcoming',
            'experimental_features', 'beta_features'
        ]
        
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith(('.json', '.js', '.mcfunction')):
                                file_path = os.path.join(root, file)
                                content = safe_file_read(file_path)
                                if content:
                                    content_lower = content.lower()
                                    for indicator in experimental_indicators:
                                        if indicator in content_lower:
                                            report.add_result(ValidationResult(
                                                ValidationLevel.ERROR,
                                                f"Experimental feature indicator '{indicator}' found - experimental features are not allowed",
                                                file_path,
                                                context={'experimental_indicator': indicator}
                                            ))
                    break  # Found the first valid path for this pack type
    
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
                                            ValidationLevel.ERROR,
                                            f"Player character modification indicator '{indicator}' found - direct player modifications are not allowed",
                                            file_path,
                                            context={'player_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
    def _check_dimension_modifications(self, report) -> None:
        """Check for dimension modifications."""
        logger.info("Checking for dimension modifications...")
        
        pack_dirs = find_pack_directories()
        bp_paths = pack_dirs.get('BP', [])
        
        dimension_indicators = [
            'dimension', 'overworld', 'nether', 'the_end', 'custom_dimension',
            'new_dimension', 'dimension_type'
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
                                for indicator in dimension_indicators:
                                    if indicator in content_lower:
                                        report.add_result(ValidationResult(
                                            ValidationLevel.ERROR,
                                            f"Dimension modification indicator '{indicator}' found - Add-Ons cannot add/subtract dimensions",
                                            file_path,
                                            context={'dimension_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
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
                                            ValidationLevel.WARNING,
                                            f"Weapon indicator '{indicator}' found - projectile weapons require additional scrutiny",
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
                                            ValidationLevel.ERROR,
                                            f"External dependency indicator '{indicator}' found - Add-Ons cannot require external sources",
                                            file_path,
                                            context={'dependency_indicator': indicator}
                                        ))
                break  # Found the first valid path
    
    def _check_size_requirements(self, report) -> None:
        """Check size requirements."""
        logger.info("Checking size requirements...")
        
        total_size = 0
        total_files = 0
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                total_size += file_size
                                total_files += 1
                            except OSError:
                                pass
                    break  # Found the first valid path for this pack type
        
        # Check 25MB limit
        size_limit_bytes = 25 * 1024 * 1024
        if total_size > size_limit_bytes:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Add-On size ({total_size / (1024*1024):.2f}MB) exceeds 25MB limit",
                context={'total_size_mb': total_size / (1024*1024), 'limit_mb': 25}
            ))
        
        # Check minimum content requirement
        if total_files < 5:
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Add-On has very few files ({total_files}) - ensure sufficient content for approval",
                context={'total_files': total_files}
            ))
