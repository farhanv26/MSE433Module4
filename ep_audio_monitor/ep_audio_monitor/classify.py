"""Conservative rule-based classification (dictionary hits only)."""

from __future__ import annotations

import re
from typing import Dict, List

from .config import ClassifierConfig, INTERNAL_TO_DISPLAY_LABEL, PhaseConfig, ROUTINE_DELAY_CATEGORY_DISPLAY

CATEGORY_ORDER = [
    "positioning_coordination",
    "communication_delay",
    "equipment_tool_delay",
    "non_routine_complexity",
]


def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _term_matches(clean_text: str, term: str) -> bool:
    term = term.strip().lower()
    if not term:
        return False
    if " " in term:
        return term in clean_text
    return bool(re.search(rf"\b{re.escape(term)}\b", clean_text))


def count_category_hits(clean_text: str, terms: List[str]) -> int:
    return sum(1 for t in terms if _term_matches(clean_text, t))


def infer_phase(transcript: str, phase_cfg: PhaseConfig) -> str:
    clean = normalize_text(transcript)
    for phase, cues in phase_cfg.phase_cues.items():
        if any(cue in clean for cue in cues):
            return phase
    return phase_cfg.default_phase


def _flagged_description(category: str, clean: str, cfg: ClassifierConfig) -> str:
    if category == "communication_delay":
        if "angle" in clean or "catheter" in clean:
            return "Repeated instructions for catheter angle"
        return "Clarification of positioning instructions"
    if category == "non_routine_complexity":
        if "anatomy" in clean or "mapping" in clean:
            return "Additional mapping due to anatomy"
        if "closure" in clean or "verify" in clean or "verification" in clean:
            return "Extra verification before closure"
        return cfg.category_description[category]
    return cfg.category_description[category]


def classify_segment(transcript: str, cfg: ClassifierConfig, procedure_phase: str) -> Dict:
    clean = normalize_text(transcript)
    if not clean:
        return _routine_none(0.0, cfg, procedure_phase)

    hits = {cat: count_category_hits(clean, cfg.category_terms[cat]) for cat in CATEGORY_ORDER}
    best = max(hits, key=hits.get)
    best_n = hits[best]
    runner_up = sorted((v for k, v in hits.items() if k != best), reverse=True)
    second_n = runner_up[0] if runner_up else 0

    if best_n < cfg.min_hits or (best_n - second_n) < cfg.min_margin:
        return _routine_none(min(0.45, 0.25 + best_n * 0.1), cfg, procedure_phase)

    desc = _flagged_description(best, clean, cfg)
    confidence = round(min(0.95, 0.52 + 0.12 * best_n + 0.05 * (best_n - second_n)), 2)

    return {
        "internal_label": best,
        "delay_category": INTERNAL_TO_DISPLAY_LABEL[best],
        "description": desc,
        "confidence": confidence,
    }


def _routine_none(confidence: float, cfg: ClassifierConfig, procedure_phase: str) -> Dict:
    desc = cfg.routine_description_by_phase.get(
        procedure_phase,
        cfg.routine_description_by_phase["Unknown"],
    )
    return {
        "internal_label": "routine_none",
        "delay_category": ROUTINE_DELAY_CATEGORY_DISPLAY,
        "description": desc,
        "confidence": round(max(0.35, min(0.55, float(confidence))), 2),
    }


def classify_segments(segments: List[Dict], cfg: ClassifierConfig, phase_cfg: PhaseConfig) -> List[Dict]:
    out: List[Dict] = []
    for row in segments:
        transcript = row.get("transcript") or ""
        procedure_phase = infer_phase(transcript, phase_cfg)
        result = classify_segment(transcript, cfg, procedure_phase)
        out.append(
            {
                **row,
                "procedure_phase": procedure_phase,
                "internal_label": result["internal_label"],
                "delay_category": result["delay_category"],
                "description": result["description"],
                "confidence": result["confidence"],
            }
        )
    return out
