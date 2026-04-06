"""End-to-end orchestration pipeline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from .classify import classify_segments
from .config import AppConfig
from .export import export_all_segments_csv, export_events_csv, export_review_excel, to_dataframes
from .preprocess import preprocess_audio
from .segment import build_analysis_segments
from .transcribe import save_transcript_segments_json, transcribe_audio

logger = logging.getLogger(__name__)


def run_pipeline(audio_path: str, case_id: str, output_dir: str, config: AppConfig) -> Dict[str, Path]:
    out_dir = config.ensure_output_dir(output_dir)
    source_audio = Path(audio_path)

    normalized_audio = out_dir / config.normalized_audio_name
    transcript_json = out_dir / config.transcript_json_name
    events_csv = out_dir / config.events_csv_name
    events_xlsx = out_dir / config.events_xlsx_name
    all_segments_csv = out_dir / config.all_segments_csv_name

    normalized = preprocess_audio(source_audio, normalized_audio, config.audio)
    transcript_segments = transcribe_audio(normalized, config.whisper)
    save_transcript_segments_json(transcript_segments, transcript_json)

    analysis_segments = build_analysis_segments(transcript_segments)
    classified = classify_segments(analysis_segments, config.classifier, config.phase)

    events_df, all_df = to_dataframes(classified, case_id=case_id, source_audio_file=source_audio.name)

    export_events_csv(events_df, events_csv)
    export_review_excel(events_df, events_xlsx)
    if config.keep_all_segments_export:
        export_all_segments_csv(all_df, all_segments_csv)

    logger.info(
        "Pipeline complete. Flagged events: %s / Total segments: %s",
        len(events_df),
        len(all_df),
    )
    return {
        "normalized_audio": normalized_audio,
        "transcript_segments_json": transcript_json,
        "events_csv": events_csv,
        "events_review_xlsx": events_xlsx,
        "all_segments_csv": all_segments_csv if config.keep_all_segments_export else Path(),
    }
