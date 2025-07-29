import os
import json
import logging
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[apply_version] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments."""
    try:
        if len(sys.argv) > 1:
            return json.loads(sys.argv[1])
        else:
            logger.warning("No settings provided, using defaults")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse settings: {e}")
        return {}

def validate_version(version: List[int]) -> bool:
    """Validate version format."""
    if not isinstance(version, list) or len(version) != 3:
        return False
    return all(isinstance(v, int) and v >= 0 for v in version)

def create_version_file(version_file_path: str) -> None:
    """Creates a version file with default version."""
    try:
        version_dir = Path(version_file_path).parent
        version_dir.mkdir(parents=True, exist_ok=True)
        
        default_version = {"version": [1, 0, 0]}
        with open(version_file_path, 'w', encoding='utf-8') as file:
            json.dump(default_version, file, indent=4)
        logger.info(f"Created version file at {version_file_path}")
    except Exception as e:
        logger.error(f"Failed to create version file: {e}")
        raise

def get_version(version_file_path: str) -> List[int]:
    """
    Gets the current version number from the version file and increments it.
    
    Args:
        version_file_path: Path to the version file
        
    Returns:
        Current version as list of integers
        
    Raises:
        ValueError: If version format is invalid
        FileNotFoundError: If version file doesn't exist and can't be created
    """
    try:
        # Create version file if it doesn't exist
        if not os.path.exists(version_file_path):
            create_version_file(version_file_path)

        # Read version file
        with open(version_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate version format
        if not validate_version(data.get('version', [])):
            raise ValueError("Invalid version format in version file")

        # Update version (increment patch version)
        current_version = data['version']
        new_version = current_version.copy()
        new_version[-1] = new_version[-1] + 1
        
        # Save updated version
        data['version'] = new_version
        with open(version_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        logger.info(f"Version incremented from {current_version} to {new_version}")
        return new_version

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in version file: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to process version file: {e}")
        raise

def update_manifest(manifest: Dict[str, Any], version: List[int]) -> Dict[str, Any]:
    """
    Apply a new version to manifest components.
    
    Args:
        manifest: Parsed JSON manifest
        version: Version triple like [1, 2, 3]
        
    Returns:
        The modified manifest
    """
    try:
        # Update header version
        if "header" in manifest and "version" in manifest["header"]:
            manifest["header"]["version"] = version
            logger.debug("Updated header version")

        # Update selected modules (resources and data types)
        allowed_types = {"resources", "data"}
        modules_updated = 0
        for module in manifest.get("modules", []):
            if module.get("type") in allowed_types:
                module["version"] = version
                modules_updated += 1
        if modules_updated > 0:
            logger.debug(f"Updated {modules_updated} modules")

        # Update dependencies with UUID
        deps_updated = 0
        for dep in manifest.get("dependencies", []):
            if dep.get("uuid") is not None:
                dep["version"] = version
                deps_updated += 1
        if deps_updated > 0:
            logger.debug(f"Updated {deps_updated} dependencies")

        return manifest

    except Exception as e:
        logger.error(f"Failed to update manifest: {e}")
        raise

def process_manifest_file(file_path: str, version: List[int]) -> bool:
    """
    Process a single manifest file.
    
    Args:
        file_path: Path to the manifest file
        version: Version to apply
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Manifest file not found: {file_path}")
            return False

        # Read manifest
        with open(file_path, 'r', encoding='utf-8') as manifest_file:
            manifest = json.load(manifest_file)

        # Update manifest
        updated_manifest = update_manifest(manifest, version)

        # Write updated manifest
        with open(file_path, 'w', encoding='utf-8') as manifest_file:
            json.dump(updated_manifest, manifest_file, indent=4)

        logger.info(f"Successfully updated {file_path}")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return False

def main():
    """Main execution function."""
    try:
        # Parse settings
        settings = parse_settings()
        
        # Get configuration from settings
        version_file = settings.get('version_file', './data/bump_manifest/version.json')
        targets = settings.get('targets', ['RP/manifest.json', 'BP/manifest.json'])
        
        logger.info("Starting version update process")
        
        # Get current version and increment it
        version = get_version(version_file)
        logger.info(f"Pack updated to version: {version}")

        # Process each target manifest file
        successful_updates = 0
        for target in targets:
            if process_manifest_file(target, version):
                successful_updates += 1

        if successful_updates == 0:
            logger.warning("No manifest files were successfully updated")
        else:
            logger.info(f"Successfully updated {successful_updates} manifest file(s)")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()