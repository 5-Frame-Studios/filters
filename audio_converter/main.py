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
        logger.debug("Initializing AudioProcessor...")
        logger.debug(f"Settings received: {json.dumps(settings, indent=2)}")
        
        self.settings = settings
        self.supported_formats = settings.get('supported_formats', ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff'])
        self.output_format = settings.get('output_format', '.ogg')
        self.quality = settings.get('quality', 6)
        self.delete_originals = settings.get('delete_originals', False)
        self.organize_by_type = settings.get('organize_by_type', True)
        self.max_workers = settings.get('max_workers', 4)
        self.timeout = settings.get('timeout', 300)
        
        # Advanced settings
        self.validate_files = settings.get('validate_files', True)
        self.calculate_hashes = settings.get('calculate_hashes', True)
        self.backup_originals = settings.get('backup_originals', False)
        self.optimize_for_minecraft = settings.get('optimize_for_minecraft', True)
        
        logger.debug(f"AudioProcessor settings:")
        logger.debug(f"  supported_formats: {self.supported_formats}")
        logger.debug(f"  output_format: {self.output_format}")
        logger.debug(f"  quality: {self.quality}")
        logger.debug(f"  delete_originals: {self.delete_originals}")
        logger.debug(f"  organize_by_type: {self.organize_by_type}")
        logger.debug(f"  max_workers: {self.max_workers}")
        logger.debug(f"  timeout: {self.timeout}")
        logger.debug(f"  validate_files: {self.validate_files}")
        logger.debug(f"  calculate_hashes: {self.calculate_hashes}")
        logger.debug(f"  backup_originals: {self.backup_originals}")
        logger.debug(f"  optimize_for_minecraft: {self.optimize_for_minecraft}")
        
        # Validate pydub availability
        self._validate_pydub()
        logger.debug("AudioProcessor initialization completed")
    
    def _validate_pydub(self) -> None:
        """Validate that pydub is available."""
        logger.debug("Validating pydub availability...")
        if not PYDUB_AVAILABLE:
            logger.error("pydub is not available")
            logger.error("Please install pydub: pip install pydub")
            sys.exit(1)
        logger.debug("pydub is available and ready to use")

def find_audio_files() -> List[str]:
    """
    Find audio files using glob patterns like the Blockbench filter.
    
    Returns:
        List of discovered audio file paths
    """
    audio_files = []
    supported_formats = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff']
    
    logger.debug("Using Blockbench-style file discovery with glob patterns")
    
    # Use glob patterns to find audio files directly, just like the Blockbench filter
    for format_ext in supported_formats:
        # Look for files in RP/sounds/**/*.ext
        rp_pattern = f"RP/sounds/**/*{format_ext}"
        logger.debug(f"Searching for files matching: {rp_pattern}")
        rp_files = glob.glob(rp_pattern, recursive=True)
        audio_files.extend(rp_files)
        if rp_files:
            logger.debug(f"Found {len(rp_files)} {format_ext} files in RP/sounds")
        
        # Look for files in BP/sounds/**/*.ext
        bp_pattern = f"BP/sounds/**/*{format_ext}"
        logger.debug(f"Searching for files matching: {bp_pattern}")
        bp_files = glob.glob(bp_pattern, recursive=True)
        audio_files.extend(bp_files)
        if bp_files:
            logger.debug(f"Found {len(bp_files)} {format_ext} files in BP/sounds")
    
    # Remove duplicates and normalize paths
    audio_files = list(set(audio_files))
    audio_files = [os.path.normpath(f) for f in audio_files]
    
    logger.info(f"Total audio files found: {len(audio_files)}")
    for file_path in audio_files:
        logger.debug(f"Found audio file: {file_path}")
    
    return audio_files

class AudioFileDiscoverer:
    """Advanced file discovery with pattern matching and categorization."""
    
    def __init__(self, supported_formats: List[str]):
        logger.debug("Initializing AudioFileDiscoverer...")
        logger.debug(f"Supported formats: {supported_formats}")
        
        self.supported_formats = supported_formats
        self.audio_patterns = self._build_patterns()
        
        logger.debug("Audio patterns built:")
        for audio_type, patterns in self.audio_patterns.items():
            logger.debug(f"  {audio_type.value}: {patterns}")
        logger.debug("AudioFileDiscoverer initialization completed")
    
    def _build_patterns(self) -> Dict[str, List[str]]:
        """Build pattern matching rules for different audio types."""
        logger.debug("Building audio type patterns...")
        
        patterns = {
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
        
        logger.debug(f"Built {len(patterns)} audio type patterns")
        return patterns
    
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
                logger.debug(f"Searching for files matching: {pattern}")
                files = glob.glob(pattern, recursive=True)
                
                if files:
                    logger.debug(f"Found {len(files)} {format_ext} files in {source_dir}")
                    # Categorize files by type
                    for file_path in files:
                        audio_type = self._categorize_file(file_path, source_dir)
                        categorized_files[audio_type].append(file_path)
                        logger.debug(f"Categorized {file_path} as {audio_type.value}")
        
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
        logger.debug(f"Categorizing file: {file_path}")
        logger.debug(f"Source directory: {source_dir}")
        
        # Get relative path from source directory
        try:
            relative_path = os.path.relpath(file_path, source_dir)
            logger.debug(f"Relative path: {relative_path}")
        except ValueError:
            # Handle case where file_path is not relative to source_dir
            relative_path = file_path
            logger.debug(f"Could not get relative path, using full path: {relative_path}")
        
        relative_path_lower = relative_path.lower()
        logger.debug(f"Lowercase relative path: {relative_path_lower}")
        
        # Check each audio type pattern
        for audio_type, patterns in self.audio_patterns.items():
            logger.debug(f"Checking patterns for {audio_type.value}: {patterns}")
            for pattern in patterns:
                # Convert pattern to checkable format
                pattern_lower = pattern.lower()
                logger.debug(f"Checking pattern: {pattern_lower}")
                
                # Check if the file path matches this pattern
                if self._matches_pattern(relative_path_lower, pattern_lower):
                    logger.debug(f"File {file_path} matches pattern {pattern_lower} -> categorized as {audio_type.value}")
                    return audio_type
                else:
                    logger.debug(f"File {file_path} does not match pattern {pattern_lower}")
        
        # If no pattern matches, categorize as unknown
        logger.debug(f"File {file_path} did not match any patterns -> categorized as unknown")
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
        logger.debug(f"Pattern matching: '{file_path}' against '{pattern}'")
        
        # Handle glob patterns
        if '**' in pattern:
            # Convert glob pattern to simple string matching
            pattern_parts = pattern.split('**')
            logger.debug(f"Glob pattern parts: {pattern_parts}")
            
            for part in pattern_parts:
                if part and part not in file_path:
                    logger.debug(f"Part '{part}' not found in '{file_path}' -> no match")
                    return False
            
            logger.debug(f"All pattern parts found in '{file_path}' -> match")
            return True
        elif '*' in pattern:
            # Handle simple wildcards
            import fnmatch
            result = fnmatch.fnmatch(file_path, pattern)
            logger.debug(f"Wildcard pattern '{pattern}' -> {result}")
            return result
        else:
            # Direct string matching
            result = pattern in file_path
            logger.debug(f"Direct string matching '{pattern}' in '{file_path}' -> {result}")
            return result

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
        logger.debug(f"Starting validation of: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.debug(f"File does not exist: {file_path}")
                return False, None
            
            logger.debug(f"File exists, checking if it's a file (not directory)")
            if not os.path.isfile(file_path):
                logger.debug(f"Path is not a file: {file_path}")
                return False, None
            
            # Check file size
            file_size = os.path.getsize(file_path)
            logger.debug(f"File size: {file_size} bytes")
            
            if file_size == 0:
                logger.debug(f"File is empty: {file_path}")
                return False, None
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            logger.debug(f"File extension: {file_ext}")
            
            # Load audio file with pydub
            logger.debug(f"Attempting to load audio file with pydub: {file_path}")
            audio = AudioSegment.from_file(file_path)
            logger.debug(f"Audio loaded successfully with pydub")
            
            # Extract audio properties
            duration = len(audio) / 1000.0  # Convert to seconds
            bitrate = audio.frame_rate * audio.sample_width * audio.channels * 8
            sample_rate = audio.frame_rate
            channels = audio.channels
            
            logger.debug(f"Audio properties - Duration: {duration}s, Sample Rate: {sample_rate}Hz, Channels: {channels}, Bitrate: {bitrate}bps")
            
            # Calculate hash if requested
            file_hash = None
            if self.calculate_hashes:
                logger.debug(f"Calculating file hash for: {file_path}")
                file_hash = self._calculate_file_hash(file_path)
                logger.debug(f"File hash: {file_hash}")
            
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
            
            logger.debug(f"File validation successful. File info: {json.dumps(file_info, indent=2, default=str)}")
            return True, file_info
            
        except Exception as e:
            logger.debug(f"Validation failed for {file_path}: {e}")
            logger.debug(f"Exception type: {type(e).__name__}")
            import traceback
            logger.debug(f"Validation error traceback:\n{traceback.format_exc()}")
            return False, None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        logger.debug(f"Calculating SHA-256 hash for: {file_path}")
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            result_hash = hash_sha256.hexdigest()
            logger.debug(f"Hash calculation completed: {result_hash}")
            return result_hash
        except Exception as e:
            logger.debug(f"Hash calculation failed: {e}")
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
        logger.debug(f"Starting conversion of: {file_path}")
        logger.debug(f"Audio type: {audio_type.value}")
        
        try:
            # Validate file
            logger.debug(f"Validating file: {file_path}")
            is_valid, file_info = self.validator.validate_audio_file(file_path)
            logger.debug(f"Validation result: valid={is_valid}")
            
            if not is_valid:
                logger.debug(f"File validation failed for: {file_path}")
                return False, f"Invalid audio file: {file_path}", {}
            
            logger.debug(f"File info: {json.dumps(file_info, indent=2, default=str)}")
            
            # Detect audio type if not provided
            if audio_type == AudioType.UNKNOWN:
                logger.debug(f"Detecting audio type for: {file_path}")
                audio_type = self.detect_audio_type(file_path)
                logger.debug(f"Detected audio type: {audio_type.value}")
            
            # Get optimized settings
            logger.debug(f"Getting optimized settings for {audio_type.value}")
            conversion_settings = self.get_optimized_settings(audio_type, file_info)
            logger.debug(f"Conversion settings: {json.dumps(conversion_settings, indent=2)}")
            
            # Generate output path
            logger.debug(f"Generating output path for: {file_path}")
            output_file = self._generate_output_path(file_path, audio_type)
            logger.debug(f"Output file path: {output_file}")
            
            # Check if conversion is needed
            logger.debug(f"Checking if conversion is needed for: {file_path}")
            if self._should_skip_conversion(file_path, output_file, file_info):
                logger.debug(f"Skipping conversion - file is up-to-date: {file_path}")
                return True, f"Skipped (up-to-date): {file_path}", {'skipped': True}
            
            # Load audio with pydub
            logger.debug(f"Loading audio file with pydub: {file_path}")
            audio = AudioSegment.from_file(file_path)
            logger.debug(f"Audio loaded successfully. Duration: {len(audio)}ms, Channels: {audio.channels}, Sample Rate: {audio.frame_rate}")
            
            # Apply optimizations
            logger.debug(f"Applying optimizations to audio")
            audio = self._apply_optimizations(audio, conversion_settings)
            logger.debug(f"Optimizations applied. Final duration: {len(audio)}ms, Channels: {audio.channels}, Sample Rate: {audio.frame_rate}")
            
            # Export to ogg format
            logger.debug(f"Converting {audio_type.value}: {file_path} -> {output_file}")
            
            # Determine export parameters based on quality
            export_params = self._get_export_params(conversion_settings)
            logger.debug(f"Export parameters: {json.dumps(export_params, indent=2)}")
            
            logger.debug(f"Starting audio export...")
            audio.export(
                output_file,
                format="ogg",
                **export_params
            )
            logger.debug(f"Audio export completed: {output_file}")
            
            # Backup original if requested
            if self.settings.get('backup_originals', False):
                logger.debug(f"Creating backup of original file: {file_path}")
                self._backup_original(file_path)
            
            # Delete original if requested
            if self.settings.get('delete_originals', False):
                logger.debug(f"Deleting original file: {file_path}")
                os.remove(file_path)
                logger.debug(f"Deleted original: {file_path}")
            
            conversion_info = {
                'input_info': file_info,
                'output_file': output_file,
                'settings_used': conversion_settings,
                'audio_type': audio_type.value
            }
            logger.debug(f"Conversion completed successfully. Info: {json.dumps(conversion_info, indent=2, default=str)}")
            
            return True, f"Converted {audio_type.value}: {file_path}", conversion_info
                
        except Exception as e:
            logger.debug(f"Error during conversion of {file_path}: {str(e)}")
            logger.debug(f"Exception type: {type(e).__name__}")
            import traceback
            logger.debug(f"Conversion error traceback:\n{traceback.format_exc()}")
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
        """Generate output path with type-based organization."""
        input_path = Path(input_file)
        base_name = input_path.stem
        
        if self.settings.get('organize_by_type', True):
            # Organize by audio type
            output_dir = input_path.parent / audio_type.value
        else:
            # Keep same directory structure
            output_dir = input_path.parent
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return str(output_dir / f"{base_name}{self.processor.output_format}")
    
    def _should_skip_conversion(self, input_file: str, output_file: str, file_info: Dict[str, Any]) -> bool:
        """Determine if conversion should be skipped."""
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
    
    def _backup_original(self, file_path: str) -> None:
        """Create backup of original file."""
        try:
            backup_dir = Path(file_path).parent / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backed up: {file_path} -> {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to backup {file_path}: {e}")

def parse_settings() -> Dict[str, Any]:
    """Parse settings from command line arguments."""
    logger.debug("Parsing settings from command line arguments...")
    logger.debug(f"sys.argv: {sys.argv}")
    logger.debug(f"Number of arguments: {len(sys.argv)}")
    
    try:
        if len(sys.argv) > 1:
            logger.debug(f"Parsing argument: {sys.argv[1]}")
            settings = json.loads(sys.argv[1])
            logger.debug(f"Successfully parsed settings: {json.dumps(settings, indent=2)}")
            return settings
        else:
            logger.warning("No valid settings provided. Using defaults.")
            logger.debug("Returning empty settings dictionary")
            return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse settings: {e}. Using defaults.")
        logger.debug(f"Exception type: {type(e).__name__}")
        logger.debug(f"Exception details: {str(e)}")
        return {}

def get_regolith_environment() -> Dict[str, str]:
    """Get Regolith environment variables for external file access if needed."""
    return {
        'ROOT_DIR': os.environ.get('ROOT_DIR', ''),
        'FILTER_DIR': os.environ.get('FILTER_DIR', ''),
        'WORKING_DIR': os.getcwd()
    }

def main():
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info("AUDIO CONVERTER FILTER - STARTING")
        logger.info("=" * 60)
        
        # Parse settings
        logger.debug("Parsing settings from command line arguments...")
        settings = parse_settings()
        logger.debug(f"Parsed settings: {json.dumps(settings, indent=2)}")
        
        # Get Regolith environment info
        logger.debug("Getting Regolith environment information...")
        env_info = get_regolith_environment()
        logger.debug(f"Environment info: {json.dumps(env_info, indent=2)}")
        logger.debug(f"Working directory: {env_info['WORKING_DIR']}")
        if env_info['ROOT_DIR']:
            logger.debug(f"Project root: {env_info['ROOT_DIR']}")
        
        # Get configuration
        logger.debug("Extracting configuration from settings...")
        log_level = settings.get('log_level', 'DEBUG')  # Changed from 'INFO' to 'DEBUG'
        logger.debug(f"Log level from settings: {log_level}")
        
        # Set log level
        logger.debug(f"Setting log level to: {log_level.upper()}")
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        logger.info("Starting advanced audio conversion process with pydub")
        logger.info("Working in Regolith temporary directory - changes will be applied after successful run")
        
        # Initialize converter
        logger.debug("Initializing AudioConverter...")
        converter = AudioConverter(settings)
        logger.debug("AudioConverter initialized successfully")
        
        # Intelligent directory detection
        logger.debug("Starting Blockbench-style file discovery...")
        source_dirs = settings.get('source_dirs')
        logger.debug(f"Source directories from settings: {source_dirs}")
        
        if not source_dirs:
            logger.info("No source directories specified, using Blockbench-style discovery")
            logger.debug("Calling find_audio_files() for direct file discovery...")
            audio_files = find_audio_files()
            logger.info(f"Discovered {len(audio_files)} audio files")
            
            if not audio_files:
                logger.warning("No audio files found to convert")
                logger.debug("Exiting due to no files found")
                return
            
            # Convert the file list to a simple categorization
            categorized_files = {AudioType.UNKNOWN: audio_files}
        else:
            logger.info(f"Using specified source directories: {source_dirs}")
            logger.debug(f"Calling discoverer.discover_audio_files with: {source_dirs}")
            categorized_files = converter.discoverer.discover_audio_files(source_dirs)
            logger.debug(f"Discovery completed. Categorized files: {json.dumps({k.value: len(v) for k, v in categorized_files.items()}, indent=2)}")
        
        if not any(files for files in categorized_files.values()):
            logger.warning("No audio files found to convert")
            logger.debug("Exiting due to no files found")
            return
        
        # Process files by type
        logger.debug("Initializing processing statistics...")
        total_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'by_type': {}
        }
        
        # Process each audio type
        logger.debug("Starting processing by audio type...")
        for audio_type, files in categorized_files.items():
            if not files:
                logger.debug(f"Skipping {audio_type.value} - no files")
                continue
            
            logger.info(f"Processing {audio_type.value} files: {len(files)}")
            logger.debug(f"Files to process for {audio_type.value}: {files}")
            total_stats['total'] += len(files)
            total_stats['by_type'][audio_type.value] = {
                'total': len(files),
                'successful': 0,
                'failed': 0,
                'skipped': 0
            }
            
            # Convert files of this type - use simple processing like Blockbench filter
            logger.debug(f"Processing {len(files)} files for {audio_type.value}")
            for file_path in files:
                logger.debug(f"Processing file: {file_path}")
                try:
                    success, message, conversion_info = converter.convert_audio_file_advanced(file_path, audio_type)
                    logger.debug(f"Conversion result for {file_path}: success={success}, message='{message}'")
                    
                    if success:
                        if conversion_info.get('skipped'):
                            total_stats['skipped'] += 1
                            total_stats['by_type'][audio_type.value]['skipped'] += 1
                            logger.debug(f"File skipped: {file_path}")
                            logger.debug(message)
                        else:
                            total_stats['successful'] += 1
                            total_stats['by_type'][audio_type.value]['successful'] += 1
                            logger.debug(f"File converted successfully: {file_path}")
                            logger.info(message)
                    else:
                        total_stats['failed'] += 1
                        total_stats['by_type'][audio_type.value]['failed'] += 1
                        logger.debug(f"File conversion failed: {file_path}")
                        logger.error(message)
                        
                except Exception as e:
                    total_stats['failed'] += 1
                    total_stats['by_type'][audio_type.value]['failed'] += 1
                    logger.debug(f"Unexpected error processing {file_path}: {str(e)}")
                    logger.error(f"Unexpected error processing {file_path}: {str(e)}")
        
        # Report detailed results
        logger.info("=" * 60)
        logger.info("CONVERSION COMPLETED - FINAL RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total files: {total_stats['total']}")
        logger.info(f"Successfully converted: {total_stats['successful']}")
        logger.info(f"Failed: {total_stats['failed']}")
        logger.info(f"Skipped: {total_stats['skipped']}")
        
        # Report by type
        logger.debug("Detailed results by audio type:")
        for audio_type, stats in total_stats['by_type'].items():
            if stats['total'] > 0:
                logger.info(f"  {audio_type}: {stats['successful']}/{stats['total']} successful")
                logger.debug(f"    {audio_type} details: {stats}")
        
        if total_stats['failed'] > 0:
            logger.warning(f"{total_stats['failed']} files failed to convert")
            logger.debug("Exiting with error code due to failed conversions")
            sys.exit(1)
        else:
            logger.info("All conversions completed successfully")
            logger.info("Changes will be applied to project files after successful filter run")
            logger.debug("Exiting successfully")
            
    except Exception as e:
        logger.error(f"Fatal error during advanced audio conversion: {e}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.debug(f"Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 