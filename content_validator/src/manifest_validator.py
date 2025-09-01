"""
Manifest validation functionality.
"""

import os
import json
from typing import Dict, Any
from .models import ValidationResult, ValidationLevel
from .utils import logger, find_pack_directories, get_first_existing_path, safe_json_load


class ManifestValidator:
    """Validate manifest requirements."""
    
    def __init__(self, settings: dict):
        self.settings = settings
    
    def validate_manifests(self, report) -> None:
        """Validate manifest requirements."""
        logger.info("Validating manifest files...")
        
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            manifest_found = False
            
            for path in possible_paths:
                manifest_path = f"{path}/manifest.json"
                if os.path.exists(manifest_path):
                    try:
                        manifest = safe_json_load(manifest_path)
                        if manifest:
                            self._validate_manifest_structure(manifest, pack_type, manifest_path, report)
                            self._validate_manifest_requirements(manifest, pack_type, manifest_path, report)
                            manifest_found = True
                            break
                        else:
                            report.add_result(ValidationResult(
                                ValidationLevel.ERROR,
                                f"Invalid JSON in {pack_type} manifest",
                                manifest_path
                            ))
                            manifest_found = True  # Found but invalid
                            break
                    except Exception as e:
                        report.add_result(ValidationResult(
                            ValidationLevel.ERROR,
                            f"Error reading {pack_type} manifest: {e}",
                            manifest_path
                        ))
                        manifest_found = True  # Found but invalid
                        break
            
            if not manifest_found:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"{pack_type} manifest.json not found (checked: {', '.join(possible_paths)})"
                ))
    
    def _validate_manifest_structure(self, manifest: Dict[str, Any], pack_type: str, file_path: str, report) -> None:
        """Validate basic manifest structure."""
        required_sections = ['format_version', 'header', 'modules']
        
        for section in required_sections:
            if section not in manifest:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Missing required section '{section}' in {pack_type} manifest",
                    file_path
                ))
        
        # Validate header structure
        if 'header' in manifest:
            header = manifest['header']
            required_header_fields = ['name', 'description', 'uuid', 'version', 'min_engine_version']
            
            for field in required_header_fields:
                if field not in header:
                    report.add_result(ValidationResult(
                        ValidationLevel.ERROR,
                        f"Missing required header field '{field}' in {pack_type} manifest",
                        file_path
                    ))
    
    def _validate_manifest_requirements(self, manifest: Dict[str, Any], pack_type: str, file_path: str, report) -> None:
        """Validate marketplace-specific manifest requirements."""
        header = manifest.get('header', {})
        
        # Check pack_scope requirement
        if 'pack_scope' not in header:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Missing 'pack_scope' field in {pack_type} manifest header",
                file_path
            ))
        elif header['pack_scope'] != 'world':
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"pack_scope must be 'world' in {pack_type} manifest, found: {header['pack_scope']}",
                file_path
            ))
        
        # Check metadata.product_type requirement
        metadata = manifest.get('metadata', {})
        if 'product_type' not in metadata:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Missing 'metadata.product_type' field in {pack_type} manifest",
                file_path
            ))
        elif metadata['product_type'] != 'addon':
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"metadata.product_type must be 'addon' in {pack_type} manifest, found: {metadata['product_type']}",
                file_path
            ))
        
        # Check dependencies between BP and RP
        dependencies = manifest.get('dependencies', [])
        if not dependencies:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Missing dependencies in {pack_type} manifest",
                file_path
            ))
        
        # Check min_engine_version requirement
        min_engine_version = header.get('min_engine_version', [])
        if not min_engine_version or not isinstance(min_engine_version, list) or len(min_engine_version) < 2:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Invalid 'min_engine_version' in {pack_type} manifest - must be array with at least 2 elements",
                file_path,
                context={'current_version': min_engine_version}
            ))
    
    def validate_version_format(self, report) -> None:
        """Validate version format in manifests."""
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            manifest_path = get_first_existing_path([f"{path}/manifest.json" for path in possible_paths])
            if not manifest_path:
                continue
                
            manifest = safe_json_load(manifest_path)
            if not manifest:
                continue
            
            header = manifest.get('header', {})
            version = header.get('version', [])
            
            if not isinstance(version, list) or len(version) != 3:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Version must be in format [Major, Minor, Patch]",
                    manifest_path,
                    context={'current_version': version}
                ))
            else:
                # Check that all version components are integers
                for i, component in enumerate(version):
                    if not isinstance(component, int) or component < 0:
                        report.add_result(ValidationResult(
                            ValidationLevel.ERROR,
                            f"Version component {i} must be a non-negative integer",
                            manifest_path,
                            context={'component': component, 'position': i}
                        ))
    
    def validate_title_requirements(self, report) -> None:
        """Check title requirements."""
        logger.info("Checking title requirements...")
        
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            manifest_path = get_first_existing_path([f"{path}/manifest.json" for path in possible_paths])
            if not manifest_path:
                continue
                
            manifest = safe_json_load(manifest_path)
            if not manifest:
                continue
            
            header = manifest.get('header', {})
            name = header.get('name', '').lower()
            
            # Check for 'Add-On' terminology in title
            if 'add-on' in name or 'addon' in name:
                report.add_result(ValidationResult(
                    ValidationLevel.WARNING,
                    f"Title contains 'Add-On' terminology - this should be handled by UI, not title",
                    manifest_path,
                    context={'title': header.get('name', '')}
                ))
            
            # Check for 'mod' terminology
            if 'mod' in name:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"Title contains 'mod' terminology - this may confuse players about Java mods",
                    manifest_path,
                    context={'title': header.get('name', '')}
                ))
