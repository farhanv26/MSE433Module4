"""Run classifier on bundled transcript CSV (no audio)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .classify import classify_segments
from .config import AppConfig
from .export import build_event_log_dataframe, export_event_log


def run_demo(output_dir: str = "outputs_demo") -> None:
    cfg = AppConfig()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    demo_csv = Path(__file__).parent / "sample_data" / "demo_segments.csv"
    segments = pd.read_csv(demo_csv).to_dict(orient="records")
    classified = classify_segments(segments, cfg.classifier, cfg.phase)
    log_df = build_event_log_dataframe(classified)
    export_event_log(log_df, out / "events.csv", out / "events_review.xlsx", sheet_name=cfg.event_log_sheet_name)
    print(f"Demo complete: {out.resolve()}")


if __name__ == "__main__":
    run_demo()
