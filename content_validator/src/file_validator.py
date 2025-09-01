"""
File structure and size validation functionality.
"""

import os
import glob
from typing import List, Dict
from .models import ValidationResult, ValidationLevel
from .utils import logger, find_pack_directories, get_first_existing_path
import json


class FileValidator:
    """Validate file structure and size requirements."""
    
    def __init__(self, settings: dict, namespace_info):
        self.settings = settings
        self.namespace_info = namespace_info
    
    def validate_file_structure(self, report) -> None:
        """Validate required folder structure."""
        logger.info("Validating file structure...")
        
        required_structure = self.settings.get('required_folder_structure', {})
        pack_dirs = find_pack_directories()
        
        for folder_type, required_paths in required_structure.items():
            for pack_type, possible_paths in pack_dirs.items():
                for path in possible_paths:
                    base_path = f"{path}/{folder_type}"
                    if os.path.exists(base_path):
                        self._validate_folder_structure(base_path, required_paths, folder_type, pack_type, report)
                        break  # Found the first valid path for this pack type
    
    def _validate_folder_structure(self, base_path: str, required_paths: List[str], folder_type: str, pack_type: str, report) -> None:
        """Validate specific folder structure."""
        if not self.namespace_info.studio_name:
            return  # Can't validate without studio name
        
        # Check for studio_name folder
        studio_path = os.path.join(base_path, self.namespace_info.studio_name)
        if not os.path.exists(studio_path):
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Missing studio folder '{self.namespace_info.studio_name}' in {pack_type}/{folder_type}/",
                base_path
            ))
            return
        
        # Check for pack_name folder
        pack_path = os.path.join(studio_path, self.namespace_info.pack_name)
        if not os.path.exists(pack_path):
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Missing pack folder '{self.namespace_info.pack_name}' in {pack_type}/{folder_type}/{self.namespace_info.studio_name}/",
                studio_path
            ))
    
    def validate_folder_depth(self, report) -> None:
        """Validate that files are placed at least 3 folders deep."""
        required_depth = self.settings.get('organization_specific', {}).get('required_folder_depth', 3)
        pack_dirs = find_pack_directories()
        
        # Special files that are allowed at 2-folder depth
        allowed_2_depth_files = {
            'crafting_item_catalog.json',  # BP/item_catalog/
            'sound_definitions.json',      # RP/sounds/
            'item_texture.json',           # RP/textures/
            'textures_list.json',          # RP/textures/
            'terrain_texture.json',        # RP/textures/
            'flipbook_textures.json',      # RP/textures/
            'en_US.lang',                  # BP/texts/ or RP/texts/
            'languages.json',              # BP/texts/ or RP/texts/
            'music_definitions.json',      # RP/sounds/
        }
        
        # Special directories that are allowed at 2-folder depth
        allowed_2_depth_dirs = {
            'texts',     # For language files
            'sounds',    # For sound definitions
            'textures',  # For texture definitions
            'item_catalog',  # For crafting catalog
        }
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, path)
                            path_parts = relative_path.split(os.sep)
                            
                            # Skip files that should be at root level (like manifest.json)
                            if len(path_parts) <= 1:
                                continue
                            
                            # Check if this is a special file allowed at 2-folder depth
                            filename = path_parts[-1]
                            if len(path_parts) == 2:
                                # Check if file is in an allowed 2-depth directory
                                parent_dir = path_parts[0]
                                if parent_dir in allowed_2_depth_dirs or filename in allowed_2_depth_files:
                                    continue
                                
                                # Check for language files (any .lang file in texts/)
                                if parent_dir == 'texts' and filename.endswith('.lang'):
                                    continue
                            
                            if len(path_parts) < required_depth:
                                report.add_result(ValidationResult(
                                    ValidationLevel.ERROR,
                                    f"File must be at least {required_depth} folders deep",
                                    file_path,
                                    context={'current_depth': len(path_parts), 'required_depth': required_depth}
                                ))
                    break  # Found the first valid path for this pack type
    
    def validate_subcategory_limits(self, report) -> None:
        """Validate that folders don't exceed subcategory limits."""
        max_subcategories = self.settings.get('organization_specific', {}).get('max_subcategories', 2)
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        # Check folder depth for subcategories
                        relative_path = os.path.relpath(root, path)
                        path_parts = relative_path.split(os.sep)
                        
                        if len(path_parts) > max_subcategories + 2:  # +2 for type/FFS/XY
                            report.add_result(ValidationResult(
                                ValidationLevel.WARNING,
                                f"Folder structure exceeds {max_subcategories} subcategories limit",
                                root,
                                context={'current_subcategories': len(path_parts) - 2, 'max_subcategories': max_subcategories}
                            ))
                    break  # Found the first valid path for this pack type
    
    def validate_size_limits(self, report) -> None:
        """Validate file size and count limits using actual zip compression."""
        logger.info("Validating size limits...")
        
        total_files = 0
        ignored_dirs = self.settings.get('ignored_directories', [])
        pack_dirs = find_pack_directories()
        
        # Get actual compressed size by creating a zip in memory
        compressed_size = self._get_actual_compressed_size(pack_dirs, ignored_dirs)
        
        # Count files
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        # Skip ignored directories
                        if any(ignored in root for ignored in ignored_dirs):
                            continue
                        total_files += len(files)
                    break  # Found the first valid path for this pack type
        
        # Check file count limit
        file_count_limit = self.settings.get('file_count_limit', 3500)
        if total_files > file_count_limit:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"File count ({total_files}) exceeds limit ({file_count_limit})",
                context={'total_files': total_files, 'limit': file_count_limit}
            ))
        
        # Check compressed size limit (25MB limit applies to zipped add-on)
        size_limit_mb = self.settings.get('file_size_limit_mb', 25)
        size_limit_bytes = size_limit_mb * 1024 * 1024
        
        if compressed_size > size_limit_bytes:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Compressed add-on size ({compressed_size / (1024*1024):.2f}MB) exceeds limit ({size_limit_mb}MB)",
                context={'compressed_size_mb': compressed_size / (1024*1024), 'limit_mb': size_limit_mb}
            ))
        elif compressed_size > size_limit_bytes * 0.8:  # Warn if > 80% of limit
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Compressed add-on size ({compressed_size / (1024*1024):.2f}MB) is approaching limit ({size_limit_mb}MB)",
                context={'compressed_size_mb': compressed_size / (1024*1024), 'limit_mb': size_limit_mb}
            ))
        
        logger.info(f"Size validation complete: {total_files} files, {compressed_size / (1024*1024):.2f}MB compressed")
    
    def _get_actual_compressed_size(self, pack_dirs: Dict[str, List[str]], ignored_dirs: List[str]) -> int:
        """Calculate actual compressed size by creating a zip in memory."""
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
            for pack_type, possible_paths in pack_dirs.items():
                for path in possible_paths:
                    if os.path.exists(path):
                        for root, dirs, files in os.walk(path):
                            # Skip ignored directories
                            if any(ignored in root for ignored in ignored_dirs):
                                continue
                            
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    # Create relative path for zip
                                    rel_path = os.path.relpath(file_path, os.path.dirname(path))
                                    zip_file.write(file_path, rel_path)
                                except (OSError, ValueError):
                                    # Skip files that can't be read or have invalid paths
                                    pass
                        break  # Found the first valid path for this pack type
        
        # Get the compressed size
        compressed_size = zip_buffer.tell()
        zip_buffer.close()
        
        return compressed_size
    
    def validate_block_permutations(self, report) -> None:
        """Validate block permutation limits."""
        logger.info("Validating block permutations...")
        
        permutation_limit = self.settings.get('block_permutation_limit', 10000)
        total_permutations = 0
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            if pack_type == 'BP':  # Only behavior packs have blocks
                for path in possible_paths:
                    if os.path.exists(path):
                        block_files = glob.glob(f"{path}/blocks/*.json")
                        
                        for file_path in block_files:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                if 'minecraft:block' in data:
                                    block_data = data['minecraft:block']
                                    permutations = block_data.get('permutations', [])
                                    total_permutations += len(permutations)
                            
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                pass
                        break  # Found the first valid path
        
        if total_permutations > permutation_limit:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Block permutations ({total_permutations}) exceed limit ({permutation_limit})",
                context={'total_permutations': total_permutations, 'limit': permutation_limit}
            ))
        
        logger.info(f"Block permutation validation complete: {total_permutations} permutations")
    
    def validate_guidebook_requirements(self, report) -> None:
        """Validate guidebook requirements."""
        logger.info("Validating guidebook requirements...")
        
        pack_dirs = find_pack_directories()
        guidebook_found = False
        
        for pack_type, possible_paths in pack_dirs.items():
            if pack_type == 'BP':  # Only behavior packs have structures
                for path in possible_paths:
                    if os.path.exists(path):
                        guidebook_structure = f"{path}/structures"
                        if os.path.exists(guidebook_structure):
                            # Look for guidebook structure
                            structure_files = glob.glob(f"{guidebook_structure}/*.mcstructure")
                            if structure_files:
                                guidebook_found = True
                                logger.info(f"Guidebook structure found: {len(structure_files)} .mcstructure files")
                        break
        
        if not guidebook_found:
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                "No guidebook structure found - .mcstructure files may be missing"
            ))
