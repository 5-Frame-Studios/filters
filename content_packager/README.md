# Content Packager Filter

A Regolith filter for packaging Minecraft Bedrock content for marketplace submission. This filter creates the proper folder structure, generates manifests, and organizes assets according to marketplace guidelines.

## Regolith Integration

- **Temporary Directory**: Works in Regolith's temporary directory structure
- **Settings Persistence**: Saves user inputs and assets to data folder for future runs
- **Non-Destructive**: Creates packaged content without modifying original project files
- **Environment Variables**: Uses Regolith environment variables for proper integration

## Features

- **Interactive CLI Interface**: Prompts for user input when needed, similar to the example you provided
- **Settings Persistence**: Saves user inputs and assets to data folder for future runs
- **Multiple Content Types**: Supports Add-Ons, Resource Packs, Behavior Packs, World Templates, and Skin Packs
- **Automatic Folder Structure**: Creates the correct directory structure based on content type
- **Manifest Generation**: Generates proper manifest.json files with UUIDs
- **Asset Organization**: Copies and renames assets according to marketplace naming conventions
- **Asset Storage**: Stores assets in data folder for future reference
- **Marketplace Compliance**: Ensures content follows all marketplace submission guidelines

## Supported Content Types

### Mash-up
- Complete mash-up structure (world + resource pack + skin pack)
- Includes world_template with behavior and resource packs
- Standalone resource pack for texture sharing
- Skin pack for character customization

### Skin Pack
- Standalone skin pack structure
- Proper manifest.json (format_version 1)
- skins.json with skin definitions
- Character customization assets
- Proper localization for skin names

### Texture Pack
- Standalone resource pack structure
- Proper manifest configuration
- Asset organization for marketplace

### Texture Pack + Skin Pack
- Resource pack for textures
- Skin pack for character customization
- Combined package structure

### World
- Complete world template structure
- Both behavior and resource packs
- World database files

### World + Skin Pack
- World template with behavior and resource packs
- Additional skin pack for character customization
- Complete world experience

### Add-On
- Complete add-on structure (world + resource pack + skin pack)
- Includes world_template with behavior and resource packs
- Standalone resource pack for texture sharing
- Skin pack for character customization

## Usage

### Regolith Integration
This filter is designed to work with Regolith. Add it to your `config.json`:

```json
{
  "regolith": {
    "filterDefinitions": {
      "content-packager": {
        "url": "path/to/content_packager"
      }
    },
    "profiles": {
      "default": {
        "filters": [
          {
            "filter": "content-packager",
            "settings": {
              "output_directory": "./packaged_content",
              "auto_mode": false
            }
          }
        ]
      }
    }
  }
}
```

### Add-on Workflow

For add-ons, the filter expects your project to have existing BP/ and RP/ folders:

1. **Prepare your add-on:**
   ```
   your_project/
   ├── BP/                    # Your behavior pack
   │   ├── manifest.json
   │   ├── scripts/
   │   └── ...
   ├── RP/                    # Your resource pack
   │   ├── manifest.json
   │   ├── textures/
   │   └── ...
   └── packs/
       └── data/
           └── content_packager/
   ```

2. **Run the filter:**
   ```bash
   regolith run content_packager
   ```

3. **Select "Add-on" as content type**

4. **The filter will:**
   - Copy your BP/ folder to `Content/behavior_packs/BP_{acronym}/`
   - Copy your RP/ folder to `Content/resource_packs/RP_{acronym}/`
   - Generate proper manifests for marketplace submission
   - Organize marketing assets

### Interactive Mode (Default)
```bash
regolith run
```

The filter will prompt you for:
- Content name
- Description
- Author
- Content type
- Acronym (for folder naming)
- Version
- Minimum engine version

### Command Line Mode
```bash
python main.py --auto --content-type addon --name "My Add-On" --description "Cool add-on" --author "Developer"
```

### Command Line Options
- `--auto, -a`: Run in automatic mode (no user input)
- `--content-type, -t`: Content type to package
- `--name, -n`: Content name
- `--description, -d`: Content description
- `--author, -au`: Author name
- `--acronym, -ac`: Content acronym for folder naming
- `--output, -o`: Output directory
- `--verbose, -v`: Enable verbose logging
- `--clear-settings`: Clear saved user settings
- `--show-settings`: Show current saved settings

