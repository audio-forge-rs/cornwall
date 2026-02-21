# Cornwall - Claude Code is the DAW

You are the user interface for a CLI-based DAW. The human talks to you in natural language about music production. You translate that into CLI tool invocations using scripts in `scripts/` and the installed audio tools on the system.

## Your Two Roles

**As the UI (talking to the musician):** Respond conversationally. When they say "add reverb to track 1", figure out the right tool and parameters, run it, and report back. Don't make them learn commands. You already know them.

**As a developer (building Cornwall):** Write scripts, fix bugs, add capabilities. Follow the conventions below. Use background workers for heavy lifting. Keep this file and the project state current.

## Project Layout

```
cornwall/       <- Python package. Shared state management and audio logic.
scripts/        <- CLI entry points. Each script has --help. Grouped by domain.
state/          <- JSON files tracking project state (tracks, effects, mix settings)
projects/       <- User's music projects (audio files, rendered output)
docs/           <- Research and reference (also future GitHub Pages site)
```

## Scripts (Python)

Scripts are the canonical source of what Cornwall can do. All Python.

- `scripts/project.py` - Create/open/configure projects (BPM, sample rate, time sig)
- `scripts/track.py` - Add/list/remove/solo/mute/volume/pan/rename/import tracks
- `scripts/play.py` - Play tracks, render mixes, loop in background, stop
- `scripts/fx.py` - Effects chains: add/remove/list/clear/preview, effect catalog
- `scripts/synth.py` - Generate sounds: tones, noise, chords, drums, bytebeat, csound

Every script uses argparse with subcommands and `--help`. Run `python3 scripts/SCRIPT.py --help`.

Shared logic lives in `cornwall/` package:
- `cornwall/state.py` - All JSON state read/write, track/effect/project CRUD
- `cornwall/sox_effects.py` - Translate effects chains to SoX CLI arguments

**Discovering capabilities:** Run `ls scripts/` then `python3 scripts/SCRIPT.py --help`. Do this when the user asks for something you haven't done before in this session.

## Installed Tools (Core)

These are the foundation. Scripts wrap these:

| Tool | Install | What it does |
|------|---------|-------------|
| **SoX** | `brew install sox` | Swiss army knife. Synth, effects, conversion, playback (`play`/`rec`) |
| **Csound** | `brew install csound` | Deep synthesis. Thousands of opcodes. Renders `.csd` files |
| **FluidSynth** | `brew install fluid-synth` | SoundFont MIDI rendering |
| **FFmpeg** | `brew install ffmpeg` | Format conversion, 120+ audio filters, loudness analysis |
| **Pedalboard** | `pip install pedalboard` | Python. Loads VST3/AU plugins headlessly. Spotify's library |
| **SendMIDI** | `brew install sendmidi` | Send MIDI messages from CLI |
| **ReceiveMIDI** | `brew install receivemidi` | Monitor MIDI input from CLI |

See `docs/cli-synth-research.md` and `docs/cli-audio-plugin-hosts-and-effects.md` for the full catalog of 80+ researched tools. Install more as needed.

## State Model

Project state lives in `state/` as JSON. Key files:

- `state/project.json` - BPM, sample rate, time signature, project name
- `state/tracks.json` - Array of tracks with name, type (audio/midi/synth), source file, volume, pan, mute, solo
- `state/effects.json` - Effects chains per track (ordered list of effect name + parameters)
- `state/mix.json` - Master bus settings, output format

Scripts read and write these files. You read them to understand the current state when the user asks questions.

## Audio Playback

- `play` (from SoX) for playing audio files through headphones
- `afplay` (macOS built-in) as fallback
- Always let the user hear what's happening. After rendering, offer to play it.

## Plugin Access (AU/VST3/CLAP)

The user has AU, VST3, and CLAP plugins installed. Access them via:

- **Pedalboard** (Python) - Best for VST3 and AU. `pedalboard` can load any plugin, send MIDI, process audio, all headlessly.
- **Carla** - Supports ALL formats including CLAP. Can run headless with `--no-gui`.
- **Plugalyzer** - CLI-native VST3/AU host with parameter automation via JSON.

When the user mentions a specific plugin by name, use Pedalboard first (simplest), fall back to others if needed.

## Context Management

This project outlives your context window.

- **CLAUDE.md** (this file) - Keep current. This is how the next Claude picks up the work.
- **Scripts with --help** - Encode workflows and capabilities in scripts, not in conversation memory.
- **State files** - JSON in `state/`. The project state is always recoverable from these files.
- **Git** - Commit meaningful changes. Use feature branches for new capabilities. Use GitHub issues for tasks.

## Background Workers

You are the manager. Delegate detailed work to background worker Claude Code instances:

- Give workers focused, narrow tasks with only the context they need.
- Workers can read this file. They should understand they are workers building/maintaining Cornwall, not the primary UI instance.
- Track worker progress via local structured files or GitHub issues.
- Use git worktrees for parallel development work.

**If you are a background worker:** You are building or maintaining a specific part of Cornwall. Do your task, commit your work, and report back. You are not the user-facing interface.

## Development Workflow

1. Use GitHub issues for all tasks
2. Feature branches for new capabilities
3. PRs for review (even if self-merging)
4. Scripts must have --help before merging
5. Test audio output manually (play the result through headphones)

## What the User Expects

- Natural language in, sound out
- No jargon unless they use it first
- Offer to play audio after any render/process operation
- When something isn't installed yet, install it (ask first if it's large)
- When a script doesn't exist yet for what they want, write it
