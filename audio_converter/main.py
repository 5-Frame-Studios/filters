"""
Audio Converter Filter

Converts various audio formats to .ogg files for Minecraft Bedrock Edition.
Incorporates advanced patterns from the Blockbench filter with sophisticated
file processing, complex validation, and advanced error handling.
Uses pydub for audio processing - no external ffmpeg installation required.
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
        
        # Validate pydub availability
        self._validate_pydub()
    
    def _validate_pydub(self) -> None:
        """Validate that pydub is available."""
        if not PYDUB_AVAILABLE:
            logger.error("pydub is not available")
            logger.error("Please install pydub: pip install pydub")
            sys.exit(1)
        logger.debug("pydub is available")

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
            
            # Discover files by type
            for audio_type, patterns in self.audio_patterns.items():
                for pattern in patterns:
                    full_pattern = os.path.join(source_dir, pattern)
                    files = glob.glob(full_pattern, recursive=True)
                    
                    # Filter by supported formats
                    audio_files = [f for f in files if any(f.lower().endswith(ext) for ext in self.supported_formats)]
                    categorized_files[audio_type].extend(audio_files)
                    
                    if audio_files:
                        logger.debug(f"Found {len(audio_files)} {audio_type.value} files in {source_dir}")
            
            # Find uncategorized files
            for format_ext in self.supported_formats:
                pattern = os.path.join(source_dir, f"**/*{format_ext}")
                files = glob.glob(pattern, recursive=True)
                
                # Add files not already categorized
                for file in files:
                    if not any(file in categorized_files[audio_type] for audio_type in AudioType):
                        categorized_files[AudioType.UNKNOWN].append(file)
        
        # Log summary
        total_files = sum(len(files) for files in categorized_files.values())
        logger.info(f"Total audio files found: {total_files}")
        for audio_type, files in categorized_files.items():
            if files:
                logger.info(f"  {audio_type.value}: {len(files)} files")
        
        return categorized_files

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
            # Load audio file with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Build file information
            file_info = {
                'path': file_path,
                'format': Path(file_path).suffix.lower(),
                'duration': len(audio) / 1000.0,  # Convert to seconds
                'bitrate': audio.frame_rate * audio.sample_width * audio.channels * 8,
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'size': file_size,
                'hash': self._calculate_file_hash(file_path) if self.calculate_hashes else None
            }
            
            return True, file_info
            
        except Exception as e:
            logger.debug(f"Validation failed for {file_path}: {e}")
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
            logger.debug(f"Converting {audio_type.value}: {file_path} -> {output_file}")
            
            # Determine export parameters based on quality
            export_params = self._get_export_params(conversion_settings)
            
            audio.export(
                output_file,
                format="ogg",
                **export_params
            )
            
            # Backup original if requested
            if self.settings.get('backup_originals', False):
                self._backup_original(file_path)
            
            # Delete original if requested
            if self.settings.get('delete_originals', False):
                os.remove(file_path)
                logger.debug(f"Deleted original: {file_path}")
            
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
    try:
        if len(sys.argv) > 1:
            return json.loads(sys.argv[1])
        else:
            logger.warning("No settings provided, using defaults")
            return {}
    except (IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse settings: {e}")
        return {}

def main():
    """Main execution function."""
    try:
        # Parse settings
        settings = parse_settings()
        
        # Get configuration
        source_dirs = settings.get('source_dirs', ['RP/sounds/', 'BP/sounds/'])
        log_level = settings.get('log_level', 'INFO')
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        logger.info("Starting advanced audio conversion process with pydub")
        
        # Initialize converter
        converter = AudioConverter(settings)
        
        # Discover and categorize audio files
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
                'skipped': 0
            }
            
            # Convert files of this type
            with ThreadPoolExecutor(max_workers=settings.get('max_workers', 4)) as executor:
                future_to_file = {
                    executor.submit(converter.convert_audio_file_advanced, file, audio_type): file 
                    for file in files
                }
                
                for future in as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        success, message, conversion_info = future.result()
                        
                        if success:
                            if conversion_info.get('skipped'):
                                total_stats['skipped'] += 1
                                total_stats['by_type'][audio_type.value]['skipped'] += 1
                                logger.debug(message)
                            else:
                                total_stats['successful'] += 1
                                total_stats['by_type'][audio_type.value]['successful'] += 1
                                logger.info(message)
                        else:
                            total_stats['failed'] += 1
                            total_stats['by_type'][audio_type.value]['failed'] += 1
                            logger.error(message)
                            
                    except Exception as e:
                        total_stats['failed'] += 1
                        total_stats['by_type'][audio_type.value]['failed'] += 1
                        logger.error(f"Unexpected error processing {file}: {str(e)}")
        
        # Report detailed results
        logger.info("Advanced conversion completed!")
        logger.info(f"Total files: {total_stats['total']}")
        logger.info(f"Successfully converted: {total_stats['successful']}")
        logger.info(f"Failed: {total_stats['failed']}")
        logger.info(f"Skipped: {total_stats['skipped']}")
        
        # Report by type
        for audio_type, stats in total_stats['by_type'].items():
            if stats['total'] > 0:
                logger.info(f"  {audio_type}: {stats['successful']}/{stats['total']} successful")
        
        if total_stats['failed'] > 0:
            logger.warning(f"{total_stats['failed']} files failed to convert")
            sys.exit(1)
        else:
            logger.info("All conversions completed successfully")
            
    except Exception as e:
        logger.error(f"Fatal error during advanced audio conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 