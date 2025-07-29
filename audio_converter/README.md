# Audio Converter Filter v1.0.0

Converts various audio formats to .ogg files for Minecraft Bedrock Edition. Incorporates advanced patterns from the Blockbench filter with sophisticated file processing, complex validation, and advanced error handling. Uses pydub for audio processing - no external ffmpeg installation required. Works like the Blockbench filter - finds files with glob patterns and replaces originals with converted files. Includes intelligent caching to skip unchanged files.

**Note**: WAV files are automatically skipped since both WAV and OGG are acceptable output formats for Minecraft Bedrock Edition.

## ✅ Features

- **Multi-Format Support**: Converts `.mp3`, `.m4a`, `.aac`, `.flac`, `.aiff` to `.ogg`
- **WAV Skipping**: Automatically skips `.wav` files (both WAV and OGG are acceptable)
- **Quality Control**: Configurable quality settings (0-10 scale)
- **Batch Processing**: Processes multiple files efficiently
- **Audio Type Detection**: Automatically categorizes audio by type (music, effects, ambient, UI, voice)
- **Minecraft Optimization**: Optimized settings for Minecraft Bedrock Edition
- **Intelligent Caching**: Skips unchanged files using hash-based detection
- **No External Dependencies**: Uses pydub - no ffmpeg installation required
- **Regolith Compatible**: Works with Regolith's non-destructive editing system
- **Blockbench-Style File Handling**: Finds files with glob patterns and replaces originals
- **Intelligent Caching**: Skips conversion for unchanged files using hashing

## 🚀 Quick Start

### Prerequisites

**Simple Python installation:**

```bash
pip install pydub
```

That's it! No external ffmpeg installation required. pydub handles all audio processing internally.

### Regolith Installation

1. **Add to your project's config.json:**
```json
{
  "filters": [
    {
      "url": "path/to/audio_converter",
      "venvSlot": 0
    }
  ]
}
```

2. **Install the filter:**
```bash
regolith install
```

3. **Run the filter:**
```bash
regolith run
```

### Basic Usage

The filter will automatically detect and scan for audio files:

```json
{
    "supported_formats": [".wav", ".mp3", ".m4a", ".aac", ".flac", ".aiff"],
    "output_format": ".ogg",
    "quality": 6
}
```

## Intelligent Directory Detection

### Automatic Discovery

The filter automatically detects audio directories using intelligent pattern matching:

#### **Primary Detection**
- **RP Directories**: Finds any directory containing "RP" in the name
- **BP Directories**: Finds any directory containing "BP" in the name
- **Sounds Subdirectories**: Looks for `sounds/` folders within RP/BP directories
- **Direct Audio Files**: Checks if RP/BP directories contain audio files directly

#### **Fallback Detection**
If no audio directories are found, the filter checks these standard locations:
- `packs/resource/sounds`
- `packs/behavior/sounds`
- `RP/sounds`
- `BP/sounds`
- `sounds`

#### **Supported Directory Structures**
```
Project/
├── RP/                    # ✅ Detected
│   └── sounds/           # ✅ Audio files processed
├── BP/                    # ✅ Detected
│   └── sounds/           # ✅ Audio files processed
├── resource_pack/         # ✅ Detected (contains "RP")
│   └── sounds/           # ✅ Audio files processed
├── behavior_pack/         # ✅ Detected (contains "BP")
│   └── sounds/           # ✅ Audio files processed
└── custom_audio/          # ❌ Not detected (manual specification needed)
```

### Manual Directory Specification

You can still specify directories manually if needed:

```json
{
    "source_dirs": ["RP/sounds/", "custom/audio/"],
    "quality": 6
}
```

