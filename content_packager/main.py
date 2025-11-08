#!/usr/bin/env python3
"""
Content Packager Filter for Regolith

Packages Minecraft Bedrock content for marketplace submission.
Supports Resource Packs, Behavior Packs, Add-Ons, World Templates, and Skin Packs
with proper folder structure, manifest generation, and interactive CLI.

Regolith Integration:
- Works in temporary directory with RP/, BP/, and data/ subdirectories
- Non-destructive packaging - creates output without modifying original files
- Uses environment variables for external file access if needed
- Generates comprehensive packaging reports

Features:
- Interactive CLI for user input when needed
- Settings persistence - saves user inputs and assets to data folder
- Automatic folder structure creation
- Manifest generation with proper UUIDs
- Asset validation and organization
- Marketplace compliance checking
- Support for all content types
"""

import sys
import json
import os
import shutil
import uuid
import logging
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[content_packager] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Supported content types for packaging."""
    MASHUP = "mashup"
    SKIN_PACK = "skin_pack"
    TEXTURE_PACK = "texture_pack"
    TEXTURE_PACK_SKIN_PACK = "texture_pack_skin_pack"
    WORLD = "world"
    WORLD_SKIN_PACK = "world_skin_pack"
    ADDON = "addon"

@dataclass
class ContentInfo:
    """Information about the content being packaged."""
    name: str
    description: str
    author: str
    content_type: ContentType
    acronym: str
    version: str = "1.0.0"
    min_engine_version: str = "1.20.0"

@dataclass
class AssetInfo:
    """Information about required assets."""
    asset_type: str
    file_path: str
    required: bool = True
    validated: bool = False

class ContentPackager:
    """Main class for packaging Minecraft Bedrock content."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.content_info: Optional[ContentInfo] = None
        self.assets: List[AssetInfo] = []
        self.output_dir = Path(settings.get('output_directory', './packaged_content'))
        
        # Use Regolith data folder structure
        self.data_dir = Path('./packs/data/content_packager')
        self.settings_file = self.data_dir / 'user_settings.json'
        self.asset_info_file = self.data_dir / 'asset_info.json'
        self.assets_dir = self.data_dir / 'assets'
        self.user_defaults: Dict[str, Any] = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with the appropriate level."""
        getattr(logger, level.lower())(message)
    
    def show_file_picker(self, title: str, file_types: List[Tuple[str, str]]) -> Optional[Path]:
        """Show a file picker dialog for selecting assets."""
        try:
            # Create a root window and hide it
            root = tk.Tk()
            root.withdraw()
            
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=file_types
            )
            
            root.destroy()
            
            if file_path:
                return Path(file_path)
            return None
        except Exception as e:
            self.log(f"Error showing file picker: {e}", "WARNING")
            return None
    
    def load_user_defaults(self) -> Dict[str, Any]:
        """Load user defaults from saved settings file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.user_defaults = json.load(f)
                self.log(f"Loaded user defaults from {self.settings_file}")
            else:
                self.user_defaults = {}
                self.log("No saved user defaults found, using system defaults")
        except Exception as e:
            self.log(f"Error loading user defaults: {e}", "WARNING")
            self.user_defaults = {}
        
        return self.user_defaults
    
    def save_user_defaults(self, content_info: ContentInfo) -> None:
        """Save user inputs as defaults for future runs."""
        try:
            # Ensure data directory exists
            self.data_dir.mkdir(exist_ok=True)
            
            # Update user defaults with current content info
            self.user_defaults.update({
                'last_content_name': content_info.name,
                'last_description': content_info.description,
                'last_author': content_info.author,
                'last_content_type': content_info.content_type.value,
                'last_acronym': content_info.acronym,
                'last_version': content_info.version,
                'last_min_engine_version': content_info.min_engine_version,
                'last_run_timestamp': str(Path().cwd().stat().st_mtime)  # Simple timestamp
            })
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_defaults, f, indent=4, ensure_ascii=False)
            
            self.log(f"Saved user defaults to {self.settings_file}")
            
        except Exception as e:
            self.log(f"Error saving user defaults: {e}", "WARNING")
    
    def get_default_value(self, key: str, fallback: Any = None) -> Any:
        """Get a default value from user settings or system settings."""
        return self.user_defaults.get(key, self.settings.get(key, fallback))
    
    def save_asset_info(self, assets: List[AssetInfo]) -> None:
        """Save asset information to data folder."""
        try:
            # Ensure data directory exists
            self.data_dir.mkdir(exist_ok=True)
            
            # Convert assets to serializable format
            asset_data = []
            for asset in assets:
                asset_data.append({
                    'asset_type': asset.asset_type,
                    'file_path': str(asset.file_path) if asset.file_path else '',
                    'required': asset.required,
                    'validated': asset.validated
                })
            
            # Save asset info
            asset_file = self.data_dir / 'asset_info.json'
            with open(asset_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'assets': asset_data,
                    'last_updated': str(Path().cwd().stat().st_mtime)
                }, f, indent=4, ensure_ascii=False)
            
            self.log(f"Saved asset information to {asset_file}")
            
        except Exception as e:
            self.log(f"Error saving asset info: {e}", "WARNING")
    
    def load_asset_info(self) -> List[AssetInfo]:
        """Load asset information from data folder."""
        try:
            asset_file = self.data_dir / 'asset_info.json'
            if asset_file.exists():
                with open(asset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                assets = []
                for asset_data in data.get('assets', []):
                    assets.append(AssetInfo(
                        asset_type=asset_data['asset_type'],
                        file_path=asset_data['file_path'],
                        required=asset_data['required'],
                        validated=asset_data['validated']
                    ))
                
                self.log(f"Loaded asset information from {asset_file}")
                return assets
            else:
                self.log("No saved asset information found")
                return []
                
        except Exception as e:
            self.log(f"Error loading asset info: {e}", "WARNING")
            return []
    
    def get_user_input(self, prompt: str, input_type: str = "input", choices: List[str] = None, default: Any = None) -> Any:
        """Get user input with validation."""
        while True:
            try:
                if input_type == "input":
                    value = input(f"{prompt}: ").strip()
                    if not value and default is not None:
                        return default
                    if not value:
                        print("This field is required. Please enter a value.")
                        continue
                    return value
                    
                elif input_type == "choice":
                    if not choices:
                        raise ValueError("Choices must be provided for choice input type")
                    
                    print(f"\n{prompt}")
                    for i, choice in enumerate(choices, 1):
                        print(f"  {i}. {choice}")
                    
                    while True:
                        try:
                            selection = int(input("Enter your choice (number): ")) - 1
                            if 0 <= selection < len(choices):
                                return choices[selection]
                            else:
                                print(f"Please enter a number between 1 and {len(choices)}")
                        except ValueError:
                            print("Please enter a valid number")
                            
                elif input_type == "confirm":
                    response = input(f"{prompt} (y/n): ").strip().lower()
                    if response in ['y', 'yes']:
                        return True
                    elif response in ['n', 'no']:
                        return False
                    else:
                        print("Please enter 'y' for yes or 'n' for no")
                        
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    def get_content_info(self) -> ContentInfo:
        """Gather content information from user."""
        self.log("=== Content Information ===")
        
        # Load user defaults first
        self.load_user_defaults()
        
        # Get content name
        default_name = self.get_default_value('last_content_name')
        name = self.get_user_input("Enter content name", default=default_name)
        
        # Get description
        default_description = self.get_default_value('last_description')
        description = self.get_user_input("Enter content description", default=default_description)
        
        # Get author
        default_author = self.get_default_value('last_author')
        author = self.get_user_input("Enter author name", default=default_author)
        
        # Get content type
        content_types = [ct.value for ct in ContentType]
        default_content_type = self.get_default_value('last_content_type', self.settings.get('default_content_type', 'addon'))
        content_type_str = self.get_user_input(
            "Select content type",
            "choice",
            content_types,
            default_content_type
        )
        content_type = ContentType(content_type_str)
        
        # Get acronym (for folder naming)
        default_acronym = self.get_default_value('last_acronym')
        if not default_acronym:
            default_acronym = name[:self.settings.get('folder_name_limit', 10)].replace(' ', '_').upper()
        
        acronym = self.get_user_input(
            f"Enter acronym for folder naming (max {self.settings.get('folder_name_limit', 10)} chars)",
            default=default_acronym
        )
        
        # Validate acronym length
        if len(acronym) > self.settings.get('folder_name_limit', 10):
            acronym = acronym[:self.settings.get('folder_name_limit', 10)]
            self.log(f"Acronym truncated to: {acronym}", "WARNING")
        
        # Get version
        default_version = self.get_default_value('last_version', "1.0.0")
        version = self.get_user_input("Enter version", default=default_version)
        
        # Get minimum engine version
        default_min_engine = self.get_default_value('last_min_engine_version', "1.20.0")
        min_engine_version = self.get_user_input("Enter minimum engine version", default=default_min_engine)
        
        return ContentInfo(
            name=name,
            description=description,
            author=author,
            content_type=content_type,
            acronym=acronym,
            version=version,
            min_engine_version=min_engine_version
        )
    
    def validate_assets(self) -> List[AssetInfo]:
        """Validate required assets for the content type."""
        self.log("=== Asset Validation ===")
        
        # Try to load previously saved assets first
        saved_assets = self.load_asset_info()
        
        required_assets = self.settings.get('required_assets', {}).get(
            self.content_info.content_type.value, []
        )
        
        assets = []
        for asset_type in required_assets:
            self.log(f"Looking for {asset_type}...")
            
            # Check if we have a saved asset for this type
            saved_asset = next((a for a in saved_assets if a.asset_type == asset_type), None)
            
            if saved_asset and saved_asset.validated and Path(saved_asset.file_path).exists():
                # Use saved asset if it still exists
                assets.append(saved_asset)
                self.log(f"✓ Using saved {asset_type}: {saved_asset.file_path}")
            else:
                # Try to find the asset file in data folder first
                asset_path = self.find_asset_in_data_folder(asset_type)
                
                if not asset_path:
                    # If not found in data folder, search in current directory
                    asset_path = self.find_asset_file(asset_type)
                
                if asset_path:
                    # Copy to data folder for future use
                    self.copy_asset_to_data_folder(asset_type, asset_path)
                    
                    assets.append(AssetInfo(
                        asset_type=asset_type,
                        file_path=str(asset_path),
                        required=True,
                        validated=True
                    ))
                    self.log(f"✓ Found {asset_type}: {asset_path}")
                else:
                    # Prompt user with file picker for missing assets
                    self.log(f"⚠ Missing {asset_type} - please select file", "WARNING")
                    asset_path = self.prompt_for_asset(asset_type)
                    
                    if asset_path:
                        # Copy asset to data folder
                        self.copy_asset_to_data_folder(asset_type, asset_path)
                        
                        assets.append(AssetInfo(
                            asset_type=asset_type,
                            file_path=str(asset_path),
                            required=True,
                            validated=True
                        ))
                        self.log(f"✓ Selected {asset_type}: {asset_path}")
                    else:
                        assets.append(AssetInfo(
                            asset_type=asset_type,
                            file_path="",
                            required=True,
                            validated=False
                        ))
                        self.log(f"✗ Missing required asset: {asset_type}", "WARNING")
        
        return assets
    
    def find_asset_in_data_folder(self, asset_type: str) -> Optional[Path]:
        """Find asset in the data folder."""
        # Look for assets in the data folder
        asset_files = list(self.assets_dir.glob(f"*{asset_type}*"))
        if asset_files:
            return asset_files[0]
        return None
    
    def copy_asset_to_data_folder(self, asset_type: str, source_path: Path) -> None:
        """Copy asset to data folder for future use."""
        try:
            # Create a descriptive filename
            extension = source_path.suffix
            filename = f"{asset_type}_{self.content_info.acronym}{extension}"
            dest_path = self.assets_dir / filename
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.log(f"Copied {asset_type} to data folder: {dest_path}")
        except Exception as e:
            self.log(f"Error copying {asset_type} to data folder: {e}", "WARNING")
    
    def prompt_for_asset(self, asset_type: str) -> Optional[Path]:
        """Prompt user to select an asset file using file picker."""
        # Define file types based on asset type
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]
        
        title = f"Select {asset_type.replace('_', ' ').title()}"
        
        asset_path = self.show_file_picker(title, file_types)
        
        if asset_path and asset_path.exists():
            return asset_path
        return None
    
    def find_asset_file(self, asset_type: str) -> Optional[Path]:
        """Find asset file based on type and naming conventions."""
        # Define search patterns for different asset types
        search_patterns = {
            'partner_art': ['*PartnerArt*', '*partner*', '*logo*'],
            'key_art': ['*KeyArt*', '*key*', '*thumbnail*'],
            'high_res_key_art': ['*MarketingKeyArt*', '*marketing*key*'],
            'screenshots': ['*screenshot*', '*screenshot_*'],
            'high_res_screenshots': ['*MarketingScreenshot*', '*marketing*screenshot*'],
            'panorama': ['*panorama*', '*pan*'],
            'pack_icon': ['*packicon*', '*pack_icon*', '*icon*']
        }
        
        patterns = search_patterns.get(asset_type, [f"*{asset_type}*"])
        
        # Search in current directory and common asset directories
        search_dirs = [Path('.'), Path('./assets'), Path('./marketing'), Path('./store')]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in patterns:
                    for file_path in search_dir.glob(pattern):
                        if file_path.is_file():
                            return file_path
        
        return None
    
    def create_folder_structure(self) -> Path:
        """Create the proper folder structure for the content type."""
        self.log("=== Creating Folder Structure ===")
        
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create content-specific structure
        content_dir = self.output_dir / "Content"
        content_dir.mkdir(exist_ok=True)
        
        if self.content_info.content_type == ContentType.MASHUP:
            # Mash-up structure (world + resource pack + skin pack)
            world_template_dir = content_dir / "world_template"
            world_template_dir.mkdir(exist_ok=True)
            
            # Behavior pack
            bp_dir = world_template_dir / "behavior_packs" / f"BP_{self.content_info.acronym}"
            bp_dir.mkdir(parents=True, exist_ok=True)
            
            # Resource pack
            rp_dir = world_template_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
            
            # World template files
            texts_dir = world_template_dir / "texts"
            texts_dir.mkdir(exist_ok=True)
            
            db_dir = world_template_dir / "db"
            db_dir.mkdir(exist_ok=True)
            
            # Also create standalone resource pack
            standalone_rp_dir = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            standalone_rp_dir.mkdir(parents=True, exist_ok=True)
            
            # Skin pack
            skin_pack_dir = content_dir / "skin_pack"
            skin_pack_dir.mkdir(exist_ok=True)
            
        elif self.content_info.content_type == ContentType.SKIN_PACK:
            # Skin pack structure
            skin_pack_dir = content_dir / "skin_pack"
            skin_pack_dir.mkdir(exist_ok=True)
            
        elif self.content_info.content_type == ContentType.TEXTURE_PACK:
            # Texture pack structure (resource pack in content/)
            rp_dir = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
            
        elif self.content_info.content_type == ContentType.TEXTURE_PACK_SKIN_PACK:
            # Texture pack + skin pack structure (resource pack in content/)
            rp_dir = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
            
            skin_pack_dir = content_dir / "skin_pack"
            skin_pack_dir.mkdir(exist_ok=True)
            
        elif self.content_info.content_type == ContentType.WORLD:
            # World structure (no standalone resource pack)
            world_template_dir = content_dir / "world_template"
            world_template_dir.mkdir(exist_ok=True)
            
            # Both behavior and resource packs
            bp_dir = world_template_dir / "behavior_packs" / f"BP_{self.content_info.acronym}"
            bp_dir.mkdir(parents=True, exist_ok=True)
            
            rp_dir = world_template_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
            
            # World template files
            texts_dir = world_template_dir / "texts"
            texts_dir.mkdir(exist_ok=True)
            
            db_dir = world_template_dir / "db"
            db_dir.mkdir(exist_ok=True)
            
        elif self.content_info.content_type == ContentType.WORLD_SKIN_PACK:
            # World + skin pack structure (no standalone resource pack)
            world_template_dir = content_dir / "world_template"
            world_template_dir.mkdir(exist_ok=True)
            
            # Both behavior and resource packs
            bp_dir = world_template_dir / "behavior_packs" / f"BP_{self.content_info.acronym}"
            bp_dir.mkdir(parents=True, exist_ok=True)
            
            rp_dir = world_template_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
            
            # World template files
            texts_dir = world_template_dir / "texts"
            texts_dir.mkdir(exist_ok=True)
            
            db_dir = world_template_dir / "db"
            db_dir.mkdir(exist_ok=True)
            
            # Skin pack
            skin_pack_dir = content_dir / "skin_pack"
            skin_pack_dir.mkdir(exist_ok=True)
            
        elif self.content_info.content_type == ContentType.ADDON:
            # Add-on structure (resource pack + behavior pack in content/, no skin pack)
            # Behavior pack
            bp_dir = content_dir / "behavior_packs" / f"BP_{self.content_info.acronym}"
            bp_dir.mkdir(parents=True, exist_ok=True)
            
            # Resource pack
            rp_dir = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            rp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create asset directories
        if self.settings.get('include_store_assets', True):
            store_art_dir = self.output_dir / "Store Art"
            store_art_dir.mkdir(exist_ok=True)
            
        if self.settings.get('include_marketing_assets', True):
            marketing_art_dir = self.output_dir / "Marketing Art"
            marketing_art_dir.mkdir(exist_ok=True)
        
        self.log(f"Created folder structure in: {self.output_dir}")
        return content_dir
    
    def generate_manifest(self, content_dir: Path) -> None:
        """Generate manifest files for the content."""
        self.log("=== Generating Manifests ===")
        
        # Generate UUIDs
        header_uuid = str(uuid.uuid4())
        module_uuid = str(uuid.uuid4())
        
        # Parse version
        version_parts = self.content_info.version.split('.')
        version_array = [int(part) for part in version_parts]
        
        # Parse min engine version
        min_engine_parts = self.content_info.min_engine_version.split('.')
        min_engine_array = [int(part) for part in min_engine_parts]
        
        # Create manifest template
        manifest_template = {
            "format_version": 2,
            "header": {
                "name": "pack.name",
                "description": "pack.description",
                "version": version_array,
                "uuid": header_uuid,
                "min_engine_version": min_engine_array
            },
            "modules": [
                {
                    "type": "resources" if self.content_info.content_type == ContentType.RESOURCE_PACK else "data",
                    "uuid": module_uuid,
                    "version": version_array
                }
            ]
        }
        
        # Write manifest files based on pack type
        if self.content_info.content_type in [ContentType.MASHUP, ContentType.TEXTURE_PACK, ContentType.TEXTURE_PACK_SKIN_PACK, ContentType.ADDON]:
            # Create resource pack manifest (all types have resource packs in content/)
            rp_manifest_path = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}" / "manifest.json"
            rp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(rp_manifest_path, 'w') as f:
                json.dump(manifest_template, f, indent=4)
            self.log(f"Created resource pack manifest: {rp_manifest_path}")
        
        if self.content_info.content_type in [ContentType.MASHUP, ContentType.WORLD, ContentType.WORLD_SKIN_PACK, ContentType.ADDON]:
            # Create behavior pack manifest
            if self.content_info.content_type == ContentType.ADDON:
                # Add-on has behavior packs in content/
                bp_manifest_path = content_dir / "behavior_packs" / f"BP_{self.content_info.acronym}" / "manifest.json"
            else:
                # World-based types have behavior packs in world_template/
                bp_manifest_path = content_dir / "world_template" / "behavior_packs" / f"BP_{self.content_info.acronym}" / "manifest.json"
            bp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(bp_manifest_path, 'w') as f:
                json.dump(manifest_template, f, indent=4)
            self.log(f"Created behavior pack manifest: {bp_manifest_path}")
        
        if self.content_info.content_type in [ContentType.SKIN_PACK, ContentType.TEXTURE_PACK_SKIN_PACK, ContentType.WORLD_SKIN_PACK, ContentType.MASHUP]:
            # Create skin pack manifest (using format_version 1 as per official docs)
            skin_manifest_template = {
                "header": {
                    "name": "pack.name",
                    "version": version_array,
                    "uuid": header_uuid
                },
                "modules": [
                    {
                        "version": version_array,
                        "type": "skin_pack",
                        "uuid": module_uuid
                    }
                ],
                "format_version": 1
            }
            skin_manifest_path = content_dir / "skin_pack" / "manifest.json"
            skin_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(skin_manifest_path, 'w') as f:
                json.dump(skin_manifest_template, f, indent=4)
            self.log(f"Created skin pack manifest: {skin_manifest_path}")
            
            # Create skins.json file
            self.create_skins_json(content_dir)
        
        # Create world template manifest for world-based content types
        if self.content_info.content_type in [ContentType.WORLD, ContentType.WORLD_SKIN_PACK, ContentType.MASHUP]:
            world_manifest_template = {
                "header": {
                    "name": "pack.name",
                    "description": "pack.description",
                    "version": version_array,
                    "uuid": header_uuid
                },
                "modules": [
                    {
                        "version": version_array,
                        "type": "world_template",
                        "uuid": module_uuid
                    }
                ],
                "format_version": 2
            }
            world_manifest_path = content_dir / "world_template" / "manifest.json"
            world_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(world_manifest_path, 'w') as f:
                json.dump(world_manifest_template, f, indent=4)
            self.log(f"Created world template manifest: {world_manifest_path}")
            
            # Create world template database folder and files
            self.create_world_template_files(content_dir)
    
    def create_skins_json(self, content_dir: Path) -> None:
        """Create skins.json file for skin packs following official specifications."""
        self.log("=== Creating skins.json ===")
        
        # Generate a serialize_name based on content name (alphanumeric + underscores only)
        serialize_name = ''.join(c for c in self.content_info.name if c.isalnum() or c == ' ').replace(' ', '')
        if not serialize_name:
            serialize_name = "SkinPack"
        
        # Get skin information from user
        skins = self.get_skin_information(serialize_name)
        
        # Create skins.json template following official schema
        skins_json = {
            "serialize_name": serialize_name,
            "localization_name": serialize_name,
            "skins": skins
        }
        
        # Save skins.json
        skin_pack_dir = content_dir / "skin_pack"
        skins_json_path = skin_pack_dir / "skins.json"
        with open(skins_json_path, 'w', encoding='utf-8') as f:
            json.dump(skins_json, f, indent=2, ensure_ascii=False)
        
        self.log(f"Created skins.json: {skins_json_path}")
        self.log("Note: You'll need to add actual skin texture PNG files to the skin_pack folder")
        self.log("Note: Ensure texture files match the geometry type (Steve vs Alex model)")
    
    def get_skin_information(self, serialize_name: str) -> List[Dict[str, str]]:
        """Get skin information from user input."""
        self.log("=== Skin Information ===")
        
        # Check if we have saved skin information
        saved_skins = self.user_defaults.get('skin_names', [])
        
        if saved_skins and not self.settings.get('auto_mode', False):
            print(f"\nFound {len(saved_skins)} previously saved skins:")
            for i, skin in enumerate(saved_skins, 1):
                print(f"  {i}. {skin['name']} ({skin['geometry']}) - {skin['type']}")
            
            use_saved = input("\nUse saved skin names? (Y/n): ").strip().lower()
            if use_saved in ['', 'y', 'yes']:
                return self.convert_saved_skins_to_json(saved_skins, serialize_name)
        
        # Get number of skins
        while True:
            try:
                num_skins = input(f"\nHow many skins do you want to include? (default: 5): ").strip()
                if not num_skins:
                    num_skins = 5
                else:
                    num_skins = int(num_skins)
                
                if num_skins < 1:
                    print("Please enter at least 1 skin.")
                    continue
                elif num_skins > 20:
                    print("Please enter 20 or fewer skins.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        skins = []
        skin_names = []
        
        for i in range(num_skins):
            print(f"\n--- Skin {i + 1} ---")
            
            # Get skin name
            while True:
                skin_name = input(f"Skin {i + 1} name: ").strip()
                if not skin_name:
                    print("Skin name cannot be empty.")
                    continue
                if skin_name in skin_names:
                    print("Skin name already used. Please choose a different name.")
                    continue
                break
            
            skin_names.append(skin_name)
            
            # Get geometry type
            print("Geometry types:")
            print("  1. Steve model (geometry.humanoid.custom)")
            print("  2. Alex model (geometry.humanoid.customSlim)")
            
            while True:
                geometry_choice = input("Choose geometry (1-2, default: 1): ").strip()
                if not geometry_choice:
                    geometry_choice = "1"
                
                if geometry_choice == "1":
                    geometry = "geometry.humanoid.custom"
                    break
                elif geometry_choice == "2":
                    geometry = "geometry.humanoid.customSlim"
                    break
                else:
                    print("Please enter 1 or 2.")
            
            # Get skin type (free/paid)
            while True:
                skin_type = input("Skin type (free/paid, default: free): ").strip().lower()
                if not skin_type:
                    skin_type = "free"
                
                if skin_type in ['free', 'paid']:
                    break
                else:
                    print("Please enter 'free' or 'paid'.")
            
            # Create skin entry
            skin_entry = {
                "localization_name": skin_name,
                "geometry": geometry,
                "texture": f"{skin_name.lower().replace(' ', '_')}.png",
                "type": skin_type
            }
            
            skins.append(skin_entry)
        
        # Save skin information for future use
        skin_data = []
        for skin in skins:
            skin_data.append({
                "name": skin["localization_name"],
                "geometry": skin["geometry"],
                "type": skin["type"]
            })
        
        self.user_defaults['skin_names'] = skin_data
        self.save_user_defaults()
        
        return skins
    
    def convert_saved_skins_to_json(self, saved_skins: List[Dict[str, str]], serialize_name: str) -> List[Dict[str, str]]:
        """Convert saved skin data to JSON format."""
        skins = []
        for skin in saved_skins:
            skin_entry = {
                "localization_name": skin["name"],
                "geometry": skin["geometry"],
                "texture": f"{skin['name'].lower().replace(' ', '_')}.png",
                "type": skin["type"]
            }
            skins.append(skin_entry)
        return skins
    
    def create_world_template_files(self, content_dir: Path) -> None:
        """Create world template database and configuration files."""
        self.log("=== Creating World Template Files ===")
        
        world_template_dir = content_dir / "world_template"
        
        # Create db folder (database files)
        db_dir = world_template_dir / "db"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder database files
        # Note: These are typically binary files created by Minecraft
        # We'll create placeholder text files for the template structure
        placeholder_files = [
            "CURRENT",
            "MANIFEST-000001",
            "000001.ldb",
            "000001.log"
        ]
        
        for filename in placeholder_files:
            placeholder_path = db_dir / filename
            with open(placeholder_path, 'w') as f:
                if filename.endswith('.ldb') or filename.endswith('.log'):
                    f.write("# Binary database file - replace with actual Minecraft database files")
                else:
                    f.write("# Placeholder file - replace with actual Minecraft world files")
        
        # Create world configuration files
        world_files = {
            "level.dat": "# Binary world data file - replace with actual level.dat from exported world",
            "level.dat_old": "# Backup world data file - replace with actual level.dat_old from exported world", 
            "levelname.txt": self.content_info.name,
            "world_icon.jpeg": "# World icon image - replace with actual 800x450 JPEG file"
        }
        
        for filename, content in world_files.items():
            file_path = world_template_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Create world pack configuration files (if add-ons are included)
        if self.content_info.content_type in [ContentType.MASHUP, ContentType.ADDON]:
            # Create world behavior pack configuration
            world_bp_config = {
                "": [
                    {
                        "pack_id": f"BP_{self.content_info.acronym}",
                        "version": [1, 0, 0]
                    }
                ]
            }
            world_bp_path = world_template_dir / "world_behavior_packs.json"
            with open(world_bp_path, 'w') as f:
                json.dump(world_bp_config, f, indent=4)
            
            # Create world resource pack configuration
            world_rp_config = {
                "": [
                    {
                        "pack_id": f"RP_{self.content_info.acronym}",
                        "version": [1, 0, 0]
                    }
                ]
            }
            world_rp_path = world_template_dir / "world_resource_packs.json"
            with open(world_rp_path, 'w') as f:
                json.dump(world_rp_config, f, indent=4)
            
            # Create pack history files
            pack_history = {
                "": []
            }
            with open(world_template_dir / "world_behavior_pack_history.json", 'w') as f:
                json.dump(pack_history, f, indent=4)
            with open(world_template_dir / "world_resource_pack_history.json", 'w') as f:
                json.dump(pack_history, f, indent=4)
        
        self.log(f"Created world template files in: {world_template_dir}")
        self.log("Note: Replace placeholder files with actual Minecraft world files from an exported world")
    
    def create_language_files(self, content_dir: Path) -> None:
        """Create required language files."""
        self.log("=== Creating Language Files ===")
        
        # Create en_US.lang content
        lang_content = f"""pack.name={self.content_info.name}
pack.description={self.content_info.description}
"""
        
        # Create languages.json
        languages_content = json.dumps(["en_US"], indent=4)
        
        # Determine where to place language files based on content type
        if self.content_info.content_type == ContentType.SKIN_PACK:
            # Skin pack only - create proper skin pack language files
            texts_dir = content_dir / "skin_pack" / "texts"
            texts_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate skin pack specific language content following official format
            serialize_name = ''.join(c for c in self.content_info.name if c.isalnum() or c == ' ').replace(' ', '')
            if not serialize_name:
                serialize_name = "SkinPack"
            
            # Generate skin pack specific language content using saved skin names
            skin_lang_content = f"""skinpack.{serialize_name}={self.content_info.name}
skinpack.{serialize_name}.by={self.content_info.author}
"""
            
            # Add skin names from saved data
            saved_skins = self.user_defaults.get('skin_names', [])
            for skin in saved_skins:
                skin_lang_content += f"skin.{serialize_name}.{skin['name']}={skin['name']}\n"
            
            with open(texts_dir / "en_US.lang", 'w', encoding='utf-8') as f:
                f.write(skin_lang_content)
            with open(texts_dir / "languages.json", 'w', encoding='utf-8') as f:
                f.write(languages_content)
            self.log(f"Created skin pack language files in: {texts_dir}")
        elif self.content_info.content_type in [ContentType.WORLD, ContentType.WORLD_SKIN_PACK]:
            # World template only - create world template language files
            texts_dir = content_dir / "world_template" / "texts"
            texts_dir.mkdir(parents=True, exist_ok=True)
            
            with open(texts_dir / "en_US.lang", 'w', encoding='utf-8') as f:
                f.write(lang_content)
            with open(texts_dir / "languages.json", 'w', encoding='utf-8') as f:
                f.write(languages_content)
            self.log(f"Created world template language files in: {texts_dir}")
        else:
            # For other content types, create in appropriate locations
            if self.content_info.content_type in [ContentType.MASHUP, ContentType.TEXTURE_PACK, ContentType.TEXTURE_PACK_SKIN_PACK, ContentType.ADDON]:
                # Create resource pack language files (all types have resource packs in content/)
                rp_texts_dir = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}" / "texts"
                rp_texts_dir.mkdir(parents=True, exist_ok=True)
                
                with open(rp_texts_dir / "en_US.lang", 'w', encoding='utf-8') as f:
                    f.write(lang_content)
                with open(rp_texts_dir / "languages.json", 'w', encoding='utf-8') as f:
                    f.write(languages_content)
                self.log(f"Created language files in: {rp_texts_dir}")
            
            if self.content_info.content_type in [ContentType.MASHUP, ContentType.WORLD, ContentType.WORLD_SKIN_PACK, ContentType.ADDON]:
                # Create behavior pack language files
                if self.content_info.content_type == ContentType.ADDON:
                    # Add-on has behavior packs in content/
                    bp_texts_dir = content_dir / "behavior_packs" / f"BP_{self.content_info.acronym}" / "texts"
                else:
                    # World-based types have behavior packs in world_template/
                    bp_texts_dir = content_dir / "world_template" / "behavior_packs" / f"BP_{self.content_info.acronym}" / "texts"
                bp_texts_dir.mkdir(parents=True, exist_ok=True)
                
                with open(bp_texts_dir / "en_US.lang", 'w', encoding='utf-8') as f:
                    f.write(lang_content)
                with open(bp_texts_dir / "languages.json", 'w', encoding='utf-8') as f:
                    f.write(languages_content)
                self.log(f"Created language files in: {bp_texts_dir}")
            
            if self.content_info.content_type in [ContentType.TEXTURE_PACK_SKIN_PACK, ContentType.WORLD_SKIN_PACK, ContentType.MASHUP]:
                # Create skin pack language files
                skin_texts_dir = content_dir / "skin_pack" / "texts"
                skin_texts_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate skin pack specific language content following official format
                serialize_name = ''.join(c for c in self.content_info.name if c.isalnum() or c == ' ').replace(' ', '')
                if not serialize_name:
                    serialize_name = "SkinPack"
                
                # Generate skin pack specific language content using saved skin names
                skin_lang_content = f"""skinpack.{serialize_name}={self.content_info.name}
skinpack.{serialize_name}.by={self.content_info.author}
"""
                
                # Add skin names from saved data
                saved_skins = self.user_defaults.get('skin_names', [])
                for skin in saved_skins:
                    skin_lang_content += f"skin.{serialize_name}.{skin['name']}={skin['name']}\n"
                
                with open(skin_texts_dir / "en_US.lang", 'w', encoding='utf-8') as f:
                    f.write(skin_lang_content)
                with open(skin_texts_dir / "languages.json", 'w', encoding='utf-8') as f:
                    f.write(languages_content)
                self.log(f"Created skin pack language files in: {skin_texts_dir}")
    
    def copy_assets(self, content_dir: Path) -> None:
        """Copy and organize assets according to marketplace requirements."""
        self.log("=== Copying Assets ===")
        
        # Copy existing add-on content if this is an add-on type
        if self.content_info.content_type == ContentType.ADDON:
            self.copy_existing_addon_content(content_dir)
        
        # Copy store assets
        if self.settings.get('include_store_assets', True):
            store_art_dir = self.output_dir / "Store Art"
            for asset in self.assets:
                if asset.validated and asset.file_path:
                    # Determine naming convention based on asset type
                    new_name = self.get_asset_filename(asset.asset_type, "store")
                    if new_name:
                        dest_path = store_art_dir / new_name
                        shutil.copy2(asset.file_path, dest_path)
                        self.log(f"Copied {asset.asset_type} to: {dest_path}")
        
        # Copy marketing assets
        if self.settings.get('include_marketing_assets', True):
            marketing_art_dir = self.output_dir / "Marketing Art"
            for asset in self.assets:
                if asset.validated and asset.file_path:
                    # Determine naming convention based on asset type
                    new_name = self.get_asset_filename(asset.asset_type, "marketing")
                    if new_name:
                        dest_path = marketing_art_dir / new_name
                        shutil.copy2(asset.file_path, dest_path)
                        self.log(f"Copied {asset.asset_type} to: {dest_path}")
    
    def copy_existing_addon_content(self, content_dir: Path) -> None:
        """Copy existing add-on content from BP/ and RP/ folders using Regolith standard paths."""
        self.log("=== Copying Existing Add-on Content ===")
        
        # Get pack paths using the same logic as content validator
        pack_paths = self._get_pack_paths()
        
        # Copy behavior pack if found
        if 'BP' in pack_paths:
            bp_source = Path(pack_paths['BP'])
            bp_dest = content_dir / "behavior_packs" / f"BP_{self.content_info.acronym}"
            self.log(f"Found existing behavior pack: {bp_source}")
            self.log(f"Copying to: {bp_dest}")
            self.copy_directory_contents(bp_source, bp_dest)
        else:
            self.log("No existing behavior pack found", "WARNING")
        
        # Copy resource pack if found
        if 'RP' in pack_paths:
            rp_source = Path(pack_paths['RP'])
            rp_dest = content_dir / "resource_packs" / f"RP_{self.content_info.acronym}"
            self.log(f"Found existing resource pack: {rp_source}")
            self.log(f"Copying to: {rp_dest}")
            self.copy_directory_contents(rp_source, rp_dest)
        else:
            self.log("No existing resource pack found", "WARNING")
    
    def _get_pack_paths(self) -> Dict[str, str]:
        """Get pack paths for add-on content, following Regolith standard paths."""
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
    
    def copy_directory_contents(self, source: Path, dest: Path) -> None:
        """Copy all contents from source directory to destination."""
        try:
            dest.mkdir(parents=True, exist_ok=True)
            
            for item in source.iterdir():
                if item.is_file():
                    shutil.copy2(item, dest / item.name)
                    self.log(f"  Copied file: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
                    self.log(f"  Copied directory: {item.name}")
            
            self.log(f"✓ Successfully copied content from {source} to {dest}")
        except Exception as e:
            self.log(f"Error copying {source} to {dest}: {e}", "ERROR")
    
    def get_asset_filename(self, asset_type: str, category: str) -> Optional[str]:
        """Get the proper filename for an asset based on marketplace conventions."""
        content_name = self.content_info.name.replace(' ', '').lower()
        
        if category == "store":
            if asset_type == "key_art":
                return f"{content_name}_Thumbnail_0.jpg"
            elif asset_type == "screenshots":
                return f"{content_name}_screenshot_0.jpg"  # This would need to be handled for multiple screenshots
            elif asset_type == "panorama":
                return f"{content_name}_panorama_0.jpg"
            elif asset_type == "pack_icon":
                return f"{content_name}_packicon_0.jpg"
        elif category == "marketing":
            content_name_cap = self.content_info.name.replace(' ', '')
            if asset_type == "key_art":
                return f"{content_name_cap}_MarketingKeyArt.jpg"
            elif asset_type == "screenshots":
                return f"{content_name_cap}_MarketingScreenshot_0.jpg"  # This would need to be handled for multiple screenshots
            elif asset_type == "partner_art":
                return f"{content_name_cap}_PartnerArt.jpg"
        
        return None
    
    def copy_assets_to_data_folder(self, assets: List[AssetInfo]) -> None:
        """Copy validated assets to data folder for future reference."""
        try:
            # Create assets directory in data folder
            assets_dir = self.data_dir / 'assets'
            assets_dir.mkdir(exist_ok=True)
            
            for asset in assets:
                if asset.validated and asset.file_path and Path(asset.file_path).exists():
                    # Create subdirectory for asset type
                    asset_type_dir = assets_dir / asset.asset_type
                    asset_type_dir.mkdir(exist_ok=True)
                    
                    # Copy asset file
                    source_path = Path(asset.file_path)
                    dest_path = asset_type_dir / source_path.name
                    shutil.copy2(source_path, dest_path)
                    
                    # Update asset path to point to data folder copy
                    asset.file_path = str(dest_path)
                    
                    self.log(f"Copied {asset.asset_type} to data folder: {dest_path}")
                    
        except Exception as e:
            self.log(f"Error copying assets to data folder: {e}", "WARNING")
    
    def package_content(self) -> bool:
        """Main method to package the content."""
        try:
            # Get content information
            self.content_info = self.get_content_info()
            
            # Validate assets
            self.assets = self.validate_assets()
            
            # Check if we have all required assets
            missing_assets = [asset for asset in self.assets if asset.required and not asset.validated]
            if missing_assets:
                self.log("Missing required assets:", "WARNING")
                for asset in missing_assets:
                    self.log(f"  - {asset.asset_type}", "WARNING")
                
                continue_without_assets = self.get_user_input(
                    "Continue without missing assets?",
                    "confirm",
                    default=False
                )
                if not continue_without_assets:
                    self.log("Packaging cancelled due to missing assets.")
                    return False
            
            # Create folder structure
            content_dir = self.create_folder_structure()
            
            # Generate manifests
            self.generate_manifest(content_dir)
            
            # Create language files
            self.create_language_files(content_dir)
            
            # Copy assets to data folder for future reference
            self.copy_assets_to_data_folder(self.assets)
            
            # Copy assets to output directory
            self.copy_assets(content_dir)
            
            # Save asset information
            self.save_asset_info(self.assets)
            
            # Save user defaults for next run
            self.save_user_defaults(self.content_info)
            
            self.log("=== Packaging Complete ===")
            self.log(f"Content packaged successfully in: {self.output_dir}")
            self.log(f"Content type: {self.content_info.content_type.value}")
            self.log(f"Content name: {self.content_info.name}")
            self.log("Settings saved for next run")
            
            return True
            
        except Exception as e:
            self.log(f"Error during packaging: {e}", "ERROR")
            return False

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
            filter_json_path = os.path.join(os.path.dirname(__file__), 'filter.json')
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
            "log_level": "INFO",
            "auto_mode": False,
            "interactive_mode": True,
            "output_directory": "./packaged_content"
        }


