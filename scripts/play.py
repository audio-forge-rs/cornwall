#!/usr/bin/env python3
"""Playback and rendering for Cornwall projects.

Usage: play.py <command> [options]

Commands:
  track <id>            Play a single track through headphones
  mix                   Render and play the full mix
  render                Render the mix to a file (no playback)
  loop <id|mix>         Loop a track or the mix in background
  stop                  Stop background playback
  status                Check if something is playing
  file <path>           Play any audio file

Examples:
  play.py track 1
  play.py mix
  play.py loop mix
  play.py stop
  play.py file ~/samples/banjo.wav
"""

import argparse
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state
from cornwall.sox_effects import build_sox_effects


def _run_sox(args: list[str], background: bool = False) -> subprocess.Popen | None:
    """Run a sox/play command."""
    try:
        if background:
            proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return proc
        else:
            subprocess.run(args, check=True)
            return None
    except FileNotFoundError:
        print("Error: 'play' (SoX) not found. Install with: brew install sox", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Playback error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_track(args):
    state.require_project()
    track = state.require_track(args.id)
    if not track["source"]:
        print(f"Error: Track {args.id} '{track['name']}' has no audio source.", file=sys.stderr)
        print(f"Use 'track.py import {args.id} <file>' first.", file=sys.stderr)
        sys.exit(1)

    cmd = ["play", track["source"]]
    if track["volume"] != 1.0:
        cmd += ["vol", str(track["volume"])]

    # Apply effects chain
    cmd += build_sox_effects(args.id)

    if args.start:
        cmd += ["trim", str(args.start)]
        if args.duration:
            cmd.append(str(args.duration))

    print(f"Playing track {args.id}: '{track['name']}' (vol={track['volume']} pan={track['pan']})")
    _run_sox(cmd)


def _render_track_to_file(track: dict, output: str):
    """Render a single track with volume and effects to a file."""
    cmd = ["sox", track["source"], output, "vol", str(track["volume"])]
    cmd += build_sox_effects(track["id"])
    subprocess.run(cmd, check=True)


def cmd_mix(args):
    state.require_project()
    active = state.get_active_tracks()
    if not active:
        print("Error: No active tracks with audio sources to mix", file=sys.stderr)
        sys.exit(1)

    project_dir = state.get_project_dir()
    project_dir.mkdir(parents=True, exist_ok=True)
    output = args.output or str(project_dir / "mix.wav")

    if len(active) == 1:
        t = active[0]
        print(f"Rendering track '{t['name']}' -> {output}")
        _render_track_to_file(t, output)
    else:
        print(f"Mixing {len(active)} tracks -> {output}")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_files = []
            for t in active:
                tmp = os.path.join(tmpdir, f"track_{t['id']}.wav")
                _render_track_to_file(t, tmp)
                tmp_files.append(tmp)
            subprocess.run(["sox", "-m"] + tmp_files + [output], check=True)

    print(f"Rendered: {output}")
    if not args.no_play:
        print("Playing mix...")
        _run_sox(["play", output])


def cmd_render(args):
    args.no_play = True
    cmd_mix(args)


def cmd_loop(args):
    state.require_project()

    # Stop existing playback
    pid = state.get_playback_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        state.clear_playback_pid()

    if args.target == "mix":
        project_dir = state.get_project_dir()
        output = str(project_dir / "mix.wav")

        # Render first
        active = state.get_active_tracks()
        if not active:
            print("Error: No active tracks with audio sources", file=sys.stderr)
            sys.exit(1)

        if len(active) == 1:
            t = active[0]
            print(f"Rendering track '{t['name']}'...")
            _render_track_to_file(t, output)
        else:
            print(f"Mixing {len(active)} tracks...")
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_files = []
                for t in active:
                    tmp = os.path.join(tmpdir, f"track_{t['id']}.wav")
                    _render_track_to_file(t, tmp)
                    tmp_files.append(tmp)
                subprocess.run(["sox", "-m"] + tmp_files + [output], check=True)

        file_to_loop = output
    else:
        track_id = int(args.target)
        track = state.require_track(track_id)
        if not track["source"]:
            print(f"Error: Track {track_id} has no audio source", file=sys.stderr)
            sys.exit(1)
        file_to_loop = track["source"]

    proc = _run_sox(["play", file_to_loop, "repeat", "999"], background=True)
    assert proc is not None  # background=True always returns a Popen
    state.save_playback_pid(proc.pid)
    print(f"Looping: {file_to_loop} (pid {proc.pid})")
    print("Use 'play.py stop' to stop")


def cmd_stop(args):
    pid = state.get_playback_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            # Kill child processes too
            subprocess.run(["pkill", "-P", str(pid)], capture_output=True)
            print(f"Stopped playback (pid {pid})")
        except ProcessLookupError:
            print("No active playback")
        state.clear_playback_pid()
    else:
        print("Nothing playing")


def cmd_status(args):
    pid = state.get_playback_pid()
    if pid:
        print(f"Playing (pid {pid})")
    else:
        print("Not playing")


def cmd_file(args):
    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    print(f"Playing: {path}")
    _run_sox(["play", str(path)])


def main():
    parser = argparse.ArgumentParser(description="Playback and rendering for Cornwall projects")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("track", help="Play a single track")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("--start", type=float, help="Start position in seconds")
    p.add_argument("--duration", type=float, help="Duration in seconds")

    p = sub.add_parser("mix", help="Render and play the full mix")
    p.add_argument("--output", help="Output file path")
    p.add_argument("--no-play", action="store_true", help="Render only, don't play")

    p = sub.add_parser("render", help="Render mix to file (no playback)")
    p.add_argument("--output", help="Output file path")

    p = sub.add_parser("loop", help="Loop a track or mix in background")
    p.add_argument("target", help="Track ID or 'mix'")

    sub.add_parser("stop", help="Stop background playback")
    sub.add_parser("status", help="Check playback status")

    p = sub.add_parser("file", help="Play any audio file")
    p.add_argument("path", help="Path to audio file")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmds = {
        "track": cmd_track, "mix": cmd_mix, "render": cmd_render,
        "loop": cmd_loop, "stop": cmd_stop, "status": cmd_status, "file": cmd_file,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
