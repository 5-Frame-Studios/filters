"""
Utility functions and imports for the content validator.
"""

import os
import sys
import json
import logging
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union, Set
import glob
import re
from collections import defaultdict

# Import validation libraries
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("PyYAML not available. YAML validation disabled.")

try:
    from jsonschema import validate, ValidationError as JSONValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available. JSON validation disabled.")

try:
    from dpath.util import search, get
    DPATH_AVAILABLE = True
except ImportError:
    DPATH_AVAILABLE = False
    logging.warning("dpath not available. Advanced JSON search disabled.")

try:
    from reticulator import *
    RETICULATOR_AVAILABLE = True
except ImportError:
    RETICULATOR_AVAILABLE = False
    logging.warning("Reticulator not available. Pack processing features disabled.")

# Optional rich output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Minecraft Creator Tools integration
try:
    import subprocess
    import tempfile
    MCT_AVAILABLE = True
except ImportError:
    MCT_AVAILABLE = False
    logging.warning("subprocess not available. Minecraft Creator Tools integration disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[content_validator] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments or filter.json."""
    try:
        # Try to get settings from command line arguments first (Regolith way)
        if len(sys.argv) > 1:
            settings = json.loads(sys.argv[1])
            logger.debug(f"Loaded settings from command line: {settings}")
            return settings
        else:
            # Fallback: try to load from filter.json
            filter_json_path = os.path.join(os.path.dirname(__file__), '..', 'filter.json')
            if os.path.exists(filter_json_path):
                with open(filter_json_path, 'r', encoding='utf-8') as f:
                    filter_data = json.load(f)
                    settings = filter_data.get('settings', {})
                    logger.debug(f"Loaded settings from filter.json: {settings}")
                    return settings
            else:
                logger.warning("No settings provided and filter.json not found, using defaults")
                return {}
    except (IndexError, json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Failed to parse settings: {e}")
        # Return default settings that match filter.json
        return {
            "exit_on_error": False,
            "log_level": "INFO",
            "strict_mode": True,
            "generate_report": True
        }


def get_regolith_environment() -> Dict[str, str]:
    """Get Regolith environment variables for external file access if needed."""
    return {
        'ROOT_DIR': os.environ.get('ROOT_DIR', ''),
        'FILTER_DIR': os.environ.get('FILTER_DIR', ''),
        'WORKING_DIR': os.getcwd()
    }


def find_pack_directories() -> Dict[str, List[str]]:
    """Find pack directories with flexible naming (Regolith temp paths first)."""
    return {
        'BP': ['BP', 'behavior', 'behavior_pack', 'packs/BP', 'packs/behavior', 'packs/behavior_pack'],
        'RP': ['RP', 'resource', 'resource_pack', 'packs/RP', 'packs/resource', 'packs/resource_pack']
    }


def get_first_existing_path(possible_paths: List[str]) -> Optional[str]:
    """Get the first existing path from a list of possible paths."""
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def safe_file_read(file_path: str) -> Optional[str]:
    """Safely read file content with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None
