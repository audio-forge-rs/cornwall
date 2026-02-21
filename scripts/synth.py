#!/usr/bin/env python3
"""Generate sounds from scratch using synthesis.

Usage: synth.py <command> [options]

Commands:
  tone      Generate a simple waveform
  noise     Generate noise
  chord     Generate a chord (multiple tones mixed)
  drum      Generate a drum hit
  bytebeat  Generate audio from a bytebeat expression
  csound    Render a Csound .csd file
  play      Generate and play immediately (wraps any command)

synth.py tone [options]
  --wave <type>       Waveform: sine, square, sawtooth, triangle (default: sine)
  --freq <hz>         Frequency in Hz (default: 440)
  --note <name>       Note name instead of freq, e.g. C4, A#3, Bb5
  --duration <sec>    Duration in seconds (default: 2)
  --volume <0-1>      Volume (default: 0.8)
  --output <file>     Output file (default: state dir temp file)
  --play              Play after generating

synth.py noise [options]
  --type <type>       Noise type: white, pink, brown, tpdf (default: white)
  --duration <sec>    Duration in seconds (default: 2)
  --volume <0-1>      Volume (default: 0.5)
  --output <file>     Output file
  --play              Play after generating

synth.py chord [options]
  --notes <n1,n2,...> Comma-separated note names, e.g. C4,E4,G4
  --freqs <f1,f2,...> Comma-separated frequencies
  --wave <type>       Waveform (default: sine)
  --duration <sec>    Duration (default: 2)
  --volume <0-1>      Volume (default: 0.8)
  --output <file>     Output file
  --play              Play after generating

synth.py drum <type> [options]
  type: kick, snare, hat, clap, tom
  --output <file>     Output file
  --play              Play after generating

synth.py bytebeat <expression> [options]
  --sample-rate <hz>  Sample rate (default: 8000)
  --duration <sec>    Duration (default: 10)
  --output <file>     Output file
  --play              Play after generating

synth.py csound <file.csd> [options]
  --output <file>     Output file (overrides -o in .csd)
  --play              Play after rendering

Examples:
  synth.py tone --note A4 --wave sine --duration 3 --play
  synth.py tone --freq 261.63 --wave sawtooth --output bass.wav
  synth.py chord --notes C4,E4,G4 --wave triangle --play
  synth.py noise --type pink --duration 5 --play
  synth.py drum kick --play
  synth.py drum snare --output snare.wav
  synth.py bytebeat "t*(t>>12&t>>8)&63+t" --play
  synth.py csound ambient.csd --play
"""

import argparse
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cornwall import state

# Note name to frequency mapping (A4 = 440Hz)
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_ALIASES = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}

SAMPLE_RATE = 44100


def note_to_freq(note: str) -> float:
    """Convert note name (e.g., 'A4', 'C#3', 'Bb5') to frequency."""
    name = note[:-1]
    octave = int(note[-1])
    name = NOTE_ALIASES.get(name, name)
    if name not in NOTE_NAMES:
        raise ValueError(f"Unknown note: {note}")
    semitone = NOTE_NAMES.index(name) - NOTE_NAMES.index("A")
    semitone += (octave - 4) * 12
    return 440.0 * (2.0 ** (semitone / 12.0))


def _default_output() -> str:
    state._ensure_dirs()
    fd, path = tempfile.mkstemp(suffix=".wav", dir=str(state.STATE_DIR), prefix="synth_")
    os.close(fd)
    return path


def _play_file(path: str):
    try:
        subprocess.run(["play", path], check=True)
    except FileNotFoundError:
        subprocess.run(["afplay", path], check=True)


