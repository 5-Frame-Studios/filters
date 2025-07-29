# Audio Converter Filter v1.0.0

Converts various audio formats to .ogg files for Minecraft Bedrock Edition. Incorporates advanced patterns from the Blockbench filter with sophisticated file processing, complex validation, and advanced error handling. Uses pydub for audio processing - no external ffmpeg installation required.

## ✅ Features

- **Multi-Format Support**: Converts .wav, .mp3, .m4a, .aac, .flac, .aiff to .ogg
- **Advanced Audio Type Detection**: Automatically categorizes files (music, effects, ambient, UI, voice)
- **Batch Processing**: Converts multiple files in parallel for faster processing
- **Quality Control**: Type-specific quality settings with intelligent optimization
- **Smart File Discovery**: Recursively finds audio files with pattern matching
- **File Validation**: Comprehensive audio file validation using pydub
- **Progress Reporting**: Real-time progress updates and detailed logging
- **Error Handling**: Robust error handling with graceful degradation
- **Directory Organization**: Optional automatic directory organization by type
- **Incremental Processing**: Skips files that are already converted and up-to-date
- **Hash-Based Integrity**: SHA-256 hash calculation for file validation
- **Backup System**: Optional backup of original files
- **Minecraft Optimization**: Specialized settings for Minecraft performance
- **No External Dependencies**: Uses pydub - no ffmpeg installation required

## 🚀 Quick Start

### Prerequisites

**Simple Python installation:**

```bash
pip install pydub
```

That's it! No external ffmpeg installation required. pydub handles all audio processing internally.

### Basic Usage

The filter will automatically scan for audio files and convert them to .ogg format:

```json
{
    "source_dirs": ["RP/sounds/", "BP/sounds/"],
    "supported_formats": [".wav", ".mp3", ".m4a", ".aac", ".flac", ".aiff"],
    "output_format": ".ogg",
    "quality": 6
}
```

## Configuration

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `source_dirs` | array | `["RP/sounds/", "BP/sounds/"]` | Directories to scan for audio files |
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
| `.wav` | Waveform Audio | Uncompressed, high quality |
| `.mp3` | MPEG Audio | Compressed, widely supported |
| `.m4a` | MPEG-4 Audio | Apple format, good quality |
| `.aac` | Advanced Audio Coding | High efficiency |
| `.flac` | Free Lossless Audio Codec | Lossless compression |
| `.aiff` | Audio Interchange File Format | Apple format, uncompressed |

## Examples

### Basic Configuration
```json
{
    "source_dirs": ["RP/sounds/"],
    "quality": 6
}
```

### Advanced Configuration
```json
{
    "source_dirs": ["RP/sounds/", "BP/sounds/", "custom/audio/"],
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
1. **Recursive Scanning**: Searches all subdirectories for audio files
2. **Pattern Matching**: Uses glob patterns to find files by extension and type
3. **Categorization**: Automatically categorizes files by audio type
4. **Validation**: Checks each file is a valid audio file using pydub

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

## Error Handling

### Common Issues

#### "pydub is not available"
**Solution**: Install pydub
```bash
pip install pydub
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
[audio_converter] INFO: Scanning directory: RP/sounds/
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

## Installation

### Simple Installation

```bash
# Install pydub
pip install pydub

# That's it! No external dependencies required.
```

### Alternative Installation Methods

```bash
# Using conda
conda install -c conda-forge pydub

# Using pip with specific version
pip install pydub>=0.25.1
```

## Version History

- **v1.0.0**: Initial release with comprehensive audio conversion capabilities using pydub

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify pydub installation with `pip install pydub`
3. Review log output for specific error messages
4. Test with a small batch of files first

The filter is designed to be both powerful and user-friendly, with comprehensive error handling and detailed logging to help diagnose any issues. Installation is simple with just one Python package required. 