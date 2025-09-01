"""
Report generation and display functionality.
"""

import os
import json
from typing import Dict, Any
from .models import ValidationReport
from .utils import logger, RICH_AVAILABLE
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    Console = Table = Panel = Text = None


class ReportGenerator:
    """Generate and display validation reports."""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.console = Console() if RICH_AVAILABLE else None
    
    def generate_report(self, report: ValidationReport, namespace_info) -> None:
        """Generate final validation report."""
        logger.info("Generating validation report...")
        
        if self.settings.get('generate_report', True):
            report_data = {
                'summary': {
                    'total_files_checked': report.total_files_checked,
                    'total_errors': report.total_errors,
                    'total_warnings': report.total_warnings,
                    'total_info': report.total_info,
                    'total_possible_issues': report.total_possible_issues,
                    'is_valid': report.is_valid()
                },
                'results': [
                    {
                        'level': result.level.value,
                        'message': result.message,
                        'file_path': result.file_path,
                        'line_number': result.line_number,
                        'context': result.context
                    }
                    for result in report.validation_results
                ],
                'namespace_info': {
                    'namespace': namespace_info.namespace,
                    'studio_name': namespace_info.studio_name,
                    'pack_name': namespace_info.pack_name
                }
            }
            
            # Save report to file
            report_path = "data/content_validator_report.json"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Validation report saved to {report_path}")
        
        # Display summary
        self._display_summary(report, namespace_info)
    
    def _display_summary(self, report: ValidationReport, namespace_info) -> None:
        """Display validation summary."""
        if self.console and RICH_AVAILABLE:
            self._display_rich_summary(report, namespace_info)
        else:
            self._display_text_summary(report, namespace_info)
    
    def _display_rich_summary(self, report: ValidationReport, namespace_info) -> None:
        """Display rich formatted summary."""
        try:
            # Create summary table
            table = Table(title="Content Validation Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Files Checked", str(report.total_files_checked))
            table.add_row("Errors", str(report.total_errors))
            table.add_row("Warnings", str(report.total_warnings))
            table.add_row("Info", str(report.total_info))
            table.add_row("Possible Issues", str(report.total_possible_issues))
            table.add_row("Valid", "Yes" if report.is_valid() else "No")
            
            self.console.print(table)
            
            # Display namespace info
            if namespace_info.namespace:
                namespace_text = Text(f"Namespace: {namespace_info.namespace}")
                if namespace_info.studio_name and namespace_info.pack_name:
                    namespace_text.append(f"\nStudio: {namespace_info.studio_name}")
                    namespace_text.append(f"\nPack: {namespace_info.pack_name}")
                
                self.console.print(Panel(namespace_text, title="Namespace Information"))
        except Exception as e:
            # Fallback to text output if rich fails
            logger.debug(f"Rich display failed: {e}")
            self._display_text_summary(report, namespace_info)
    
    def _display_text_summary(self, report: ValidationReport, namespace_info) -> None:
        """Display text summary."""
        logger.info("=" * 50)
        logger.info("CONTENT VALIDATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Files Checked: {report.total_files_checked}")
        logger.info(f"Errors: {report.total_errors}")
        logger.info(f"Warnings: {report.total_warnings}")
        logger.info(f"Info: {report.total_info}")
        logger.info(f"Possible Issues: {report.total_possible_issues}")
        logger.info(f"Valid: {'Yes' if report.is_valid() else 'No'}")
        
        if namespace_info.namespace:
            logger.info(f"Namespace: {namespace_info.namespace}")
            if namespace_info.studio_name and namespace_info.pack_name:
                logger.info(f"Studio: {namespace_info.studio_name}")
                logger.info(f"Pack: {namespace_info.pack_name}")
        
        logger.info("=" * 50)
