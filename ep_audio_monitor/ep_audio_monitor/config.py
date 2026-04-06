"""Configuration and editable rules for ep_audio_monitor."""

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
    min_score_threshold: float = 2.0
    min_margin_threshold: float = 0.75
    phrase_weight: float = 1.5
    keyword_weight: float = 1.0
    weak_keyword_weight: float = 0.6
    confidence_cap: float = 0.99

    phrases: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "positioning_coordination": [
                "wait for access",
                "need space",
                "adjust again",
                "back a bit",
                "not there",
                "hold there",
                "move left",
                "move right",
                "reposition",
                "crowded",
                "need room",
                "multiple adjustments",
            ],
            "communication_delay": [
                "say that again",
                "repeat that",
                "what did you say",
                "confirm again",
                "clarify",
                "no, the other one",
                "can you repeat",
                "i did not hear",
                "misheard",
            ],
            "equipment_tool_delay": [
                "where is the catheter",
                "wrong tool",
                "bring the other one",
                "this is not working",
                "need replacement",
                "not set up",
                "missing tool",
                "recalibrate",
                "calibration issue",
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
            ],
        }
    )

    keywords: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "positioning_coordination": [
                "reposition",
                "adjust",
                "access",
                "space",
                "crowding",
                "sequence",
                "hold",
                "back",
            ],
            "communication_delay": [
                "repeat",
                "clarify",
                "again",
                "misheard",
                "confirm",
                "instruction",
                "hear",
            ],
            "equipment_tool_delay": [
                "tool",
                "catheter",
                "setup",
                "calibrate",
                "replacement",
                "broken",
                "wrong",
                "working",
            ],
            "non_routine_complexity": [
                "mapping",
                "anatomy",
                "unexpected",
                "verify",
                "complication",
                "additional",
                "troubleshoot",
            ],
        }
    )

    weak_keywords: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "positioning_coordination": ["left", "right", "there", "move"],
            "communication_delay": ["say", "what", "did", "again"],
            "equipment_tool_delay": ["bring", "other", "set", "up"],
            "non_routine_complexity": ["extra", "more", "check"],
        }
    )

    description_templates: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "positioning_coordination": [
                "Multiple adjustments before next site",
                "Waiting for physical access to proceed",
                "Inefficient repositioning between applications",
            ],
            "communication_delay": [
                "Repeated instructions for catheter angle",
                "Clarification of positioning instructions",
                "Delayed response to instruction sequence",
            ],
            "equipment_tool_delay": [
                "Delay waiting for correct catheter",
                "Tool setup or calibration delay",
                "Tool handling issue requiring replacement",
            ],
            "non_routine_complexity": [
                "Additional mapping due to anatomy",
                "Unexpected procedural adjustment",
                "Extra verification before closure",
            ],
            "routine_none": ["No clear workflow delay evidence"],
        }
    )


@dataclass
class PhaseConfig:
    phase_cues: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "Positioning": ["position", "angle", "access", "reposition", "adjust"],
            "Confirmation": ["confirm", "verified", "looks good", "check"],
            "Energy Delivery": ["deliver", "energy", "application", "pfa", "ablation"],
            "Repositioning": ["move", "back", "again", "next site"],
        }
    )
    default_phase: str = "Unknown"


@dataclass
class AppConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    phase: PhaseConfig = field(default_factory=PhaseConfig)

    keep_all_segments_export: bool = True
    transcript_json_name: str = "transcript_segments.json"
    all_segments_csv_name: str = "all_segments.csv"
    events_csv_name: str = "events.csv"
    events_xlsx_name: str = "events_review.xlsx"
    normalized_audio_name: str = "normalized_audio.wav"
    logs_name: str = "run.log"

    @staticmethod
    def ensure_output_dir(output_dir: str | Path) -> Path:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        return out