def _sox_synth(output: str, duration: float, volume: float, synth_args: list[str]):
    """Use SoX to generate synthesis."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "sox", "-n", "-r", str(SAMPLE_RATE), "-b", "16", output,
        "synth", str(duration),
    ] + synth_args + ["vol", str(volume)]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: 'sox' not found. Install with: brew install sox", file=sys.stderr)
        sys.exit(1)


def _write_wav(path: str, samples: list[int], sample_rate: int = SAMPLE_RATE, sample_width: int = 2):
    """Write raw samples to a WAV file."""
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        if sample_width == 1:
            data = struct.pack(f"{len(samples)}B", *[max(0, min(255, s)) for s in samples])
        else:
            data = struct.pack(f"{len(samples)}h", *[max(-32768, min(32767, s)) for s in samples])
        wf.writeframes(data)


def cmd_tone(args):
    output = args.output or _default_output()
    freq = args.freq
    if args.note:
        try:
            freq = note_to_freq(args.note)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    _sox_synth(output, args.duration, args.volume, [args.wave, str(freq)])
    print(f"Generated {args.wave} tone at {freq:.1f}Hz, {args.duration}s -> {output}")
    if args.play:
        _play_file(output)


def cmd_noise(args):
    output = args.output or _default_output()

    noise_map = {
        "white": "whitenoise",
        "pink": "pinknoise",
        "brown": "brownnoise",
        "tpdf": "tpdfnoise",
    }
    sox_type = noise_map.get(args.type)
    if not sox_type:
        print(f"Error: Unknown noise type: {args.type}. Use: white, pink, brown, tpdf", file=sys.stderr)
        sys.exit(1)

    _sox_synth(output, args.duration, args.volume, [sox_type])
    print(f"Generated {args.type} noise, {args.duration}s -> {output}")
    if args.play:
        _play_file(output)


def cmd_chord(args):
    output = args.output or _default_output()

    freqs = []
    if args.notes:
        for note in args.notes.split(","):
            try:
                freqs.append(note_to_freq(note.strip()))
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.freqs:
        freqs = [float(f.strip()) for f in args.freqs.split(",")]
    else:
        print("Error: Provide --notes or --freqs", file=sys.stderr)
        sys.exit(1)

    if not freqs:
        print("Error: No frequencies specified", file=sys.stderr)
        sys.exit(1)

    # SoX can layer multiple synths with the : separator
    synth_args = []
    for i, freq in enumerate(freqs):
        if i > 0:
            synth_args.append(":")
            synth_args.append("synth")
            synth_args.append(str(args.duration))
        synth_args.append(args.wave)
        synth_args.append(str(freq))

    # Mix by creating individual files and combining
    with tempfile.TemporaryDirectory() as tmpdir:
        parts = []
        per_volume = args.volume / math.sqrt(len(freqs))  # Equal-power mixing
        for i, freq in enumerate(freqs):
            part = os.path.join(tmpdir, f"tone_{i}.wav")
            _sox_synth(part, args.duration, per_volume, [args.wave, str(freq)])
            parts.append(part)

        subprocess.run(["sox", "-m"] + parts + [output], check=True)

    note_str = args.notes or ",".join(f"{f:.1f}Hz" for f in freqs)
    print(f"Generated {args.wave} chord [{note_str}], {args.duration}s -> {output}")
    if args.play:
        _play_file(output)


def cmd_drum(args):
    output = args.output or _default_output()
    drum_type = args.type

    if drum_type == "kick":
        # Sine wave pitch sweep from 150Hz to 40Hz with fast decay
        _sox_synth(output, 0.5, 0.9, [
            "sine", "150-40",
        ])
        # Add a click at the start
        with tempfile.TemporaryDirectory() as tmpdir:
            click = os.path.join(tmpdir, "click.wav")
            _sox_synth(click, 0.01, 0.9, ["noise", "whitenoise"])
            body = os.path.join(tmpdir, "body.wav")
            os.rename(output, body)
            subprocess.run([
                "sox", body, output,
                "fade", "t", "0", "0.5", "0.4",
            ], check=True)

    elif drum_type == "snare":
        with tempfile.TemporaryDirectory() as tmpdir:
            tone_part = os.path.join(tmpdir, "tone.wav")
            _sox_synth(tone_part, 0.2, 0.7, ["sine", "200"])
            noise_part = os.path.join(tmpdir, "noise.wav")
            _sox_synth(noise_part, 0.2, 0.5, ["whitenoise"])
            # Mix and apply fade
            mixed = os.path.join(tmpdir, "mixed.wav")
            subprocess.run(["sox", "-m", tone_part, noise_part, mixed], check=True)
            subprocess.run([
                "sox", mixed, output,
                "fade", "t", "0", "0.2", "0.15",
                "highpass", "200",
            ], check=True)

    elif drum_type == "hat":
        _sox_synth(output, 0.1, 0.5, ["whitenoise"])
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = os.path.join(tmpdir, "hat.wav")
            os.rename(output, tmp)
            subprocess.run([
                "sox", tmp, output,
                "fade", "t", "0", "0.1", "0.08",
                "highpass", "7000",
            ], check=True)

    elif drum_type == "clap":
        _sox_synth(output, 0.15, 0.6, ["whitenoise"])
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = os.path.join(tmpdir, "clap.wav")
            os.rename(output, tmp)
            subprocess.run([
                "sox", tmp, output,
                "fade", "t", "0", "0.15", "0.12",
                "bandpass", "1500", "2000",
            ], check=True)

    elif drum_type == "tom":
        _sox_synth(output, 0.4, 0.8, ["sine", "120-60"])
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = os.path.join(tmpdir, "tom.wav")
            os.rename(output, tmp)
            subprocess.run([
                "sox", tmp, output,
                "fade", "t", "0", "0.4", "0.3",
            ], check=True)

    else:
        print(f"Error: Unknown drum type: {drum_type}. Use: kick, snare, hat, clap, tom", file=sys.stderr)
        sys.exit(1)

    print(f"Generated {drum_type} -> {output}")
    if args.play:
        _play_file(output)


def cmd_bytebeat(args):
    output = args.output or _default_output()
    expr = args.expression
    sr = args.sample_rate
    num_samples = int(sr * args.duration)

    # Bytebeat: evaluate expression for each sample where t is the sample index
    # Output is 8-bit unsigned
    samples = []
    for t in range(num_samples):
        try:
            # Provide t and common operations
            val = eval(expr, {"__builtins__": {}}, {"t": t, "abs": abs, "int": int})
            samples.append(int(val) & 0xFF)
        except Exception:
            samples.append(128)

    _write_wav(output, samples, sample_rate=sr, sample_width=1)
    print(f"Generated bytebeat ({len(samples)} samples at {sr}Hz) -> {output}")
    if args.play:
        _play_file(output)


def cmd_csound(args):
    csd_file = Path(args.file).expanduser().resolve()
    if not csd_file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    output = args.output or _default_output()
    cmd = ["csound", "-o", output, str(csd_file)]

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: 'csound' not found. Install with: brew install csound", file=sys.stderr)
        sys.exit(1)

    print(f"Rendered Csound: {csd_file.name} -> {output}")
    if args.play:
        _play_file(output)


def main():
    parser = argparse.ArgumentParser(description="Generate sounds from scratch using synthesis")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("tone", help="Generate a simple waveform")
    p.add_argument("--wave", default="sine", choices=["sine", "square", "sawtooth", "triangle"],
                   help="Waveform type (default: sine)")
    p.add_argument("--freq", type=float, default=440, help="Frequency in Hz (default: 440)")
    p.add_argument("--note", help="Note name, e.g. C4, A#3, Bb5")
    p.add_argument("--duration", type=float, default=2, help="Duration in seconds (default: 2)")
    p.add_argument("--volume", type=float, default=0.8, help="Volume 0-1 (default: 0.8)")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after generating")

    p = sub.add_parser("noise", help="Generate noise")
    p.add_argument("--type", default="white", help="Noise type: white, pink, brown, tpdf (default: white)")
    p.add_argument("--duration", type=float, default=2, help="Duration in seconds (default: 2)")
    p.add_argument("--volume", type=float, default=0.5, help="Volume 0-1 (default: 0.5)")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after generating")

    p = sub.add_parser("chord", help="Generate a chord")
    p.add_argument("--notes", help="Comma-separated note names, e.g. C4,E4,G4")
    p.add_argument("--freqs", help="Comma-separated frequencies")
    p.add_argument("--wave", default="sine", help="Waveform type (default: sine)")
    p.add_argument("--duration", type=float, default=2, help="Duration in seconds (default: 2)")
    p.add_argument("--volume", type=float, default=0.8, help="Volume 0-1 (default: 0.8)")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after generating")

    p = sub.add_parser("drum", help="Generate a drum hit")
    p.add_argument("type", choices=["kick", "snare", "hat", "clap", "tom"], help="Drum type")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after generating")

    p = sub.add_parser("bytebeat", help="Generate audio from a bytebeat expression")
    p.add_argument("expression", help="Bytebeat expression using 't' as sample index")
    p.add_argument("--sample-rate", type=int, default=8000, help="Sample rate (default: 8000)")
    p.add_argument("--duration", type=float, default=10, help="Duration in seconds (default: 10)")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after generating")

    p = sub.add_parser("csound", help="Render a Csound .csd file")
    p.add_argument("file", help="Path to .csd file")
    p.add_argument("--output", help="Output WAV file")
    p.add_argument("--play", action="store_true", help="Play after rendering")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmds = {
        "tone": cmd_tone, "noise": cmd_noise, "chord": cmd_chord,
        "drum": cmd_drum, "bytebeat": cmd_bytebeat, "csound": cmd_csound,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
