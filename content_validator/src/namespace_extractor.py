"""
Namespace extraction and validation functionality.
"""

import os
import json
import glob
import re
from typing import Optional, List
from .models import NamespaceInfo, ValidationResult, ValidationLevel
from .utils import logger, safe_json_load


class NamespaceExtractor:
    """Extract and validate namespace information from pack files."""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.namespace_info = NamespaceInfo()
    
    def extract_namespace_info(self) -> NamespaceInfo:
        """Extract namespace information from pack files."""
        # Use find_pack_directories to get the correct paths in any environment
        from .utils import find_pack_directories
        pack_dirs = find_pack_directories()
        
        logger.debug(f"Namespace extraction: pack_dirs = {pack_dirs}")
        
        # Try to find namespace from pack directories
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    logger.debug(f"Namespace extraction: checking path {path}")
                    # Try manifest file first
                    manifest_path = os.path.join(path, "manifest.json")
                    if os.path.exists(manifest_path):
                        logger.debug(f"Namespace extraction: trying manifest {manifest_path}")
                        self._extract_namespace_from_file(manifest_path)
                        if self.namespace_info.namespace:
                            break
                    
                    # Try entity files
                    entity_patterns = [
                        os.path.join(path, "entities", "*.json"),
                        os.path.join(path, "entities", "*", "*.json"),
                        os.path.join(path, "entities", "*", "*", "*.json"),
                        os.path.join(path, "entities", "*", "*", "*", "*.json"),
                        os.path.join(path, "entities", "*", "*", "*", "*", "*.json")
                    ]
                    
                    for pattern in entity_patterns:
                        try:
                            files = glob.glob(pattern)
                            for file_path in files:
                                self._extract_namespace_from_file(file_path)
                                if self.namespace_info.namespace:
                                    break
                            if self.namespace_info.namespace:
                                break
                        except Exception as e:
                            logger.debug(f"Error globbing {pattern}: {e}")
                    
                    if self.namespace_info.namespace:
                        break
                    
                    # Try item files
                    item_patterns = [
                        os.path.join(path, "items", "*.json"),
                        os.path.join(path, "items", "*", "*.json"),
                        os.path.join(path, "items", "*", "*", "*.json"),
                        os.path.join(path, "items", "*", "*", "*", "*.json"),
                        os.path.join(path, "items", "*", "*", "*", "*", "*.json")
                    ]
                    
                    for pattern in item_patterns:
                        try:
                            files = glob.glob(pattern)
                            for file_path in files:
                                self._extract_namespace_from_file(file_path)
                                if self.namespace_info.namespace:
                                    break
                            if self.namespace_info.namespace:
                                break
                        except Exception as e:
                            logger.debug(f"Error globbing {pattern}: {e}")
                    
                    if self.namespace_info.namespace:
                        break
                    
                    # Try block files
                    block_patterns = [
                        os.path.join(path, "blocks", "*.json"),
                        os.path.join(path, "blocks", "*", "*.json"),
                        os.path.join(path, "blocks", "*", "*", "*.json")
                    ]
                    
                    for pattern in block_patterns:
                        try:
                            files = glob.glob(pattern)
                            for file_path in files:
                                self._extract_namespace_from_file(file_path)
                                if self.namespace_info.namespace:
                                    break
                            if self.namespace_info.namespace:
                                break
                        except Exception as e:
                            logger.debug(f"Error globbing {pattern}: {e}")
                    
                break  # Found the first valid path for this pack type
            
            if self.namespace_info.namespace:
                break
        
        if self.namespace_info.namespace:
            logger.info(f"Detected namespace: {self.namespace_info.namespace}")
            # Extract studio_name and pack_name from namespace
            if "_" in self.namespace_info.namespace:
                parts = self.namespace_info.namespace.split("_", 1)
                self.namespace_info.studio_name = parts[0]
                self.namespace_info.pack_name = parts[1]
                logger.info(f"Studio: {self.namespace_info.studio_name}, Pack: {self.namespace_info.pack_name}")
        else:
            logger.warning("No namespace detected - some validation may be limited")
        
        return self.namespace_info
    
    def _extract_namespace_from_file(self, file_path: str):
        """Extract namespace from a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError, FileNotFoundError):
            return
        
        if not isinstance(data, dict):
            return
        
        # Look for namespace in various structures
        namespaces_found = set()
        
        # Check minecraft:entity structure
        if 'minecraft:entity' in data:
            entity_data = data['minecraft:entity']
            if isinstance(entity_data, dict) and 'description' in entity_data:
                description = entity_data['description']
                if isinstance(description, dict) and 'identifier' in description:
                    identifier = description['identifier']
                    if isinstance(identifier, str) and ':' in identifier:
                        namespace = identifier.split(':')[0]
                        if namespace not in self.settings.get('forbidden_namespaces', ['minecraft']):
                            namespaces_found.add(namespace)
        
        # Check minecraft:item structure
        if 'minecraft:item' in data:
            item_data = data['minecraft:item']
            if isinstance(item_data, dict) and 'description' in item_data:
                description = item_data['description']
                if isinstance(description, dict) and 'identifier' in description:
                    identifier = description['identifier']
                    if isinstance(identifier, str) and ':' in identifier:
                        namespace = identifier.split(':')[0]
                        if namespace not in self.settings.get('forbidden_namespaces', ['minecraft']):
                            namespaces_found.add(namespace)
        
        # Check minecraft:block structure
        if 'minecraft:block' in data:
            block_data = data['minecraft:block']
            if isinstance(block_data, dict) and 'description' in block_data:
                description = block_data['description']
                if isinstance(description, dict) and 'identifier' in description:
                    identifier = description['identifier']
                    if isinstance(identifier, str) and ':' in identifier:
                        namespace = identifier.split(':')[0]
                        if namespace not in self.settings.get('forbidden_namespaces', ['minecraft']):
                            namespaces_found.add(namespace)
        
        # Check common identifier fields at root level
        identifier_fields = ['identifier', 'name', 'id']
        for field in identifier_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str) and ':' in value:
                    namespace = value.split(':')[0]
                    if namespace not in self.settings.get('forbidden_namespaces', ['minecraft']):
                        namespaces_found.add(namespace)
        
        # Recursively search for any identifier-like fields
        self._extract_namespace_recursive(data, namespaces_found)
        
        # Use the first valid namespace found
        if namespaces_found:
            # Prefer longer namespaces (more specific)
            self.namespace_info.namespace = max(namespaces_found, key=len)
            logger.debug(f"Found namespace '{self.namespace_info.namespace}' in {file_path}")
    
    def _extract_namespace_recursive(self, data, namespaces_found, path=""):
        """Recursively search for namespace identifiers."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Look for identifier fields
                if key in ['identifier', 'name', 'id'] and isinstance(value, str) and ':' in value:
                    namespace = value.split(':')[0]
                    if namespace not in self.settings.get('forbidden_namespaces', ['minecraft']):
                        namespaces_found.add(namespace)
                
                # Recurse into nested structures
                self._extract_namespace_recursive(value, namespaces_found, current_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._extract_namespace_recursive(item, namespaces_found, current_path)
    
    def validate_namespace_requirements(self, report) -> None:
        """Validate namespace requirements."""
        logger.info("Checking namespace requirements...")
        
        if not self.namespace_info.namespace:
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                "Add-On must have a unique namespace"
            ))
            return
        
        # Check namespace format (studio_pack)
        if not re.match(r'^[a-zA-Z0-9_]+$', self.namespace_info.namespace):
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Namespace '{self.namespace_info.namespace}' contains invalid characters - use only letters, numbers, and underscores",
                context={'namespace': self.namespace_info.namespace}
            ))
        
        # Check namespace length
        if len(self.namespace_info.namespace) > 50:
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Namespace '{self.namespace_info.namespace}' is very long - consider using a shorter namespace",
                context={'namespace': self.namespace_info.namespace, 'length': len(self.namespace_info.namespace)}
            ))
    
    def validate_namespace_prefix(self, report) -> None:
        """Validate that namespace starts with required prefix."""
        required_prefix = self.settings.get('organization_specific', {}).get('required_namespace_prefix', 'FFS')
        
        if self.namespace_info.namespace and not self.namespace_info.namespace.startswith(required_prefix):
            report.add_result(ValidationResult(
                ValidationLevel.ERROR,
                f"Namespace must start with '{required_prefix}' prefix",
                context={'current_namespace': self.namespace_info.namespace, 'required_prefix': required_prefix}
            ))
        
        # Validate namespace format (FFS_XY)
        if self.namespace_info.namespace:
            if not re.match(r'^FFS_[A-Z]{2}$', self.namespace_info.namespace):
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    "Namespace must follow format 'FFS_XY' where XY is a 2-letter project abbreviation",
                    context={'current_namespace': self.namespace_info.namespace}
                ))
