# ep_audio_monitor

Course **proof-of-concept**: procedural audio → transcript → **AI Event Log** (CSV + Excel).

**Not** clinical decision support, diagnosis, or physician/team evaluation. Workflow analysis only.

---

## Event log format

Exports use these columns **in order** (all transcript segments, chronological):

| Column | Notes |
|--------|--------|
| Start Time | Segment start (seconds) |
| End Time | Segment end (seconds) |
| Duration (s) | Segment length |
| Procedure Phase | Heuristic phase (e.g. Positioning, Confirmation); `Unknown` if unclear |
| Delay Category | One of the four delay types, or **`-`** for routine / no delay |
| Description | Short review-friendly phrase |
| Confidence | Heuristic score (not calibrated probability) |

**Delay categories (flagged rows only):**  
Positioning/Coordination · Communication Delay · Equipment/Tool Delay · Non-Routine Complexity  

**Internal label** `routine_none` is still used in code; in the event log it appears as **Delay Category = `-`**.

---

## Workflow

1. Preprocess → mono WAV  
2. Transcribe (`faster-whisper`) → `transcript_segments.json`  
3. Segment (one row per transcript segment)  
4. Classify (rule-based dictionaries in `config.py`)  
5. Export `events.csv` + `events_review.xlsx` (sheet **AI Event Log**)

---

## Setup

```bash
cd /path/to/ep_audio_monitor
python -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt && pip install -e .
```

Install **ffmpeg** for non-WAV inputs if needed.

---

## Run

```bash
python -m ep_audio_monitor --audio /path/to/recording.wav --case-id CASE001 --output-dir outputs/
python -m ep_audio_monitor.demo
```

Empty or silent audio yields **no data rows**; CSV/Excel still contain **headers** (no crash).

---

## Classification

- Editable terms: `ClassifierConfig.category_terms`  
- Conservative: needs enough hit count and margin vs runner-up; otherwise `routine_none` → **`-`** in the log  
- Routine descriptions use `routine_description_by_phase` (e.g. “Catheter positioned”, “PFA application”)

---

## Troubleshooting

- **`No module named ep_audio_monitor`**: use project root + `pip install -e .`  
- **Empty log body**: normal if transcription is empty or every segment is routine
