# Apply Version Filter v1.1.0

Automatically applies and increments version numbers in Minecraft Bedrock Edition manifest files.

## ✅ Backward Compatibility

**This version is fully backward compatible with v1.0.0.** Existing projects using this filter will continue to work without any changes to their configuration files.

## Features

- **Automatic Version Incrementing**: Increments the patch version (last number) automatically
- **Comprehensive Manifest Updates**: Updates version in header, resource/data modules, and dependencies
- **Enhanced Error Handling**: Robust error handling with detailed logging (New in v1.1.0)
- **Validation**: Validates version format and manifest structure (New in v1.1.0)
- **Configurable**: Supports custom version files and target manifests
- **UTF-8 Support**: Full UTF-8 encoding support
- **Improved Logging**: Structured logging with configurable levels (New in v1.1.0)

## Quick Start

For existing users, no changes are required. The filter works exactly as before but with improved reliability and error reporting.

## Configuration

### Basic Settings (Backward Compatible)

Your existing configuration will continue to work:

```json
{
    "version_file": "./data/bump_manifest/version.json",
    "targets": ["RP/manifest.json", "BP/manifest.json"]
}
```

### Enhanced Settings (Optional - New in v1.1.0)

You can optionally add these new settings for enhanced functionality:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `version_file` | string | `./data/bump_manifest/version.json` | Path to version tracking file |
| `targets` | array | `["RP/manifest.json", "BP/manifest.json"]` | List of manifest files to update |
| `log_level` | string | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `backup_manifests` | boolean | `false` | Whether to create backups before updating |

### Version File Format

The version file format remains unchanged:

```json
{
    "version": [1, 0, 0]
}
```

## Usage

The filter behavior is identical to v1.0.0:

1. Read the current version from the version file
2. Increment the patch version (last number)
3. Update all target manifest files with the new version
4. Save the updated version back to the version file

## What's Updated in Manifest Files

The filter updates the same sections as before:

- `header.version` - Main manifest version
- `modules[].version` - For modules with type "resources" or "data"
- `dependencies[].version` - For dependencies with UUID fields

## New in v1.1.0

### Enhanced Error Handling
- **Invalid JSON**: Better error messages for malformed JSON files
- **Missing Files**: Clearer messages when files don't exist
- **Invalid Version Format**: Validates version structure with helpful error messages
- **File Permissions**: More graceful handling of permission errors

### Improved Logging
- **Structured Logging**: Consistent log format with `[apply_version]` prefix
- **Configurable Levels**: Control verbosity with `log_level` setting
- **Progress Reporting**: See which files were successfully updated
- **Debug Information**: Detailed processing information when needed

### Better Validation
- **Version Format**: Ensures version arrays have exactly 3 integers
- **Settings Validation**: Validates configuration parameters
- **Manifest Structure**: Checks manifest file structure before updating

## Migration Guide

### From v1.0.0 to v1.1.0

**No migration required!** Your existing setup will work immediately.

#### Optional Enhancements

If you want to take advantage of new features, you can add these optional settings:

```json
{
    "version_file": "./data/bump_manifest/version.json",
    "targets": ["RP/manifest.json", "BP/manifest.json"],
    "log_level": "INFO"
}
```

## Examples

### Existing Configuration (Still Works)
```json
{
    "version_file": "./data/bump_manifest/version.json",
    "targets": ["RP/manifest.json", "BP/manifest.json"]
}
```

### Enhanced Configuration (Optional)
```json
{
    "version_file": "./custom/version.json",
    "targets": ["packs/resource/manifest.json", "packs/behavior/manifest.json"],
    "log_level": "DEBUG",
    "backup_manifests": true
}
```

## Troubleshooting

### Common Issues

1. **"Invalid version format"**: Ensure your version file contains a valid version array
2. **"Manifest file not found"**: Check that the target paths are correct
3. **Permission errors**: Ensure the filter has write access to manifest files

### Log Levels

- **ERROR**: Only critical errors
- **WARNING**: Important notices and non-critical issues
- **INFO**: General progress information (recommended)
- **DEBUG**: Detailed processing information

## Version History

- **v1.1.0**: Enhanced error handling, improved logging, better validation (backward compatible)
- **v1.0.0**: Initial release

## Support

If you encounter any issues after upgrading, the filter maintains full backward compatibility. All existing configurations and workflows will continue to function as before. 