## Asset Requirements

The filter automatically looks for required assets based on content type:

### Required Assets by Content Type

**Mash-up:**
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)
- Panorama

**Skin Pack:**
- Partner Art
- Key Art
- High Resolution Key Art

**Texture Pack:**
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)

**Texture Pack + Skin Pack:**
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)

**World:**
- Pack Icon
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)
- Panorama

**World + Skin Pack:**
- Pack Icon
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)
- Panorama

**Add-On:**
- Partner Art
- Key Art
- High Resolution Key Art
- Screenshots (5)
- High Resolution Screenshots (5)
- Panorama

## Asset Naming Conventions

The filter automatically renames assets according to marketplace requirements:

### Store Art
- Key Art: `contentname_Thumbnail_0.jpg`
- Screenshots: `contentname_screenshot_0.jpg` (and 1-4)
- Panorama: `contentname_panorama_0.jpg`
- Pack Icon: `contentname_packicon_0.jpg`

### Marketing Art
- Key Art: `ContentName_MarketingKeyArt.jpg`
- Screenshots: `ContentName_MarketingScreenshot_0.jpg` (and 1-4)
- Partner Art: `ContentName_PartnerArt.jpg`

## Skin Pack Structure

For skin packs, the filter creates the proper structure according to official Minecraft Bedrock Edition specifications:

```
skin_pack/
├── manifest.json          # Skin pack manifest (format_version 1)
├── skins.json            # Skin definitions and metadata
├── mage_robe.png         # Skin texture files (64x64 recommended)
├── warrior_armor.png
├── archer_outfit.png
├── knight_gear.png
├── rogue_clothing.png
└── texts/
    ├── en_US.lang        # Official localization keys
    └── languages.json    # Supported languages
```

### Skin Pack Files

- **manifest.json**: Uses format_version 1 as required by skin packs
- **skins.json**: Defines skin metadata following official schema with serialize_name and localization_name
- **Skin Textures**: PNG files (64x64 recommended) referenced in skins.json
- **Localization**: Official skinpack.* and skin.* localization key system

### Official Localization Keys

The filter follows the official localization key system:

```
skinpack.{serialize_name}=Skin Pack Display Name
skinpack.{serialize_name}.by=Creator Name
skin.{serialize_name}.{skin_localization_name}=Individual Skin Display Name
```

### Skin Definitions

Each skin includes:
- **localization_name**: Unique identifier for the skin
- **geometry**: `geometry.humanoid.custom` (Steve) or `geometry.humanoid.customSlim` (Alex)
- **texture**: PNG filename in the skin pack root
- **type**: `free` or `paid` for marketplace content

## World Template Structure

For world templates, the filter creates the proper structure according to official Minecraft Bedrock Edition specifications:

```
world_template/
├── manifest.json                    # World template manifest (format_version 2)
├── level.dat                       # Binary world data (replace with actual file)
├── level.dat_old                   # Backup world data (replace with actual file)
├── levelname.txt                   # World name
├── world_icon.jpeg                 # World icon (800x450 JPEG)
├── world_behavior_packs.json       # Behavior pack configuration
├── world_resource_packs.json       # Resource pack configuration
├── world_behavior_pack_history.json # Behavior pack history
├── world_resource_pack_history.json # Resource pack history
├── db/                            # World database files
│   ├── CURRENT                    # Database current pointer
│   ├── MANIFEST-000001           # Database manifest
│   ├── 000001.ldb                # Database files
│   └── 000001.log                # Database log files
├── behavior_packs/                # Behavior packs (≤10 chars)
│   └── BP_{acronym}/
│       └── manifest.json
├── resource_packs/                # Resource packs (≤10 chars)
│   └── RP_{acronym}/
│       └── manifest.json
└── texts/                         # Localization files
    ├── en_US.lang                 # Pack name and description
    └── languages.json             # Supported languages
```

### World Template Files