## Configuration

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `source_dirs` | array/null | `null` | Directories to scan (null = auto-detect) |
| `supported_formats` | array | `[".wav", ".mp3", ".m4a", ".aac", ".flac", ".aiff"]` | Audio formats to convert |
| `output_format` | string | `".ogg"` | Output format (currently only .ogg supported) |
| `quality` | integer | `6` | Audio quality (0-10, higher = better quality, larger file) |
| `delete_originals` | boolean | `false` | Whether to delete original files after conversion |
| `organize_by_type` | boolean | `true` | Whether to organize files by type |
| `log_level` | string | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `max_workers` | integer | `4` | Maximum number of parallel conversion workers |
| `timeout` | integer | `300` | Timeout for individual file conversions (seconds) |
| `validate_files` | boolean | `true` | Whether to validate audio files before conversion |
| `calculate_hashes` | boolean | `true` | Whether to calculate file hashes for integrity |
| `backup_originals` | boolean | `false` | Whether to backup original files before conversion |
| `optimize_for_minecraft` | boolean | `true` | Whether to apply Minecraft-specific optimizations |
| `normalize_audio` | boolean | `false` | Whether to normalize audio levels |

### Audio Type Detection

The filter automatically detects and categorizes audio files:

| Audio Type | Patterns | Quality Preset | Use Case |
|------------|----------|----------------|----------|
| **Music** | `music/`, `bgm/`, `*music*` | 8 | Background music, themes |
| **Effects** | `effects/`, `sfx/`, `*effect*` | 6 | Sound effects, explosions |
| **Ambient** | `ambient/`, `env/`, `*ambient*` | 5 | Environmental sounds |
| **UI** | `ui/`, `*click*`, `*button*` | 4 | Interface sounds |
| **Voice** | `voice/`, `speech/`, `*voice*` | 7 | Character dialogue |
| **Unknown** | Other files | 6 | Default processing |

### Quality Settings

The quality setting affects both file size and audio quality:

| Quality | Bitrate | Description | File Size | Use Case |
|---------|---------|-------------|-----------|----------|
| 0-2 | 32k-64k | Low quality | Small | Background ambient sounds |
| 3-5 | 80k-112k | Medium quality | Medium | General sound effects |
| 6-8 | 128k-192k | High quality | Large | Music, important sounds |
| 9-10 | 256k-320k | Very high quality | Very large | High-fidelity audio |

## File Organization

### Directory Structure

The filter supports two organization modes:

#### Organized Mode (Default)
```
RP/sounds/
├── music/
│   ├── theme.ogg
│   └── ambient.ogg
├── effects/
│   ├── explosion.ogg
│   └── footsteps.ogg
└── ui/
    └── click.ogg
```

#### Flat Mode
```
RP/sounds/
├── theme.ogg
├── ambient.ogg
├── explosion.ogg
├── footsteps.ogg
└── click.ogg
```

### Supported Input Formats

| Format | Description | Notes |
|--------|-------------|-------|
| `.mp3` | MPEG Audio | Compressed, widely supported |
| `.m4a` | MPEG-4 Audio | Apple format, good quality |
| `.aac` | Advanced Audio Coding | High efficiency |
| `.flac` | Free Lossless Audio Codec | Lossless compression |
| `.aiff` | Audio Interchange File Format | Apple format, uncompressed |

### Skipped Formats (Already Acceptable)

| Format | Description | Notes |
|--------|-------------|-------|
| `.wav` | Waveform Audio | Skipped - already acceptable for Minecraft Bedrock Edition |

## Examples

### Basic Configuration (Auto-Detection)
```json
{
    "quality": 6
}
```

### Manual Directory Specification
```json
{
    "source_dirs": ["RP/sounds/", "custom/audio/"],
    "quality": 6
}
```

### Advanced Configuration
```json
{
    "source_dirs": ["RP/sounds/", "custom/audio/"],
    "supported_formats": [".wav", ".mp3", ".flac"],
    "quality": 8,
    "delete_originals": true,
    "organize_by_type": false,
    "log_level": "DEBUG",
    "max_workers": 8,
    "validate_files": true,
    "calculate_hashes": true,
    "backup_originals": true,
    "optimize_for_minecraft": true,
    "normalize_audio": true
}
```

