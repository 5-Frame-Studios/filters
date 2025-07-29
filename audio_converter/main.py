"""
Audio Converter Filter for Regolith

Converts various audio formats to .ogg files for Minecraft Bedrock Edition.
Incorporates advanced patterns from the Blockbench filter with sophisticated
file processing, complex validation, and advanced error handling.
Uses pydub for audio processing - no external ffmpeg installation required.

Regolith Integration:
- Works in temporary directory with RP/, BP/, and data/ subdirectories
- Non-destructive editing - changes only apply after successful run
- Uses environment variables for external file access if needed
- Intelligent directory detection for flexible project structures
"""

import os
import sys
import json
import logging
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob
from dataclasses import dataclass
from enum import Enum

# Audio processing with pydub
try:
    from pydub import AudioSegment
    from pydub.utils import make_chunks
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.error("pydub is not available. Please install with: pip install pydub")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[audio_converter] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class AudioType(Enum):
    """Enumeration of audio file types."""
    MUSIC = "music"
    EFFECT = "effect"
    AMBIENT = "ambient"
    UI = "ui"
    VOICE = "voice"
    UNKNOWN = "unknown"

@dataclass
class AudioFileInfo:
    """Information about an audio file."""
    path: str
    format: str
    duration: float
    bitrate: int
    sample_rate: int
    channels: int
    size: int
    audio_type: AudioType
    hash: str