def get_regolith_environment() -> Dict[str, str]:
    """Get Regolith environment variables for external file access if needed."""
    return {
        'ROOT_DIR': os.environ.get('ROOT_DIR', ''),
        'FILTER_DIR': os.environ.get('FILTER_DIR', ''),
        'WORKING_DIR': os.getcwd()
    }

def main():
    """Main entry point for Regolith filter."""
    parser = argparse.ArgumentParser(description='Content Packager Filter for Regolith')
    parser.add_argument('--auto', '-a', action='store_true', help='Run in automatic mode (no user input)')
    parser.add_argument('--content-type', '-t', help='Content type to package')
    parser.add_argument('--name', '-n', help='Content name')
    parser.add_argument('--description', '-d', help='Content description')
    parser.add_argument('--author', '-au', help='Author name')
    parser.add_argument('--acronym', '-ac', help='Content acronym for folder naming')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--clear-settings', action='store_true', help='Clear saved user settings')
    parser.add_argument('--show-settings', action='store_true', help='Show current saved settings')
    
    args = parser.parse_args()
    
    try:
        logger.info("Content Packager Filter - Starting")
        
        # Parse settings from Regolith
        settings = parse_settings()
        logger.info(f"Loaded settings: {settings}")
        
        # Get Regolith environment info
        env_info = get_regolith_environment()
        logger.info(f"Working directory: {env_info['WORKING_DIR']}")
        
        # Override settings with command line arguments
        if args.auto:
            settings['auto_mode'] = True
        if args.content_type:
            settings['default_content_type'] = args.content_type
        if args.output:
            settings['output_directory'] = args.output
        if args.verbose:
            settings['log_level'] = 'DEBUG'
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Create packager
        packager = ContentPackager(settings)
        
        # Handle special commands
        if args.clear_settings:
            if packager.settings_file.exists():
                packager.settings_file.unlink()
                logger.info("✅ Cleared saved user settings")
            else:
                logger.info("ℹ️  No saved settings to clear")
            sys.exit(0)
        
        if args.show_settings:
            packager.load_user_defaults()
            if packager.user_defaults:
                logger.info("📋 Current saved settings:")
                for key, value in packager.user_defaults.items():
                    logger.info(f"  {key}: {value}")
            else:
                logger.info("ℹ️  No saved settings found")
            sys.exit(0)
        
        # Run packaging
        logger.info("Starting content packaging...")
        success = packager.package_content()
        
        if success:
            logger.info("✅ Content packaging completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Content packaging failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
