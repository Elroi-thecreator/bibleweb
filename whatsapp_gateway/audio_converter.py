"""
Audio Format Transcoding & Compatibility Utilities for WhatsApp Gateway.

Ensures audio synthesized via Edge-TTS (MP3) or gTTS (MP3) is reliably converted
to WhatsApp-compliant ISO MP4 containers (AAC audio, .m4a) with faststart atom,
or OGG Opus for voice notes, avoiding ExoPlayer decoder crashes on mobile devices.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)


def get_ffmpeg_binary() -> Optional[str]:
    """
    Locates an available ffmpeg executable.
    Checks system PATH first, then falls back to bundled imageio-ffmpeg.
    """
    # 1. System PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # 2. Bundled imageio-ffmpeg (cross-platform static binary)
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            return exe
    except Exception as exc:
        logger.debug("imageio_ffmpeg lookup failed: %s", exc)

    return None


def is_mp4_container(data: bytes) -> bool:
    """Checks whether the byte buffer starts with an ISO/IEC Base Media File Format (MP4/M4A) box."""
    if len(data) < 12:
        return False
    # Standard MP4 box header: 4-byte length + 'ftyp'
    return data[4:8] == b"ftyp"


def is_ogg_container(data: bytes) -> bool:
    """Checks whether the byte buffer starts with an Ogg container header ('OggS')."""
    return len(data) >= 4 and data[:4] == b"OggS"


def convert_audio_to_m4a(
    input_bytes: bytes,
    bitrate: str = "64k",
    ffmpeg_bin: Optional[str] = None,
    timeout_sec: float = 20.0,
) -> bytes:
    """
    Converts raw audio bytes (MP3, WAV, etc.) to a WhatsApp-compliant M4A container
    encoded with AAC-LC audio and +faststart flag for instant mobile streaming.

    Raises:
        RuntimeError if ffmpeg is missing or transcoding fails.
    """
    if is_mp4_container(input_bytes):
        logger.debug("Audio buffer is already an MP4/M4A container, skipping conversion.")
        return input_bytes

    ffmpeg_exe = ffmpeg_bin or get_ffmpeg_binary()
    if not ffmpeg_exe:
        raise RuntimeError("ffmpeg binary not found on system PATH or via imageio-ffmpeg.")

    # Write input bytes to temporary file
    temp_dir = tempfile.gettempdir()
    in_fd, in_path = tempfile.mkstemp(suffix=".tmp", dir=temp_dir)
    out_path = in_path + ".m4a"

    try:
        with os.fdopen(in_fd, "wb") as f_in:
            f_in.write(input_bytes)

        cmd = [
            ffmpeg_exe,
            "-y",
            "-loglevel", "error",
            "-i", in_path,
            "-c:a", "aac",
            "-b:a", bitrate,
            "-movflags", "+faststart",
            out_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout_sec,
            check=False,
        )

        if result.returncode != 0:
            err_msg = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"FFmpeg conversion failed (exit {result.returncode}): {err_msg}")

        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise RuntimeError("FFmpeg generated an empty M4A output file.")

        with open(out_path, "rb") as f_out:
            m4a_data = f_out.read()

        logger.info(
            "Transcoded audio to M4A (in: %d bytes -> out: %d bytes, aac %s)",
            len(input_bytes),
            len(m4a_data),
            bitrate,
        )
        return m4a_data

    finally:
        for path in (in_path, out_path):
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError:
                pass


def prepare_whatsapp_audio_payload(
    file_bytes: bytes,
    preferred_name: Optional[str] = None,
    ptt: bool = False,
) -> Tuple[bytes, str, str, str]:
    """
    Prepares audio bytes and metadata for safe dispatch to WA-AKG.

    Returns:
        (output_bytes, file_name, media_type, mime_type)
        - If converted to M4A: (m4a_bytes, "name.m4a", "audio", "audio/mp4")
        - If conversion fails and input is MP3: (file_bytes, "name.mp3", "document", "audio/mpeg")
    """
    base_name = Path(preferred_name or "audio").stem
    ffmpeg_exe = get_ffmpeg_binary()

    if ffmpeg_exe:
        try:
            m4a_bytes = convert_audio_to_m4a(file_bytes, ffmpeg_bin=ffmpeg_exe)
            return m4a_bytes, f"{base_name}.m4a", "audio", "audio/mp4"
        except Exception as exc:
            logger.warning("Failed to transcode audio to M4A (%s). Falling back to document.", exc)

    # Fallback when ffmpeg is unavailable or fails:
    # Send as document with audio/mpeg so WA-AKG doesn't force audio/mp4 on MP3
    if not is_mp4_container(file_bytes):
        logger.info("Dispatching MP3 as document to preserve audio/mpeg MIME type without ffmpeg.")
        return file_bytes, f"{base_name}.mp3", "document", "audio/mpeg"

    return file_bytes, f"{base_name}.m4a", "audio", "audio/mp4"
