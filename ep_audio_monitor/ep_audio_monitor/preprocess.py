"""Audio preprocessing utilities."""

from __future__ import annotations

import logging
from pathlib import Path

from pydub import AudioSegment

from .config import AudioConfig

logger = logging.getLogger(__name__)


def preprocess_audio(input_audio_path: str | Path, output_audio_path: str | Path, config: AudioConfig) -> Path:
    """Convert input audio to mono WAV at a fixed sample rate.

    This keeps timing aligned by avoiding aggressive transforms.
    """
    input_path = Path(input_audio_path)
    output_path = Path(output_audio_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input audio not found: {input_path}")

    logger.info("Loading audio file: %s", input_path)
    audio = AudioSegment.from_file(input_path)

    logger.info(
        "Normalizing audio format (channels=%s, sample_rate=%s)",
        config.target_channels,
        config.target_sample_rate,
    )
    normalized = audio.set_channels(config.target_channels).set_frame_rate(config.target_sample_rate)
    normalized.export(output_path, format=config.target_format)

    logger.info("Saved normalized audio: %s", output_path)
    return output_path
