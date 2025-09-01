"""
Naming convention validation test.
Validates naming conventions for various asset types like geometry, animations, and render controllers.
"""

import os
import json
import glob
from typing import Dict, Any
from .base_test import BaseValidatorTest
from ..models import ValidationLevel, ValidationReport
from ..utils import find_pack_directories


class NamingTest(BaseValidatorTest):
    """Test for validating naming conventions."""
    
    def get_test_name(self) -> str:
        return "Naming Conventions"
    
    def get_test_description(self) -> str:
        return "Validates naming conventions for various asset types"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """Validate naming conventions."""
        self.log_info("Validating naming conventions...")
        
        if not self.namespace_info or not self.namespace_info.namespace:
            return self.report
        
        naming_patterns = self.settings.get('naming_patterns', {})
        pack_dirs = find_pack_directories()
        
        for pack_type, possible_paths in pack_dirs.items():
            for path in possible_paths:
                if os.path.exists(path):
                    # Validate geometry identifiers
                    self._validate_geometry_naming(path)
                    
                    # Validate animation naming
                    self._validate_animation_naming(path)
                    
                    # Validate render controller naming
                    self._validate_render_controller_naming(path)
                    break  # Found the first valid path for this pack type
        
        return self.report
    
    def _validate_geometry_naming(self, pack_path: str):
        """Validate geometry identifier naming."""
        geometry_files = glob.glob(f"{pack_path}/models/entity/*.json")
        
        for file_path in geometry_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'minecraft:geometry' in data:
                    geometry_id = data['minecraft:geometry']
                    if not geometry_id.startswith(f"geometry.{self.namespace_info.namespace}."):
                        self.add_result(
                            ValidationLevel.WARNING,
                            f"Geometry identifier should start with 'geometry.{self.namespace_info.namespace}.'",
                            file_path,
                            context={'current_id': geometry_id}
                        )
            
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    
    def _validate_animation_naming(self, pack_path: str):
        """Validate animation naming."""
        animation_files = glob.glob(f"{pack_path}/animations/*.json")
        
        for file_path in animation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for animation_name in data.get('animations', {}):
                    if not animation_name.startswith(f"animation.{self.namespace_info.namespace}."):
                        self.add_result(
                            ValidationLevel.WARNING,
                            f"Animation name should start with 'animation.{self.namespace_info.namespace}.'",
                            file_path,
                            context={'animation_name': animation_name}
                        )
            
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    
    def _validate_render_controller_naming(self, pack_path: str):
        """Validate render controller naming."""
        render_files = glob.glob(f"{pack_path}/render_controllers/*.json")
        
        for file_path in render_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for controller_name in data.get('render_controllers', {}):
                    if not controller_name.startswith(f"controller.render.{self.namespace_info.namespace}."):
                        self.add_result(
                            ValidationLevel.WARNING,
                            f"Render controller name should start with 'controller.render.{self.namespace_info.namespace}.'",
                            file_path,
                            context={'controller_name': controller_name}
                        )
            
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
