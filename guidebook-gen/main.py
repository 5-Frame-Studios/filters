import os
import json
import frontmatter
import sys
import builtins
import functools
import re

# --- NEW MINECRAFT FORMATTING PARSER ---

def parse_minecraft_formatting(text):
    """
    Converts specific Markdown syntax and color codes into Minecraft formatting codes.
    """
    if not isinstance(text, str):
        return text
    
    # Order of operations is important to avoid conflicts.
    
    # 1. Links: [link text](url) -> link text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # 2. Bold: **text** -> §ltext§r
    text = re.sub(r'\*\*(.*?)\*\*', r'§l\1§r', text)
    # 3. Underline: __text__ -> §ntext§r
    text = re.sub(r'__(.*?)__', r'§n\1§r', text)
    # 4. Strikethrough: ~~text~~ -> §mtext§r
    text = re.sub(r'~~(.*?)~~', r'§m\1§r', text)
    # 5. Italic: *text* -> §otext§r
    text = re.sub(r'\*(.*?)\*', r'§o\1§r', text)
    # 6. Code: `text` -> §7text§r
    text = re.sub(r'`(.*?)`', r'§7\1§r', text)
    # 7. Color Codes: &0 -> §0, &c -> §c, etc.
    text = re.sub(r'&([0-9a-fk-or])', r'§\1', text)
    
    return text

def recursive_parse(data):
    """
    Recursively traverses a dictionary or list and applies Minecraft
    formatting to all string values.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = recursive_parse(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = recursive_parse(item)
    elif isinstance(data, str):
        return parse_minecraft_formatting(data)
    return data

# --- SCRIPT CORE LOGIC (UNCHANGED) ---

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

def find_bp_dir():
    # In Regolith's temp environment, CWD is the project root
    for entry in os.listdir('.'):
        if os.path.isdir(entry) and 'BP' in entry:
            return entry
    # Fallback for local testing
    if os.path.isdir('packs/behavior'):
        return 'packs/behavior'
    raise FileNotFoundError("Behavior Pack directory not found.")

def parse_settings():
    try:
        settings = json.loads(sys.argv[1])
    except (IndexError, json.JSONDecodeError):
        print("[guidebook-gen] Warning: No valid settings provided. Using defaults.")
        settings = {}
    return settings

def gather_guidebook_pages(source_dir):
    all_pages = []
    if not os.path.isdir(source_dir):
        print(f"[guidebook-gen] [ERROR] Source directory not found: {source_dir}")
        return all_pages
        
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    page_data = frontmatter.load(file_path)
                    page_json = page_data.metadata
                    page_json['body'] = page_data.content.strip()

                    # --- ID GENERATION LOGIC ---
                    relative_path = os.path.relpath(file_path, source_dir)
                    normalized_path = relative_path.replace(os.path.sep, '/')
                    filename_base, _ = os.path.splitext(os.path.basename(normalized_path))
                    
                    if filename_base == 'main':
                        page_id = os.path.dirname(normalized_path)
                        if not page_id:
                            page_id = 'main'
                    else:
                        page_id, _ = os.path.splitext(normalized_path)
                    
                    page_json['id'] = page_id
                    
                    # --- APPLY FORMATTING PARSER ---
                    # This will parse the body, title, and all other string values.
                    page_json = recursive_parse(page_json)
                    # --- END OF NEW LOGIC ---

                    all_pages.append(page_json)
                except Exception as e:
                    print(f"[guidebook-gen] [ERROR] Failed to process {file_path}: {e}")
    return all_pages

def main():
    settings = parse_settings()
    source_dir = 'data/guidebook/'
    
    try:
        bp_dir = find_bp_dir()
    except FileNotFoundError as e:
        print(f"[guidecode-gen] [ERROR] {e}")
        return
        
    target_file = settings.get('output', os.path.join(bp_dir, 'scripts', 'guidebook.json'))
    
    print(f"[guidebook-gen] Scanning for markdown files in {source_dir}...")
    all_pages = gather_guidebook_pages(source_dir)
    
    if not all_pages:
        print("[guidebook-gen] [WARN] No markdown files found or processed. No output file will be generated.")
        return
        
    final_guidebook_content = {"pages": all_pages}
    
    try:
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, 'w') as f:
            json.dump(final_guidebook_content, f, indent=2)
        print(f"[guidebook-gen] Successfully generated {target_file} with {len(all_pages)} pages.")
    except Exception as e:
        print(f"[guidebook-gen] [ERROR] Failed to write output file {target_file}: {e}")

if __name__ == '__main__':
    main()
