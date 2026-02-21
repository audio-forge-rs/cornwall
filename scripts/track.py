#!/usr/bin/env python3
"""Manage tracks in the current Cornwall project.

Usage: track.py <command> [options]

Commands:
  add       Add a new track
  list      List all tracks
  remove    Remove a track
  solo      Solo a track
  unsolo    Unsolo a track
  mute      Mute a track
  unmute    Unmute a track
  volume    Set track volume
  pan       Set track pan
  rename    Rename a track
  info      Show detailed track info
  import    Import an audio file to a track

Examples:
  track.py add --name "mandolin" --type audio
  track.py list
  track.py solo 1
  track.py volume 2 0.8
  track.py pan 1 -0.3
  track.py import 1 ~/samples/mandolin-riff.wav
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state


def cmd_add(args):
    if args.type not in ("audio", "midi", "synth"):
        print("Error: --type must be audio, midi, or synth", file=sys.stderr)
        sys.exit(1)
    track = state.add_track(args.name, args.type)
    print(f"Added track {track['id']}: '{track['name']}' ({track['type']})")


def cmd_list(args):
    state.require_project()
    tracks = state.get_tracks()
    if args.json:
        print(json.dumps(tracks, indent=2))
        return
    if not tracks:
        print("No tracks. Use 'track.py add --name <name>' to add one.")
        return
    header = f"{'ID':<4} {'Name':<20} {'Type':<6} {'Vol':<6} {'Pan':<6} {'M':>1} {'S':>1}  Source"
    print(header)
    print("-" * len(header))
    for t in tracks:
        m = "M" if t["mute"] else "-"
        s = "S" if t["solo"] else "-"
        source = t["source"] or "(empty)"
        # Shorten source path for display
        if t["source"]:
            source = Path(t["source"]).name
        print(f"{t['id']:<4} {t['name']:<20} {t['type']:<6} {t['volume']:<6} {t['pan']:<6} {m:>1} {s:>1}  {source}")


def cmd_remove(args):
    track = state.remove_track(args.id)
    print(f"Removed track {args.id}: '{track['name']}'")


def cmd_solo(args):
    track = state.update_track(args.id, solo=True)
    print(f"Solo: track {args.id} '{track['name']}'")


def cmd_unsolo(args):
    track = state.update_track(args.id, solo=False)
    print(f"Unsolo: track {args.id} '{track['name']}'")


def cmd_mute(args):
    track = state.update_track(args.id, mute=True)
    print(f"Muted: track {args.id} '{track['name']}'")


def cmd_unmute(args):
    track = state.update_track(args.id, mute=False)
    print(f"Unmuted: track {args.id} '{track['name']}'")


def cmd_volume(args):
    track = state.update_track(args.id, volume=args.level)
    print(f"Volume: track {args.id} '{track['name']}' = {args.level}")


def cmd_pan(args):
    track = state.update_track(args.id, pan=args.position)
    print(f"Pan: track {args.id} '{track['name']}' = {args.position}")


def cmd_rename(args):
    track = state.update_track(args.id, name=args.new_name)
    print(f"Renamed: track {args.id} -> '{args.new_name}'")


def cmd_info(args):
    track = state.require_track(args.id)
    effects = state.get_track_effects(args.id)
    if args.json:
        data = dict(track)
        data["effects"] = effects
        print(json.dumps(data, indent=2))
        return
    print(f"Track:   {track['id']}")
    print(f"Name:    {track['name']}")
    print(f"Type:    {track['type']}")
    print(f"Volume:  {track['volume']}")
    print(f"Pan:     {track['pan']}")
    print(f"Mute:    {track['mute']}")
    print(f"Solo:    {track['solo']}")
    print(f"Source:  {track['source'] or '(empty)'}")
    if effects:
        print("Effects:")
        for i, fx in enumerate(effects):
            params = " ".join(f"{k}={v}" for k, v in fx["params"].items())
            print(f"  [{i}] {fx['name']} {params}")
    else:
        print("Effects: (none)")


def cmd_import(args):
    state.require_project()
    state.require_track(args.id)
    src = Path(args.file).expanduser().resolve()
    if not src.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    project_dir = state.get_project_dir()
    audio_dir = project_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    dest = audio_dir / src.name
    if src != dest:
        shutil.copy2(src, dest)
    track = state.update_track(args.id, source=str(dest))
    print(f"Imported '{src.name}' to track {args.id} '{track['name']}'")


def main():
    parser = argparse.ArgumentParser(description="Manage tracks in the current Cornwall project")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("add", help="Add a new track")
    p.add_argument("--name", required=True, help="Track name")
    p.add_argument("--type", default="audio", help="Track type: audio, midi, synth (default: audio)")

    p = sub.add_parser("list", help="List all tracks")
    p.add_argument("--json", action="store_true", help="Output as raw JSON")

    p = sub.add_parser("remove", help="Remove a track")
    p.add_argument("id", type=int, help="Track ID")

    p = sub.add_parser("solo", help="Solo a track")
    p.add_argument("id", type=int, help="Track ID")

    p = sub.add_parser("unsolo", help="Unsolo a track")
    p.add_argument("id", type=int, help="Track ID")

    p = sub.add_parser("mute", help="Mute a track")
    p.add_argument("id", type=int, help="Track ID")

    p = sub.add_parser("unmute", help="Unmute a track")
    p.add_argument("id", type=int, help="Track ID")

    p = sub.add_parser("volume", help="Set track volume")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("level", type=float, help="Volume level 0.0-2.0 (1.0 = unity)")

    p = sub.add_parser("pan", help="Set track pan")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("position", type=float, help="Pan position -1.0 (left) to 1.0 (right)")

    p = sub.add_parser("rename", help="Rename a track")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("new_name", help="New track name")

    p = sub.add_parser("info", help="Show detailed track info")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("--json", action="store_true", help="Output as raw JSON")

    p = sub.add_parser("import", help="Import an audio file to a track")
    p.add_argument("id", type=int, help="Track ID")
    p.add_argument("file", help="Path to audio file")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmds = {
        "add": cmd_add, "list": cmd_list, "remove": cmd_remove,
        "solo": cmd_solo, "unsolo": cmd_unsolo, "mute": cmd_mute, "unmute": cmd_unmute,
        "volume": cmd_volume, "pan": cmd_pan, "rename": cmd_rename,
        "info": cmd_info, "import": cmd_import,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
