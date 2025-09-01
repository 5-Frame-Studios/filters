"""
Data models and enums for the content validator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
import logging


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult:
    """Represents a validation result."""
    
    def __init__(self, level: ValidationLevel, message: str, file_path: Optional[str] = None, 
                 line_number: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        self.level = level
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.context = context or {}
        self.timestamp = logging.time.time()


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_files_checked: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    total_info: int = 0
    validation_results: List[ValidationResult] = field(default_factory=list)
    namespace_usage: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    file_structure_issues: List[str] = field(default_factory=list)
    manifest_issues: List[str] = field(default_factory=list)
    naming_issues: List[str] = field(default_factory=list)
    technical_issues: List[str] = field(default_factory=list)
    size_issues: List[str] = field(default_factory=list)
    
    def add_result(self, result: ValidationResult):
        """Add a validation result to the report."""
        self.validation_results.append(result)
        if result.level == ValidationLevel.ERROR:
            self.total_errors += 1
        elif result.level == ValidationLevel.WARNING:
            self.total_warnings += 1
        else:
            self.total_info += 1
    
    def is_valid(self) -> bool:
        """Check if the Add-On passes validation."""
        return self.total_errors == 0
    
    def merge(self, other_report: 'ValidationReport'):
        """Merge another validation report into this one."""
        self.total_files_checked += other_report.total_files_checked
        self.total_errors += other_report.total_errors
        self.total_warnings += other_report.total_warnings
        self.total_info += other_report.total_info
        
        # Merge validation results
        self.validation_results.extend(other_report.validation_results)
        
        # Merge namespace usage
        for namespace, files in other_report.namespace_usage.items():
            self.namespace_usage[namespace].update(files)
        
        # Merge other lists
        self.file_structure_issues.extend(other_report.file_structure_issues)
        self.manifest_issues.extend(other_report.manifest_issues)
        self.naming_issues.extend(other_report.naming_issues)
        self.technical_issues.extend(other_report.technical_issues)
        self.size_issues.extend(other_report.size_issues)
    
    @property
    def results(self):
        """Get validation results as a list of dictionaries for JSON serialization."""
        return [
            {
                'level': result.level.value,
                'message': result.message,
                'file_path': result.file_path,
                'line_number': result.line_number,
                'context': result.context
            }
            for result in self.validation_results
        ]
    
    @property
    def summary(self):
        """Get summary information for JSON serialization."""
        return {
            'total_files_checked': self.total_files_checked,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'total_info': self.total_info,
            'is_valid': self.is_valid()
        }


@dataclass
class NamespaceInfo:
    """Namespace information extracted from pack files."""
    namespace: Optional[str] = None
    studio_name: Optional[str] = None
    pack_name: Optional[str] = None
