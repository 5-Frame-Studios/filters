"""
Base class for all validation tests.
Defines the standard API that all tests must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..models import ValidationReport, ValidationResult, ValidationLevel
from ..utils import logger


class BaseValidatorTest(ABC):
    """Base class for all validation tests."""
    
    def __init__(self, settings: Dict[str, Any], namespace_info=None):
        self.settings = settings
        self.namespace_info = namespace_info
        self.report = ValidationReport()
    
    @abstractmethod
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        """
        Main validation method - must be implemented by subclasses.
        
        Args:
            pack_paths: Dictionary with 'BP' and 'RP' keys pointing to pack directories
            
        Returns:
            ValidationReport with results
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_test_name(self) -> str:
        """Return human-readable test name."""
        raise NotImplementedError
    
    @abstractmethod
    def get_test_description(self) -> str:
        """Return test description."""
        raise NotImplementedError
    
    def add_result(self, level: ValidationLevel, message: str, file_path: str = None, context: Dict[str, Any] = None):
        """Helper method to add validation results."""
        self.report.add_result(ValidationResult(level, message, file_path, context))
    
    def log_info(self, message: str):
        """Helper method to log info messages."""
        logger.info(f"[{self.get_test_name()}] {message}")
    
    def log_warning(self, message: str):
        """Helper method to log warning messages."""
        logger.warning(f"[{self.get_test_name()}] {message}")
    
    def log_error(self, message: str):
        """Helper method to log error messages."""
        logger.error(f"[{self.get_test_name()}] {message}")
