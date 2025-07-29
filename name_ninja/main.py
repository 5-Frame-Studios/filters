"""
This filter is used to automatically generate entity, block, and item names,
based on a custom 'name' field, or automatically generated based on the entities
identifier. See 'readme.md' for more information.
"""

import sys
import json
import logging
from typing import List, NamedTuple, Dict, Any, Optional
from enum import Enum
import builtins
import functools
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[name_ninja] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# defining open function
original_open = builtins.open

# applying utf8 formatting to default open method
@functools.wraps(original_open)
def utf8_open(*args, **kwargs):
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return original_open(*args, **kwargs)
builtins.open = utf8_open

from reticulator import *

class AssetType(Enum):
    """Enumeration of supported asset types."""
    SPAWN_EGG = "spawn_egg"
    ITEM = "item"
    BLOCK = "block"
    ENTITY = "entity"

class NameJsonPath(NamedTuple):
    """Describes a jsonpath candidate when gathering translations.

    path: the JSONPath to read
    should_pop: whether the value should be removed from the underlying JSON once read
    add_affixes: if True, the gathered value will be wrapped with prefix/postfix.
    """
    path: str
    should_pop: bool = False
    add_affixes: bool = False

class LocalizationGenerator:
    """Handles generation of localization keys and values."""
    
    @staticmethod
    def generate_localization_key(asset_type: AssetType, identifier: str) -> Optional[str]:
        """
        Generates the localization key for the asset type.
        
        Args:
            asset_type: Type of asset (entity, item, block, spawn_egg)
            identifier: Asset identifier
            
        Returns:
            Localization key or None if not supported
        """
        key_templates = {
            AssetType.ENTITY: "entity.{}.name",
            AssetType.ITEM: "item.{}.name",
            AssetType.BLOCK: "tile.{}.name",
            AssetType.SPAWN_EGG: "item.spawn_egg.entity.{}.name"
        }
        
        template = key_templates.get(asset_type)
        if not template:
            logger.warning(f"Unsupported asset type: {asset_type}")
            return None
            
        return template.format(identifier)
    
    @staticmethod
    def format_name(identifier: str) -> str:
        """
        Formats a name based on the identifier, removing the namespace.
        
        Args:
            identifier: Asset identifier (e.g., "namespace:asset_name")
            
        Returns:
            Formatted name (e.g., "Asset Name")
        """
        try:
            # Split by namespace and take the asset name part
            asset_name = identifier.split(":", 1)[1] if ":" in identifier else identifier
            # Replace underscores with spaces and title case
            return asset_name.replace("_", " ").title()
        except (IndexError, AttributeError):
            logger.warning(f"Invalid identifier format: {identifier}")
            return identifier

class AssetProcessor:
    """Handles processing of individual assets."""
    
    def __init__(self, settings: Dict[str, Any], ignored_namespaces: List[str]):
        self.settings = settings
        self.ignored_namespaces = ignored_namespaces
        self.generator = LocalizationGenerator()
    
    def should_process_asset(self, asset: JsonResource) -> bool:
        """Check if asset should be processed based on namespace."""
        try:
            identifier = asset.identifier
            namespace = identifier.split(':', 1)[0] if ':' in identifier else ''
            return namespace not in self.ignored_namespaces
        except AssetNotFoundError:
            logger.warning(f"Asset {asset.filepath} has no identifier, skipping...")
            return False
    
    def extract_localization_value(self, asset: JsonResource, name_jsonpaths: List[NameJsonPath]) -> Optional[str]:
        """
        Extract localization value from asset using JSON paths.
        
        Args:
            asset: Asset to process
            name_jsonpaths: List of JSON paths to try
            
        Returns:
            Localization value or None if not found
        """
        for jp in name_jsonpaths:
            try:
                if jp.should_pop:
                    value = asset.pop_jsonpath(jp.path)
                else:
                    value = asset.get_jsonpath(jp.path)
                
                if value is not None:
                    # Add affixes if requested
                    if jp.add_affixes:
                        prefix = self.settings.get('prefix', '')
                        postfix = self.settings.get('postfix', '')
                        value = prefix + value + postfix
                    return value
                    
            except AssetNotFoundError:
                continue
        
        return None
    
    def generate_auto_name(self, asset: JsonResource) -> Optional[str]:
        """Generate automatic name from identifier."""
        auto_name = self.settings.get('auto_name', False)
        
        if auto_name in [True, "from_entity_name"]:
            try:
                identifier = asset.identifier
                formatted_name = self.generator.format_name(identifier)
                prefix = self.settings.get('prefix', '')
                postfix = self.settings.get('postfix', '')
                return prefix + formatted_name + postfix
            except AssetNotFoundError:
                return None
        
        return None
    
    def process_asset(self, asset: JsonResource, asset_type: AssetType, name_jsonpaths: List[NameJsonPath]) -> Optional[Translation]:
        """
        Process a single asset and return translation if successful.
        
        Args:
            asset: Asset to process
            asset_type: Type of asset
            name_jsonpaths: JSON paths to try for name extraction
            
        Returns:
            Translation object or None if processing failed
        """
        # Check if asset should be processed
        if not self.should_process_asset(asset):
            return None
        
        try:
            identifier = asset.identifier
        except AssetNotFoundError:
            return None
        
        # Generate localization key
        localization_key = self.generator.generate_localization_key(asset_type, identifier)
        if not localization_key:
            return None
        
        # Try to extract localization value
        localization_value = self.extract_localization_value(asset, name_jsonpaths)
        
        # Try auto-generation if no value found
        if localization_value is None:
            localization_value = self.generate_auto_name(asset)
        
        # Skip if no value could be determined
        if localization_value is None:
            return None
        
        return Translation(localization_key, localization_value, "")

