# Cornwall

A DAW where the interface is a conversation.

Cornwall is named after the birthplace of Richard D. James. It is a collection of open-source CLI audio tools orchestrated by Claude Code. There is no GUI. You talk to Claude, Claude runs the tools, you listen through your headphones.

## Getting Started

```bash
# Install dependencies
brew install sox csound fluid-synth ffmpeg sendmidi receivemidi

# Optional but recommended
pip install pedalboard

# Start the DAW
claude
```

Then just talk:

> "Create a new project at 120 BPM"
> "Load a mandolin sample on track 1"
> "Add reverb to track 2, long tail, mostly wet"
> "Solo track 1 and play from bar 8"
> "Render the mix to wav"

Claude reads the CLAUDE.md, discovers the scripts, and handles the rest. If a tool isn't installed yet, ask Claude to install it.

## Philosophy

- **No GUI.** Sound goes to headphones. Everything else is text.
- **No special syntax.** No slash commands to memorize. Just natural language.
- **Scripts are the truth.** Every capability is a script in `scripts/` with `--help`. Claude discovers them at runtime.
- **Open source tools.** SoX, Csound, SuperCollider, Pedalboard, FFmpeg, and dozens more. Nothing proprietary, nothing paid.
- **Claude is disposable.** Any Claude instance can pick up where another left off. The project state is in files, not in a conversation.
