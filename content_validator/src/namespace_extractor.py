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
        # Try to find namespace from various sources with flexible paths
        namespace_sources = [
            "BP/manifest.json",
            "RP/manifest.json",
            "behavior/manifest.json",
            "resource/manifest.json",
            "behavior_pack/manifest.json",
            "resource_pack/manifest.json",
            "packs/behavior/manifest.json",
            "packs/resource/manifest.json",
            "BP/entities/*.json",
            "BP/blocks/*.json",
            "BP/items/*.json",
            "behavior/entities/*.json",
            "behavior/blocks/*.json",
            "behavior/items/*.json"
        ]
        
        for source in namespace_sources:
            if "*" in source:
                # Handle glob patterns
                try:
                    files = glob.glob(source)
                    for file_path in files:
                        self._extract_namespace_from_file(file_path)
                except Exception as e:
                    logger.debug(f"Error globbing {source}: {e}")
            else:
                self._extract_namespace_from_file(source)
        
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
        data = safe_json_load(file_path)
        if not data:
            return
        
        # Look for namespace in various fields
        if isinstance(data, dict):
            # Check common identifier fields
            identifier_fields = ['identifier', 'name', 'id']
            for field in identifier_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, str) and ':' in value:
                        namespace = value.split(':')[0]
                        if namespace not in self.settings.get('forbidden_namespaces', []):
                            self.namespace_info.namespace = namespace
                            return
            
            # Check for minecraft:entity structure
            if 'minecraft:entity' in data:
                entity_data = data['minecraft:entity']
                if isinstance(entity_data, dict) and 'description' in entity_data:
                    description = entity_data['description']
                    if isinstance(description, dict) and 'identifier' in description:
                        identifier = description['identifier']
                        if isinstance(identifier, str) and ':' in identifier:
                            namespace = identifier.split(':')[0]
                            if namespace not in self.settings.get('forbidden_namespaces', []):
                                self.namespace_info.namespace = namespace
                                return
    
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
