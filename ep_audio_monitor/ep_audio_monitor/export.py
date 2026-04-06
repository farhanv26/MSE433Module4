"""Export helpers for review-friendly outputs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

EVENT_COLUMNS = [
    "start_time",
    "end_time",
    "duration_sec",
    "procedure_phase",
    "delay_category",
    "description",
    "confidence",
    "transcript",
    "case_id",
    "source_audio_file",
    "verified_label",
    "review_notes",
]


def to_dataframes(classified_segments: List[Dict], case_id: str, source_audio_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for seg in classified_segments:
        row = {
            "start_time": seg.get("start_time"),
            "end_time": seg.get("end_time"),
            "duration_sec": seg.get("duration_sec"),
            "procedure_phase": seg.get("procedure_phase", "Unknown"),
            "delay_category": seg.get("delay_category", ""),
            "description": seg.get("description", ""),
            "confidence": seg.get("confidence", 0.0),
            "transcript": seg.get("transcript", ""),
            "case_id": case_id,
            "source_audio_file": source_audio_file,
            "verified_label": "",
            "review_notes": "",
            "internal_label": seg.get("internal_label", "routine_none"),
        }
        rows.append(row)

    all_df = pd.DataFrame(rows)
    events_df = all_df[all_df["internal_label"] != "routine_none"].copy()

    for df in (all_df, events_df):
        for col in EVENT_COLUMNS:
            if col not in df.columns:
                df[col] = ""

    events_df = events_df[EVENT_COLUMNS]
    all_df = all_df[EVENT_COLUMNS + ["internal_label"]]
    return events_df, all_df


def export_events_csv(events_df: pd.DataFrame, output_path: str | Path) -> Path:
    path = Path(output_path)
    events_df.to_csv(path, index=False)
    logger.info("Saved events CSV: %s", path)
    return path


def export_all_segments_csv(all_df: pd.DataFrame, output_path: str | Path) -> Path:
    path = Path(output_path)
    all_df.to_csv(path, index=False)
    logger.info("Saved all-segments CSV: %s", path)
    return path


def export_review_excel(events_df: pd.DataFrame, output_path: str | Path) -> Path:
    path = Path(output_path)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        events_df.to_excel(writer, index=False, sheet_name="FlaggedEvents")
    logger.info("Saved review Excel: %s", path)
    return path