### Music-Focused Configuration
```json
{
    "source_dirs": ["RP/sounds/music/"],
    "supported_formats": [".wav", ".flac"],
    "quality": 9,
    "delete_originals": false,
    "optimize_for_minecraft": true,
    "normalize_audio": true
}
```

### Sound Effects Configuration
```json
{
    "source_dirs": ["RP/sounds/effects/"],
    "supported_formats": [".wav", ".mp3"],
    "quality": 4,
    "delete_originals": true,
    "max_workers": 6,
    "normalize_audio": false
}
```

## Processing Behavior

### File Discovery
1. **Intelligent Detection**: Automatically finds RP/BP directories
2. **Recursive Scanning**: Searches all subdirectories for audio files
3. **Pattern Matching**: Uses glob patterns to find files by extension and type
4. **Categorization**: Automatically categorizes files by audio type
5. **Validation**: Checks each file is a valid audio file using pydub

### Conversion Process
1. **Parallel Processing**: Converts multiple files simultaneously
2. **Type-Based Optimization**: Applies different settings based on audio type
3. **Incremental Updates**: Skips files that are already converted and newer
4. **Quality Control**: Applies specified quality settings with intelligent adjustment
5. **Error Recovery**: Continues processing even if individual files fail

### Output Generation
1. **Directory Creation**: Automatically creates output directories
2. **File Naming**: Preserves original filename with .ogg extension
3. **Organization**: Optionally organizes files by type
4. **Cleanup**: Optionally removes original files or creates backups

## Regolith Integration

### Working Directory Structure

The filter operates in Regolith's temporary directory structure:
```
./RP/          # Resource pack files
./BP/          # Behavior pack files  
./data/        # Data files (if needed)
```

### Non-Destructive Editing

- **Temporary Processing**: All conversions happen in temporary directories
- **Safe Operation**: Original project files are never modified during processing
- **Change Application**: Changes are only applied after successful filter completion
- **Error Recovery**: Failed runs don't affect your project files

### Environment Variables

The filter can access Regolith's environment variables if needed:
- `ROOT_DIR`: Project root directory path
- `FILTER_DIR`: Filter definition directory path
- `WORKING_DIR`: Current working directory (temporary)

### Important: Temporary Directory File Access

**⚠️ Common Issue**: Regolith's temporary directory may not contain the actual audio files, only the directory structure. This is a known limitation of Regolith's non-destructive editing system.

**Symptoms**:
- Filter detects `RP/sounds` directory but finds 0 audio files
- Warning messages about temporary directory not containing files
- No files are processed despite files existing in the original project

**Solutions**:

#### 1. Automatic Detection (Recommended)
The filter now automatically detects when the temporary directory doesn't contain files and tries to use the original project directory instead.

#### 2. Manual Directory Specification
Specify the original project directory manually in your filter settings:

```json
{
    "source_dirs": ["C:/Users/yourname/Documents/GitHub/YourProject/packs/RP/sounds"],
    "quality": 6
}
```

#### 3. Relative Path Specification
Use relative paths from your project root:

```json
{
    "source_dirs": ["packs/RP/sounds", "packs/BP/sounds"],
    "quality": 6
}
```

#### 4. Multiple Directory Support
Specify multiple directories to scan:

```json
{
    "source_dirs": [
        "packs/RP/sounds",
        "packs/BP/sounds", 
        "custom/audio"
    ],
    "quality": 6
}
```

### Troubleshooting Regolith Issues

#### "No audio files found in any detected directories"

**Cause**: Regolith's temporary directory doesn't contain the actual audio files.

**Solutions**:
1. **Use manual directory specification** (see above)
2. **Check original project structure**: Verify files exist in `packs/RP/sounds/`
3. **Use absolute paths**: Specify the full path to your audio directories
4. **Check file extensions**: Ensure files have supported extensions (`.wav`, `.mp3`, etc.)

