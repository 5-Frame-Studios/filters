"""
Test registry for managing all validation tests.
Handles test discovery, registration, and execution order.
"""

from typing import Dict, List, Type
from .base_test import BaseValidatorTest

# Import all test classes
from .pack_structure_test import PackStructureTest
from .manifest_test import ManifestTest
from .namespace_test import NamespaceTest
from .file_structure_test import FileStructureTest
from .naming_test import NamingTest
from .technical_test import TechnicalTest
from .debug_test import DebugTest
from .translatable_test import TranslatableTest
from .content_guidelines_test import ContentGuidelinesTest
from .mct_test import MCTTest
from .organization_test import OrganizationTest


class TestRegistry:
    """Registry for managing all validation tests."""
    
    def __init__(self):
        self._tests: Dict[str, Type[BaseValidatorTest]] = {}
        self._execution_order: List[str] = []
        self._register_default_tests()
    
    def _register_default_tests(self):
        """Register all default tests in execution order."""
        # Register tests in execution order (dependencies first)
        self.register_test(PackStructureTest, 0)  # Must run first to detect pack structure
        self.register_test(ManifestTest, 1)  # Early validation
        self.register_test(NamespaceTest, 2)  # Namespace info needed by other tests
        self.register_test(FileStructureTest, 3)  # File structure validation
        self.register_test(NamingTest, 4)  # Naming conventions
        self.register_test(TechnicalTest, 5)  # Technical restrictions
        self.register_test(DebugTest, 6)  # Debug statements
        self.register_test(TranslatableTest, 7)  # Translatable text
        self.register_test(OrganizationTest, 8)  # Organization requirements
        self.register_test(ContentGuidelinesTest, 9)  # Content guidelines
        self.register_test(MCTTest, 10)  # MCT validation (last)
    
    def register_test(self, test_class: Type[BaseValidatorTest], execution_order: int = None):
        """
        Register a test class.
        
        Args:
            test_class: The test class to register
            execution_order: Optional execution order (lower numbers run first)
        """
        test_name = test_class.__name__
        self._tests[test_name] = test_class
        
        if execution_order is not None:
            # Insert at the specified position
            if execution_order >= len(self._execution_order):
                self._execution_order.append(test_name)
            else:
                self._execution_order.insert(execution_order, test_name)
        else:
            # Add to end if no order specified
            if test_name not in self._execution_order:
                self._execution_order.append(test_name)
    
    def get_test(self, test_name: str) -> Type[BaseValidatorTest]:
        """Get a test class by name."""
        return self._tests.get(test_name)
    
    def list_tests(self) -> List[str]:
        """List all registered test names."""
        return list(self._tests.keys())
    
    def get_execution_order(self) -> List[str]:
        """Get the execution order of tests."""
        return self._execution_order.copy()
    
    def create_test_instance(self, test_name: str, settings: Dict, namespace_info=None) -> BaseValidatorTest:
        """Create an instance of a test."""
        test_class = self.get_test(test_name)
        if test_class:
            return test_class(settings, namespace_info)
        raise ValueError(f"Test '{test_name}' not found")
    
    def run_all_tests(self, settings: Dict, pack_paths: Dict[str, str], namespace_info=None) -> List[BaseValidatorTest]:
        """Run all tests in execution order."""
        test_instances = []
        
        for test_name in self._execution_order:
            test_instance = self.create_test_instance(test_name, settings, namespace_info)
            test_instance.validate(pack_paths)
            test_instances.append(test_instance)
        
        return test_instances


# Global test registry instance
test_registry = TestRegistry()
