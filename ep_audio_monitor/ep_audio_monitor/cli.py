"""CLI entrypoint for ep_audio_monitor."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import AppConfig
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ep_audio_monitor",
        description="Prototype workflow delay monitor for EP procedural audio.",
    )
    parser.add_argument(
        "--audio",
        required=True,
        help="Path to a real audio file (WAV/MP3/M4A). Not a placeholder like path/to/file.wav.",
    )
    parser.add_argument("--case-id", required=True, help="Case identifier (e.g., CASE001).")
    parser.add_argument("--output-dir", required=True, help="Directory for output artifacts.")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING).")
    parser.add_argument("--whisper-model", default="small", help="faster-whisper model size.")
    parser.add_argument("--language", default="en", help="Transcription language code.")
    return parser


def setup_logging(level: str, output_dir: str, config: AppConfig) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(output_dir) / config.logs_name
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8")],
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = AppConfig()
    config.whisper.model_size = args.whisper_model
    config.whisper.language = args.language

    setup_logging(args.log_level, args.output_dir, config)
    logging.getLogger(__name__).info("Starting ep_audio_monitor prototype run")

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.is_file():
        raise SystemExit(
            f"Audio file not found: {args.audio}\n\n"
            "Do not paste placeholder examples such as /path/to/..., /full/path/to/..., or "
            "path/to/file.wav — those are not real files.\n"
            "Use the actual path on your Mac, for example:\n"
            "  /Users/yourname/Desktop/my_recording.wav\n"
            "Tip: type `open .` in Finder, drag your audio file into Terminal to paste its path.\n\n"
            "Smoke test from project root (this path is real in the repo):\n"
            "  python -m ep_audio_monitor --audio sample_data/sample_silence_2s.wav "
            "--case-id DEMO --output-dir outputs/"
        )

    outputs = run_pipeline(
        audio_path=str(audio_path),
        case_id=args.case_id,
        output_dir=args.output_dir,
        config=config,
    )

    print("\nRun complete:")
    for key, path in outputs.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
