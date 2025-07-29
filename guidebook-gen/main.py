import os
import json
import frontmatter
import sys
import builtins
import functools
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[guidebook-gen] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

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
        elif isinstance(data, list):
            return [cls.format_data(item) for item in data]
        elif isinstance(data, str):
            return cls.format_text(data)
        return data

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
        else:
            logger.warning("No valid settings provided. Using defaults.")
            return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse settings: {e}. Using defaults.")
        return {}

def validate_frontmatter(metadata: Dict[str, Any], file_path: str) -> bool:
    """Validate frontmatter metadata structure."""
    required_fields = ['title']
    missing_fields = [field for field in required_fields if field not in metadata]
    
    if missing_fields:
        logger.warning(f"Missing required fields in {file_path}: {missing_fields}")
        return False
    
    return True

def generate_page_id(file_path: str, source_dir: str) -> str:
    """Generate a unique page ID from file path."""
    relative_path = os.path.relpath(file_path, source_dir)
    normalized_path = relative_path.replace(os.path.sep, '/')
    filename_base, _ = os.path.splitext(os.path.basename(normalized_path))
    
    if filename_base == 'main':
        page_id = os.path.dirname(normalized_path)
        return page_id if page_id else 'main'
    else:
        return os.path.splitext(normalized_path)[0]

def process_markdown_file(file_path: str, source_dir: str) -> Optional[Dict[str, Any]]:
    """Process a single markdown file and return page data."""
    try:
        page_data = frontmatter.load(file_path)
        page_json = page_data.metadata.copy()
        page_json['body'] = page_data.content.strip()
        
        # Validate frontmatter
        if not validate_frontmatter(page_json, file_path):
            return None
        
        # Generate page ID
        page_json['id'] = generate_page_id(file_path, source_dir)
        
        # Apply Minecraft formatting
        page_json = MinecraftFormatter.format_data(page_json)
        
        return page_json
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return None

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
    
    # Process each file
    for i, file_path in enumerate(markdown_files, 1):
        logger.debug(f"Processing file {i}/{len(markdown_files)}: {file_path}")
        
        page_data = process_markdown_file(file_path, source_dir)
        if page_data:
            all_pages.append(page_data)
            logger.debug(f"Successfully processed: {page_data.get('id', 'unknown')}")
    
    logger.info(f"Successfully processed {len(all_pages)} pages")
    return all_pages

def write_guidebook_file(target_file: str, pages: List[Dict[str, Any]]) -> bool:
    """Write the guidebook JSON file."""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # Write guidebook content
        guidebook_content = {"pages": pages}
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(guidebook_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully generated guidebook with {len(pages)} pages")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write output file {target_file}: {e}")
        return False

def main():
    """Main execution function."""
    try:
        # Parse settings
        settings = parse_settings()
        source_dir = settings.get('source_dir', 'data/guidebook/')
        
        # Find behavior pack directory
        try:
            bp_dir = find_bp_dir()
        except FileNotFoundError as e:
            logger.error(f"Behavior Pack directory not found: {e}")
            return
        
        # Determine output file
        target_file = settings.get('output', os.path.join(bp_dir, 'scripts', 'guidebook.json'))
        
        logger.info(f"Starting guidebook generation from {source_dir}")
        
        # Gather pages
        all_pages = gather_guidebook_pages(source_dir)
        
        if not all_pages:
            logger.warning("No pages were processed. No output file will be generated.")
            return
        
        # Write guidebook file
        if write_guidebook_file(target_file, all_pages):
            logger.info(f"Guidebook generation completed: {target_file}")
        else:
            logger.error("Failed to write guidebook file")
            
    except Exception as e:
        logger.error(f"Fatal error during guidebook generation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
