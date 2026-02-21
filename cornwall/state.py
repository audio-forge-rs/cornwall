"""Shared state management for Cornwall.

All project state lives in state/ as JSON files. This module provides
read/write access with sensible defaults so scripts don't duplicate logic.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve paths relative to the repo root (one level up from cornwall/ package)
ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
PROJECTS_DIR = ROOT / "projects"

PROJECT_FILE = STATE_DIR / "project.json"
TRACKS_FILE = STATE_DIR / "tracks.json"
EFFECTS_FILE = STATE_DIR / "effects.json"
MIX_FILE = STATE_DIR / "mix.json"
PID_FILE = STATE_DIR / ".playback.pid"


def _ensure_dirs():
    STATE_DIR.mkdir(exist_ok=True)
    PROJECTS_DIR.mkdir(exist_ok=True)


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def _write_json(path: Path, data: Any):
    _ensure_dirs()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


# --- Project ---

def project_exists() -> bool:
    return PROJECT_FILE.exists()


def require_project():
    if not project_exists():
        raise SystemExit("Error: No project loaded. Run 'scripts/project.py create' first.")


def get_project() -> dict:
    require_project()
    return _read_json(PROJECT_FILE)


def save_project(data: dict):
    _write_json(PROJECT_FILE, data)


def create_project(name: str, bpm: int = 120, sample_rate: int = 44100, time_sig: str = "4/4") -> dict:
    _ensure_dirs()
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(exist_ok=True)

    project = {
        "name": name,
        "bpm": bpm,
        "sample_rate": sample_rate,
        "time_sig": time_sig,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_dir": name,
    }
    save_project(project)
    _write_json(TRACKS_FILE, [])
    _write_json(EFFECTS_FILE, {})
    _write_json(MIX_FILE, {"master_volume": 1.0, "output_format": "wav", "output_file": "mix.wav"})
    return project


def get_project_dir() -> Path:
    project = get_project()
    return PROJECTS_DIR / project.get("project_dir", project["name"])


# --- Tracks ---

def get_tracks() -> list[dict]:
    return _read_json(TRACKS_FILE, [])


def save_tracks(tracks: list[dict]):
    _write_json(TRACKS_FILE, tracks)


def next_track_id() -> int:
    tracks = get_tracks()
    if not tracks:
        return 1
    return max(t["id"] for t in tracks) + 1


def get_track(track_id: int) -> dict | None:
    for t in get_tracks():
        if t["id"] == track_id:
            return t
    return None


def require_track(track_id: int) -> dict:
    track = get_track(track_id)
    if track is None:
        raise SystemExit(f"Error: Track {track_id} not found")
    return track


def add_track(name: str, track_type: str = "audio") -> dict:
    require_project()
    tracks = get_tracks()
    track = {
        "id": next_track_id(),
        "name": name,
        "type": track_type,
        "source": None,
        "volume": 1.0,
        "pan": 0.0,
        "mute": False,
        "solo": False,
    }
    tracks.append(track)
    save_tracks(tracks)

    # Initialize empty effects chain
    effects = get_effects()
    effects[str(track["id"])] = []
    save_effects(effects)

    return track


def update_track(track_id: int, **fields) -> dict:
    tracks = get_tracks()
    for t in tracks:
        if t["id"] == track_id:
            t.update(fields)
            save_tracks(tracks)
            return t
    raise SystemExit(f"Error: Track {track_id} not found")


def remove_track(track_id: int) -> dict:
    tracks = get_tracks()
    removed = None
    new_tracks = []
    for t in tracks:
        if t["id"] == track_id:
            removed = t
        else:
            new_tracks.append(t)
    if removed is None:
        raise SystemExit(f"Error: Track {track_id} not found")
    save_tracks(new_tracks)

    # Remove effects chain
    effects = get_effects()
    effects.pop(str(track_id), None)
    save_effects(effects)

    return removed


def get_active_tracks() -> list[dict]:
    """Get tracks that should be heard: if any solo, only solo'd; otherwise all unmuted."""
    tracks = get_tracks()
    solo_tracks = [t for t in tracks if t["solo"] and t["source"]]
    if solo_tracks:
        return solo_tracks
    return [t for t in tracks if not t["mute"] and t["source"]]


# --- Effects ---

def get_effects() -> dict:
    return _read_json(EFFECTS_FILE, {})


def save_effects(effects: dict):
    _write_json(EFFECTS_FILE, effects)


def get_track_effects(track_id: int) -> list[dict]:
    effects = get_effects()
    return effects.get(str(track_id), [])


def add_effect(track_id: int, name: str, params: dict | None = None) -> dict:
    require_track(track_id)
    effects = get_effects()
    chain = effects.get(str(track_id), [])
    effect = {"name": name, "params": params or {}}
    chain.append(effect)
    effects[str(track_id)] = chain
    save_effects(effects)
    return effect


def remove_effect(track_id: int, index: int) -> dict:
    effects = get_effects()
    chain = effects.get(str(track_id), [])
    if index < 0 or index >= len(chain):
        raise SystemExit(f"Error: Effect index {index} out of range (track has {len(chain)} effects)")
    removed = chain.pop(index)
    effects[str(track_id)] = chain
    save_effects(effects)
    return removed


def clear_effects(track_id: int):
    require_track(track_id)
    effects = get_effects()
    effects[str(track_id)] = []
    save_effects(effects)


# --- Mix ---

def get_mix() -> dict:
    return _read_json(MIX_FILE, {"master_volume": 1.0, "output_format": "wav", "output_file": "mix.wav"})


def save_mix(data: dict):
    _write_json(MIX_FILE, data)


# --- Playback PID ---

def get_playback_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return pid
    except (ValueError, ProcessLookupError, PermissionError):
        PID_FILE.unlink(missing_ok=True)
        return None


def save_playback_pid(pid: int):
    _ensure_dirs()
    PID_FILE.write_text(str(pid))


def clear_playback_pid():
    PID_FILE.unlink(missing_ok=True)