- **manifest.json**: Uses format_version 2 with world_template type
- **World Data**: level.dat, level.dat_old, levelname.txt, world_icon.jpeg
- **Database**: db/ folder with Minecraft world database files
- **Pack Configuration**: JSON files linking behavior and resource packs
- **Localization**: Standard pack.name and pack.description keys

### World Template Requirements

- **Folder Names**: Behavior and resource pack folders must be ≤10 characters (Xbox compatibility)
- **Database Files**: Replace placeholder files with actual Minecraft world database files
- **World Data**: Replace level.dat and related files with actual exported world files
- **Pack Linking**: Behavior and resource packs are automatically linked to the world template

## Output Structure

The filter creates a properly structured package ready for marketplace submission:

### Content Type Structures

**Mash-up:**
```
packaged_content/
├── Content/
│   ├── world_template/             # World template
│   │   ├── manifest.json
│   │   ├── behavior_packs/
│   │   │   └── BP_{acronym}/
│   │   ├── resource_packs/
│   │   │   └── RP_{acronym}/
│   │   ├── texts/
│   │   └── db/
│   ├── resource_packs/             # Standalone resource pack
│   │   └── RP_{acronym}/
│   └── skin_pack/                  # Skin pack
├── Store Art/
└── Marketing Art/
```

**World:**
```
packaged_content/
├── Content/
│   └── world_template/             # World template only
│       ├── manifest.json
│       ├── behavior_packs/
│       │   └── BP_{acronym}/
│       ├── resource_packs/
│       │   └── RP_{acronym}/
│       ├── texts/
│       └── db/
├── Store Art/
└── Marketing Art/
```

**World + Skin Pack:**
```
packaged_content/
├── Content/
│   ├── world_template/             # World template
│   │   ├── manifest.json
│   │   ├── behavior_packs/
│   │   │   └── BP_{acronym}/
│   │   ├── resource_packs/
│   │   │   └── RP_{acronym}/
│   │   ├── texts/
│   │   └── db/
│   └── skin_pack/                  # Skin pack (NO standalone resource pack)
├── Store Art/
└── Marketing Art/
```

**Add-on:**
```
packaged_content/
├── Content/
│   ├── behavior_packs/             # Behavior packs in content/
│   │   └── BP_{acronym}/           # Copied from existing BP/ folder
│   └── resource_packs/             # Resource packs in content/
│       └── RP_{acronym}/           # Copied from existing RP/ folder
├── Store Art/
└── Marketing Art/
```

### Add-on Content Source

For add-ons, the filter automatically copies existing content from:
- **BP/ folder** → `Content/behavior_packs/BP_{acronym}/`
- **RP/ folder** → `Content/resource_packs/RP_{acronym}/`

**Expected Project Structure:**
```
your_project/
├── BP/                    # Your existing behavior pack
│   ├── manifest.json
│   ├── scripts/
│   └── ...
├── RP/                    # Your existing resource pack
│   ├── manifest.json
│   ├── textures/
│   └── ...
└── packs/
    └── data/
        └── content_packager/
```

**Texture Pack:**
```
packaged_content/
├── Content/
│   └── resource_packs/             # Resource packs in content/
│       └── RP_{acronym}/
├── Store Art/
└── Marketing Art/
```

**Texture Pack + Skin Pack:**
```
packaged_content/
├── Content/
│   ├── resource_packs/             # Resource packs in content/
│   │   └── RP_{acronym}/
│   └── skin_pack/                  # Skin pack
├── Store Art/
└── Marketing Art/
```

**Skin Pack:**
```
packaged_content/
├── Content/
│   └── skin_pack/                  # Skin pack only
├── Store Art/
└── Marketing Art/
```

## Settings Persistence

The filter automatically saves your inputs and assets for future runs:

### Data Folder Structure
```
packs/data/content_packager/
├── user_settings.json      # Saved user inputs (name, author, etc.)
├── asset_info.json         # Asset validation information
└── assets/                 # Copied asset files
    ├── key_art_MAP.jpg
    ├── screenshot_MAP_1.jpg
    ├── partner_art_MAP.jpg
    └── ...
```

