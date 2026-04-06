"""Transcription utilities using faster-whisper."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

from faster_whisper import WhisperModel

from .config import WhisperConfig

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: str | Path, config: WhisperConfig) -> List[Dict]:
    """Transcribe audio into timestamped segments."""
    logger.info("Loading faster-whisper model: %s", config.model_size)
    model = WhisperModel(config.model_size, device=config.device, compute_type=config.compute_type)

    logger.info("Running transcription on: %s", audio_path)
    segments, _ = model.transcribe(
        str(audio_path),
        language=config.language,
        beam_size=config.beam_size,
        vad_filter=config.vad_filter,
    )

    rows: List[Dict] = []
    for seg in segments:
        text = (seg.text or "").strip()
        if not text:
            continue
        rows.append(
            {
                "start_time": round(float(seg.start), 2),
                "end_time": round(float(seg.end), 2),
                "duration_sec": round(float(seg.end - seg.start), 2),
                "transcript": text,
            }
        )

    logger.info("Transcription produced %s segments", len(rows))
    return rows


def save_transcript_segments_json(segments: List[Dict], output_path: str | Path) -> Path:
    """Save transcript segments as inspectable JSON."""
    path = Path(output_path)
    path.write_text(json.dumps(segments, indent=2), encoding="utf-8")
    logger.info("Saved transcript artifact: %s", path)
    return path
