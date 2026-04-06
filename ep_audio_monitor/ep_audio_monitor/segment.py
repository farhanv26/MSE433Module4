"""Segmentation logic for prototype pipeline."""

from __future__ import annotations

from typing import Dict, List


def build_analysis_segments(transcript_segments: List[Dict]) -> List[Dict]:
    """Return transcript segments as analysis units.

    Kept simple for v1; future versions can merge neighboring segments.
    """
    return transcript_segments.copy()
