"""
Minecraft Creator Tools validation functionality.
"""

import os
import json
import shutil
from typing import Dict, Any
from .models import ValidationResult, ValidationLevel
from .utils import logger, MCT_AVAILABLE, subprocess, tempfile


class MCTValidator:
    """Validate using official Minecraft Creator Tools."""
    
    def __init__(self, settings: dict):
        self.settings = settings
    
    def validate_with_minecraft_creator_tools(self, report) -> None:
        """Validate using official Minecraft Creator Tools."""
        logger.info("Running Minecraft Creator Tools validation...")
        
        # Check if MCT integration is enabled
        mct_settings = self.settings.get('minecraft_creator_tools', {})
        if not mct_settings.get('enabled', True):
            logger.info("Minecraft Creator Tools integration disabled in settings")
            return
        
        if not MCT_AVAILABLE:
            logger.warning("Minecraft Creator Tools integration not available")
            return
        
        try:
            # Check if mct is available (use shell=True on Windows for proper path resolution)
            result = subprocess.run(['npx', 'mct', 'version'], 
                                  capture_output=True, text=True, timeout=30, shell=True)
            
            if result.returncode != 0:
                logger.warning(f"Minecraft Creator Tools not found. Return code: {result.returncode}, stderr: {result.stderr}")
                logger.warning("Install with: npm install -g @minecraft/creator-tools")
                return
            
            logger.info("Minecraft Creator Tools found, running validation...")
            
            # Create temporary output directory
            output_dir = tempfile.mkdtemp(prefix="mct_validation_")
            
            # Get MCT settings
            validation_suite = mct_settings.get('validation_suite', 'addon')
            timeout_seconds = mct_settings.get('timeout_seconds', 300)
            log_verbose = mct_settings.get('log_verbose', True)
            
            # Run MCT validation
            cmd = [
                'npx', 'mct', 'validate', validation_suite,
                '-i', os.getcwd(),  # Current working directory (Regolith temp dir)
                '-o', output_dir,  # Output to temp directory
            ]
            
            if log_verbose:
                cmd.append('--log-verbose')
            
            logger.info(f"Running MCT command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, shell=True)
            
            if result.returncode == 0:
                logger.info("Minecraft Creator Tools validation completed successfully")
                
                # Parse MCT output files
                self._parse_mct_results(output_dir, report)
            else:
                logger.warning(f"Minecraft Creator Tools validation failed: {result.stderr}")
                report.add_result(ValidationResult(
                    ValidationLevel.WARNING,
                    "Minecraft Creator Tools validation failed",
                    context={'mct_error': result.stderr}
                ))
            
            # Clean up temporary directory
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                logger.debug(f"Failed to clean up temp directory: {e}")
                
        except subprocess.TimeoutExpired:
            logger.warning("Minecraft Creator Tools validation timed out")
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                "Minecraft Creator Tools validation timed out"
            ))
        except FileNotFoundError as e:
            logger.warning(f"npx not found. Node.js and npm must be installed for MCT integration. Error: {e}")
            logger.debug(f"PATH: {os.environ.get('PATH', 'Not set')}")
        except Exception as e:
            logger.error(f"Error running Minecraft Creator Tools: {e}")
            report.add_result(ValidationResult(
                ValidationLevel.WARNING,
                f"Minecraft Creator Tools integration error: {e}"
            ))
    
    def _parse_mct_results(self, output_dir: str, report) -> None:
        """Parse Minecraft Creator Tools validation results."""
        try:
            # Look for MCT output files
            mct_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.json') or file.endswith('.txt'):
                        mct_files.append(os.path.join(root, file))
            
            if not mct_files:
                logger.info("No MCT output files found")
                return
            
            logger.info(f"Found {len(mct_files)} MCT output files")
            
            # Parse each output file
            for file_path in mct_files:
                self._parse_mct_file(file_path, report)
                
        except Exception as e:
            logger.error(f"Error parsing MCT results: {e}")
    
    def _parse_mct_file(self, file_path: str, report) -> None:
        """Parse a single MCT output file."""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract validation results from MCT JSON output
                if isinstance(data, dict):
                    self._extract_mct_validation_results(data, file_path, report)
                    
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse MCT text output
                self._parse_mct_text_output(content, file_path, report)
                
        except Exception as e:
            logger.debug(f"Error parsing MCT file {file_path}: {e}")
    
    def _extract_mct_validation_results(self, data: Dict[str, Any], file_path: str, report) -> None:
        """Extract validation results from MCT JSON output."""
        # Common MCT output patterns
        if 'errors' in data:
            for error in data['errors']:
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"MCT Error: {error.get('message', 'Unknown error')}",
                    file_path,
                    context={'mct_error': error}
                ))
        
        if 'warnings' in data:
            for warning in data['warnings']:
                report.add_result(ValidationResult(
                    ValidationLevel.WARNING,
                    f"MCT Warning: {warning.get('message', 'Unknown warning')}",
                    file_path,
                    context={'mct_warning': warning}
                ))
        
        if 'validation' in data:
            validation = data['validation']
            if isinstance(validation, dict):
                for key, value in validation.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                message = item.get('message', f'MCT {key}: {item}')
                                level = ValidationLevel.ERROR if 'error' in key.lower() else ValidationLevel.WARNING
                                report.add_result(ValidationResult(
                                    level,
                                    f"MCT {key}: {message}",
                                    file_path,
                                    context={'mct_validation': item}
                                ))
    
    def _parse_mct_text_output(self, content: str, file_path: str, report) -> None:
        """Parse MCT text output for validation results."""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for common MCT output patterns
            if 'ERROR:' in line.upper():
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"MCT Error: {line}",
                    file_path,
                    context={'mct_line': line}
                ))
            elif 'WARNING:' in line.upper():
                report.add_result(ValidationResult(
                    ValidationLevel.WARNING,
                    f"MCT Warning: {line}",
                    file_path,
                    context={'mct_line': line}
                ))
            elif 'FAILED:' in line.upper():
                report.add_result(ValidationResult(
                    ValidationLevel.ERROR,
                    f"MCT Failed: {line}",
                    file_path,
                    context={'mct_line': line}
                ))