class AudioProcessor:
    """Advanced audio processing with sophisticated file handling using pydub."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        # Remove .wav from supported formats since it's already an acceptable output
        self.supported_formats = settings.get('supported_formats', ['.mp3', '.m4a', '.aac', '.flac', '.aiff'])
        self.output_format = settings.get('output_format', '.ogg')
        self.quality = settings.get('quality', 6)
        self.max_workers = settings.get('max_workers', 4)
        self.timeout = settings.get('timeout', 300)
        
        # Advanced settings
        self.validate_files = settings.get('validate_files', True)
        self.calculate_hashes = settings.get('calculate_hashes', True)
        self.optimize_for_minecraft = settings.get('optimize_for_minecraft', True)
        
        # Validate pydub availability
        self._validate_pydub()
    
    def _validate_pydub(self) -> None:
        """Validate that pydub is available."""
        if not PYDUB_AVAILABLE:
            logger.error("pydub is not available")
            logger.error("Please install pydub: pip install pydub")
            sys.exit(1)

def find_audio_files() -> List[str]:
    """
    Find audio files using glob patterns like the Blockbench filter.
    
    Returns:
        List of discovered audio file paths
    """
    audio_files = []
    supported_formats = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff']
    
    # Use glob patterns to find audio files directly, just like the Blockbench filter
    for format_ext in supported_formats:
        # Look for files in RP/sounds/**/*.ext
        rp_pattern = f"RP/sounds/**/*{format_ext}"
        rp_files = glob.glob(rp_pattern, recursive=True)
        audio_files.extend(rp_files)
        
        # Look for files in BP/sounds/**/*.ext
        bp_pattern = f"BP/sounds/**/*{format_ext}"
        bp_files = glob.glob(bp_pattern, recursive=True)
        audio_files.extend(bp_files)
    
    # Remove duplicates and normalize paths
    audio_files = list(set(audio_files))
    audio_files = [os.path.normpath(f) for f in audio_files]
    
    return audio_files

class AudioFileDiscoverer:
    """Advanced file discovery with pattern matching and categorization."""
    
    def __init__(self, supported_formats: List[str]):
        self.supported_formats = supported_formats
        self.audio_patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, List[str]]:
        """Build pattern matching rules for different audio types."""
        return {
            AudioType.MUSIC: [
                "**/music/**/*",
                "**/bgm/**/*",
                "**/soundtrack/**/*",
                "**/*music*",
                "**/*bgm*"
            ],
            AudioType.EFFECT: [
                "**/effects/**/*",
                "**/sfx/**/*",
                "**/sounds/**/*",
                "**/*effect*",
                "**/*sfx*"
            ],
            AudioType.AMBIENT: [
                "**/ambient/**/*",
                "**/environment/**/*",
                "**/*ambient*",
                "**/*env*"
            ],
            AudioType.UI: [
                "**/ui/**/*",
                "**/interface/**/*",
                "**/*ui*",
                "**/*click*",
                "**/*button*"
            ],
            AudioType.VOICE: [
                "**/voice/**/*",
                "**/speech/**/*",
                "**/*voice*",
                "**/*speech*"
            ]
        }
    
    def discover_audio_files(self, source_dirs: List[str]) -> Dict[AudioType, List[str]]:
        """
        Discover and categorize audio files by type.
        
        Args:
            source_dirs: List of directories to search
            
        Returns:
            Dictionary mapping audio types to file lists
        """
        categorized_files = {audio_type: [] for audio_type in AudioType}
        
        for source_dir in source_dirs:
            if not os.path.exists(source_dir):
                logger.warning(f"Source directory not found: {source_dir}")
                continue
                
            logger.info(f"Scanning directory: {source_dir}")
            
            # Use simple glob patterns like the Blockbench filter
            for format_ext in self.supported_formats:
                pattern = os.path.join(source_dir, f"**/*{format_ext}")
                files = glob.glob(pattern, recursive=True)
                
                if files:
                    # Categorize files by type
                    for file_path in files:
                        audio_type = self._categorize_file(file_path, source_dir)
                        categorized_files[audio_type].append(file_path)
        
        # Log summary
        total_files = sum(len(files) for files in categorized_files.values())
        logger.info(f"Total audio files found: {total_files}")
        for audio_type, files in categorized_files.items():
            if files:
                logger.info(f"  {audio_type.value}: {len(files)} files")
        
        return categorized_files
    
    def _categorize_file(self, file_path: str, source_dir: str) -> AudioType:
        """
        Categorize a single file based on its path and patterns.
        
        Args:
            file_path: Path to the audio file
            source_dir: Source directory being scanned
            
        Returns:
            AudioType for the file
        """
        # Get relative path from source directory
        try:
            relative_path = os.path.relpath(file_path, source_dir)
        except ValueError:
            # Handle case where file_path is not relative to source_dir
            relative_path = file_path
        
        relative_path_lower = relative_path.lower()
        
        # Check each audio type pattern
        for audio_type, patterns in self.audio_patterns.items():
            for pattern in patterns:
                # Convert pattern to checkable format
                pattern_lower = pattern.lower()
                
                # Check if the file path matches this pattern
                if self._matches_pattern(relative_path_lower, pattern_lower):
                    return audio_type
        
        # If no pattern matches, categorize as unknown
        return AudioType.UNKNOWN
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if a file path matches a pattern.
        
        Args:
            file_path: Lowercase file path to check
            pattern: Lowercase pattern to match against
            
        Returns:
            True if the file matches the pattern
        """
        # Handle glob patterns
        if '**' in pattern:
            # Convert glob pattern to simple string matching
            pattern_parts = pattern.split('**')
            
            for part in pattern_parts:
                if part and part not in file_path:
                    return False
            
            return True
        elif '*' in pattern:
            # Handle simple wildcards
            import fnmatch
            return fnmatch.fnmatch(file_path, pattern)
        else:
            # Direct string matching
            return pattern in file_path

class AudioValidator:
    """Advanced audio file validation with detailed analysis using pydub."""
    
    def __init__(self, calculate_hashes: bool = True):
        self.calculate_hashes = calculate_hashes
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate audio file and extract detailed information using pydub.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (is_valid, file_info)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, None
            
            if not os.path.isfile(file_path):
                return False, None
            
            # Check file size
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                return False, None
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            
            # Load audio file with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Extract audio properties
            duration = len(audio) / 1000.0  # Convert to seconds
            bitrate = audio.frame_rate * audio.sample_width * audio.channels * 8
            sample_rate = audio.frame_rate
            channels = audio.channels
            
            # Calculate hash if requested
            file_hash = None
            if self.calculate_hashes:
                file_hash = self._calculate_file_hash(file_path)
            
            # Build file information
            file_info = {
                'path': file_path,
                'format': file_ext,
                'duration': duration,
                'bitrate': bitrate,
                'sample_rate': sample_rate,
                'channels': channels,
                'size': file_size,
                'hash': file_hash
            }
            
            return True, file_info
            
        except Exception:
            return False, None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

