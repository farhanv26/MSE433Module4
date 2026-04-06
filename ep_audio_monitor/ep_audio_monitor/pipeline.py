"""Linear pipeline: preprocess → transcribe → segment → classify → export."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from .classify import classify_segments
from .config import AppConfig
from .export import build_event_log_dataframe, export_event_log
from .preprocess import preprocess_audio
from .segment import build_analysis_segments
from .transcribe import save_transcript_segments_json, transcribe_audio

logger = logging.getLogger(__name__)


def run_pipeline(audio_path: str, case_id: str, output_dir: str, config: AppConfig) -> Dict[str, Path]:
    out_dir = config.ensure_output_dir(output_dir)
    source_audio = Path(audio_path)

    paths = {
        "normalized_audio": out_dir / config.normalized_audio_name,
        "transcript_segments_json": out_dir / config.transcript_json_name,
        "events_csv": out_dir / config.events_csv_name,
        "events_review_xlsx": out_dir / config.events_xlsx_name,
    }

    preprocess_audio(source_audio, paths["normalized_audio"], config.audio)

    segments = transcribe_audio(paths["normalized_audio"], config.whisper)
    save_transcript_segments_json(segments, paths["transcript_segments_json"])
    if not segments:
        logger.warning("Transcription produced 0 segments; event log will be empty (headers only).")

    analysis = build_analysis_segments(segments)
    classified = classify_segments(analysis, config.classifier, config.phase)

    log_df = build_event_log_dataframe(classified)
    export_event_log(
        log_df,
        paths["events_csv"],
        paths["events_review_xlsx"],
        sheet_name=config.event_log_sheet_name,
    )

    flagged = sum(1 for s in classified if s.get("internal_label") != "routine_none")
    logger.info(
        "Case %s | event log rows: %s | flagged delay rows: %s",
        case_id,
        len(log_df),
        flagged,
    )
    return paths