def gather_translations(
    asset_type: AssetType, 
    assets: List[JsonFileResource], 
    settings: Dict[str, Any], 
    name_jsonpaths: List[NameJsonPath], 
    ignored_namespaces: List[str]
) -> List[Translation]:
    """
    Gathers translations from assets.
    
    Args:
        asset_type: Type of assets to process
        assets: List of assets to process
        settings: Processing settings
        name_jsonpaths: JSON paths to try for name extraction
        ignored_namespaces: Namespaces to ignore
        
    Returns:
        List of translations
    """
    processor = AssetProcessor(settings, ignored_namespaces)
    translations = []
    
    logger.info(f"Processing {len(assets)} {asset_type.value} assets")
    
    for i, asset in enumerate(assets, 1):
        logger.debug(f"Processing {asset_type.value} {i}/{len(assets)}: {asset.filepath}")
        
        translation = processor.process_asset(asset, asset_type, name_jsonpaths)
        if translation:
            translations.append(translation)
            logger.debug(f"Generated translation: {translation.key}")
    
    logger.info(f"Generated {len(translations)} translations for {asset_type.value}")
    return translations

def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments."""
    try:
        if len(sys.argv) > 1:
            return json.loads(sys.argv[1])
        else:
            logger.warning("No settings provided. Using default settings.")
            return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse settings: {e}")
        return {}

def validate_language_settings(settings: Dict[str, Any]) -> List[str]:
    """Validate and extract language settings."""
    # Handle backward compatibility
    if "languages" in settings:
        languages = settings["languages"]
        if isinstance(languages, str):
            languages = [languages]
            logger.warning("The 'languages' setting should be an array of strings. A single string was provided and automatically converted to a list.")
        elif not isinstance(languages, list):
            raise ValueError("The 'languages' setting must be a list of strings.")
    else:
        language = settings.get("language", "en_US.lang")
        if isinstance(language, str):
            languages = [language]
            logger.warning("The 'language' setting is deprecated in the latest version. Please use 'languages' instead for future configurations.")
        else:
            raise ValueError("The 'language' setting must be a string if 'languages' is not provided.")
    
    return languages

def create_language_file_if_missing(language: str, resource_pack: ResourcePack) -> LanguageFile:
    """Create language file if it doesn't exist."""
    try:
        return resource_pack.get_language_file(f"texts/{language}")
    except AssetNotFoundError:
        logger.info(f"Creating language file: {language}")
        Path(os.path.join(resource_pack.input_path, 'texts')).mkdir(parents=True, exist_ok=True)
        builtins.open(os.path.join(resource_pack.input_path, 'texts', language), 'a', encoding='utf-8').close()
        return LanguageFile(filepath=f'texts/{language}', pack=resource_pack)

def main():
    """The entry point for the script."""
    try:
        # Parse settings
        settings = parse_settings()
        
        # Extract and validate settings
        overwrite = settings.get("overwrite", False)
        languages = validate_language_settings(settings)
        sort = settings.get("sort", False)
        ignored_namespaces = settings.get("ignored_namespaces", ['minecraft'])
        
        logger.info("Starting localization generation")
        logger.info(f"Languages: {languages}")
        logger.info(f"Ignored namespaces: {ignored_namespaces}")
        
        # Initialize project
        project = Project("./BP", "./RP")
        behavior_pack = project.behavior_pack
        resource_pack = project.resource_pack
        
        # Define JSON paths for each asset type
        asset_configs = {
            AssetType.SPAWN_EGG: {
                'assets': behavior_pack.entities,
                'settings': settings.get("spawn_eggs", {}),
                'jsonpaths': [
                    NameJsonPath("minecraft:entity/description/spawn_egg_name", True, False),
                    NameJsonPath("minecraft:entity/description/name", False, 
                               settings.get("spawn_eggs", {}).get("auto_name") == "from_entity_name"),
                ]
            },
            AssetType.ITEM: {
                'assets': behavior_pack.items,
                'settings': settings.get("items", {}),
                'jsonpaths': [NameJsonPath("minecraft:item/description/name", True, False)]
            },
            AssetType.BLOCK: {
                'assets': behavior_pack.blocks,
                'settings': settings.get("blocks", {}),
                'jsonpaths': [NameJsonPath("minecraft:block/description/name", True, False)]
            },
            AssetType.ENTITY: {
                'assets': behavior_pack.entities,
                'settings': settings.get("entities", {}),
                'jsonpaths': [NameJsonPath("minecraft:entity/description/name", True, False)]
            }
        }
        
        # Gather all translations
        all_translations = []
        for asset_type, config in asset_configs.items():
            translations = gather_translations(
                asset_type,
                config['assets'],
                config['settings'],
                config['jsonpaths'],
                ignored_namespaces
            )
            all_translations.extend(translations)
        
        logger.info(f"Total translations generated: {len(all_translations)}")
        
        # Write translations to language files
        for language in languages:
            try:
                language_file = create_language_file_if_missing(language, resource_pack)
                
                for translation in all_translations:
                    language_file.add_translation(translation, overwrite=overwrite)
                
                if sort:
                    language_file.translations.sort(key=lambda t: t.key)
                
                logger.info(f"Updated language file: {language}")
                
            except Exception as e:
                logger.error(f"Failed to process language file {language}: {e}")
        
        # Save project
        project.save()
        logger.info("Localization generation completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()