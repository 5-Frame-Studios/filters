"""
Main content validator class that orchestrates all validation modules.
Now uses the new test registry system for modular validation.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from .models import ValidationReport, ValidationResult, ValidationLevel
import json
import glob

from .utils import logger, find_pack_directories, get_first_existing_path
from .namespace_extractor import NamespaceExtractor
from .report_generator import ReportGenerator
from .tests.test_registry import test_registry


class MainValidator:
    """Main content validation class that orchestrates all validation modules."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.report = ValidationReport()
        self.namespace_info = None
        
        # Initialize namespace extractor and report generator
        self.namespace_extractor = NamespaceExtractor(settings)
        self.report_generator = ReportGenerator(settings)
    
    def validate_addon(self) -> ValidationReport:
        """Main validation method using the new test registry system."""
        logger.info("Starting Add-On content validation...")
        
        # Extract namespace and names (needed by many tests)
        self.namespace_info = self.namespace_extractor.extract_namespace_info()
        
        # Get pack paths
        pack_paths = self._get_pack_paths()
        
        # Run all tests using the registry
        test_instances = test_registry.run_all_tests(
            self.settings, 
            pack_paths,
            self.namespace_info
        )
        
        # Merge all test results into the main report
        for test_instance in test_instances:
            self.report.merge(test_instance.report)
        
        # Generate final report
        self.report_generator.generate_report(self.report, self.namespace_info)
        
        return self.report
    
    def _get_pack_paths(self) -> Dict[str, str]:
        """Get pack paths for the tests."""
        pack_paths = {}
        
        # Check for Regolith standard paths first
        regolith_bp_paths = [Path("packs/BP"), Path("packs/behavior"), Path("packs/behavior_pack")]
        regolith_rp_paths = [Path("packs/RP"), Path("packs/resource"), Path("packs/resource_pack")]
        
        for bp_path in regolith_bp_paths:
            if bp_path.exists():
                pack_paths['BP'] = str(bp_path)
                break
        
        for rp_path in regolith_rp_paths:
            if rp_path.exists():
                pack_paths['RP'] = str(rp_path)
                break
        
        # Check legacy directory names if Regolith paths not found
        if 'BP' not in pack_paths:
            legacy_bp_paths = [Path("BP"), Path("behavior"), Path("behavior_pack")]
            for alt_path in legacy_bp_paths:
                if alt_path.exists():
                    pack_paths['BP'] = str(alt_path)
                    break
        
        if 'RP' not in pack_paths:
            legacy_rp_paths = [Path("RP"), Path("resource"), Path("resource_pack")]
            for alt_path in legacy_rp_paths:
                if alt_path.exists():
                    pack_paths['RP'] = str(alt_path)
                    break
        
        return pack_paths
    
    def run_specific_test(self, test_name: str) -> ValidationReport:
        """Run a specific test by name."""
        logger.info(f"Running specific test: {test_name}")
        
        # Extract namespace info if needed
        if not self.namespace_info:
            self.namespace_info = self.namespace_extractor.extract_namespace_info()
        
        # Get pack paths
        pack_paths = self._get_pack_paths()
        
        # Map test name to class name
        test_name_mapping = {
            "Pack Structure": "PackStructureTest",
            "Manifest Validation": "ManifestTest", 
            "Namespace Usage": "NamespaceTest",
            "File Structure": "FileStructureTest",
            "Naming Conventions": "NamingTest",
            "Technical Restrictions": "TechnicalTest",
            "Debug Statements": "DebugTest",
            "Translatable Text": "TranslatableTest",
            "Organization Requirements": "OrganizationTest",
            "Content Guidelines": "ContentGuidelinesTest",
            "Minecraft Creator Tools": "MCTTest"
        }
        
        class_name = test_name_mapping.get(test_name, test_name)
        
        # Run the specific test
        test_instance = test_registry.create_test_instance(
            class_name, 
            self.settings, 
            self.namespace_info
        )
        test_instance.validate(pack_paths)
        
        return test_instance.report
    
    def list_available_tests(self) -> List[str]:
        """List all available tests."""
        return test_registry.list_tests()
    
    def get_test_execution_order(self) -> List[str]:
        """Get the execution order of tests."""
        return test_registry.get_execution_order()
