"""
Pack structure validation test.
Validates that BP and RP directories exist and are properly structured.
"""

import os
from pathlib import Path
from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import logger


class PackStructureTest(BaseValidatorTest):
    """Test for validating pack structure."""
    
    def get_test_name(self) -> str:
        return "Pack Structure"
    
    def get_test_description(self) -> str:
        return "Validates that BP and RP directories exist and are properly structured"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate pack structure."""
        self.log_info("Starting pack structure validation...")
        
        # Check for BP and RP directories
        bp_found = self._check_bp_directory(pack_paths)
        rp_found = self._check_rp_directory(pack_paths)
        
        if bp_found and rp_found:
            self.log_info("Pack structure detected: BP and RP directories found")
        else:
            self.log_warning("Incomplete pack structure detected - some validation may be limited")
        
        return self.report
    
    def _check_bp_directory(self, pack_paths: Dict[str, str]) -> bool:
        """Check for behavior pack directory."""
        # Check if BP path is provided in pack_paths
        if 'BP' in pack_paths and os.path.exists(pack_paths['BP']):
            return True
        
        # Check for Regolith standard paths first
        regolith_bp_paths = [Path("packs/BP"), Path("packs/behavior"), Path("packs/behavior_pack")]
        for bp_path in regolith_bp_paths:
            if bp_path.exists():
                self.log_info(f"Behavior Pack found at: {bp_path}")
                return True
        
        # Check legacy directory names
        legacy_bp_paths = [Path("BP"), Path("behavior"), Path("behavior_pack")]
        for alt_path in legacy_bp_paths:
            if alt_path.exists():
                self.log_info(f"Behavior Pack found at: {alt_path}")
                return True
        
        self.add_result(
            ValidationLevel.ERROR,
            "Behavior Pack directory not found (checked: packs/BP/, packs/behavior/, packs/behavior_pack/, BP/, behavior/, behavior_pack/)"
        )
        return False
    
    def _check_rp_directory(self, pack_paths: Dict[str, str]) -> bool:
        """Check for resource pack directory."""
        # Check if RP path is provided in pack_paths
        if 'RP' in pack_paths and os.path.exists(pack_paths['RP']):
            return True
        
        # Check for Regolith standard paths first
        regolith_rp_paths = [Path("packs/RP"), Path("packs/resource"), Path("packs/resource_pack")]
        for rp_path in regolith_rp_paths:
            if rp_path.exists():
                self.log_info(f"Resource Pack found at: {rp_path}")
                return True
        
        # Check legacy directory names
        legacy_rp_paths = [Path("RP"), Path("resource"), Path("resource_pack")]
        for alt_path in legacy_rp_paths:
            if alt_path.exists():
                self.log_info(f"Resource Pack found at: {alt_path}")
                return True
        
        self.add_result(
            ValidationLevel.ERROR,
            "Resource Pack directory not found (checked: packs/RP/, packs/resource/, packs/resource_pack/, RP/, resource/, resource_pack/)"
        )
        return False