#### "Filter not found"

**Cause**: Filter URL or configuration issue.

**Solutions**:
1. Check filter URL in `config.json`
2. Run `regolith install` to reinstall the filter
3. Verify filter directory structure

#### "Virtual environment issues"

**Cause**: Python dependencies not installed correctly.

**Solutions**:
1. Check `venvSlot` configuration
2. Run `regolith install` to reinstall dependencies
3. Verify `requirements.txt` exists and is correct

#### "Cache problems"

**Cause**: Stale cache data.

**Solutions**:
1. Run `regolith clean` to clear project cache
2. Run `regolith clean --filter-cache` to clear filter cache
3. Reinstall the filter with `regolith install`

## Error Handling

### Common Issues

#### "pydub is not available"
**Solution**: Install pydub
```bash
pip install pydub
```

#### "No audio directories found"
**Solution**: The filter will use fallback directories or you can specify manually
```json
{
    "source_dirs": ["your/audio/directory/"]
}
```

#### "Invalid audio file"
**Solution**: Check that the file is a valid audio file
- Try playing the file in a media player
- Check file permissions
- Verify file isn't corrupted

#### "Conversion timeout"
**Solution**: Large files may take longer to convert
- Increase timeout settings if needed
- Check available disk space
- Verify system resources

### Error Recovery

The filter includes robust error handling:
- **Individual File Failures**: Continues processing other files
- **Directory Access Issues**: Skips inaccessible directories
- **Invalid Files**: Logs warnings and continues
- **System Errors**: Graceful degradation with helpful error messages

## Performance

### Optimization Tips

1. **Parallel Processing**: Uses ThreadPoolExecutor for concurrent conversions
2. **Incremental Updates**: Skips already-converted files
3. **Quality Settings**: Lower quality = faster conversion
4. **File Validation**: Quick validation before conversion
5. **Type-Based Optimization**: Different settings for different audio types

### Performance Metrics

Typical conversion speeds (varies by system):
- **Small files (< 1MB)**: 1-5 seconds per file
- **Medium files (1-10MB)**: 5-30 seconds per file
- **Large files (> 10MB)**: 30+ seconds per file

### Minecraft-Specific Optimizations

- **Sample Rate Limiting**: Ensures compatibility with 44.1kHz maximum
- **Channel Reduction**: Limits to stereo for performance
- **Bitrate Optimization**: Different limits for different audio types
- **Audio Normalization**: Optional audio level normalization

## Logging

### Log Levels

- **ERROR**: Only critical errors that prevent operation
- **WARNING**: Non-critical issues (missing files, etc.)
- **INFO**: General progress and conversion status (recommended)
- **DEBUG**: Detailed processing information for each file

### Log Output Example

```
[audio_converter] INFO: Starting advanced audio conversion process with pydub
[audio_converter] INFO: Working in Regolith temporary directory - changes will be applied after successful run
[audio_converter] INFO: No source directories specified, using intelligent detection
[audio_converter] INFO: Discovered audio directories: ['RP/sounds', 'BP/sounds']
[audio_converter] INFO: Scanning directory: RP/sounds
[audio_converter] INFO: Scanning directory: BP/sounds
[audio_converter] INFO: Total audio files found: 15
[audio_converter] INFO:   music: 5 files
[audio_converter] INFO:   effects: 8 files
[audio_converter] INFO:   ui: 2 files
[audio_converter] INFO: Processing music files: 5
[audio_converter] INFO: Converted music: RP/sounds/music/theme.wav
[audio_converter] INFO: Processing effects files: 8
[audio_converter] INFO: Converted effects: RP/sounds/effects/explosion.mp3
[audio_converter] INFO: Advanced conversion completed!
[audio_converter] INFO: Total files: 15
[audio_converter] INFO: Successfully converted: 15
[audio_converter] INFO: Failed: 0
[audio_converter] INFO: Skipped: 0
[audio_converter] INFO:   music: 5/5 successful
[audio_converter] INFO:   effects: 8/8 successful
[audio_converter] INFO:   ui: 2/2 successful
[audio_converter] INFO: Changes will be applied to project files after successful filter run
```

