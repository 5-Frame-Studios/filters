# Advanced Guidebook Generator v2.0.0

**Complete rewrite with comprehensive frontmatter support!** Generates advanced interactive guidebook JSON files from markdown documents with extensive frontmatter metadata for Minecraft Bedrock Edition.

## 🚀 Major New Features in v2.0

- **📄 Multiple Page Types**: Content, Form, and Dialog pages with validation
- **🎮 Interactive Elements**: Buttons, form fields, and page events
- **🔄 Page Versioning**: Conditional content based on property values  
- **🏗️ Nested Pages**: Hierarchical page structure with auto-flattening
- **🔗 Property System**: Full placeholder support with player/world/const scopes
- **✅ Advanced Validation**: Comprehensive frontmatter validation with detailed error reporting
- **🎯 Associated Blocks/Items**: Direct page access and creative mode integration

## Page Types & Validation

### Content Pages
- **Purpose**: Navigation and content display
- **Elements**: `buttons` + `body` (optional)
- **Restrictions**: Cannot have `fields`

### Form Pages  
- **Purpose**: Data collection
- **Elements**: `fields` only
- **Restrictions**: Cannot have `buttons` (forms have built-in submit)

### Dialog Pages
- **Purpose**: Confirmation dialogs
- **Elements**: Exactly 2 `buttons` + `body`
- **Restrictions**: Cannot have `fields`, must have exactly 2 buttons

## Interactive Elements

### Buttons
```yaml
buttons:
  - text: "Next Page"
    action: "navigateTo:advanced"
    icon: "textures/ui/arrow_right"
  - text: "Save Progress"
    action:
      - action: "set_properties"
        properties:
          - property: { name: "progress_saved", scope: "player" }
            value: "true"
      - "navigateTo:main"
```

### Form Fields
```yaml
fields:
  - type: "textField"
    label: "Your Name:"
    property: { name: "player_name", scope: "player" }
    placeholder: "Enter your name..."
    
  - type: "slider"
    label: "Volume Level"
    property: { name: "volume", scope: "player" }
    min: 0
    max: 100
    step: 10
    default: 50
    
  - type: "dropdown"
    label: "Language:"
    property: { name: "language", scope: "player" }
    options: ["English", "Spanish", "French"]
    default: 0
```

## Property System

### Property Placeholders
- `{{p:property_name}}` - Player property value
- `{{p:property_name|default}}` - Property with fallback
- `{{c:player_name}}` - Player constants (name, gamemode, etc.)
- `{{parser:current_time}}` - Parser functions

### Property Scopes
- **player**: Per-player data, persists across sessions
- **world**: Global server data, shared by all players  
- **const**: Read-only player constants (name, gamemode, level, etc.)

## Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `source_dir` | string | `data/guidebook/` | Directory containing markdown files |
| `output` | string | `scripts/guidebook.json` | Output guidebook JSON file |
| `log_level` | string | `"INFO"` | Logging level |
| `validate_frontmatter` | boolean | `true` | Enable validation |

## Complete Page Examples

### Content Page Example
```markdown
---
title: "Welcome Guide"
showInSearch: true
associated_block: "minecraft:lectern"
associated_item: "minecraft:diamond"

on_first_open:
  - action: "set_property"
    property: { name: "tutorial_started", scope: "player" }
    value: "true"

buttons:
  - text: "Next: {{p:next_chapter|Chapter 2}}"
    action: "navigateTo:chapter2"
    icon: "textures/ui/arrow_right"
  - text: "Settings"
    action: "navigateTo:settings"
---

# Welcome to the Server!

Hello {{c:player_name}}! This is your **first** visit.

Current progress: {{p:tutorial_progress|0}}%
```

### Form Page Example  
```markdown
---
title: "Server Settings"
on_submit_action: "save_settings"

fields:
  - type: "textField" 
    label: "Display Name:"
    property: { name: "display_name", scope: "player" }
    placeholder: "{{c:player_name}}"
    default: "{{c:player_name}}"
    
  - type: "toggle"
    label: "Enable Notifications"
    property: { name: "notifications", scope: "player" }
    default: true
    
  - type: "slider"
    label: "UI Scale:"
    property: { name: "ui_scale", scope: "player" }
    min: 50
    max: 150
    step: 10
    default: 100
    
  - type: "dropdown"
    label: "Language:"
    property: { name: "language", scope: "player" }
    options: ["English", "Español", "Français"]
    default: 0
---

**Player Settings**

Customize your experience on the server.
```

### Dialog Page Example
```markdown
---
title: "Delete Confirmation"
buttons:
  - text: "Yes, Delete All"
    action:
      - action: "set_property"
        property: { name: "player_data", scope: "player" }
        value: "deleted"
      - "navigateTo:main"
  - text: "Cancel"
    action: "back"
---

**⚠️ Warning: Permanent Action**

Are you sure you want to delete all your player data?

This action **cannot be undone**. All progress will be lost.
```

### Versioned Page Example
```markdown
---
title: "Dynamic Content"
versions:
  - value: "beginner"
    title: "Beginner Tutorial"
    body: "Welcome new player! Start with the basics."
    buttons:
      - text: "Basic Tutorial"
        action: "navigateTo:tutorial_basic"
  - value: "advanced"
    title: "Advanced Features"
    body: "Ready for advanced content!"
    buttons:
      - text: "Advanced Tutorial"
        action: "navigateTo:tutorial_advanced"

version_control_property:
  name: "skill_level"
  scope: "player"
  defaultValue: "beginner"
---

This content changes based on your skill level!
```

### Nested Page Example
```markdown
---
title: "Chapter Hub"
children:
  - title: "Section 1: Basics"
    body: "Learn the fundamentals"
    buttons:
      - text: "Continue"
        action: "navigateTo:section2"
  - title: "Section 2: Advanced"
    body: "Master advanced techniques"
---

# Chapter Overview

This chapter covers essential topics.
```

## Page Events & Actions

### Event Types
```yaml
on_open:          # Every time page opens
on_close:         # When page closes/navigates away  
on_first_open:    # Only first visit per player
on_submit_action: # Custom form submission (form pages)
```

### Action Types
```yaml
# Navigation
"navigateTo:page_id"
"back"
"close"

# Properties  
action: "set_properties"
properties:
  - property: { name: "score", scope: "player" }
    value: 100

# Custom actions
"search"              # Enable search
"custom_action_name"  # Your registered action
```

## Advanced Features

### Associated Integration
- **associated_block**: Open page when using guidebook on specific block
- **associated_item**: Add "Get Item" button in creative mode

### Minecraft Formatting
| Markdown | Minecraft | Description |
|----------|-----------|-------------|
| `**text**` | `§ltext§r` | Bold |
| `__text__` | `§ntext§r` | Underline |
| `~~text~~` | `§mtext§r` | Strikethrough |
| `*text*` | `§otext§r` | Italic |
| `` `text` `` | `§7text§r` | Code |
| `&color` | `§color` | Color codes |

## Migration from v1.x

### ✅ Fully Backward Compatible
All existing v1.x markdown files work unchanged! The system automatically detects simple pages and treats them as Content pages.

### 🆕 Optional Enhancements
Add new features gradually:
```markdown
---
title: "My Page"        # ✅ Works as before
buttons:                # 🆕 Add interactivity
  - text: "Click me"
    action: "navigateTo:next"
---
```

## Version History

- **v2.0.0**: Complete rewrite with interactive elements, versioning, forms, validation
- **v1.1.0**: Enhanced error handling, improved performance  
- **v1.0.0**: Initial release