"""Paths, audio/transcription defaults, phase cues, and editable classifier dictionaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

INTERNAL_TO_DISPLAY_LABEL: Dict[str, str] = {
    "positioning_coordination": "Positioning/Coordination",
    "communication_delay": "Communication Delay",
    "equipment_tool_delay": "Equipment/Tool Delay",
    "non_routine_complexity": "Non-Routine Complexity",
}

# Excel/CSV "Delay Category" for non-flagged rows (internal label remains routine_none).
ROUTINE_DELAY_CATEGORY_DISPLAY = "-"


@dataclass
class AudioConfig:
    target_sample_rate: int = 16000
    target_channels: int = 1
    target_format: str = "wav"


@dataclass
class WhisperConfig:
    model_size: str = "small"
    device: str = "auto"
    compute_type: str = "int8"
    language: str = "en"
    beam_size: int = 3
    vad_filter: bool = True


@dataclass
class ClassifierConfig:
    """Rule-based: count hits in category_terms. Tune lists and thresholds here only."""

    min_hits: int = 1
    min_margin: int = 1

    category_terms: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "positioning_coordination": [
                "wait for access",
                "need space",
                "adjust again",
                "reposition",
                "not there",
                "hold there",
                "crowded",
                "need room",
                "multiple adjustments",
                "back a bit",
                "move left",
                "inefficient sequencing",
                "physical access",
            ],
            "communication_delay": [
                "say that again",
                "repeat that",
                "what did you say",
                "confirm again",
                "clarify",
                "misheard",
                "can you repeat",
                "no, the other one",
                "i did not hear",
                "delayed response",
            ],
            "equipment_tool_delay": [
                "where is the catheter",
                "wrong tool",
                "bring the other one",
                "this is not working",
                "need replacement",
                "not set up",
                "recalibrate",
                "missing tool",
                "calibration issue",
                "tool handling",
            ],
            "non_routine_complexity": [
                "need more mapping",
                "anatomy is unusual",
                "additional mapping",
                "unexpected procedural adjustment",
                "verify again",
                "extra check",
                "complication",
                "troubleshoot",
                "extra verification",
            ],
        }
    )

    # Default flagged descriptions (refined in classify.py when keyword cues are specific enough).
    category_description: Dict[str, str] = field(
        default_factory=lambda: {
            "positioning_coordination": "Multiple adjustments before next site",
            "communication_delay": "Clarification of positioning instructions",
            "equipment_tool_delay": "Delay waiting for correct catheter",
            "non_routine_complexity": "Unexpected procedural adjustment",
        }
    )

    # Human-readable line for routine rows, keyed by inferred procedure phase.
    routine_description_by_phase: Dict[str, str] = field(
        default_factory=lambda: {
            "Positioning": "Catheter positioned",
            "Confirmation": "Position confirmed",
            "Energy Delivery": "PFA application",
            "Repositioning": "Routine repositioning",
            "Unknown": "Routine procedural audio",
        }
    )


@dataclass
class PhaseConfig:
    phase_cues: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "Positioning": ["position", "angle", "reposition", "adjust", "catheter"],
            "Confirmation": ["confirm", "verified", "check", "looks good"],
            "Energy Delivery": ["energy", "application", "pfa", "ablation", "deliver"],
            "Repositioning": ["move", "next site", "back"],
        }
    )
    default_phase: str = "Unknown"


@dataclass
class AppConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    phase: PhaseConfig = field(default_factory=PhaseConfig)

    transcript_json_name: str = "transcript_segments.json"
    events_csv_name: str = "events.csv"
    events_xlsx_name: str = "events_review.xlsx"
    normalized_audio_name: str = "normalized_audio.wav"
    logs_name: str = "run.log"

    event_log_sheet_name: str = "AI Event Log"

    @staticmethod
    def ensure_output_dir(output_dir: str | Path) -> Path:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        return out
