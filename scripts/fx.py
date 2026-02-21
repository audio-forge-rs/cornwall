#!/usr/bin/env python3
"""Manage effects chains on Cornwall tracks.

Usage: fx.py <command> [options]

Commands:
  add       Add an effect to a track's chain
  remove    Remove an effect by index
  list      List effects on a track
  clear     Clear all effects from a track
  preview   Play a track with its effects applied
  catalog   Show all available effects and their parameters

fx.py add <track_id> <effect> [param=value ...]
  Add an effect to the end of a track's effects chain.
  Parameters are key=value pairs.

fx.py remove <track_id> <index>
  Remove an effect by its index in the chain.

fx.py list <track_id>
  Show the effects chain for a track.

fx.py clear <track_id>
  Remove all effects from a track.

fx.py preview <track_id>
  Play the track with effects applied (doesn't save to file).

fx.py catalog
  List all available effects with their parameters.

Available effects (SoX-based):
  reverb       Reverb (reverberance, hf_damping, room_scale)
  delay        Echo/delay (gain_in, gain_out, delay_ms, decay)
  chorus       Chorus (gain_in, gain_out, delay_ms, decay, speed, shape)
  flanger      Flanger (no params needed)
  phaser       Phaser (no params needed)
  tremolo      Tremolo (speed, depth)
  overdrive    Overdrive/distortion (gain)
  compressor   Compressor (attack_decay, transfer)
  eq           Parametric EQ (frequency, width, gain)
  bass         Bass boost/cut (gain)
  treble       Treble boost/cut (gain)
  lowpass      Low-pass filter (frequency)
  highpass     High-pass filter (frequency)
  pitch        Pitch shift (cents)
  tempo        Time stretch (factor)
  norm         Normalize (level)
  fade         Fade in/out (type, fade_in, stop, fade_out)

Examples:
  fx.py add 1 reverb reverberance=80 room_scale=100
  fx.py add 1 delay delay_ms=350 decay=0.4
  fx.py add 2 bass gain=6
  fx.py add 2 treble gain=-3
  fx.py add 3 overdrive gain=30
  fx.py list 1
  fx.py remove 1 0
  fx.py preview 1
  fx.py catalog
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state

EFFECTS_CATALOG = {
    "reverb": {
        "description": "Reverberation - simulates acoustic space",
        "params": {
            "reverberance": "Reverb amount 0-100 (default: 50)",
            "hf_damping": "High frequency damping 0-100 (default: 50)",
            "room_scale": "Room size 0-100 (default: 100)",
        },
    },
    "delay": {
        "description": "Echo / delay effect",
        "params": {
            "gain_in": "Input gain 0-1 (default: 0.8)",
            "gain_out": "Output gain 0-1 (default: 0.9)",
            "delay_ms": "Delay time in milliseconds (default: 500)",
            "decay": "Decay factor 0-1 (default: 0.3)",
        },
    },
    "chorus": {
        "description": "Chorus effect - thickens sound",
        "params": {
            "gain_in": "Input gain (default: 0.7)",
            "gain_out": "Output gain (default: 0.9)",
            "delay_ms": "Modulation delay in ms (default: 55)",
            "decay": "Decay (default: 0.4)",
            "speed": "Modulation speed in Hz (default: 0.25)",
            "shape": "Modulation shape: s=sine, t=triangle (default: s)",
        },
    },
    "flanger": {
        "description": "Flanger effect",
        "params": {},
    },
    "phaser": {
        "description": "Phaser effect",
        "params": {},
    },
    "tremolo": {
        "description": "Tremolo - amplitude modulation",
        "params": {
            "speed": "Speed in Hz (default: 6)",
            "depth": "Depth 0-100 (default: 40)",
        },
    },
    "overdrive": {
        "description": "Overdrive / distortion",
        "params": {
            "gain": "Drive amount in dB (default: 20)",
        },
    },
    "compressor": {
        "description": "Dynamic range compression",
        "params": {
            "attack_decay": "Attack,decay in seconds (default: 0.3,1)",
            "transfer": "Transfer function (default: 6:-70,-60,-20)",
        },
    },
    "eq": {
        "description": "Parametric equalizer",
        "params": {
            "frequency": "Center frequency in Hz (default: 1000)",
            "width": "Bandwidth (default: 1q)",
            "gain": "Gain in dB (default: 0)",
        },
    },
    "bass": {
        "description": "Bass boost/cut shelving EQ",
        "params": {
            "gain": "Gain in dB, positive=boost negative=cut (default: 0)",
        },
    },
    "treble": {
        "description": "Treble boost/cut shelving EQ",
        "params": {
            "gain": "Gain in dB, positive=boost negative=cut (default: 0)",
        },
    },
    "lowpass": {
        "description": "Low-pass filter - cuts high frequencies",
        "params": {
            "frequency": "Cutoff frequency in Hz (default: 3000)",
        },
    },
    "highpass": {
        "description": "High-pass filter - cuts low frequencies",
        "params": {
            "frequency": "Cutoff frequency in Hz (default: 300)",
        },
    },
    "pitch": {
        "description": "Pitch shift",
        "params": {
            "cents": "Pitch shift in cents, 100=one semitone (default: 0)",
        },
    },
    "tempo": {
        "description": "Time stretch without pitch change",
        "params": {
            "factor": "Speed factor, 2.0=double speed (default: 1.0)",
        },
    },
    "norm": {
        "description": "Normalize audio level",
        "params": {
            "level": "Target level in dB (default: -3)",
        },
    },
    "fade": {
        "description": "Fade in and/or out",
        "params": {
            "type": "Curve type: t=linear, q=quarter-sine, h=half-sine, l=log, p=exp (default: t)",
            "fade_in": "Fade in duration in seconds (default: 0)",
            "stop": "Stop time in seconds, 0=end of file (default: 0)",
            "fade_out": "Fade out duration in seconds (default: 0)",
        },
    },
}


def parse_params(param_args: list[str]) -> dict:
    """Parse key=value parameter pairs."""
    params = {}
    for arg in param_args:
        if "=" not in arg:
            print(f"Error: Parameter must be key=value format, got: {arg}", file=sys.stderr)
            sys.exit(1)
        key, value = arg.split("=", 1)
        # Try to convert to number
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
        params[key] = value
    return params


def cmd_add(args):
    state.require_project()
    if args.effect not in EFFECTS_CATALOG:
        print(f"Warning: '{args.effect}' is not in the catalog. Adding as raw SoX effect.", file=sys.stderr)

    params = parse_params(args.params)
    effect = state.add_effect(args.track_id, args.effect, params)
    chain = state.get_track_effects(args.track_id)
    track = state.require_track(args.track_id)
    params_str = " ".join(f"{k}={v}" for k, v in effect["params"].items())
    print(f"Added {args.effect} to track {args.track_id} '{track['name']}' [{len(chain) - 1}] {params_str}")


def cmd_remove(args):
    state.require_project()
    track = state.require_track(args.track_id)
    removed = state.remove_effect(args.track_id, args.index)
    print(f"Removed [{args.index}] {removed['name']} from track {args.track_id} '{track['name']}'")


def cmd_list(args):
    state.require_project()
    track = state.require_track(args.track_id)
    effects = state.get_track_effects(args.track_id)
    if not effects:
        print(f"Track {args.track_id} '{track['name']}': no effects")
        return
    print(f"Track {args.track_id} '{track['name']}' effects chain:")
    for i, fx in enumerate(effects):
        params_str = " ".join(f"{k}={v}" for k, v in fx["params"].items())
        desc = EFFECTS_CATALOG.get(fx["name"], {}).get("description", "")
        print(f"  [{i}] {fx['name']:<12} {params_str:<30} {desc}")


def cmd_clear(args):
    state.require_project()
    track = state.require_track(args.track_id)
    state.clear_effects(args.track_id)
    print(f"Cleared all effects from track {args.track_id} '{track['name']}'")


def cmd_preview(args):
    state.require_project()
    track = state.require_track(args.track_id)
    if not track["source"]:
        print(f"Error: Track {args.track_id} has no audio source", file=sys.stderr)
        sys.exit(1)

    # Build sox effects inline (same logic as play.py)
    from cornwall.sox_effects import build_sox_effects

    cmd = ["play", track["source"]]
    if track["volume"] != 1.0:
        cmd += ["vol", str(track["volume"])]
    cmd += build_sox_effects(args.track_id)

    print(f"Preview: track {args.track_id} '{track['name']}' with {len(state.get_track_effects(args.track_id))} effects")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: 'play' (SoX) not found. Install with: brew install sox", file=sys.stderr)
        sys.exit(1)


def cmd_catalog(args):
    print("Available effects:\n")
    for name, info in EFFECTS_CATALOG.items():
        print(f"  {name:<12} {info['description']}")
        for pname, pdesc in info["params"].items():
            print(f"    {pname:<16} {pdesc}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Manage effects chains on Cornwall tracks")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("add", help="Add an effect to a track")
    p.add_argument("track_id", type=int, help="Track ID")
    p.add_argument("effect", help="Effect name (see 'fx.py catalog')")
    p.add_argument("params", nargs="*", help="Parameters as key=value pairs")

    p = sub.add_parser("remove", help="Remove an effect by index")
    p.add_argument("track_id", type=int, help="Track ID")
    p.add_argument("index", type=int, help="Effect index in chain")

    p = sub.add_parser("list", help="List effects on a track")
    p.add_argument("track_id", type=int, help="Track ID")

    p = sub.add_parser("clear", help="Clear all effects from a track")
    p.add_argument("track_id", type=int, help="Track ID")

    p = sub.add_parser("preview", help="Play a track with effects applied")
    p.add_argument("track_id", type=int, help="Track ID")

    sub.add_parser("catalog", help="Show available effects and parameters")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmds = {
        "add": cmd_add, "remove": cmd_remove, "list": cmd_list,
        "clear": cmd_clear, "preview": cmd_preview, "catalog": cmd_catalog,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