class AudioConverter:
    """Advanced audio conversion with sophisticated processing using pydub."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.processor = AudioProcessor(settings)
        self.discoverer = AudioFileDiscoverer(settings.get('supported_formats', []))
        self.validator = AudioValidator(settings.get('calculate_hashes', True))
        
        # Quality presets for different audio types
        self.quality_presets = {
            AudioType.MUSIC: 8,
            AudioType.EFFECT: 6,
            AudioType.AMBIENT: 5,
            AudioType.UI: 4,
            AudioType.VOICE: 7,
            AudioType.UNKNOWN: 6
        }
    
    def detect_audio_type(self, file_path: str) -> AudioType:
        """Detect audio type based on file path and content."""
        file_path_lower = file_path.lower()
        
        for audio_type, patterns in self.discoverer.audio_patterns.items():
            for pattern in patterns:
                if any(keyword in file_path_lower for keyword in pattern.split('/')):
                    return audio_type
        
        return AudioType.UNKNOWN
    
    def get_optimized_settings(self, audio_type: AudioType, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized conversion settings for audio type and file characteristics."""
        base_quality = self.quality_presets.get(audio_type, 6)
        
        # Adjust quality based on file characteristics
        if file_info['duration'] > 300:  # Long files (music)
            quality = min(base_quality + 1, 10)
        elif file_info['duration'] < 5:  # Short files (UI sounds)
            quality = max(base_quality - 1, 1)
        else:
            quality = base_quality
        
        # Minecraft-specific optimizations
        if self.settings.get('optimize_for_minecraft', True):
            # Ensure sample rate is compatible
            sample_rate = min(file_info['sample_rate'], 44100)
            # Limit bitrate for performance
            max_bitrate = 128000 if audio_type in [AudioType.UI, AudioType.EFFECT] else 192000
        else:
            sample_rate = file_info['sample_rate']
            max_bitrate = None
        
        return {
            'quality': quality,
            'sample_rate': sample_rate,
            'max_bitrate': max_bitrate,
            'channels': min(file_info['channels'], 2)  # Stereo max
        }
    
    def convert_audio_file_advanced(self, file_path: str, audio_type: AudioType) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Convert audio file with advanced processing using pydub.
        
        Args:
            file_path: Path to input audio file
            audio_type: Type of audio file
            
        Returns:
            Tuple of (success, message, conversion_info)
        """
        try:
            # Validate file
            is_valid, file_info = self.validator.validate_audio_file(file_path)
            
            if not is_valid:
                return False, f"Invalid audio file: {file_path}", {}
            
            # Check if file is already in acceptable format (WAV or OGG)
            input_ext = Path(file_path).suffix.lower()
            if input_ext in ['.wav', '.ogg']:
                return True, f"Skipped (acceptable format): {file_path}", {'skipped': True, 'reason': 'acceptable_format'}
            
            # Detect audio type if not provided
            if audio_type == AudioType.UNKNOWN:
                audio_type = self.detect_audio_type(file_path)
            
            # Get optimized settings
            conversion_settings = self.get_optimized_settings(audio_type, file_info)
            
            # Generate output path
            output_file = self._generate_output_path(file_path, audio_type)
            
            # Check if conversion is needed
            if self._should_skip_conversion(file_path, output_file, file_info):
                return True, f"Skipped (up-to-date): {file_path}", {'skipped': True}
            
            # Load audio with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Apply optimizations
            audio = self._apply_optimizations(audio, conversion_settings)
            
            # Export to ogg format
            export_params = self._get_export_params(conversion_settings)
            
            audio.export(
                output_file,
                format="ogg",
                **export_params
            )
            
            # Always delete the original file after successful conversion, just like Blockbench filter
            os.remove(file_path)
            
            conversion_info = {
                'input_info': file_info,
                'output_file': output_file,
                'settings_used': conversion_settings,
                'audio_type': audio_type.value
            }
            
            return True, f"Converted {audio_type.value}: {file_path}", conversion_info
                
        except Exception as e:
            return False, f"Error converting {file_path}: {str(e)}", {}
    
    def _apply_optimizations(self, audio: AudioSegment, settings: Dict[str, Any]) -> AudioSegment:
        """Apply optimizations to audio segment."""
        # Sample rate conversion
        if settings.get('sample_rate') and audio.frame_rate != settings['sample_rate']:
            audio = audio.set_frame_rate(settings['sample_rate'])
        
        # Channel conversion
        if settings.get('channels') and audio.channels != settings['channels']:
            if settings['channels'] == 1:
                audio = audio.set_channels(1)
            elif settings['channels'] == 2:
                audio = audio.set_channels(2)
        
        # Normalize audio if needed
        if self.settings.get('normalize_audio', False):
            audio = audio.normalize()
        
        return audio
    
    def _get_export_params(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Get export parameters for ogg format."""
        params = {}
        
        # Quality setting (0-10, higher is better)
        quality = settings.get('quality', 6)
        params['bitrate'] = self._quality_to_bitrate(quality)
        
        # Additional parameters
        if settings.get('sample_rate'):
            params['parameters'] = [f"-ar", str(settings['sample_rate'])]
        
        return params
    
    def _quality_to_bitrate(self, quality: int) -> str:
        """Convert quality setting to bitrate string."""
        # Quality 0-10 to bitrate mapping
        bitrate_map = {
            0: "32k", 1: "48k", 2: "64k", 3: "80k", 4: "96k",
            5: "112k", 6: "128k", 7: "160k", 8: "192k", 9: "256k", 10: "320k"
        }
        return bitrate_map.get(quality, "128k")
    
    def _generate_output_path(self, input_file: str, audio_type: AudioType) -> str:
        """Generate output path - always replace the original file like Blockbench filter."""
        input_path = Path(input_file)
        base_name = input_path.stem
        
        # Always place the output file exactly where the original was, replacing it
        # Just like the Blockbench filter: resultName = file.substr(0, file.lastIndexOf(".")) + ".json"
        output_file = str(input_path.parent / f"{base_name}{self.processor.output_format}")
        
        logger.debug(f"Output path: {input_file} -> {output_file}")
        return output_file
    
    def _should_skip_conversion(self, input_file: str, output_file: str, file_info: Dict[str, Any]) -> bool:
        """Determine if conversion should be skipped."""
        # Skip conversion if input file is already WAV or OGG (acceptable formats)
        input_ext = Path(input_file).suffix.lower()
        if input_ext in ['.wav', '.ogg']:
            return True
        
        if not os.path.exists(output_file):
            return False
        
        # Check file timestamps
        input_mtime = os.path.getmtime(input_file)
        output_mtime = os.path.getmtime(output_file)
        
        if output_mtime > input_mtime:
            return True
        
        # Check file hashes if available
        if file_info.get('hash') and self.settings.get('calculate_hashes', True):
            # This would require storing hash information, simplified for now
            pass
        
        return False

