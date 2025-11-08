import os
import json
import frontmatter
import sys
import builtins
import functools
import re
import logging
import zipfile
from copy import deepcopy
from typing import Dict, Any, List, Optional, Union, Tuple, NamedTuple
from pathlib import Path
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[guidebook-gen] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import reticulator for Minecraft pack processing
try:
    from reticulator import *  # type: ignore
    RETICULATOR_AVAILABLE = True
except ImportError:
    RETICULATOR_AVAILABLE = False
    logger.warning("Reticulator not available. Pack processing features disabled.")


class PageType(Enum):
    """Page type definitions with validation rules."""
    CONTENT = "content"  # buttons + body (optional) - Navigation and content display
    FORM = "form"        # fields - Data collection only
    DIALOG = "dialog"    # exactly 2 buttons + body - Confirmation dialogs


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class PropertyScope(Enum):
    """Property scope definitions."""
    PLAYER = "player"    # Stored per-player, persists across sessions
    WORLD = "world"      # Stored globally, shared by all players
    CONST = "const"      # Read-only player constants


# Always use UTF-8 encoding for open, but only for text mode
original_open = builtins.open


@functools.wraps(original_open)
def utf8_open(*args, **kwargs):
    mode = 'r'
    if len(args) > 1:
        mode = args[1]
    elif 'mode' in kwargs:
        mode = kwargs['mode']
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return original_open(*args, **kwargs)


builtins.open = utf8_open


class PropertyPlaceholderProcessor:
    """Handles property placeholder parsing and processing."""

    # Property placeholder patterns
    PLACEHOLDER_PATTERNS = [
        (r'\{\{p:([^|]+)\|([^}]*)\}\}', 'property_with_default'),   # {{p:property_name|default}}
        (r'\{\{p:([^}]+)\}\}', 'property'),                        # {{p:property_name}}
        (r'\{\{c:([^}]+)\}\}', 'constant'),                        # {{c:constant_name}}
        (r'\{\{parser:([^}]+)\}\}', 'parser')                      # {{parser:function_name}}
    ]

    @classmethod
    def process_placeholders(cls, text: str) -> str:
        """Process property placeholders in text."""
        if not isinstance(text, str):
            return text

        result = text
        for pattern, _placeholder_type in cls.PLACEHOLDER_PATTERNS:
            matches = re.finditer(pattern, result)
            for _match in matches:
                # For now, preserve placeholders as-is (runtime processing)
                pass

        return result

    @classmethod
    def process_data(cls, data: Any) -> Any:
        """Recursively process placeholders in all string values."""
        if isinstance(data, dict):
            return {key: cls.process_data(value) for key, value in data.items()}
        if isinstance(data, list):
            return [cls.process_data(item) for item in data]
        if isinstance(data, str):
            return cls.process_placeholders(data)
        return data


class MinecraftFormatter:
    """Handles conversion of Markdown to Minecraft formatting codes."""

    # Simplified regex patterns for better performance
    PATTERNS = [
        (r'\[(.*?)\]\(.*?\)', r'\1'),  # Links: [text](url) -> text
        (r'\*\*(.*?)\*\*', r'§l\1§r'),  # Bold: **text** -> §ltext§r
        (r'__(.*?)__', r'§n\1§r'),  # Underline: __text__ -> §ntext§r
        (r'~~(.*?)~~', r'§m\1§r'),  # Strikethrough: ~~text~~ -> §mtext§r
        (r'\*(.*?)\*', r'§o\1§r'),  # Italic: *text* -> §otext§r
        (r'`(.*?)`', r'§7\1§r'),  # Code: `text` -> §7text§r
        (r'&([0-9a-fk-or])', r'§\1'),  # Color codes: &0 -> §0, &c -> §c, etc.
    ]

    @classmethod
    def format_text(cls, text: str) -> str:
        """Convert Markdown formatting to Minecraft formatting codes."""
        if not isinstance(text, str):
            return text

        result = text
        for pattern, replacement in cls.PATTERNS:
            result = re.sub(pattern, replacement, result)

        return result

    @classmethod
    def format_data(cls, data: Any) -> Any:
        """Recursively format all string values in a data structure."""
        if isinstance(data, dict):
            return {key: cls.format_data(value) for key, value in data.items()}
        if isinstance(data, list):
            return [cls.format_data(item) for item in data]
        if isinstance(data, str):
            return cls.format_text(data)
        return data


# Global search results page configuration (populated from markdown or settings)
GLOBAL_SEARCH_RESULTS_CONFIG: Optional[Dict[str, Any]] = None