## Troubleshooting

### Installation Issues

1. **pydub not found**: Ensure pydub is installed with `pip install pydub`
2. **Permission errors**: Check file and directory permissions
3. **Python version**: Requires Python 3.6+ for f-strings and type hints

### Conversion Issues

1. **File format not supported**: Check supported_formats setting
2. **Quality issues**: Adjust quality setting (0-10)
3. **File size too large**: Lower quality setting or check source file
4. **Conversion fails**: Check source file integrity

### Performance Issues

1. **Slow conversion**: Reduce parallel workers or quality setting
2. **Memory usage**: Process smaller batches of files
3. **Disk space**: Ensure sufficient space for output files

### Regolith-Specific Issues

1. **Filter not found**: Check filter URL in config.json
2. **Virtual environment issues**: Verify venvSlot configuration
3. **Cache problems**: Run `regolith clean` to clear caches

### Directory Detection Issues

1. **No audio directories found**: Check project structure or specify manually
2. **Wrong directories detected**: Use manual specification with `source_dirs`
3. **Missing audio files**: Verify audio files exist in detected directories

## Best Practices

### File Organization
- Use descriptive filenames
- Organize by sound type (music, effects, ambient)
- Keep consistent naming conventions

### Quality Settings
- Use higher quality (7-9) for music and important sounds
- Use lower quality (3-5) for background effects
- Test different settings for your specific use case

### Batch Processing
- Process files in logical groups
- Monitor system resources during conversion
- Keep backups of original files

### Regolith Integration
- Use appropriate venvSlot for dependency management
- Test filters in development before production
- Monitor filter cache and clean when needed

### Directory Detection
- Let the filter auto-detect when possible
- Use manual specification for custom directory structures
- Test with different project layouts

## Advanced Features

### Hash-Based Integrity
- SHA-256 hash calculation for file validation
- Integrity checking for converted files
- Hash-based skipping for incremental processing

### Backup System
- Optional backup of original files
- Automatic backup directory creation
- Preserves original file metadata

### Type-Based Optimization
- Automatic audio type detection
- Quality presets for different types
- Duration-based quality adjustment
- Minecraft-specific optimizations

### Audio Processing
- Sample rate conversion
- Channel conversion (mono/stereo)
- Audio normalization
- Bitrate optimization

### Intelligent Detection
- Automatic RP/BP directory discovery
- Flexible naming convention support
- Fallback directory checking
- Audio file presence validation

## Installation

### Simple Installation

```bash
# Install pydub
pip install pydub

# That's it! No external dependencies required.
```

### Regolith Installation

1. **Add to config.json:**
```json
{
  "filters": [
    {
      "url": "path/to/audio_converter",
      "venvSlot": 0
    }
  ]
}
```

2. **Install:**
```bash
regolith install
```

### Alternative Installation Methods

```bash
# Using conda
conda install -c conda-forge pydub

# Using pip with specific version
pip install pydub>=0.25.1
```

## Version History

- **v1.0.0**: Initial release with comprehensive audio conversion capabilities using pydub, Regolith integration, and intelligent directory detection

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify pydub installation with `pip install pydub`
3. Review log output for specific error messages
4. Test with a small batch of files first
5. Check Regolith documentation for filter-specific issues

The filter is designed to be both powerful and user-friendly, with comprehensive error handling and detailed logging to help diagnose any issues. Installation is simple with just one Python package required, and it integrates seamlessly with Regolith's non-destructive editing system while providing intelligent directory detection for maximum flexibility. 