def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments."""
    try:
        if len(sys.argv) > 1:
            return json.loads(sys.argv[1])
        else:
            logger.warning("No settings provided, using defaults")
            return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse settings: {e}. Using defaults.")
        return {}

def get_regolith_environment() -> Dict[str, str]:
    """Get Regolith environment variables for external file access if needed."""
    return {
        'ROOT_DIR': os.environ.get('ROOT_DIR', ''),
        'FILTER_DIR': os.environ.get('FILTER_DIR', ''),
        'WORKING_DIR': os.getcwd()
    }

def get_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""

def get_cache_file_path() -> str:
    """Get the path to the cache file."""
    cache_dir = ".regolith"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "audio_converter_cache.json")

def load_cache() -> Dict[str, str]:
    """Load the conversion cache."""
    cache_file = get_cache_file_path()
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return {}

def save_cache(cache: Dict[str, str]) -> None:
    """Save the conversion cache."""
    cache_file = get_cache_file_path()
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def is_file_unchanged(file_path: str, expected_hash: str) -> bool:
    """Check if a file has changed by comparing its hash."""
    if not os.path.exists(file_path):
        return False
    
    current_hash = get_file_hash(file_path)
    return current_hash == expected_hash

def main():
    """Main execution function."""
    try:
        logger.info("Audio Converter Filter - Starting")
        
        # Parse settings
        settings = parse_settings()
        
        # Get Regolith environment info
        env_info = get_regolith_environment()
        
        # Get configuration
        log_level = settings.get('log_level', 'INFO')
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        logger.info("Starting audio conversion process")
        
        # Initialize converter
        converter = AudioConverter(settings)
        
        # Load conversion cache
        enable_cache = settings.get('enable_cache', True)
        if enable_cache:
            cache = load_cache()
        else:
            cache = {}
        
        # Blockbench-style file discovery
        source_dirs = settings.get('source_dirs')
        
        if not source_dirs:
            logger.info("Discovering audio files...")
            audio_files = find_audio_files()
            logger.info(f"Found {len(audio_files)} audio files")
            
            if not audio_files:
                logger.warning("No audio files found to convert")
                return
            
            # Convert the file list to a simple categorization
            categorized_files = {AudioType.UNKNOWN: audio_files}
        else:
            logger.info(f"Using specified directories: {source_dirs}")
            categorized_files = converter.discoverer.discover_audio_files(source_dirs)
        
        if not any(files for files in categorized_files.values()):
            logger.warning("No audio files found to convert")
            return
        
        # Process files by type
        total_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'cached': 0,
            'by_type': {}
        }
        
        # Process each audio type
        for audio_type, files in categorized_files.items():
            if not files:
                continue
            
            logger.info(f"Processing {audio_type.value} files: {len(files)}")
            total_stats['total'] += len(files)
            total_stats['by_type'][audio_type.value] = {
                'total': len(files),
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'cached': 0
            }
            
            # Convert files of this type
            for file_path in files:
                # Check cache first
                if file_path in cache:
                    if is_file_unchanged(file_path, cache[file_path]):
                        logger.info(f"Skipped (unchanged): {file_path}")
                        total_stats['cached'] += 1
                        total_stats['by_type'][audio_type.value]['cached'] += 1
                        continue
                
                try:
                    success, message, conversion_info = converter.convert_audio_file_advanced(file_path, audio_type)
                    
                    if success:
                        if conversion_info.get('skipped'):
                            total_stats['skipped'] += 1
                            total_stats['by_type'][audio_type.value]['skipped'] += 1
                        else:
                            total_stats['successful'] += 1
                            total_stats['by_type'][audio_type.value]['successful'] += 1
                            logger.info(message)
                            
                            # Update cache with new hash
                            if conversion_info.get('input_info', {}).get('hash'):
                                cache[file_path] = conversion_info['input_info']['hash']
                    else:
                        total_stats['failed'] += 1
                        total_stats['by_type'][audio_type.value]['failed'] += 1
                        logger.error(message)
                        
                except Exception as e:
                    total_stats['failed'] += 1
                    total_stats['by_type'][audio_type.value]['failed'] += 1
                    logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Save updated cache
        if enable_cache:
            save_cache(cache)
        
        # Report results
        logger.info("=" * 50)
        logger.info("CONVERSION COMPLETED")
        logger.info("=" * 50)
        logger.info(f"Total files: {total_stats['total']}")
        logger.info(f"Converted: {total_stats['successful']}")
        logger.info(f"Failed: {total_stats['failed']}")
        logger.info(f"Skipped: {total_stats['skipped']}")
        logger.info(f"Cached (unchanged): {total_stats['cached']}")
        logger.info("Note: WAV and OGG files are considered acceptable formats and are skipped")
        
        # Report by type
        for audio_type, stats in total_stats['by_type'].items():
            if stats['total'] > 0:
                logger.info(f"  {audio_type}: {stats['successful']} converted, {stats['cached']} cached")
        
        if total_stats['failed'] > 0:
            logger.warning(f"{total_stats['failed']} files failed to convert")
            sys.exit(1)
        else:
            logger.info("All conversions completed successfully")
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 