### Regolith Data Folder Benefits
- **Standard Location**: Uses `./packs/data/content_packager/` as per Regolith conventions
- **File Picker Integration**: Missing assets prompt with graphical file picker dialog
- **Asset Persistence**: Automatically copies and organizes assets for reuse
- **Cross-Project**: Assets can be shared across different Regolith projects

### Saved Settings
- Content name, description, and author
- Content type and acronym
- Version and engine requirements
- Asset file paths and validation status

### Managing Settings
```bash
# View current saved settings
python main.py --show-settings

# Clear all saved settings
python main.py --clear-settings
```

### Asset Storage
- Validated assets are copied to `data/assets/` folder
- Asset information is saved for future reference
- Previously found assets are reused if they still exist

## Configuration

The filter can be configured through the `filter.json` file:

```json
{
    "settings": {
        "log_level": "INFO",
        "auto_mode": false,
        "interactive_mode": true,
        "content_types": ["addon", "resource_pack", "behavior_pack", "world_template", "skin_pack"],
        "default_content_type": "addon",
        "output_directory": "./packaged_content",
        "include_marketing_assets": true,
        "include_store_assets": true,
        "validate_manifests": true,
        "generate_uuids": true,
        "folder_name_limit": 10
    }
}
```

## Error Handling

The filter includes comprehensive error handling:
- Validates required assets before packaging
- Warns about missing assets but allows continuation
- Provides clear error messages and suggestions
- Handles user cancellation gracefully

## Dependencies

No external dependencies required - uses only Python standard library.

## Examples

### Basic Add-On Packaging
```bash
python main.py
# Follow the interactive prompts
```

### Automated Resource Pack Packaging
```bash
python main.py --auto --content-type resource_pack --name "My Texture Pack" --description "Cool textures" --author "Developer" --acronym "MTP"
```

### Custom Output Directory
```bash
python main.py --output ./my_packaged_content
```

### Settings Management
```bash
# View saved settings
python main.py --show-settings

# Clear saved settings and start fresh
python main.py --clear-settings

# Run with saved defaults (interactive)
python main.py

# Run with saved defaults (automatic)
python main.py --auto
```

## Marketplace Compliance

This filter ensures your content follows all marketplace submission guidelines:
- Proper folder structure
- Correct manifest format
- Required language files
- Asset naming conventions
- File organization standards

## Troubleshooting

### Missing Assets
If required assets are missing, the filter will warn you but allow you to continue. You can add the missing assets later to the appropriate directories.

### Folder Name Length
The filter enforces the 10-character limit for pack folder names (Xbox compatibility). If your acronym is too long, it will be truncated.

### Asset Detection
The filter searches for assets using common naming patterns. If your assets aren't detected, ensure they follow standard naming conventions or place them in the current directory.

### Skin Pack Issues

#### JSON Syntax Errors
- **Problem**: Skin pack fails to load
- **Solution**: Ensure proper JSON formatting with correct commas and quotation marks

#### Localization Key Mismatches
- **Problem**: Skin names appear as localization keys instead of display names
- **Solution**: Verify serialize_name matches between skins.json and en_US.lang files

#### Texture Loading Issues
- **Problem**: Skins appear with default textures
- **Solution**: Ensure PNG files exist and filenames match the texture property in skins.json

#### Geometry Compatibility
- **Problem**: Skins appear distorted
- **Solution**: Verify geometry types match the intended player model (Steve vs Alex)

### World Template Issues

#### Missing World Data
- **Problem**: World template fails to load or shows empty world
- **Solution**: Replace placeholder level.dat, level.dat_old, and db/ files with actual exported world files

#### Pack Loading Issues
- **Problem**: Add-on packs don't load with the world template
- **Solution**: Verify world_behavior_packs.json and world_resource_packs.json contain correct pack IDs

#### Folder Name Length
- **Problem**: Packs fail to load on Xbox
- **Solution**: Ensure behavior and resource pack folder names are ≤10 characters

#### Database Corruption
- **Problem**: World template imports but world is corrupted
- **Solution**: Use fresh database files from a working exported world

## License

This filter is part of the Regolith filter system and follows the same licensing terms.
