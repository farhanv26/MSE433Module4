"""Rule-based workflow event classification."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .config import ClassifierConfig, INTERNAL_TO_DISPLAY_LABEL, PhaseConfig

CATEGORY_ORDER = [
    "positioning_coordination",
    "communication_delay",
    "equipment_tool_delay",
    "non_routine_complexity",
]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _count_phrase_hits(text: str, phrases: List[str]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def _count_keyword_hits(text: str, keywords: List[str]) -> int:
    return sum(1 for keyword in keywords if re.search(rf"\b{re.escape(keyword)}\b", text))


def _score_category(clean_text: str, category: str, cfg: ClassifierConfig) -> Tuple[float, Dict[str, int]]:
    phrase_hits = _count_phrase_hits(clean_text, cfg.phrases[category])
    keyword_hits = _count_keyword_hits(clean_text, cfg.keywords[category])
    weak_hits = _count_keyword_hits(clean_text, cfg.weak_keywords[category])
    score = (
        phrase_hits * cfg.phrase_weight
        + keyword_hits * cfg.keyword_weight
        + weak_hits * cfg.weak_keyword_weight
    )
    return score, {"phrase_hits": phrase_hits, "keyword_hits": keyword_hits, "weak_hits": weak_hits}


def infer_phase(transcript: str, phase_cfg: PhaseConfig) -> str:
    clean = normalize_text(transcript)
    for phase, cues in phase_cfg.phase_cues.items():
        if any(cue in clean for cue in cues):
            return phase
    return phase_cfg.default_phase


def classify_segment(transcript: str, cfg: ClassifierConfig) -> Dict:
    """Classify one segment with conservative decision rules."""
    clean = normalize_text(transcript)
    scores: Dict[str, float] = {}
    evidence: Dict[str, Dict[str, int]] = {}

    for category in CATEGORY_ORDER:
        score, ev = _score_category(clean, category, cfg)
        scores[category] = score
        evidence[category] = ev

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    sorted_scores = sorted(scores.values(), reverse=True)
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
    margin = best_score - second_score

    strong_enough = evidence[best_category]["phrase_hits"] >= 1 or (
        evidence[best_category]["keyword_hits"] + evidence[best_category]["weak_hits"] >= 2
    )

    if (
        best_score < cfg.min_score_threshold
        or margin < cfg.min_margin_threshold
        or not strong_enough
    ):
        return {
            "internal_label": "routine_none",
            "delay_category": "",
            "confidence": round(min(0.55, best_score / max(cfg.min_score_threshold, 1.0)), 2),
            "description": cfg.description_templates["routine_none"][0],
            "scores": scores,
            "evidence": evidence,
        }

    confidence = min(cfg.confidence_cap, 0.6 + 0.15 * best_score + 0.05 * margin)
    desc = cfg.description_templates[best_category][0]

    return {
        "internal_label": best_category,
        "delay_category": INTERNAL_TO_DISPLAY_LABEL[best_category],
        "confidence": round(confidence, 2),
        "description": desc,
        "scores": scores,
        "evidence": evidence,
    }


def classify_segments(segments: List[Dict], cfg: ClassifierConfig, phase_cfg: PhaseConfig) -> List[Dict]:
    """Classify all segments and add workflow fields."""
    output: List[Dict] = []
    for row in segments:
        result = classify_segment(row.get("transcript", ""), cfg)
        phase = infer_phase(row.get("transcript", ""), phase_cfg)
        combined = {
            **row,
            "procedure_phase": phase,
            "internal_label": result["internal_label"],
            "delay_category": result["delay_category"],
            "description": result["description"],
            "confidence": result["confidence"],
        }
        output.append(combined)
    return output