def deep_merge_dicts(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-merge source dict into target dict."""
    for key, value in source.items():
        if (
            key in target
            and isinstance(target[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge_dicts(target[key], value)
        else:
            target[key] = deepcopy(value)
    return target


def register_search_results_config(config: Dict[str, Any], source: str) -> None:
    """Register or merge a search results page configuration."""
    global GLOBAL_SEARCH_RESULTS_CONFIG

    if not isinstance(config, dict):
        logger.error(f"{source}: search_results_page must be an object")
        return

    processed_config = PropertyPlaceholderProcessor.process_data(config)
    processed_config = MinecraftFormatter.format_data(processed_config)

    if GLOBAL_SEARCH_RESULTS_CONFIG is None:
        GLOBAL_SEARCH_RESULTS_CONFIG = deepcopy(processed_config)
        logger.info(f"Registered search results page configuration from {source}")
    else:
        deep_merge_dicts(GLOBAL_SEARCH_RESULTS_CONFIG, processed_config)
        logger.info(f"Merged search results page configuration from {source}")


def find_bp_dir() -> str:
    """Find the behavior pack directory."""
    # In Regolith's temp environment, CWD is the project root
    for entry in os.listdir('.'):
        if os.path.isdir(entry) and 'BP' in entry:
            return entry

    # Fallback for local testing
    if os.path.isdir('packs/behavior'):
        return 'packs/behavior'

    raise FileNotFoundError("Behavior Pack directory not found.")


def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments."""
    try:
        if len(sys.argv) > 1:
            return json.loads(sys.argv[1])
        logger.warning("No valid settings provided. Using defaults.")
        return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse settings: {e}. Using defaults.")
        return {}


def validate_property_definition(prop_def: Any, context: str) -> bool:
    """Validate a property definition structure."""
    if not isinstance(prop_def, dict):
        logger.error(f"{context}: Property definition must be an object")
        return False

    if 'name' not in prop_def:
        logger.error(f"{context}: Property definition missing 'name' field")
        return False

    if 'scope' not in prop_def:
        logger.error(f"{context}: Property definition missing 'scope' field")
        return False

    valid_scopes = [scope.value for scope in PropertyScope]
    if prop_def['scope'] not in valid_scopes:
        logger.error(f"{context}: Invalid property scope '{prop_def['scope']}'. Must be one of: {valid_scopes}")
        return False

    return True


def validate_button(button: Any, context: str) -> bool:
    """Validate a button definition."""
    if not isinstance(button, dict):
        logger.error(f"{context}: Button must be an object")
        return False

    if 'text' not in button:
        logger.error(f"{context}: Button missing required 'text' field")
        return False

    if 'action' not in button:
        logger.error(f"{context}: Button missing required 'action' field")
        return False

    return True


def validate_field(field: Any, context: str) -> bool:
    """Validate a form field definition."""
    if not isinstance(field, dict):
        logger.error(f"{context}: Field must be an object")
        return False

    required_fields = ['type', 'label', 'property']
    for req_field in required_fields:
        if req_field not in field:
            logger.error(f"{context}: Field missing required '{req_field}' field")
            return False

    valid_field_types = ['textField', 'toggle', 'slider', 'dropdown']
    if field['type'] not in valid_field_types:
        logger.error(f"{context}: Invalid field type '{field['type']}'. Must be one of: {valid_field_types}")
        return False

    # Validate property definition
    if not validate_property_definition(field['property'], f"{context}.property"):
        return False

    # Type-specific validation
    if field['type'] == 'slider':
        required_slider_fields = ['min', 'max', 'step']
        for req_field in required_slider_fields:
            if req_field not in field:
                logger.error(f"{context}: Slider field missing required '{req_field}' field")
                return False

    if field['type'] == 'dropdown':
        if 'options' not in field:
            logger.error(f"{context}: Dropdown field missing required 'options' field")
            return False
        if not isinstance(field['options'], list):
            logger.error(f"{context}: Dropdown 'options' must be an array")
            return False

    return True


def determine_page_type(metadata: Dict[str, Any]) -> PageType:
    """Determine the page type based on frontmatter content."""
    has_buttons = 'buttons' in metadata and metadata['buttons']
    has_fields = 'fields' in metadata and metadata['fields']
    has_body = 'body' in metadata or True  # Body can come from markdown content

    if has_fields and not has_buttons:
        return PageType.FORM
    if has_buttons and not has_fields:
        if isinstance(metadata.get('buttons'), list) and len(metadata['buttons']) == 2:
            return PageType.DIALOG
        return PageType.CONTENT
    if not has_fields and not has_buttons:
        return PageType.CONTENT

    raise ValidationError("Invalid page type combination: cannot mix buttons and fields")


def validate_page_type_constraints(metadata: Dict[str, Any], page_type: PageType, file_path: str) -> bool:
    """Validate page type specific constraints."""
    has_buttons = 'buttons' in metadata and metadata['buttons']
    has_fields = 'fields' in metadata and metadata['fields']

    if page_type == PageType.FORM:
        if has_buttons:
            logger.error(f"{file_path}: Form pages cannot have buttons (forms have their own submit button)")
            return False
        if not has_fields:
            logger.error(f"{file_path}: Form pages must have fields")
            return False

    elif page_type == PageType.DIALOG:
        if has_fields:
            logger.error(f"{file_path}: Dialog pages cannot have fields")
            return False
        if not has_buttons or len(metadata['buttons']) != 2:
            logger.error(f"{file_path}: Dialog pages must have exactly 2 buttons")
            return False

    elif page_type == PageType.CONTENT:
        if has_fields:
            logger.error(f"{file_path}: Content pages cannot have fields")
            return False

    return True


def validate_frontmatter(metadata: Dict[str, Any], file_path: str) -> bool:
    """Validate frontmatter metadata structure with comprehensive rules."""
    try:
        # Determine page type
        page_type = determine_page_type(metadata)
        logger.debug(f"{file_path}: Detected page type: {page_type.value}")

        # Validate page type constraints
        if not validate_page_type_constraints(metadata, page_type, file_path):
            return False

        # Validate buttons if present
        if 'buttons' in metadata:
            if not isinstance(metadata['buttons'], list):
                logger.error(f"{file_path}: 'buttons' must be an array")
                return False
            for i, button in enumerate(metadata['buttons']):
                if not validate_button(button, f"{file_path}.buttons[{i}]"):
                    return False

        # Validate fields if present
        if 'fields' in metadata:
            if not isinstance(metadata['fields'], list):
                logger.error(f"{file_path}: 'fields' must be an array")
                return False
            for i, field in enumerate(metadata['fields']):
                if not validate_field(field, f"{file_path}.fields[{i}]"):
                    return False

        # Validate version control if versions are present
        if 'versions' in metadata:
            if 'version_control_property' not in metadata:
                logger.error(f"{file_path}: 'versions' requires 'version_control_property'")
                return False
            if not validate_property_definition(metadata['version_control_property'], f"{file_path}.version_control_property"):
                return False

        # Validate children if present
        if 'children' in metadata:
            if not isinstance(metadata['children'], list):
                logger.error(f"{file_path}: 'children' must be an array")
                return False

        return True

    except ValidationError as e:
        logger.error(f"{file_path}: {e}")
        return False


def generate_page_id(file_path: str, source_dir: str) -> str:
    """Generate a unique page ID from file path."""
    relative_path = os.path.relpath(file_path, source_dir)
    normalized_path = relative_path.replace(os.path.sep, '/')
    filename_base, _ = os.path.splitext(os.path.basename(normalized_path))

    if filename_base == 'main':
        page_id = os.path.dirname(normalized_path)
        return page_id if page_id else 'main'
    return os.path.splitext(normalized_path)[0]


def flatten_children(parent_page: Dict[str, Any], parent_id: str) -> List[Dict[str, Any]]:
    """Recursively flatten nested children into separate pages."""
    flattened_pages = []

    if 'children' not in parent_page:
        return [parent_page]

    children = parent_page.pop('children')  # Remove children from parent
    flattened_pages.append(parent_page)  # Add parent without children

    for i, child in enumerate(children):
        # Generate child ID based on parent path
        child_id = f"{parent_id}/child_{i+1}"
        if 'id' not in child:
            child['id'] = child_id

        # Recursively process child's children
        child_pages = flatten_children(child, child['id'])
        flattened_pages.extend(child_pages)

    return flattened_pages


def process_versions(page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process page versions into separate page entries."""
    if 'versions' not in page_data:
        return [page_data]

    versions = page_data.pop('versions')
    version_control_property = page_data.pop('version_control_property', None)
    base_page = page_data.copy()

    processed_pages = []

    for i, version in enumerate(versions):
        version_page = base_page.copy()

        # Apply version-specific overrides
        for key, value in version.items():
            if key != 'value':  # 'value' is the condition, not page content
                version_page[key] = value

        # Add version metadata
        version_page['_version_value'] = version.get('value')
        version_page['_version_control_property'] = version_control_property
        version_page['_version_index'] = i

        processed_pages.append(version_page)

    return processed_pages


def load_source_config(source_dir: str) -> None:
    """Load configuration from `_config.json` residing in the source directory."""
    config_path = os.path.join(source_dir, "_config.json")
    if not os.path.isfile(config_path):
        logger.debug(f"No _config.json found in {source_dir}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = json.load(config_file)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {config_path}: {e}")
        return
    except Exception as e:
        logger.error(f"Error reading {config_path}: {e}")
        return

    if not isinstance(config_data, dict):
        logger.error(f"{config_path} must contain a JSON object at the top level")
        return

    if "search_results_page" in config_data:
        register_search_results_config(config_data["search_results_page"], config_path)
    else:
        logger.debug(f"{config_path} does not define search_results_page")


def process_markdown_file(file_path: str, source_dir: str) -> List[Dict[str, Any]]:
    """Process a single markdown file and return page data."""
    try:
        page_data = frontmatter.load(file_path)
        page_json = page_data.metadata.copy()

        # Detect and register search results configuration files
        if 'search_results_page' in page_json:
            config_data = page_json.get('search_results_page')
            register_search_results_config(config_data, file_path)
            logger.debug(f"{file_path}: Processed search results configuration")
            return []

        # Use body from frontmatter if specified, otherwise use markdown content
        if 'body' not in page_json:
            page_json['body'] = page_data.content.strip()

        # Validate frontmatter
        if not validate_frontmatter(page_json, file_path):
            return []

        # Generate page ID
        page_json['id'] = generate_page_id(file_path, source_dir)

        # Set default values
        if 'showInSearch' not in page_json:
            page_json['showInSearch'] = True

        # Process property placeholders
        page_json = PropertyPlaceholderProcessor.process_data(page_json)

        # Apply Minecraft formatting
        page_json = MinecraftFormatter.format_data(page_json)

        # Process versions (creates multiple pages if versions exist)
        versioned_pages = process_versions(page_json)

        # Flatten children for each versioned page
        final_pages = []
        for page in versioned_pages:
            flattened = flatten_children(page, page['id'])
            final_pages.extend(flattened)

        return final_pages

    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return []


def gather_guidebook_pages(source_dir: str) -> List[Dict[str, Any]]:
    """Gather all guidebook pages from markdown files."""
    all_pages = []

    if not os.path.isdir(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        return all_pages

    # Find all markdown files
    markdown_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    if not markdown_files:
        logger.warning(f"No markdown files found in {source_dir}")
        return all_pages

    logger.info(f"Found {len(markdown_files)} markdown files to process")

    # Process each file (can return multiple pages due to versions/children)
    total_pages_generated = 0
    for i, file_path in enumerate(markdown_files, 1):
        logger.debug(f"Processing file {i}/{len(markdown_files)}: {file_path}")

        page_list = process_markdown_file(file_path, source_dir)
        if page_list:
            all_pages.extend(page_list)
            total_pages_generated += len(page_list)

            # Log the main page ID(s)
            main_ids = [page.get('id', 'unknown') for page in page_list[:3]]  # Show up to 3 IDs
            id_display = ', '.join(main_ids)
            if len(page_list) > 3:
                id_display += f" (and {len(page_list)-3} more)"
            logger.debug(f"Successfully processed {len(page_list)} pages: {id_display}")

    logger.info(f"Successfully processed {total_pages_generated} total pages from {len(markdown_files)} files")
    return all_pages


class NameJsonPath(NamedTuple):
    path: str
    should_pop: bool = False
    add_affixes: bool = False


def get_jsonpath(data, path, default=None):
    """Get value from JSON using path notation."""
    keys = [k for k in path.strip('/').split('/') if k]
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, list):
            try:
                index = int(key)
                current = current[index]
            except (ValueError, IndexError):
                return default
        else:
            return default
        if current is None:
            return default
    return current


def format_asset_name(name: str) -> str:
    """Format asset name for display."""
    parts = name.split(":")
    if len(parts) == 2:
        return parts[1].replace("_", " ").title()
    return name.replace("_", " ").title()


def get_json_value(asset, path, should_pop):
    """Get JSON value from asset with optional pop operation."""
    try:
        if should_pop:
            return asset.pop_jsonpath(path)
        return get_jsonpath(asset.data, path)
    except Exception:
        return None


def assign_translation_value(path, value, translation_dict, key_list):
    """Assign translation value based on path matching."""
    for key in key_list:
        if key in path:
            translation_dict[key] = value


def process_asset(asset, jsonpaths_list, key_list):
    """Process a single asset and extract data."""
    translation_data = {}
    for jsonpaths in jsonpaths_list:
        for jp in jsonpaths:
            value = get_json_value(asset, jp.path, jp.should_pop)
            if value is not None:
                assign_translation_value(jp.path, value, translation_data, key_list)
    return translation_data


def gather_asset_data(assets, settings: dict, jsonpaths_list, ignored_namespaces: List[str], key_list: List[str], target_namespace: str = "5fs") -> Dict[str, Dict[str, Any]]:
    """Gather asset data from Minecraft pack assets."""
    all_assets = {}

    for asset in assets:
        try:
            identifier = asset.identifier
        except Exception:
            continue

        namespace = identifier.split(':')[0] if ':' in identifier else ''

        # Skip ignored namespaces
        if namespace in ignored_namespaces:
            continue

        # Only process target namespace by default
        if target_namespace and namespace != target_namespace:
            continue

        short_id = identifier.split(':')[1] if ':' in identifier else identifier
        if short_id not in all_assets:
            all_assets[short_id] = {'id': identifier}

        asset_info = process_asset(asset, jsonpaths_list, key_list)
        all_assets[short_id].update(asset_info)

    return all_assets


def map_pattern_grid(patterns):
    """Map recipe pattern to grid slots."""
    slot_mapping = {}
    slot_number = 1

    for row in patterns:
        for ch in row:
            key = f"slot_{slot_number}"
            if ch.strip():
                slot_mapping[key] = ch
            else:
                slot_mapping[key] = None
            slot_number += 1

    return slot_mapping


def is_valid_frontmatter_property(key: str, value: Any) -> bool:
    """Check if a property is valid according to the frontmatter specification."""
    # Skip empty or None values
    if value is None or value == '' or value == 0:
        return False

    # Skip properties that start with underscore (internal)
    if key.startswith('_'):
        return False

    # Valid frontmatter properties according to the specification
    valid_frontmatter_properties = {
        # Basic properties
        'title', 'body', 'showInSearch', 'associated_block', 'associated_item', 'search_icon',

        # Interactive elements (handled separately)
        'buttons', 'fields',

        # Page events (handled separately)
        'on_open', 'on_close', 'on_first_open', 'on_submit_action',

        # Versioning (handled separately)
        'versions', 'version_control_property',

        # Nested structure (handled separately)
        'children',

        # Asset-specific (only name and description from pack data)
        'name', 'description'
    }

    # Only include properties that are in the official frontmatter spec
    return key.lower() in valid_frontmatter_properties


def create_asset_markdown(item_name: str, item_data: Dict[str, Any], asset_type: str, all_recipes: Dict = None) -> str:
    """Create markdown content with rich frontmatter for an asset."""
    # Extract basic information
    display_name = item_data.get('name', format_asset_name(item_name))
    description = item_data.get('description', f"{asset_type.title()} {display_name}")
    item_id = item_data.get('id', item_name)

    # Create comprehensive frontmatter
    frontmatter_data = {
        'title': display_name,
        'body': description,
        'type': asset_type,
        'id': item_name,
        'showInSearch': True,
        'associated_item': item_id  # Enables "Get Item" button in creative mode
    }

    # Add page events for tracking
    frontmatter_data['on_open'] = [{
        'action': 'increment_property',
        'property': {'name': f'{asset_type}_views', 'scope': 'player'},
        'value': 1
    }]

    frontmatter_data['on_first_open'] = [{
        'action': 'set_property',
        'property': {'name': f'{item_name}_discovered', 'scope': 'player'},
        'value': 'true'
    }]

    # Create navigation buttons
    buttons = []

    # Add recipe viewing if available
    recipe_data = item_data.get('recipe')
    pattern_data = item_data.get('pattern')

    if recipe_data and pattern_data:
        # Add "View Recipe" button
        buttons.append({
            'text': 'View Crafting Recipe',
            'action': f'navigateTo:{item_name}_recipe',
            'icon': 'textures/ui/crafting_table'
        })

    # Add category navigation
    buttons.append({
        'text': f'Browse All {asset_type.title()}',
        'action': f'navigateTo:{asset_type}_index',
        'icon': 'textures/ui/list'
    })

    if buttons:
        frontmatter_data['buttons'] = buttons

    lines = ['---']

    import yaml
    yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
    lines.append(yaml_content.strip())
    lines.extend(['---', ''])

    # Add body content
    lines.append(f"# {display_name}")
    lines.append("")
    lines.append(description)
    lines.append("")

    # Add recipe information if available
    if recipe_data and pattern_data:
        lines.extend([
            "## Crafting Recipe",
            "",
            "**Ingredients:**"
        ])

        if isinstance(recipe_data, dict):
            for ingredient, symbol in recipe_data.items():
                if symbol:
                    ingredient_name = format_asset_name(ingredient)
                    lines.append(f"- **{symbol}**: {ingredient_name}")

        lines.extend(["", "**Pattern:**", "```"])

        if isinstance(pattern_data, dict):
            current_row = ""
            for i in range(1, 10):
                slot_key = f"slot_{i}"
                symbol = pattern_data.get(slot_key, ' ')
                if symbol is None:
                    symbol = ' '
                current_row += f"[{symbol}]"
                if i % 3 == 0:
                    lines.append(current_row)
                    current_row = ""

        lines.extend(["```", ""])

    return '\n'.join(lines)


def create_recipe_page_markdown(item_name: str, item_data: Dict[str, Any], asset_type: str) -> Optional[str]:
    """Create a dedicated recipe page for items with crafting recipes."""
    recipe_data = item_data.get('recipe')
    pattern_data = item_data.get('pattern')

    if not (recipe_data and pattern_data):
        return None

    display_name = item_data.get('name', format_asset_name(item_name))

    frontmatter_data = {
        'title': f'{display_name} Recipe',
        'id': f'{item_name}_recipe',
        'showInSearch': True,
        'buttons': [
            {
                'text': f'Back to {display_name}',
                'action': f'navigateTo:{item_name}',
                'icon': 'textures/ui/arrow_left'
            },
            {
                'text': 'Get Item',
                'action': {
                    'action': 'set_properties',
                    'properties': [{
                        'property': {'name': 'requested_item', 'scope': 'player'},
                        'value': item_data.get('id', item_name)
                    }]
                },
                'icon': 'textures/ui/give'
            }
        ]
    }

    lines = ['---']
    import yaml
    yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
    lines.append(yaml_content.strip())
    lines.extend(['---', ''])

    lines.extend([
        f"# {display_name} Recipe",
        "",
        f"Here's how to craft **{display_name}**:",
        "",
        "## Ingredients"
    ])

    if isinstance(recipe_data, dict):
        for ingredient, symbol in recipe_data.items():
            if symbol:
                ingredient_name = format_asset_name(ingredient)
                lines.append(f"- **{symbol}**: {ingredient_name}")

    lines.extend(["", "## Crafting Pattern", "```"])

    if isinstance(pattern_data, dict):
        current_row = ""
        for i in range(1, 10):
            slot_key = f"slot_{i}"
            symbol = pattern_data.get(slot_key, ' ')
            if symbol is None:
                symbol = ' '
            current_row += f"[{symbol}]"
            if i % 3 == 0:
                lines.append(current_row)
                current_row = ""

    lines.extend(["```", ""])

    return '\n'.join(lines)


def create_index_page_markdown(asset_type: str, assets: Dict[str, Dict[str, Any]]) -> str:
    """Create an index page for an asset category."""

    frontmatter_data = {
        'title': f'{asset_type.title()} Index',
        'id': f'{asset_type}_index',
        'showInSearch': True,
        'buttons': []
    }

    # Add navigation to each asset
    for asset_name, asset_data in sorted(assets.items()):
        display_name = asset_data.get('name', format_asset_name(asset_name))
        frontmatter_data['buttons'].append({
            'text': display_name,
            'action': f'navigateTo:{asset_name}',
            'icon': 'textures/ui/item_frame'
        })

    # Add back button
    frontmatter_data['buttons'].append({
        'text': 'Back to Main',
        'action': 'navigateTo:main',
        'icon': 'textures/ui/arrow_left'
    })

    lines = ['---']
    import yaml
    yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
    lines.append(yaml_content.strip())
    lines.extend(['---', ''])

    lines.extend([
        f"# {asset_type.title()} Index",
        "",
        f"Browse all available {asset_type}:",
        "",
        f"**{len(assets)} {asset_type} found**"
    ])

    return '\n'.join(lines)


def write_guidebook_file(target_file: str, pages: List[Dict[str, Any]]) -> bool:
    """Write the guidebook JSON file."""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        # Write guidebook content
        guidebook_content: Dict[str, Any] = {"pages": pages}
        if GLOBAL_SEARCH_RESULTS_CONFIG is not None:
            guidebook_content["search_results_page"] = GLOBAL_SEARCH_RESULTS_CONFIG

        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(guidebook_content, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully generated guidebook with {len(pages)} pages")
        if GLOBAL_SEARCH_RESULTS_CONFIG is not None:
            logger.info("Included custom search results page configuration")
        return True

    except Exception as e:
        logger.error(f"Failed to write output file {target_file}: {e}")
        return False


def process_minecraft_packs(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process Minecraft behavior and resource packs to generate guidebook pages."""
    if not RETICULATOR_AVAILABLE:
        logger.error("Reticulator library not available. Cannot process Minecraft packs.")
        return []

    try:
        # Initialize project
        project = Project("./BP", "./RP")  # type: ignore
        behavior_pack = project.behavior_pack

        # Get settings
        ignored_namespaces = settings.get("ignored_namespaces", ['minecraft'])
        target_namespace = settings.get("target_namespace", "5fs")
        key_list = settings.get("key_list", ["name", "description"])

        # Generate NameJsonPath objects dynamically
        entity_jsonpaths = [NameJsonPath(f"minecraft:entity/description/{key}", True, False) for key in key_list]
        block_jsonpaths = [NameJsonPath(f"minecraft:block/description/{key}", True, False) for key in key_list]
        item_jsonpaths = [NameJsonPath(f"minecraft:item/description/{key}", True, False) for key in key_list]
        recipe_jsonpaths = [NameJsonPath(f"minecraft:recipe_shaped/{key}", False, False) for key in key_list]

        # Gather asset data
        entities = gather_asset_data(behavior_pack.entities, settings.get("entity", {}), [entity_jsonpaths], ignored_namespaces, key_list, target_namespace)
        blocks = gather_asset_data(behavior_pack.blocks, settings.get("blocks", {}), [block_jsonpaths], ignored_namespaces, key_list, target_namespace)
        items = gather_asset_data(behavior_pack.items, settings.get("items", {}), [item_jsonpaths], ignored_namespaces, key_list, target_namespace)
        recipes = gather_asset_data(behavior_pack.recipes, settings.get("recipes", {}), [recipe_jsonpaths], ignored_namespaces, key_list, target_namespace)

        # Process recipes and associate them with items/blocks
        recipe_lookup = {}
        for recipe_asset in behavior_pack.recipes:
            try:
                recipe_id = recipe_asset.identifier
                recipe_data = recipe_asset.data
                if isinstance(recipe_data, dict) and 'key' in recipe_data:
                    recipe_lookup[recipe_id] = recipe_data['key']
                if isinstance(recipe_data, dict) and 'pattern' in recipe_data:
                    if recipe_id in recipes:
                        recipes[recipe_id]['pattern'] = map_pattern_grid(recipe_data['pattern'])
            except Exception:
                continue

        # Associate recipes with items and blocks
        def associate_recipes(asset_dict, recipe_data):
            for asset_name, asset_info in asset_dict.items():
                recipe_id = asset_info.get('recipe')
                if recipe_id and recipe_id in recipe_data:
                    recipe_info = recipe_data[recipe_id]
                    key_value = recipe_info.get('key', None)
                    pattern = recipe_info.get('pattern', None)

                    if isinstance(key_value, str):
                        try:
                            asset_info['recipe'] = json.loads(key_value)
                        except json.JSONDecodeError:
                            asset_info['recipe'] = key_value
                    else:
                        asset_info['recipe'] = key_value

                    if pattern:
                        asset_info['pattern'] = pattern

        associate_recipes(items, recipes)
        associate_recipes(blocks, recipes)
        associate_recipes(entities, recipes)

        # Generate markdown pages
        all_pages = []

        # Create asset pages
        for asset_name, asset_data in entities.items():
            if asset_data and len(asset_data) > 1:  # More than just 'id'
                markdown_content = create_asset_markdown(asset_name, asset_data, 'entities')
                page_data = frontmatter.loads(markdown_content)
                page_json = page_data.metadata.copy()
                page_json['body'] = page_data.content.strip()
                page_json = MinecraftFormatter.format_data(page_json)
                all_pages.append(page_json)

                # Create recipe page if applicable
                recipe_page = create_recipe_page_markdown(asset_name, asset_data, 'entities')
                if recipe_page:
                    recipe_page_data = frontmatter.loads(recipe_page)
                    recipe_json = recipe_page_data.metadata.copy()
                    recipe_json['body'] = recipe_page_data.content.strip()
                    recipe_json = MinecraftFormatter.format_data(recipe_json)
                    all_pages.append(recipe_json)

        for asset_name, asset_data in blocks.items():
            if asset_data and len(asset_data) > 1:
                markdown_content = create_asset_markdown(asset_name, asset_data, 'blocks')
                page_data = frontmatter.loads(markdown_content)
                page_json = page_data.metadata.copy()
                page_json['body'] = page_data.content.strip()
                page_json = MinecraftFormatter.format_data(page_json)
                all_pages.append(page_json)

                recipe_page = create_recipe_page_markdown(asset_name, asset_data, 'blocks')
                if recipe_page:
                    recipe_page_data = frontmatter.loads(recipe_page)
                    recipe_json = recipe_page_data.metadata.copy()
                    recipe_json['body'] = recipe_page_data.content.strip()
                    recipe_json = MinecraftFormatter.format_data(recipe_json)
                    all_pages.append(recipe_json)

        for asset_name, asset_data in items.items():
            if asset_data and len(asset_data) > 1:
                markdown_content = create_asset_markdown(asset_name, asset_data, 'items')
                page_data = frontmatter.loads(markdown_content)
                page_json = page_data.metadata.copy()
                page_json['body'] = page_data.content.strip()
                page_json = MinecraftFormatter.format_data(page_json)
                all_pages.append(page_json)

                recipe_page = create_recipe_page_markdown(asset_name, asset_data, 'items')
                if recipe_page:
                    recipe_page_data = frontmatter.loads(recipe_page)
                    recipe_json = recipe_page_data.metadata.copy()
                    recipe_json['body'] = recipe_page_data.content.strip()
                    recipe_json = MinecraftFormatter.format_data(recipe_json)
                    all_pages.append(recipe_json)

        # Create index pages
        if entities:
            index_content = create_index_page_markdown('entities', entities)
            index_data = frontmatter.loads(index_content)
            index_json = index_data.metadata.copy()
            index_json['body'] = index_data.content.strip()
            index_json = MinecraftFormatter.format_data(index_json)
            all_pages.append(index_json)

        if blocks:
            index_content = create_index_page_markdown('blocks', blocks)
            index_data = frontmatter.loads(index_content)
            index_json = index_data.metadata.copy()
            index_json['body'] = index_data.content.strip()
            index_json = MinecraftFormatter.format_data(index_json)
            all_pages.append(index_json)

        if items:
            index_content = create_index_page_markdown('items', items)
            index_data = frontmatter.loads(index_content)
            index_json = index_data.metadata.copy()
            index_json['body'] = index_data.content.strip()
            index_json = MinecraftFormatter.format_data(index_json)
            all_pages.append(index_json)

        logger.info(f"Generated {len(all_pages)} pages from Minecraft pack assets")
        return all_pages

    except Exception as e:
        logger.error(f"Error processing Minecraft packs: {e}")
        return []


def main():
    """Main execution function."""
    try:
        # Parse settings
        settings = parse_settings()
        source_dir = settings.get('source_dir', 'data/guidebook/')
        process_packs = settings.get('process_packs', False)

        # Register search results configuration from settings (if provided)
        if 'search_results_page' in settings:
            register_search_results_config(settings['search_results_page'], 'settings')

        # Find behavior pack directory
        try:
            bp_dir = find_bp_dir()
        except FileNotFoundError as e:
            logger.error(f"Behavior Pack directory not found: {e}")
            return

        # Determine output file
        target_file = settings.get('output', os.path.join(bp_dir, 'scripts', 'guidebook.json'))

        all_pages: List[Dict[str, Any]] = []

        if process_packs:
            logger.info("Processing Minecraft packs for asset information")
            pack_pages = process_minecraft_packs(settings)
            all_pages.extend(pack_pages)

        # Load configuration from source directory (_config.json)
        load_source_config(source_dir)

        # Always try to gather markdown pages as well
        logger.info(f"Gathering guidebook pages from {source_dir}")
        markdown_pages = gather_guidebook_pages(source_dir)
        all_pages.extend(markdown_pages)

        if not all_pages and GLOBAL_SEARCH_RESULTS_CONFIG is None:
            logger.warning("No pages were processed and no search configuration provided. No output file will be generated.")
            return

        # Write guidebook file
        if write_guidebook_file(target_file, all_pages):
            logger.info(f"Guidebook generation completed: {target_file}")
            logger.info(f"Total pages: {len(all_pages)}")
        else:
            logger.error("Failed to write guidebook file")

    except Exception as e:
        logger.error(f"Fatal error during guidebook generation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

