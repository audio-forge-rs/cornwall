#!/usr/bin/env python3
"""Manage Cornwall projects.

Usage: project.py <command> [options]

Commands:
  create    Create a new project
  info      Show current project info
  set       Change a project setting
  open      Open (switch to) an existing project

project.py create [options]
  --name <name>         Project name (required)
  --bpm <number>        Tempo in BPM (default: 120)
  --sample-rate <rate>  Sample rate in Hz (default: 44100)
  --time-sig <n/d>      Time signature (default: 4/4)

project.py info
  Print current project settings.
  --json    Output as raw JSON

project.py set <key> <value>
  Change a project setting. Keys: name, bpm, sample-rate, time-sig

project.py open <name>
  Switch to an existing project by name.

Examples:
  project.py create --name "folk-session" --bpm 110
  project.py info
  project.py set bpm 140
  project.py set time-sig 3/4
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state


def cmd_create(args):
    project = state.create_project(
        name=args.name,
        bpm=args.bpm,
        sample_rate=args.sample_rate,
        time_sig=args.time_sig,
    )
    project_dir = state.PROJECTS_DIR / project["name"]
    print(f"Created project '{args.name}' at {args.bpm} BPM, {args.sample_rate}Hz, {args.time_sig}")
    print(f"Project directory: {project_dir}")


def cmd_info(args):
    project = state.get_project()
    if args.json:
        print(json.dumps(project, indent=2))
        return
    tracks = state.get_tracks()
    print(f"Project: {project['name']}")
    print(f"BPM:     {project['bpm']}")
    print(f"Rate:    {project['sample_rate']}Hz")
    print(f"Time:    {project['time_sig']}")
    print(f"Created: {project['created']}")
    print(f"Tracks:  {len(tracks)}")


def cmd_set(args):
    project = state.get_project()
    key, value = args.key, args.value
    if key == "name":
        project["name"] = value
    elif key == "bpm":
        project["bpm"] = int(value)
    elif key == "sample-rate":
        project["sample_rate"] = int(value)
    elif key == "time-sig":
        project["time_sig"] = value
    else:
        print(f"Unknown key: {key}. Valid keys: name, bpm, sample-rate, time-sig", file=sys.stderr)
        sys.exit(1)
    state.save_project(project)
    print(f"Set {key} = {value}")


def cmd_open(args):
    project_dir = state.PROJECTS_DIR / args.name
    if not project_dir.exists():
        print(f"Project '{args.name}' not found in {state.PROJECTS_DIR}/", file=sys.stderr)
        available = [d.name for d in state.PROJECTS_DIR.iterdir() if d.is_dir()]
        if available:
            print("Available projects: " + ", ".join(available), file=sys.stderr)
        else:
            print("No projects exist yet.", file=sys.stderr)
        sys.exit(1)
    print(f"Opened project '{args.name}'")
    # Trigger info display
    class InfoArgs:
        json = False
    cmd_info(InfoArgs())


def main():
    parser = argparse.ArgumentParser(description="Manage Cornwall projects", add_help=True)
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create a new project")
    p_create.add_argument("--name", required=True, help="Project name")
    p_create.add_argument("--bpm", type=int, default=120, help="Tempo in BPM (default: 120)")
    p_create.add_argument("--sample-rate", type=int, default=44100, help="Sample rate in Hz (default: 44100)")
    p_create.add_argument("--time-sig", default="4/4", help="Time signature (default: 4/4)")

    p_info = sub.add_parser("info", help="Show current project info")
    p_info.add_argument("--json", action="store_true", help="Output as raw JSON")

    p_set = sub.add_parser("set", help="Change a project setting")
    p_set.add_argument("key", help="Setting key: name, bpm, sample-rate, time-sig")
    p_set.add_argument("value", help="New value")

    p_open = sub.add_parser("open", help="Open an existing project")
    p_open.add_argument("name", help="Project name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    {"create": cmd_create, "info": cmd_info, "set": cmd_set, "open": cmd_open}[args.command](args)


if __name__ == "__main__":
    main()
