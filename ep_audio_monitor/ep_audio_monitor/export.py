"""AI Event Log export (CSV + Excel): seven columns, all segments, chronological."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

# Human-readable headers matching the AI Event Log layout.
EVENT_LOG_COLUMNS = [
    "Start Time",
    "End Time",
    "Duration (s)",
    "Procedure Phase",
    "Delay Category",
    "Description",
    "Confidence",
]


def _sort_key(seg: Dict) -> Any:
    t = seg.get("start_time")
    if t is None:
        return 0.0
    try:
        return float(t)
    except (TypeError, ValueError):
        return 0.0


def build_event_log_dataframe(classified_segments: List[Dict]) -> pd.DataFrame:
    """Full event log: every segment, sorted by start time. Empty input → valid empty schema."""
    ordered = sorted(classified_segments, key=_sort_key)
    rows: List[Dict] = []
    for seg in ordered:
        rows.append(
            {
                "Start Time": seg.get("start_time"),
                "End Time": seg.get("end_time"),
                "Duration (s)": seg.get("duration_sec"),
                "Procedure Phase": seg.get("procedure_phase", "Unknown"),
                "Delay Category": seg.get("delay_category", "-"),
                "Description": seg.get("description", ""),
                "Confidence": seg.get("confidence", 0.0),
            }
        )
    return pd.DataFrame(rows, columns=EVENT_LOG_COLUMNS)


def export_event_log(
    events_df: pd.DataFrame,
    csv_path: str | Path,
    xlsx_path: str | Path,
    *,
    sheet_name: str = "AI Event Log",
) -> None:
    csv_path, xlsx_path = Path(csv_path), Path(xlsx_path)
    if list(events_df.columns) != EVENT_LOG_COLUMNS:
        events_df = events_df.reindex(columns=EVENT_LOG_COLUMNS)
    events_df.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        events_df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    logger.info("Saved event log CSV/XLSX: %s, %s", csv_path, xlsx_path)
