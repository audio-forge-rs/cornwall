#!/usr/bin/env python3
"""Query the Cornwall player's state from Claude Code.

Usage: player.py <command>

Commands:
  status    Show current player state (JSON)
  playing   Exit 0 if playing, 1 if stopped
  position  Print current position in seconds
  bar       Print current bar number

The player TUI runs in a separate terminal. This script reads its state
file to report what it's doing, so Claude Code can make decisions based
on playback state.

To start the player TUI in another terminal:
  cd /path/to/cornwall && ./cornwall-player

Or with a specific file:
  ./cornwall-player projects/folk-jam/audio/mandolin-gm.wav

Examples:
  player.py status
  player.py playing && echo "Music is playing"
  player.py bar
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state


def cmd_status(args):
    status_file = state.STATE_DIR / ".player.json"
    if status_file.exists():
        data = json.loads(status_file.read_text())
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            playing = "▶ PLAYING" if data.get("playing") else "■ STOPPED"
            print(f"State:    {playing}")
            print(f"Position: {data.get('position_secs', 0):.1f}s")
            print(f"Bar:      {data.get('bar', 0)}.{data.get('beat', 0)}")
            print(f"Tempo:    {data.get('bpm', 0)} BPM  {data.get('time_sig', '')}")
            print(f"Level:    L={data.get('level_l', 0):.3f}  R={data.get('level_r', 0):.3f}")
            print(f"File:     {data.get('file', '')}")
    else:
        if args.json:
            print('{"playing": false}')
        else:
            print("Player not running")


def cmd_playing(args):
    status_file = state.STATE_DIR / ".player.json"
    if status_file.exists():
        data = json.loads(status_file.read_text())
        sys.exit(0 if data.get("playing") else 1)
    sys.exit(1)


def cmd_position(args):
    status_file = state.STATE_DIR / ".player.json"
    if status_file.exists():
        data = json.loads(status_file.read_text())
        print(f"{data.get('position_secs', 0):.2f}")
    else:
        print("0.00")


def cmd_bar(args):
    status_file = state.STATE_DIR / ".player.json"
    if status_file.exists():
        data = json.loads(status_file.read_text())
        print(f"{data.get('bar', 0)}.{data.get('beat', 0)}")
    else:
        print("0.0")


def main():
    parser = argparse.ArgumentParser(description="Query the Cornwall player state")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("status", help="Show current player state")
    p.add_argument("--json", action="store_true", help="Output as raw JSON")

    sub.add_parser("playing", help="Exit 0 if playing, 1 if stopped")
    sub.add_parser("position", help="Print current position in seconds")
    sub.add_parser("bar", help="Print current bar number")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    {"status": cmd_status, "playing": cmd_playing, "position": cmd_position, "bar": cmd_bar}[
        args.command
    ](args)


if __name__ == "__main__":
    main()
