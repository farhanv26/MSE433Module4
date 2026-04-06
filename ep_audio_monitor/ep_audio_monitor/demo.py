"""Run classifier on sample transcript segments without audio transcription."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .classify import classify_segments
from .config import AppConfig
from .export import to_dataframes


def run_demo(output_dir: str = "outputs_demo", case_id: str = "DEMO001") -> None:
    cfg = AppConfig()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    demo_csv = Path(__file__).parent / "sample_data" / "demo_segments.csv"
    df = pd.read_csv(demo_csv)
    segments = df.to_dict(orient="records")

    classified = classify_segments(segments, cfg.classifier, cfg.phase)
    events_df, all_df = to_dataframes(classified, case_id=case_id, source_audio_file="demo_segments.csv")

    events_df.to_csv(out / "events.csv", index=False)
    all_df.to_csv(out / "all_segments.csv", index=False)
    with pd.ExcelWriter(out / "events_review.xlsx", engine="openpyxl") as writer:
        events_df.to_excel(writer, index=False, sheet_name="FlaggedEvents")

    print(f"Demo complete. Outputs written to: {out.resolve()}")


if __name__ == "__main__":
    run_demo()
