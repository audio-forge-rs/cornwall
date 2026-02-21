# CLI Music Synthesizers & Sound Generators Research

Comprehensive survey of open-source, command-line-controllable music synthesis tools for macOS.
Emphasis on programmatic control, terminal workflows, and the weird/experimental end of the spectrum.

---

## Table of Contents

1. [Heavyweight Languages & Environments](#1-heavyweight-languages--environments)
2. [Live Coding Environments](#2-live-coding-environments)
3. [Terminal-Native Synths & Trackers](#3-terminal-native-synths--trackers)
4. [Unix Workhorses](#4-unix-workhorses)
5. [Stack-Based / Esoteric Languages](#5-stack-based--esoteric-languages)
6. [Text-Based Composition Languages](#6-text-based-composition-languages)
7. [Python Audio Ecosystem](#7-python-audio-ecosystem)
8. [Rust Audio Ecosystem](#8-rust-audio-ecosystem)
9. [AI / Neural Audio Generation](#9-ai--neural-audio-generation)
10. [Bytebeat & Noise Generators](#10-bytebeat--noise-generators)
11. [Quick Reference Matrix](#11-quick-reference-matrix)
12. [Audio Analysis & Feature Extraction](#12-audio-analysis--feature-extraction)
13. [Audio Source Separation (AI/ML)](#13-audio-source-separation-aiml)
14. [Audio Format Conversion & Processing](#14-audio-format-conversion--processing)
15. [Loudness Normalization & Metering](#15-loudness-normalization--metering)
16. [Terminal Audio Visualization](#16-terminal-audio-visualization)
17. [CLI Music Theory Tools](#17-cli-music-theory-tools)
18. [MIDI CLI Tools](#18-midi-cli-tools)
19. [Algorithmic & Generative Music](#19-algorithmic--generative-music)
20. [Music Library Management & Metadata](#20-music-library-management--metadata)
21. [Terminal DAW Projects](#21-terminal-daw-projects)
22. [Terminal Music Players](#22-terminal-music-players)
23. [Additional Esoteric & Notable Tools](#23-additional-esoteric--notable-tools)

---

## 1. Heavyweight Languages & Environments

### Csound

- **GitHub:** https://github.com/csound/csound
- **What:** The grandfather of all software synthesizers. A sound design, music synthesis, and signal processing engine. Csound programs (`.csd` files) define instruments and scores in a text format, compiled and rendered from the command line.
- **Install:** `brew install csound`
- **License:** LGPL-2.1+
- **Output:** Real-time speakers (via `-odac` flag) or render to file (WAV, AIFF, etc.)
- **CLI Examples:**
  ```bash
  # Render a .csd file to speakers
  csound -odac mypiece.csd

  # Render to WAV file
  csound -o output.wav mypiece.csd

  # Use PortAudio real-time output on macOS
  csound -+rtaudio=portaudio -odac mypiece.csd

  # Set sample rate and control rate
  csound -odac -r 48000 -k 4800 mypiece.csd
  ```
- **Notes:** Thousands of opcodes for every synthesis technique imaginable. The `.csd` format is plain text (XML-like wrapper around orchestra and score sections). Extremely well-documented with decades of academic and artistic use. Can be scripted, piped, and automated. One of the most powerful audio programming environments in existence.

---

### SuperCollider (sclang / scsynth)

- **GitHub:** https://github.com/supercollider/supercollider
- **What:** A platform for audio synthesis and algorithmic composition. Three components: `scsynth` (real-time audio server), `sclang` (interpreted programming language / client), and `scide` (IDE). The server/language split means you can drive synthesis from the terminal.
- **Install:** `brew install --cask supercollider` (GUI app bundle), or build from source for headless
- **License:** GPL-3.0+
- **Output:** Real-time speakers (via scsynth audio server) or render to file
- **CLI Examples:**
  ```bash
  # Run sclang from terminal (after adding to PATH)
  ln -s /Applications/SuperCollider.app/Contents/MacOS/sclang /usr/local/bin/sclang

  # Execute a SuperCollider script
  sclang my_script.scd

  # Pipe code to sclang
  echo '{ SinOsc.ar(440, 0, 0.2) }.play; 3.wait; 0.exit;' | sclang

  # Boot scsynth server directly
  scsynth -u 57110
  ```
- **Notes:** The backbone of much of the live coding world. TidalCycles, FoxDot/Renardo, Sardine, and Overtone all use SuperCollider's audio engine under the hood. `sclang` can run in terminal but macOS builds currently require Qt (generates warnings in headless mode). Extremely powerful synthesis engine with real-time capability.

---

### ChucK

- **GitHub:** https://github.com/ccrma/chuck
- **What:** A strongly-timed, concurrent audio programming language for real-time synthesis, composition, and performance. Created at Princeton/Stanford (CCRMA). Unique time-based concurrency model where you explicitly advance time.
- **Install:** `brew install chuck`
- **License:** MIT / GPL-2.0+ (dual-licensed)
- **Output:** Real-time speakers (default) or render to file
- **CLI Examples:**
  ```bash
  # Play a ChucK program
  chuck my_synth.ck

  # Run multiple shreds (concurrent programs)
  chuck synth.ck drums.ck effects.ck

  # Run with specific audio settings
  chuck --srate48000 --bufsize512 my_synth.ck

  # Add code on-the-fly to a running ChucK VM
  chuck --loop &
  chuck + new_shred.ck
  chuck - 1  # remove shred 1
  chuck --replace 1 updated_shred.ck
  ```
- **Notes:** The on-the-fly programming model is killer -- you can add, remove, and replace concurrent audio programs while the VM is running. Great for live performance and experimentation. The `=>` (ChucK) operator for connecting unit generators is elegant. Supports MIDI, OSC, HID devices.

---

### Faust

- **GitHub:** https://github.com/grame-cncm/faust
- **What:** A functional programming language for real-time signal processing and synthesis. The compiler translates DSP specifications into highly optimized C++, C, LLVM IR, WebAssembly, and more. You write the DSP algorithm; Faust generates deployable code for dozens of targets.
- **Install:** `brew install faust`
- **License:** GPL-2.0 (compiler); LGPL with exception (libraries -- generated code can be any license)
- **Output:** Depends on target architecture. Can generate standalone apps that output to speakers, or render to file.
- **CLI Examples:**
  ```bash
  # Compile Faust DSP to a command-line ALSA program (Linux)
  faust2alsaconsole synth.dsp

  # Compile to a CoreAudio app (macOS)
  faust2caqt synth.dsp

  # Generate C++ code
  faust -lang cpp -o synth.cpp synth.dsp

  # Generate block diagram (SVG)
  faust2svg synth.dsp

  # Debug with sample plotting
  faust2plot synth.dsp
  ```
- **Notes:** Faust is a meta-tool -- it generates code for other platforms. The functional approach to DSP is mathematically elegant. The fact that generated code is not bound by the compiler's GPL is a major practical advantage. Excellent for creating audio plugins, embedded systems, and web audio. The `faust2...` scripts cover an enormous range of targets.

---

### Pure Data (Pd) / libpd

- **GitHub:** https://github.com/pure-data/pure-data (Pd), https://github.com/libpd/libpd (embeddable library)
- **What:** A visual programming language for multimedia. Despite being primarily graphical, Pd can run headless from the command line (`pd -nogui`), making it scriptable. libpd turns Pd into an embeddable audio synthesis library.
- **Install:** `brew install --cask pd` (GUI), or build from source for headless
- **License:** BSD (Standard Improved BSD License)
- **Output:** Real-time speakers or render to file
- **CLI Examples:**
  ```bash
  # Run a Pd patch headless (no GUI)
  pd -nogui -audiodev 1 -r 44100 my_patch.pd

  # Run with specific buffer settings
  pd -nogui -audiobuf 50 -blocksize 64 my_patch.pd

  # No audio output (offline rendering)
  pd -nogui -nosound my_patch.pd
  ```
- **Notes:** Pd's visual patching paradigm is powerful but the headless mode means you can deploy patches as command-line audio processors. libpd is particularly interesting for embedding Pd's synthesis engine in other applications. The ecosystem of Pd externals is vast.

---

### Nyquist

- **GitHub:** https://github.com/vijayrudraraju/nyquist (community mirror)
- **Official:** https://www.cs.cmu.edu/~music/nyquist/
- **What:** A Lisp-based language for sound synthesis and music composition by Roger Dannenberg (CMU). Extends Lisp/SAL with audio primitives. Also powers Audacity's scripting via Nyquist Prompt.
- **Install:** Build from source, or use via Audacity
- **License:** BSD-style
- **Output:** Real-time speakers or render to file
- **CLI Examples:**
  ```bash
  # Run Nyquist interpreter
  ny

  # Execute a Nyquist script
  ny < my_composition.lsp

  # Inside the REPL
  (play (osc 60))           ; play middle C
  (play (stretch 4 (osc 60)))  ; 4-second middle C
  ```
- **Notes:** Deep Lisp heritage. The functional approach to audio is elegant -- sound is a first-class data type. Less actively developed than the other heavyweights but academically respected and still functional.

---

## 2. Live Coding Environments

### TidalCycles

- **GitHub:** https://github.com/tidalcycles/Tidal
- **Website:** https://tidalcycles.org
- **What:** A domain-specific language embedded in Haskell for live coding musical patterns. Uses SuperCollider's SuperDirt as its audio engine. The pattern language is extraordinarily expressive for rhythmic and melodic manipulation.
- **Install:**
  ```bash
  # Install prerequisites
  brew install ghcup supercollider
  ghcup install ghc
  cabal update
  cabal install tidal --lib

  # Or use the bootstrap script
  curl https://raw.githubusercontent.com/tidalcycles/tidal-bootstrap/master/tidal-bootstrap.command -sSf | sh
  ```
- **License:** GPL-3.0
- **Output:** Real-time speakers (via SuperDirt/SuperCollider)
- **CLI Examples:**
  ```bash
  # Start GHCi with Tidal loaded (typically from a text editor)
  ghci -e ':script BootTidal.hs'

  # In the Tidal REPL
  d1 $ sound "bd sn bd sn"
  d1 $ sound "bd*4" # speed (run 4)
  d2 $ n "0 3 5 7" # sound "superpiano"
  hush  -- silence everything
  ```
- **Notes:** TidalCycles is the gold standard for pattern-based live coding. The mini-notation for rhythmic patterns is incredibly dense and powerful. Typically driven from Vim (vim-tidal), Emacs, VS Code, or Pulsar. Requires SuperCollider + SuperDirt running as the audio backend. Aphex Twin aesthetic territory for sure.

---

### Sardine

- **GitHub:** https://github.com/Bubobubobubobubo/sardine
- **What:** Python's missing "algorave" module. A live coding library that turns your Python interpreter into a musical instrument. Sends MIDI, OSC, and/or SuperCollider messages.
- **Install:**
  ```bash
  pip install sardine-system
  # Also needs SuperCollider + SuperDirt for audio output
  ```
- **License:** GPL-3.0
- **Output:** Real-time speakers (via SuperDirt/SuperCollider, MIDI, or OSC)
- **CLI Examples:**
  ```python
  # In the Python REPL after importing sardine
  from sardine import *

  @swim
  def pattern(p=0.5, i=0):
      D('bd', speed=1, i=i)
      again(pattern, p=0.5, i=i+1)

  # Melodic pattern
  @swim
  def melody(p=0.25, i=0):
      N("C4 E4 G4 B4", i=i)
      again(melody, p=0.25, i=i+1)
  ```
- **Notes:** The most Pythonic approach to live coding. Still in active early development but already used in performances and algoraves. Python 3.10+ required. Modular architecture with swappable clocks, parsers, and handlers.

---

### Renardo (FoxDot fork)

- **GitHub:** https://github.com/e-lie/renardo
- **What:** A modernized fork of FoxDot, the Python live coding environment. Provides a high-level, user-friendly abstraction over SuperCollider for making music with Python code.
- **Install:**
  ```bash
  pip install renardo
  # Requires SuperCollider running
  ```
- **License:** CC-BY-SA-4.0 (inherited from FoxDot)
- **Output:** Real-time speakers (via SuperCollider)
- **CLI Examples:**
  ```python
  # Start Renardo from command line
  # renardo

  # In the environment
  p1 >> pluck([0, 2, 4, 7], dur=0.5)
  p2 >> bass([0, 3, 5], dur=1)
  d1 >> play("x-o-")
  Clock.bpm = 140
  ```
- **Notes:** More actively maintained than the original FoxDot (which is no longer actively developed). Friendly syntax designed for musicians who do not necessarily know how to program.

---

### Overtone

- **GitHub:** https://github.com/overtone/overtone
- **What:** Collaborative programmable music in Clojure. Provides a Clojure API to the SuperCollider synthesis engine plus a growing library of musical functions (scales, chords, rhythms, arpeggiators).
- **Install:**
  ```bash
  # Add to deps.edn: overtone/overtone {:mvn/version "0.16.3331"}
  # Then in a Clojure REPL:
  clj
  (require '[overtone.live :refer :all])
  ```
- **License:** MIT
- **Output:** Real-time speakers (via SuperCollider's scsynth)
- **CLI Examples:**
  ```clojure
  ;; In a Clojure REPL
  (use 'overtone.live)
  (demo (sin-osc 440))
  (definst my-synth [freq 440]
    (* 0.3 (saw freq)))
  (my-synth 220)
  (stop)
  ```
- **Notes:** Brings the power of Clojure's REPL-driven development to audio. 6100+ GitHub stars. The Clojure ecosystem means you get all of Java/JVM interop. Great for algorithmic composition and interactive exploration.

---

### Extempore

- **GitHub:** https://github.com/digego/extempore
- **What:** A cyber-physical programming environment for live coding. Two integrated languages: Scheme (with extensions) and xtlang (a statically typed, C-like language for real-time DSP). Can JIT-compile audio DSP code with near-C performance.
- **Install:**
  ```bash
  # Download binary release or build from source
  git clone https://github.com/digego/extempore
  mkdir extempore/build && cd extempore/build
  cmake -DASSETS=ON ..
  make
  ```
- **License:** BSD
- **Output:** Real-time speakers
- **CLI Examples:**
  ```bash
  # Start extempore server
  ./extempore

  # Then connect from a text editor and evaluate:
  (bind-func dsp:DSP
    (lambda (in time chan dat)
      (* 0.3 (sin (* 2.0 3.14159 440.0 (/ (i64tof time) 44100.0))))))
  (dsp:set! dsp)
  ```
- **Notes:** The xtlang component compiles to native code at runtime -- meaning you can write and modify DSP algorithms in real-time with performance close to hand-written C. This is remarkable. Developed by Andrew Sorensen, originally from Impromptu. Supports VSCode and Emacs integration.

---

### Sonic Pi (via CLI tools)

- **GitHub:** https://github.com/sonic-pi-net/sonic-pi
- **CLI tools:** https://github.com/lpil/sonic-pi-tool (Rust), https://github.com/emlyn/sonic-pi-tool (Python)
- **What:** An education-focused live coding music synth. While primarily GUI-based, third-party CLI tools allow sending code to a running Sonic Pi instance from the command line.
- **Install:**
  ```bash
  # Sonic Pi itself: download from sonic-pi.net
  # Rust CLI tool:
  cargo install sonic-pi-tool
  # Python CLI tool:
  pip install sonic-pi-tool
  ```
- **License:** MIT (Sonic Pi); MIT (CLI tools)
- **Output:** Real-time speakers
- **CLI Examples:**
  ```bash
  # Send code to running Sonic Pi instance
  sonic-pi-tool eval "play 60; sleep 0.5; play 64; sleep 0.5; play 67"

  # Run from a file
  sonic-pi-tool eval-file my_song.rb

  # Pipe code in
  echo 'use_synth :prophet; play_pattern_timed [60,64,67], [0.25]' | sonic-pi-tool eval-stdin

  # Stop all running jobs
  sonic-pi-tool stop
  ```
- **Notes:** Sonic Pi needs to be running (it has its own audio server). The CLI tools communicate with it over OSC. Good for scripting and automation even though it is not natively headless.

---

## 3. Terminal-Native Synths & Trackers

### Cursynth

- **GitHub:** https://github.com/mtytel/cursynth
- **GNU page:** https://www.gnu.org/software/cursynth/
- **What:** A polyphonic, MIDI-enabled, subtractive synthesizer that runs entirely in your terminal using ncurses. Full ASCII interface with keyboard playback.
- **Install:** Build from source:
  ```bash
  git clone https://github.com/mtytel/cursynth
  cd cursynth
  autoreconf -i && ./configure && make && sudo make install
  ```
- **License:** GPL-3.0 (GNU project)
- **Output:** Real-time speakers (default audio device)
- **CLI Examples:**
  ```bash
  cursynth
  cursynth --buffer-size 256 --sample-rate 48000

  # Controls inside the TUI:
  # awsedftgyhujkolp;' = playable keyboard
  # `1234567890 = parameter sliders
  # up/down = navigate controls
  # F1 = help
  ```
- **Notes:** A GNU project. Matt Tytel (who later created Vital synth) made this. Pure terminal experience -- subtractive synthesis with oscillators, filters, envelopes. Connects to all MIDI devices automatically. Very Aphex Twin terminal aesthetic.

---

### PLEBTracker

- **GitHub:** https://github.com/danfrz/PLEBTracker
- **What:** An ncurses-based audio tracker program inspired by GoatTracker and MilkyTracker. All sounds are synthesized (no samples). Compose music in the classic tracker paradigm entirely in your terminal.
- **Install:** Build from source (requires ncurses, portaudio)
- **License:** GPL (implied from project structure)
- **Output:** Real-time speakers
- **Notes:** Tracker interface with wave tables, pulse tables, and filter tables. The instrument editor has ASCII volume envelope visualization. Supports arbitrary chromatic scales via preprocessor directives. A niche, beautiful terminal music tool.

---

### terminal-tracker

- **GitHub:** https://github.com/2bt/terminal-tracker
- **What:** A custom ncurses chiptune tracker. Minimal, purpose-built for chiptune composition in the terminal.
- **Install:** Build from source
- **License:** Not specified
- **Output:** Real-time speakers
- **Notes:** From the same developer who made fakesid (a SID-based chiptune tracker for Android). Extremely minimal and focused.

---

### Open Cubic Player

- **GitHub:** https://github.com/mywave82/opencubicplayer
- **What:** A music player/visualizer for tracked music formats (Amiga modules, S3M, IT, XM), chiptunes, and other demoscene formats. Has an ncurses mode for pure terminal use.
- **Install:** Build from source or check package managers
- **License:** GPL-2.0
- **Output:** Real-time speakers
- **CLI Examples:**
  ```bash
  ocp-curses mytrack.mod     # ncurses terminal mode
  ocp mytrack.xm             # graphical mode
  ```
- **Notes:** One of the oldest (circa 1994) and most comprehensive module players. The terminal visualization is gorgeous in a retro way. Supports an enormous range of tracked music formats from the demoscene era.

---

### textbeat

- **GitHub:** https://github.com/flipcoder/textbeat
- **What:** A plaintext music sequencer and MIDI shell with Vim playback integration. Write music in `.txbt` files using a tracker-like vertical notation with music theory shortcuts.
- **Install:**
  ```bash
  pip install textbeat
  ```
- **License:** MIT
- **Output:** MIDI output (needs a MIDI synth or DAW to produce sound)
- **CLI Examples:**
  ```bash
  # Play a textbeat file
  textbeat play mysong.txbt

  # Interactive MIDI shell
  textbeat shell
  ```
- **Notes:** Supports chord notation (Cmaj, 1min7, slash chords), tempo control, subdivisions. Has a companion Vim plugin (vim-textbeat). Designed for people who think in music theory. MIDI-only output means you need something else to actually produce sound.

---

## 4. Unix Workhorses

### SoX (Sound eXchange)

- **GitHub:** (SourceForge origin) https://sourceforge.net/projects/sox/ ; mirrors: https://github.com/rbouqueau/SoX
- **What:** The Swiss Army knife of audio processing. Can convert, record, play, and generate audio from the command line. The `synth` effect is a capable tone/waveform generator.
- **Install:** `brew install sox`
- **License:** GPL-2.0+ (sox/soxi programs); LGPL-2.1+ (libsox)
- **Output:** Both real-time speakers (via `play` command) and file output
- **CLI Examples:**
  ```bash
  # Play a 440Hz sine wave for 2 seconds
  play -n synth 2 sine 440

  # Generate a WAV file with a 300Hz sine
  sox -n output.wav synth 2.25 sine 300

  # Pink noise for 10 seconds
  play -n synth 10 pinknoise

  # Swept frequency (chirp) from 200Hz to 2000Hz
  play -n synth 3 sine 200:2000

  # Mix two waveforms
  sox -n output.wav synth 2 sine 300 synth 2 square mix 250

  # Generate a chord (stack sine waves)
  play -n synth 2 sine 261.63 synth 2 sine mix 329.63 synth 2 sine mix 392.00

  # DTMF tone
  sox -n dtmf.wav synth 0.1 sine 697 sine 1209 channels 1

  # Brown noise with fade
  play -n synth 5 brownnoise fade 0.5 5 0.5

  # Tremolo effect on a sine wave
  play -n synth 3 sine 440 tremolo 5 50

  # Pipe to another process
  sox -n -t raw -r 44100 -b 16 -c 1 -e signed - synth 2 sine 440 | my_processor
  ```
- **Notes:** SoX is probably the single most useful CLI audio tool. Available everywhere, does everything. The `play` command outputs to speakers; `sox` writes to files; `rec` records. The synth effect supports sine, square, triangle, sawtooth, trapezium, whitenoise, pinknoise, brownnoise. Can chain effects (reverb, echo, chorus, flanger, phaser, tremolo, overdrive, compand, etc.). Scripts beautifully -- you can compose entire pieces in bash. Not updated since 2015 but rock solid.

---

### FluidSynth

- **GitHub:** https://github.com/FluidSynth/fluidsynth
- **What:** A real-time software MIDI synthesizer based on the SoundFont 2 specifications. Feed it a SoundFont (.sf2/.sf3) and MIDI data, get audio out. No GUI -- pure command line and API.
- **Install:** `brew install fluid-synth`
- **License:** LGPL-2.1+
- **Output:** Real-time speakers or file rendering
- **CLI Examples:**
  ```bash
  # Play a MIDI file with a SoundFont
  fluidsynth /path/to/soundfont.sf2 myfile.mid

  # Render MIDI to WAV (fast, no real-time playback)
  fluidsynth -a file -F output.wav /path/to/soundfont.sf2 myfile.mid

  # Start as a MIDI server (listen for MIDI input)
  fluidsynth -a coreaudio -m coremidi /path/to/soundfont.sf2

  # Interactive shell
  fluidsynth -i /path/to/soundfont.sf2
  # Then type: noteon 0 60 100
  #            noteoff 0 60
  ```
- **Notes:** The standard open-source SoundFont synthesizer. Widely used as a backend for other tools. The interactive shell lets you send MIDI commands directly. Great for rendering MIDI compositions to audio files programmatically. Python wrapper available: `pip install midi2audio`.

---

### eSpeak-NG

- **GitHub:** https://github.com/espeak-ng/espeak-ng
- **What:** A text-to-speech synthesizer using formant synthesis. Not music per se, but the formant synthesis engine can be abused for musical/experimental sound generation. Think vocal synthesis, speech-as-instrument.
- **Install:** `brew install espeak-ng`
- **License:** GPL-3.0
- **Output:** Real-time speakers or file output
- **CLI Examples:**
  ```bash
  # Basic speech
  espeak-ng "hello world"

  # Vary pitch and speed for musical effect
  espeak-ng -p 80 -s 120 "aaaaaa"

  # Use voice variants for different timbres
  espeak-ng -v en+f3 "singing"

  # Output to WAV
  espeak-ng -w output.wav "test"
  ```
- **Notes:** Listed here for its experimental potential. Formant synthesis is inherently "musical" -- it is generating waveforms. Combined with pitch/speed manipulation, you can create alien vocal textures. The macOS built-in `say` command offers similar capabilities with different voices (try `say -v Cellos`).

---

## 5. Stack-Based / Esoteric Languages

### Sporth

- **GitHub:** https://github.com/PaulBatchelor/Sporth
- **What:** SoundPipe fORTH -- a small stack-based audio language inspired by Forth and PostScript. Essentially a text-based modular synthesis environment using a stack paradigm.
- **Install:** Build from source (requires Soundpipe library):
  ```bash
  git clone https://github.com/PaulBatchelor/Soundpipe
  cd Soundpipe && make && sudo make install
  git clone https://github.com/PaulBatchelor/Sporth
  cd Sporth && make && sudo make install
  ```
- **License:** MIT / Unlicense (dual-licensed)
- **Output:** Real-time speakers or file output
- **CLI Examples:**
  ```bash
  # Render a 5-second patch to WAV
  sporth -d 5s -o output.wav examples/dialtone.sp

  # Play a patch in real-time (pipe notation)
  echo "440 0.5 sine" | sporth

  # Example patch file (dialtone.sp):
  # 440 0.5 sine
  # 350 0.5 sine
  # add
  ```
- **Notes:** 100+ unit generators from the Soundpipe library. The stack-based approach means patches are concise -- just push numbers and call unit generators. Unix-friendly, small codebase, powerful C API. Paul Batchelor also created a "Sporth Cookbook" with documented patches. Can be live-coded with Vim. This is deep esoteric territory.

---

### Orca

- **GitHub:** https://github.com/hundredrabbits/Orca (Electron), https://github.com/hundredrabbits/Orca-c (C port)
- **What:** An esoteric 2D programming language where every letter of the alphabet is an operator. Designed for procedural sequencing. Orca does not generate sound itself -- it sends MIDI, OSC, or UDP messages to other software/hardware.
- **Install (C port):**
  ```bash
  git clone https://github.com/hundredrabbits/Orca-c
  cd Orca-c
  ./tool build --portmidi   # enable MIDI output
  ```
- **License:** MIT
- **Output:** No audio output -- MIDI/OSC/UDP sequencer only. Pair with a synth.
- **CLI Examples:**
  ```bash
  # Run Orca-c
  ./build/orca

  # Inside Orca, the grid is your program. Example:
  # .D2..
  # ..3Ac
  # This creates a bang every 2 frames that sends MIDI note
  ```
- **Notes:** Visually mesmerizing -- your code is a grid of characters that animate as the sequencer runs. Created by Hundred Rabbits (Devine Lu Linvega). The C port is lightweight and terminal-native. Pair it with Pilot (a companion UDP synth), SuperCollider, or any MIDI device. Deeply weird, deeply compelling. Maximum Aphex Twin energy.

---

## 6. Text-Based Composition Languages

### Alda

- **GitHub:** https://github.com/alda-lang/alda
- **Website:** https://alda.io
- **What:** A text-based programming language for music composition. Write music in a readable notation (instrument assignments, notes, chords, rests) and play it from the command line. Has an interactive REPL.
- **Install:** `brew install alda`
- **License:** EPL-2.0 (Eclipse Public License)
- **Output:** Real-time speakers (MIDI output via built-in synth)
- **CLI Examples:**
  ```bash
  # Play an Alda score file
  alda play -f my_score.alda

  # Play inline code
  alda play -c "piano: c8 d e f g a b > c"

  # Start the REPL
  alda repl

  # In the REPL:
  # piano: (tempo 120) c8 d e f g2
  # violin: e8 f g a b > c2

  # Export to MIDI
  alda export -f my_score.alda -o output.mid
  ```
- **Notes:** Designed to be readable by musicians. The notation is intuitive (note names, octave markers, durations). Supports all General MIDI instruments. The REPL gives instant feedback. Written in Go/Kotlin. Good entry point for people who want to write music as text without learning a full programming language.

---

### PySynth

- **GitHub:** https://github.com/mdoege/PySynth
- **What:** A suite of simple music synthesizers in Python 3. Turns ABC-like notation or MIDI into WAV files. Nine variants with different synthesis methods (FM, subtractive, additive).
- **Install:**
  ```bash
  git clone https://github.com/mdoege/PySynth
  cd PySynth
  python setup.py install
  ```
- **License:** GPL-3.0
- **Output:** WAV file output; can play via system player
- **CLI Examples:**
  ```bash
  # Command-line musical interpreter
  python menv.py --bpm 120 --sound pysynth_e

  # Inside the interpreter, enter notes:
  # c4 d4 e4 f4 g2 r4
  ```
- **Notes:** Nine synth variants: PySynth A (flute/organ), B (complex, needs NumPy), C/D/P (1970s analog-style subtractive), E (FM e-piano), S (sampler). Simple and educational. Good for quick WAV generation from note data without setting up a heavyweight environment.

---

## 7. Python Audio Ecosystem

### SignalFlow

- **GitHub:** https://github.com/ideoforms/signalflow
- **Website:** https://signalflow.dev
- **What:** A sound synthesis framework for Python with 100+ signal processing classes. Core written in C++11 for performance; clean Python API for experimentation.
- **Install:** `pip install signalflow`
- **License:** MIT
- **Output:** Real-time speakers or file output
- **CLI Examples:**
  ```python
  from signalflow import *

  graph = AudioGraph()
  sine = SineOscillator(440)
  output = sine * 0.2
  output.play()
  graph.wait()
  ```
- **Notes:** Designed for Jupyter/iPython/CLI prototyping. macOS/Linux/Windows/Raspberry Pi support. Includes filters, delays, FFT spectral processing, Euclidean rhythm generators, granular synthesis. Hardware-accelerated C++11 core means real-time performance. Beta status but actively maintained.

---

### pyo

- **GitHub:** https://github.com/belangeo/pyo
- **What:** A Python DSP module for audio signal processing. Comprehensive library of synthesis and processing objects.
- **Install:** `pip install pyo`
- **License:** LGPL-3.0
- **Output:** Real-time speakers or file output
- **CLI Examples:**
  ```python
  from pyo import *
  s = Server().boot()
  s.start()
  a = Sine(freq=440, mul=0.3).out()
  # Process runs until stopped
  ```
- **Notes:** Full-featured audio DSP -- granular synthesis, spectral processing, physical modeling, effects, analysis. MIDI and OSC support. Historically wants wxPython for its GUI components, but can be used programmatically without them. Developed by Olivier Belanger.

---

### AudioLDM / AudioLDM2

- **GitHub:** https://github.com/haoheliu/AudioLDM, https://github.com/haoheliu/AudioLDM2
- **What:** AI text-to-audio generation. Generate speech, sound effects, music from text prompts. Uses latent diffusion models.
- **Install:** `pip install audioldm`
- **License:** MIT (AudioLDM); check repo (AudioLDM2)
- **Output:** Audio file output (WAV)
- **CLI Examples:**
  ```bash
  # Generate audio from text
  audioldm -t "A synthesizer playing a dark ambient drone"
  audioldm -t "A distorted 808 drum pattern"

  # Specify duration and guidance scale
  audioldm -t "Ethereal choir pad" --duration 10 --guidance_scale 2.5
  ```
- **Notes:** Requires a GPU for reasonable performance. The AI-generated audio is a different paradigm from traditional synthesis but can produce remarkably weird/experimental results. Good for generating source material to feed into other tools.

---

## 8. Rust Audio Ecosystem

### Glicol (glicol-cli)

- **GitHub:** https://github.com/glicol/glicol-cli (CLI), https://github.com/chaosprint/glicol (core)
- **Website:** https://glicol.org
- **What:** A graph-oriented live coding language written in Rust. The CLI tool watches a `.glicol` file for changes and updates the music in real-time. Edit a text file, hear the changes instantly.
- **Install:**
  ```bash
  cargo install --git https://github.com/glicol/glicol-cli.git
  ```
- **License:** MIT
- **Output:** Real-time speakers
- **CLI Examples:**
  ```bash
  # Create a .glicol file and start watching it
  glicol-cli test.glicol

  # With options
  glicol-cli -b 140 -d default test.glicol
  glicol-cli --headless test.glicol

  # Example test.glicol content:
  # ~t1: speed 4.0 >> seq 60 >> bd 0.2 >> mul 0.6
  # ~t2: seq 33_33_ _33 33__33 _33 >> sawsynth 0.01 0.1 >> mul 0.5 >> lpf 1000.0 1.0
  # out: mix ~t.. >> plate 0.1
  ```
- **Notes:** The file-watching approach is brilliant for live coding -- just edit the `.glicol` file in any text editor (Vim, VS Code, whatever) and the audio updates in real-time. The graph-oriented syntax is intuitive (signal flows left to right with `>>`). Runs on Web, Desktop, DAW, and embedded systems. Pure Rust, cross-platform.

---

### FunDSP

- **GitHub:** https://github.com/SamiPerttu/fundsp
- **Crate:** https://crates.io/crates/fundsp
- **What:** An audio processing and synthesis library for Rust. Uses algebraic graph notation to express audio networks concisely.
- **Install:** `cargo add fundsp cpal` (as a library in a Rust project)
- **License:** MIT / Apache-2.0 (dual-licensed)
- **Output:** Real-time speakers (via cpal) or generate audio data programmatically
- **CLI Examples:**
  ```rust
  // Example Rust program using fundsp + cpal
  use fundsp::hacker::*;

  // Pink noise through a lowpass filter
  let sound = pink() >> lowpass_hz(1000.0, 1.0);

  // FM synthesis
  let fm = sine_hz(5.0) * 100.0 + 440.0 >> sine();
  ```
- **Notes:** The algebraic notation for connecting audio nodes (`>>` for series, `&` for parallel, `|` for branching) minimizes typing. Analytic frequency responses for any linear network. Excellent documentation. Not a standalone CLI tool -- you build programs with it as a library. Combine with `cpal` for audio output and `crossterm` for terminal UI.

---

### synthrs

- **GitHub:** https://github.com/gyng/synthrs
- **What:** A toy audio synthesizer library in Rust with basic MIDI support. Good for learning and quick WAV generation.
- **Install:** Add as dependency in Cargo.toml
- **License:** MIT
- **Output:** WAV file output
- **Notes:** Basic waveforms (sine, square, triangle, sawtooth, tangent, Karplus-Strong), basic filters (low-pass, high-pass, band-pass, comb, delay, envelope). Educational, not production-grade. Good starting point for building a custom CLI synth in Rust.

---

## 9. AI / Neural Audio Generation

### Stable Audio Tools

- **GitHub:** https://github.com/Stability-AI/stable-audio-tools
- **What:** Generative models for conditional audio generation from Stability AI. Text-to-audio and audio-to-audio generation.
- **Install:** `pip install stable-audio-tools`
- **License:** MIT
- **Output:** Audio file output
- **Notes:** Requires PyTorch 2.0+, CUDA GPU recommended. Powerful for generating experimental audio textures, drones, and musical elements from text descriptions. More heavyweight than AudioLDM but potentially higher quality.

---

## 10. Bytebeat & Noise Generators

### Bytebeat (various implementations)

- **GitHub (C):** https://github.com/radavis/bytebeat
- **GitHub (SuperCollider UGen):** https://github.com/midouest/bytebeat
- **What:** One-liner music. A bytebeat formula defines a waveform as a function of time `t`, typically processed 8000 times per second. The entire musical composition is a single mathematical expression.
- **Install:** Just need a C compiler and audio pipe
- **License:** Various (MIT, public domain)
- **Output:** Raw PCM data -- pipe to speakers via SoX or similar
- **CLI Examples:**
  ```bash
  # Classic bytebeat one-liner (compile and pipe to sox)
  echo 'main(t){for(;;t++)putchar(t*(t>>12&t>>8)&63+t);}' > beat.c
  gcc beat.c -o beat
  ./beat | sox -t raw -r 8000 -b 8 -e unsigned -c 1 - -d

  # Or directly with sox
  # (requires a bytebeat program that writes to stdout)
  ```
- **Notes:** Bytebeat was invented in 2011 and is one of the most beautiful intersections of mathematics and music. A single C expression like `t*(t>>5|t>>8)` produces surprisingly complex rhythmic and melodic patterns. Maximally esoteric. The results sound like alien transmissions from a broken computer -- pure Aphex Twin territory. Resources: http://canonical.org/~kragen/bytebeat/

---

### macOS Built-in: afplay / say

- **What:** macOS ships with `afplay` (audio file player) and `say` (text-to-speech with synthesized voices).
- **Install:** Pre-installed on macOS
- **License:** Proprietary (Apple)
- **CLI Examples:**
  ```bash
  # Play an audio file
  afplay output.wav

  # Text-to-speech (various voices)
  say "hello world"
  say -v Cellos "doo doo doo"    # musical voice
  say -v Whisper "creepy"
  say -v Samantha -r 50 "slow"   # slow rate
  say -o output.aiff "save to file"
  ```
- **Notes:** `afplay` is the simplest way to play generated audio files on macOS. `say` with the Cellos voice can produce surprisingly musical output. Useful as a quick output mechanism for other tools.

---

## 11. Quick Reference Matrix

| Tool | Install | Language | Real-time | File Out | Standalone | License |
|------|---------|----------|-----------|----------|------------|---------|
| **Csound** | `brew install csound` | Csound | Yes | Yes | Yes | LGPL-2.1 |
| **SuperCollider** | `brew cask supercollider` | sclang | Yes | Yes | Yes | GPL-3.0 |
| **ChucK** | `brew install chuck` | ChucK | Yes | Yes | Yes | MIT/GPL-2.0 |
| **Faust** | `brew install faust` | Faust | Via targets | Via targets | Meta-tool | GPL-2.0 |
| **Pure Data** | `brew cask pd` | Visual/Pd | Yes | Yes | Yes | BSD |
| **SoX** | `brew install sox` | CLI flags | Yes (`play`) | Yes (`sox`) | Yes | GPL-2.0 |
| **FluidSynth** | `brew install fluid-synth` | CLI/API | Yes | Yes | Yes | LGPL-2.1 |
| **TidalCycles** | cabal + SuperCollider | Haskell DSL | Yes | No | No (needs SC) | GPL-3.0 |
| **Sardine** | `pip install sardine-system` | Python | Yes | No | No (needs SC) | GPL-3.0 |
| **Renardo** | `pip install renardo` | Python | Yes | No | No (needs SC) | CC-BY-SA |
| **Overtone** | Clojure dep | Clojure | Yes | No | No (needs SC) | MIT |
| **Extempore** | Build from source | Scheme/xtlang | Yes | No | Yes | BSD |
| **Alda** | `brew install alda` | Alda | Yes (MIDI) | MIDI export | Yes | EPL-2.0 |
| **Glicol** | `cargo install` (git) | Glicol | Yes | No | Yes | MIT |
| **Sporth** | Build from source | Forth-like | Yes | Yes | Yes | MIT/Unlicense |
| **Orca** | Build from source (C) | Orca (2D) | No (sequencer) | No | Needs synth | MIT |
| **Cursynth** | Build from source | C++ (TUI) | Yes | No | Yes | GPL-3.0 |
| **SignalFlow** | `pip install signalflow` | Python | Yes | Yes | Yes | MIT |
| **pyo** | `pip install pyo` | Python | Yes | Yes | Yes | LGPL-3.0 |
| **FunDSP** | `cargo add fundsp` | Rust (lib) | Yes (w/cpal) | Yes | Library | MIT/Apache |
| **PySynth** | git clone | Python | Via player | Yes (WAV) | Yes | GPL-3.0 |
| **AudioLDM** | `pip install audioldm` | Python (AI) | No | Yes (WAV) | Yes | MIT |
| **Bytebeat** | gcc | C one-liners | Yes (piped) | Yes (piped) | Yes | Public domain |
| **textbeat** | `pip install textbeat` | Text notation | MIDI only | MIDI | Needs synth | MIT |
| **eSpeak-NG** | `brew install espeak-ng` | CLI | Yes | Yes | Yes | GPL-3.0 |
| **Aubio** | `brew install aubio` | CLI | Analysis only | Text | Yes | GPL-3.0 |
| **Essentia** | `pip install essentia` | Python/CLI | Analysis only | JSON | Yes | AGPL-3.0 |
| **Sonic Annotator** | `brew install sonic-annotator` | CLI | Analysis only | CSV/RDF | Needs plugins | GPL-2.0 |
| **Chromaprint** | `brew install chromaprint` | CLI | No | Text | Yes | LGPL-2.1 |
| **keyfinder-cli** | Build from source | CLI | No | Text | Needs lib | GPL-3.0 |
| **CREPE** | `pip install crepe` | Python/CLI | No | CSV | Yes | MIT |
| **Demucs** | `pip install demucs` | Python/CLI | No | WAV stems | Yes | MIT |
| **Spleeter** | `pip install spleeter` | Python/CLI | No | WAV stems | Yes | MIT |
| **FFmpeg** | `brew install ffmpeg` | CLI | Yes | Any format | Yes | LGPL/GPL |
| **r128gain** | `pip install r128gain` | CLI | No | Tags files | Yes | GPL-3.0 |
| **loudgain** | Build from source | CLI | No | Tags files | Yes | BSD-2 |
| **CAVA** | `brew install cava` | CLI (TUI) | Visual only | No | Yes | MIT |
| **Coltrane** | `gem install coltrane` | Ruby CLI | No | Text/ASCII | Yes | MIT |
| **SendMIDI** | Download binary | CLI | MIDI only | No | Yes | GPL-3.0 |
| **ReceiveMIDI** | Download binary | CLI | MIDI monitor | No | Yes | GPL-3.0 |
| **isobar** | `pip install isobar` | Python | MIDI only | MIDI files | Needs synth | MIT |
| **athenaCL** | `pip install athenaCL` | Python CLI | Via backends | Multi-format | Yes | GPL-3.0 |
| **Beets** | `pip install beets` | Python CLI | No | Tags files | Yes | MIT |
| **Jackdaw** | Build from source | C (SDL2) | Yes | Yes | Yes | GPL-3.0 |
| **Ecasound** | Build from source | CLI | Yes | Yes | Yes | GPL-2.0 |
| **musikcube** | `brew install musikcube` | C++ (TUI) | Yes | No | Yes | BSD-3 |
| **cmus** | `brew install cmus` | C (TUI) | Yes | No | Yes | GPL-2.0 |
| **LilyPond** | `brew install lilypond` | Text notation | MIDI | PDF/SVG/MIDI | Yes | GPL-3.0 |
| **Polyrhythmix** | Build from source | Haskell CLI | No | MIDI | Yes | BSD-3 |
| **Celltone** | Build from source | Custom lang | MIDI | MIDI | Needs synth | N/A |
| **Gwion** | Build from source | Gwion | Yes | Yes | Yes | MIT |

---

## 12. Audio Analysis & Feature Extraction

### Aubio

- **GitHub:** https://github.com/aubio/aubio
- **Website:** https://aubio.org
- **What:** A library and CLI toolset for audio labelling: onset detection, beat tracking, pitch detection, tempo estimation, MFCC extraction, and note transcription. The CLI tools are first-class -- not wrappers around a library, but purpose-built command-line utilities.
- **Install:** `brew install aubio`
- **License:** GPL-3.0
- **Output:** Text output (analysis data), no audio output
- **CLI Examples:**
  ```bash
  # Detect onsets (attack transients)
  aubio onset input.wav

  # Extract pitch (fundamental frequency)
  aubio pitch input.wav

  # Get pitch with specific method and silence threshold
  aubio pitch input.wav -m mcomb -s -90.0

  # Beat tracking
  aubio beat input.wav

  # Overall tempo (BPM)
  aubio tempo input.wav

  # Note detection (MIDI-like output)
  aubio notes input.wav

  # MFCC extraction
  aubio mfcc input.wav

  # Mel-frequency energy per band
  aubio melbands input.wav
  ```
- **Notes:** The go-to CLI tool for audio analysis. Each subcommand (`onset`, `pitch`, `beat`, `tempo`, `notes`, `mfcc`, `melbands`) is a complete analysis pipeline. Output is plain text, perfect for piping into other tools or scripts. Supports WAV and many other formats. Python bindings available (`pip install aubio`).

---

### Essentia

- **GitHub:** https://github.com/MTG/essentia
- **Website:** https://essentia.upf.edu
- **What:** A comprehensive C++ library for audio analysis and music information retrieval (MIR) from the Music Technology Group at UPF Barcelona. Hundreds of algorithms covering spectral, temporal, tonal, and high-level descriptors.
- **Install:** `pip install essentia` (Python bindings), or build from source
- **License:** AGPL-3.0
- **Output:** Analysis data (text, JSON)
- **CLI Examples:**
  ```bash
  # Use the streaming music extractor (produces JSON)
  essentia_streaming_extractor_music input.wav output.json

  # Python usage for beat detection
  python -c "
  import essentia.standard as es
  audio = es.MonoLoader(filename='input.wav')()
  rhythm = es.RhythmExtractor2013(method='multifeature')
  bpm, beats, conf, _, _ = rhythm(audio)
  print(f'BPM: {bpm}')
  "
  ```
- **Notes:** Broader than aubio -- covers key/scale detection, chord estimation, danceability, loudness (EBU R128), spectral analysis, and more. Pre-built extractors can dump comprehensive JSON descriptors. Used in production at Freesound.org. The AGPL license is restrictive for commercial use but fine for research/personal projects.

---

### Sonic Annotator

- **GitHub:** https://github.com/sonic-visualiser/sonic-annotator
- **Website:** https://vamp-plugins.org/sonic-annotator/
- **What:** A command-line batch tool for feature extraction using Vamp plugins. Vamp is a plugin API for audio analysis (as opposed to audio effects). Think of it as a CLI host for analysis algorithms.
- **Install:** Download binary from website, or `brew install sonic-annotator`
- **License:** GPL-2.0
- **Output:** CSV, RDF, or text output
- **CLI Examples:**
  ```bash
  # List all available Vamp transforms
  sonic-annotator -l

  # Run a specific transform
  sonic-annotator -d vamp:qm-vamp-plugins:qm-tempotracker:tempo \
    -w csv input.wav

  # Extract key with BBC Vamp plugins
  sonic-annotator -d vamp:bbc-vamp-plugins:bbc-energy:rmsenergy \
    -w csv --csv-stdout input.wav

  # Process all WAV files in a directory
  sonic-annotator -d vamp:qm-vamp-plugins:qm-chromagram:chromagram \
    -w csv *.wav
  ```
- **Notes:** The power here is the plugin ecosystem. Install different Vamp plugins to get different analysis capabilities. The BBC Vamp plugins add speech/music detection, intensity, rhythm patterns. The QM (Queen Mary) plugins add chromagram, key detection, onset, tempo. A framework for extensible audio analysis from the command line.

---

### Chromaprint / fpcalc

- **GitHub:** https://github.com/acoustid/chromaprint
- **Website:** https://acoustid.org/chromaprint
- **What:** Audio fingerprinting library and CLI tool. Given an audio file, `fpcalc` generates a compact fingerprint that can identify the song via the AcoustID service. Used by MusicBrainz Picard.
- **Install:** `brew install chromaprint`
- **License:** LGPL-2.1+
- **Output:** Text (fingerprint hash)
- **CLI Examples:**
  ```bash
  # Generate fingerprint
  fpcalc input.mp3

  # JSON output
  fpcalc -json input.mp3

  # Limit analysis to first 30 seconds
  fpcalc -length 30 input.mp3

  # Raw fingerprint (for custom matching)
  fpcalc -raw input.mp3
  ```
- **Notes:** Essential for music identification and deduplication workflows. The fingerprint is a compact representation of the audio's spectral characteristics that survives transcoding, volume changes, and minor edits. Pairs with the AcoustID web service for lookup.

---

### keyfinder-cli

- **GitHub:** https://github.com/evanpurkhiser/keyfinder-cli
- **Library:** https://github.com/mixxxdj/libkeyfinder
- **What:** CLI wrapper for libkeyfinder -- estimates the musical key of audio files. Originally written by Ibrahim Sha'ath, now maintained by the Mixxx DJ team.
- **Install:** Build from source (requires libkeyfinder)
- **License:** GPL-3.0
- **Output:** Text (key name, e.g. "Eb" or "Am")
- **CLI Examples:**
  ```bash
  # Detect key of a file
  keyfinder-cli track.mp3

  # Output: Am
  ```
- **Notes:** Simple, single-purpose tool. Useful for DJs and producers who need to tag large libraries with key information. Three notation modes supported (standard, Camelot, Open Key). Very fast.

---

### CREPE

- **GitHub:** https://github.com/marl/crepe
- **What:** A deep convolutional neural network for monophonic pitch tracking. State-of-the-art accuracy, outperforming pYIN and SWIPE. CLI and Python API.
- **Install:** `pip install crepe` (requires TensorFlow >= 2.0)
- **License:** MIT
- **Output:** CSV file (timestamp, frequency, confidence)
- **CLI Examples:**
  ```bash
  # Analyze a file (default 10ms step size)
  crepe input.wav

  # Custom step size (50ms)
  crepe --step-size 50 input.wav

  # Save activation matrix plot
  crepe --save-plot input.wav

  # Process all WAV files in a folder
  crepe /path/to/folder/
  ```
- **Notes:** Neural network approach to pitch detection. Produces a CSV with timestamp, estimated Hz, and confidence per frame. The activation plot shows the model's internal pitch probability distribution -- genuinely beautiful visual output. Requires a decent amount of compute (GPU recommended for large files).

---

### audioFlux

- **GitHub:** https://github.com/libAudioFlux/audioFlux
- **Website:** https://libaudioflux.github.io/audioFlux/
- **What:** A library for audio and music analysis, feature extraction. Supports dozens of time-frequency analysis methods and hundreds of corresponding feature combinations. Core written in C with Python bindings.
- **Install:** `pip install audioflux`
- **License:** MIT
- **Output:** Programmatic (numpy arrays, plots)
- **Notes:** Comprehensive spectral analysis (CQT, STFT, BFT, NSGT, etc.), pitch detection (YIN, STFT), chroma features, cepstral coefficients, deconvolution. Cross-platform (macOS, Linux, Windows, iOS, Android). More of a library than a CLI tool, but scripts can be written quickly.

---

### TapTempo

- **Website:** https://taptempo.tuxfamily.org
- **GitHub:** https://github.com/moleculext/taptempo
- **What:** The simplest possible CLI BPM detector. Press Enter rhythmically and it calculates beats per minute.
- **Install:** Build from source, or available in some package managers
- **License:** GPL-3.0
- **Output:** BPM value to stdout
- **CLI Examples:**
  ```bash
  # Just run it and tap Enter
  taptempo

  # Set precision
  taptempo --precision 2

  # Set sample size
  taptempo --sample-size 8
  ```
- **Notes:** Beautifully minimal. Does one thing, does it well. Useful for quickly getting a BPM without launching a full DAW.

---

## 13. Audio Source Separation (AI/ML)

### Demucs

- **GitHub:** https://github.com/facebookresearch/demucs
- **What:** Meta/Facebook Research's deep learning model for music source separation. Separates songs into stems: vocals, drums, bass, and other. State-of-the-art quality, CLI interface.
- **Install:** `pip install -U demucs`
- **License:** MIT
- **Output:** WAV files (separate stems)
- **CLI Examples:**
  ```bash
  # Default 4-stem separation (vocals, drums, bass, other)
  demucs input.mp3

  # Two-stem separation (vocals + instrumental)
  demucs --two-stems vocals input.mp3

  # Use specific model
  demucs -n htdemucs_ft input.mp3

  # Output as MP3 instead of WAV
  demucs --mp3 input.mp3

  # Process multiple files
  demucs track1.mp3 track2.mp3 track3.mp3
  ```
- **Notes:** Genuinely impressive separation quality. The htdemucs_ft (fine-tuned) model is the best quality but slower. Output goes to a `separated/` directory. Requires significant compute (GPU recommended but CPU works). Revolutionary for producers -- extract drum patterns, isolate vocals, create stems from any mixed recording.

---

### Spleeter

- **GitHub:** https://github.com/deezer/spleeter
- **What:** Deezer's audio source separation library. Separates audio into 2, 4, or 5 stems. Was the first major open-source stem separator (2019).
- **Install:** `pip install spleeter`
- **License:** MIT
- **Output:** WAV files (separate stems)
- **CLI Examples:**
  ```bash
  # 2-stem separation (vocals + accompaniment)
  spleeter separate -p spleeter:2stems input.mp3

  # 4-stem separation
  spleeter separate -p spleeter:4stems input.mp3

  # 5-stem separation (vocals, drums, bass, piano, other)
  spleeter separate -p spleeter:5stems input.mp3

  # Specify output format
  spleeter separate -p spleeter:2stems -o output_dir input.mp3
  ```
- **Notes:** Faster than Demucs but generally lower quality. Good for batch processing where speed matters. The 5-stem model is unique (separates piano). Models are downloaded on first use.

---

## 14. Audio Format Conversion & Processing

### FFmpeg

- **GitHub:** https://github.com/FFmpeg/FFmpeg
- **Website:** https://ffmpeg.org
- **What:** The universal media processing tool. Converts between virtually any audio/video format, applies filters, analyzes loudness, and much more. The most essential tool in any CLI audio workflow.
- **Install:** `brew install ffmpeg`
- **License:** LGPL-2.1+ / GPL-2.0+ (depending on build configuration)
- **Output:** Any audio/video format
- **CLI Examples:**
  ```bash
  # Convert WAV to MP3 (320kbps)
  ffmpeg -i input.wav -b:a 320k output.mp3

  # Convert WAV to FLAC
  ffmpeg -i input.wav output.flac

  # Convert to OGG Vorbis
  ffmpeg -i input.wav -c:a libvorbis -q:a 6 output.ogg

  # Convert to Opus
  ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

  # Measure loudness (EBU R128)
  ffmpeg -i input.wav -af loudnorm=print_format=summary -f null -

  # Volume detection (mean and max)
  ffmpeg -i input.wav -af volumedetect -f null /dev/null

  # EBU R128 loudness analysis
  ffmpeg -nostats -i input.wav -filter_complex ebur128 -f null -

  # Loudness normalization (two-pass)
  ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 output.wav

  # Extract audio from video
  ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

  # Trim audio (start at 30s, duration 10s)
  ffmpeg -i input.wav -ss 30 -t 10 output.wav

  # Audio visualization (spectrogram to video)
  ffmpeg -i input.wav -lavfi showspectrumpic=s=1024x512 spectrum.png
  ```
- **Notes:** If SoX is the Swiss Army knife, FFmpeg is the entire workshop. The loudnorm filter for EBU R128 loudness normalization is professional-grade. The volumedetect filter provides peak/RMS analysis. Audio visualization filters (showspectrumpic, showwavespic, showcqt) can generate images and videos of audio data. Absolutely essential.

---

### FLAC (official encoder/decoder)

- **Website:** https://xiph.org/flac/
- **What:** The official command-line FLAC encoder and decoder from Xiph.org.
- **Install:** `brew install flac`
- **License:** BSD / GPL-2.0 (dual-licensed)
- **CLI Examples:**
  ```bash
  # Encode WAV to FLAC
  flac input.wav

  # Decode FLAC to WAV
  flac -d input.flac

  # Encode with maximum compression
  flac -8 input.wav

  # Verify file integrity
  flac -t input.flac

  # View metadata
  metaflac --list input.flac
  ```

---

### LAME

- **Website:** https://lame.sourceforge.io
- **What:** The standard open-source MP3 encoder. High quality variable and constant bitrate encoding.
- **Install:** `brew install lame`
- **License:** LGPL-2.0
- **CLI Examples:**
  ```bash
  # Encode WAV to MP3 (VBR, high quality)
  lame -V 0 input.wav output.mp3

  # Constant bitrate 320kbps
  lame -b 320 input.wav output.mp3

  # Decode MP3 to WAV
  lame --decode input.mp3 output.wav
  ```

---

### opusenc / opusdec

- **Website:** https://opus-codec.org
- **What:** Official Opus encoder/decoder. Opus is the modern codec for voice and music, superior to MP3 and Vorbis at most bitrates.
- **Install:** `brew install opus-tools`
- **License:** BSD
- **CLI Examples:**
  ```bash
  # Encode WAV to Opus
  opusenc --bitrate 128 input.wav output.opus

  # Decode Opus to WAV
  opusdec input.opus output.wav
  ```

---

### vorbis-tools (oggenc / oggdec)

- **Website:** https://xiph.org/vorbis/
- **What:** Official Ogg Vorbis encoder/decoder tools.
- **Install:** `brew install vorbis-tools`
- **License:** BSD
- **CLI Examples:**
  ```bash
  # Encode WAV to OGG
  oggenc -q 6 input.wav -o output.ogg

  # Decode OGG to WAV
  oggdec input.ogg -o output.wav
  ```

---

## 15. Loudness Normalization & Metering

### r128gain

- **GitHub:** https://github.com/desbma/r128gain
- **What:** Fast audio loudness scanner and tagger implementing ReplayGain v2 / EBU R128. Scans audio files and tags them with loudness metadata.
- **Install:** `pip install r128gain` (requires FFmpeg)
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Scan and display loudness info
  r128gain -d track.mp3

  # Scan and tag a single file
  r128gain track.mp3

  # Scan and tag recursively with album gain
  r128gain -r -a /path/to/music/

  # Dry run (show what would be done)
  r128gain -d -r /path/to/music/
  ```
- **Notes:** Supports all common audio formats (MP3, AAC, Vorbis, Opus, FLAC, WavPack). Tags are written as ReplayGain v2 metadata -- no audio data is modified. Essential for consistent playback loudness across a music library.

---

### loudgain

- **GitHub:** https://github.com/Moonbase59/loudgain
- **What:** ReplayGain 2.0 loudness normalizer based on the EBU R128 / ITU BS.1770 standard. Targets -18 LUFS. Drop-in replacement for mp3gain's command-line syntax.
- **Install:** Build from source (requires libebur128, taglib, ffmpeg)
- **License:** BSD-2-Clause
- **CLI Examples:**
  ```bash
  # Scan and tag files
  loudgain -s e *.flac

  # Album mode
  loudgain -a -s e *.flac

  # Display results without tagging
  loudgain -n *.mp3
  ```
- **Notes:** Unlike r128gain (Python/FFmpeg), loudgain is a compiled C program -- much faster for large libraries. Supports FLAC, Ogg, MP2, MP3, MP4, M4A, ALAC, Opus, ASF, WMA, WAV, WavPack, AIFF, APE. Never modifies audio data, only writes tags.

---

## 16. Terminal Audio Visualization

### CAVA

- **GitHub:** https://github.com/karlstav/cava
- **What:** Console Audio Visualizer for ALSA (but also works with PulseAudio, PipeWire, sndio, JACK, and portaudio). A bar spectrum audio visualizer that runs in your terminal.
- **Install:** `brew install cava`
- **License:** MIT
- **Output:** Terminal display (ASCII/Unicode bar visualizer)
- **CLI Examples:**
  ```bash
  # Just run it (auto-detects audio source)
  cava

  # Specify a config file
  cava -p /path/to/config
  ```
- **Notes:** Aesthetically gorgeous. Configurable colors, bar widths, smoothing, and sensitivity. On macOS, requires a loopback audio device (like BlackHole or Soundflower) to capture system audio. Uses Unicode block characters for smooth rendering. The go-to terminal visualizer.

---

### cli-visualizer

- **GitHub:** https://github.com/PosixAlchemist/cli-visualizer
- **What:** CLI-based audio visualizer with multiple visualization modes: spectrum, lorenz, and ellipse.
- **Install:** Build from source (requires fftw, ncurses)
- **License:** MIT
- **Output:** Terminal display (ncurses)
- **Notes:** Multiple visualization modes go beyond simple bar charts. The Lorenz attractor visualization driven by audio is particularly striking. Requires FFTW for FFT computation.

---

### mpv audio visualization

- **GitHub:** https://github.com/mpv-player/mpv
- **Website:** https://mpv.io
- **What:** mpv is a powerful command-line media player that includes built-in audio visualization using FFmpeg's lavfi filters.
- **Install:** `brew install mpv`
- **License:** GPL-2.0+ / LGPL-2.1+
- **CLI Examples:**
  ```bash
  # Play with CQT (Constant-Q Transform) spectrogram
  mpv --lavfi-complex="[aid1]asplit[ao][a]; [a]showcqt[vo]" music.mp3

  # Waveform visualization
  mpv --lavfi-complex="[aid1]asplit[ao][a]; [a]showwaves=mode=cline[vo]" music.mp3

  # Vector scope
  mpv --lavfi-complex="[aid1]asplit[ao][a]; [a]avectorscope=s=640x640[vo]" music.mp3

  # Frequency spectrum
  mpv --lavfi-complex="[aid1]asplit[ao][a]; [a]showfreqs=mode=line[vo]" music.mp3
  ```
- **Notes:** The lavfi-complex option provides access to all of FFmpeg's audio visualization filters. The CQT display is musically meaningful (logarithmic frequency scale). Can render to a window while playing audio. Excellent for quick inspection of audio files.

---

## 17. CLI Music Theory Tools

### Coltrane

- **GitHub:** https://github.com/pedrozath/coltrane
- **What:** A music calculation library and CLI written in Ruby. Generate chords, scales, and progressions. Visualize on guitar, bass, piano, or ukulele fretboards/keyboards.
- **Install:** `gem install coltrane`
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Show a scale on guitar fretboard
  coltrane scale C major --on guitar

  # Show a chord on piano
  coltrane chord Cmaj7 --on piano

  # Find chords in a key
  coltrane progression I IV V vi --in C

  # List all scales
  coltrane scale --list
  ```
- **Notes:** Beautiful ASCII-art fretboard and piano visualizations. Named after John Coltrane. Covers a wide range of scales (major, minor, pentatonic, modes, blues, whole tone, diminished, etc.) and chord types. Written in Ruby.

---

### musthe

- **GitHub:** https://github.com/gciruelos/musthe
- **What:** Music theory implemented in Python. Notes, intervals, scales, and chords as Python objects.
- **Install:** `pip install musthe`
- **License:** MIT
- **Notes:** Not a CLI tool per se, but easily scriptable. Check if notes/chords are in scales, generate chord voicings, calculate intervals. Useful for building custom music theory scripts.

---

## 18. MIDI CLI Tools

### SendMIDI / ReceiveMIDI

- **GitHub:** https://github.com/gbevin/SendMIDI, https://github.com/gbevin/ReceiveMIDI
- **What:** Multi-platform command-line tools for sending and monitoring MIDI messages. Concise, easy-to-remember command syntax.
- **Install:** Download binaries from GitHub releases, or build from source
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Send a note on/off
  sendmidi dev "IAC Driver" on 60 100
  sendmidi dev "IAC Driver" off 60

  # Send a chord
  sendmidi dev "IAC Driver" on 60 100 on 64 100 on 67 100

  # Send CC
  sendmidi dev "IAC Driver" cc 1 64

  # Monitor all incoming MIDI
  receivemidi dev "IAC Driver"

  # Monitor specific channels
  receivemidi dev "IAC Driver" ch 1
  ```
- **Notes:** By Geert Bevin (creator of various JUCE-based tools). The command syntax is designed to be fast and intuitive. Great for MIDI debugging, testing, and scripting. Works with macOS IAC Driver for inter-application MIDI routing.

---

### Midish

- **Website:** https://midish.org
- **What:** An open-source command-line MIDI sequencer and filter for Unix. Real-time performance-oriented, minimal and fast.
- **Install:** Build from source
- **License:** ISC
- **Notes:** A full MIDI sequencer in the terminal. Record, edit, and play back MIDI sequences. Designed for real-time performance. Lightweight and efficient. One of the few true terminal MIDI sequencers.

---

### midi2audio

- **GitHub:** https://github.com/bzamecnik/midi2audio
- **What:** Python/CLI wrapper around FluidSynth for easy MIDI-to-audio conversion.
- **Install:** `pip install midi2audio` (requires FluidSynth)
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Convert MIDI to WAV
  midi2audio input.mid output.wav

  # Convert MIDI to FLAC
  midi2audio input.mid output.flac
  ```

---

### abc2midi / midi2abc

- **Website:** https://abcmidi.sourceforge.io
- **What:** Convert between ABC music notation and MIDI. ABC notation is a compact text-based music notation system popular in folk music.
- **Install:** `brew install abcmidi`
- **License:** GPL-2.0
- **CLI Examples:**
  ```bash
  # ABC notation to MIDI
  abc2midi tune.abc -o output.mid

  # MIDI to ABC notation
  midi2abc input.mid -o output.abc

  # Transpose ABC notation
  abc2abc tune.abc -t 2  # transpose up 2 semitones
  ```
- **Notes:** ABC notation is remarkably compact. A simple melody can be notated as: `X:1\nT:Example\nK:C\nCDEF|GABc|`. The `abc2midi` tool handles repeat marks, dynamics, drum accompaniment, and guitar chord expansion. Essential for folk music digitization workflows.

---

### Polyrhythmix

- **GitHub:** https://github.com/dredozubov/polyrhythmix
- **What:** A CLI drum MIDI generator designed for polyrhythmic composition. Describe drum parts in a DSL, and it calculates convergence points and generates MIDI files.
- **Install:** Build from source (Haskell)
- **License:** BSD-3-Clause
- **CLI Examples:**
  ```bash
  # Generate a polyrhythmic drum pattern
  poly --time-signature '3/4' --kick '8x--x--' --snare '4-x' -o out.mid

  # Dry run (show convergence without output)
  poly --time-signature '7/8' --kick '8x--x-x-' --snare '4-x-x'
  ```
- **Notes:** Designed for progressive rock, metal, djent, fusion, and Indian Carnatic music. Can also generate a bass MIDI track following the kick pattern. Niche but genuinely useful for complex rhythmic composition.

---

## 19. Algorithmic & Generative Music

### isobar

- **GitHub:** https://github.com/ideoforms/isobar
- **Website:** https://ideoforms.github.io/isobar/
- **What:** A Python library for creating and manipulating musical patterns. Designed for algorithmic composition, generative music, and sonification. Outputs MIDI events, MIDI files, OSC messages, or custom actions.
- **Install:** `pip install isobar`
- **License:** MIT
- **Output:** MIDI, MIDI files, OSC
- **CLI Examples:**
  ```python
  from isobar import *

  # Create a timeline
  timeline = Timeline(120)

  # Simple melodic pattern
  timeline.schedule({
      "note": PDegree(PSequence([0, 2, 4, 7], 4), Scale.major),
      "duration": PSequence([0.5, 0.25, 0.25, 1.0]),
      "gate": PSequence([0.9, 0.5, 0.5, 0.8])
  })

  # Euclidean rhythm
  timeline.schedule({
      "note": 60,
      "duration": PEuclidean(5, 8, 0.5)
  })

  # Markov chain melody
  learner = MarkovLearner()
  learner.learn_sequence([60, 62, 64, 67, 69, 67, 64, 62])
  timeline.schedule({"note": PMarkov(learner)})

  timeline.run()
  ```
- **Notes:** Rich pattern library: sequences, Euclidean rhythms, L-systems, Markov chains, random walks, probability distributions, degree-to-note mapping, key filtering. The `PMarkov` pattern is particularly interesting -- learn from existing melodies and generate new ones. Pairs well with FluidSynth for audio output or any DAW for MIDI input.

---

### athenaCL

- **GitHub:** https://github.com/ales-tsurko/athenaCL
- **Website:** https://athenacl.alestsurko.by
- **What:** A modular, polyphonic, poly-paradigm algorithmic music composition system with an interactive command-line environment. Over 80 specialized Generator, Rhythm, and Filter ParameterObjects.
- **Install:** `pip install athenaCL`
- **License:** GPL-3.0
- **Output:** Csound, SuperCollider, Pure Data, MIDI, audio files, XML, text
- **CLI Examples:**
  ```bash
  # Start the interactive environment
  athenacl

  # Inside the CLI:
  # tin a 21     (create a new texture instrument)
  # tie t ds,e,10,0,.3,1  (set texture parameters)
  # eln          (render to audio)
  ```
- **Notes:** Includes stochastic, chaotic, cellular automata, Markov chain, L-system, waveform, fractional noise (1/f), genetic algorithm, Xenakis sieve, and many other algorithmic models. Outputs to virtually any format. Under development since 2000. One of the most comprehensive algorithmic composition systems in existence.

---

### Celltone

- **GitHub:** https://github.com/andreasjansson/Celltone
- **What:** A programming language for generative music composition using cellular automata. Define rules; the automata evolve; the states map to music.
- **Install:** Build from source (requires PortMidi)
- **License:** Not specified
- **CLI Examples:**
  ```bash
  # Play a Celltone file via MIDI in real-time
  celltone program.cell

  # Generate a MIDI file instead
  celltone --file program.cell
  ```
- **Notes:** One of the weirdest and most interesting tools on this list. Cellular automata produce emergent, evolving musical structures. The results are unpredictable and alien-sounding. Deep generative territory.

---

### Fractal Music Generator

- **GitHub:** https://github.com/betaiotazeta/FractalMusicGenerator
- **What:** A cross-platform application for creating polyphonic audio and MIDI music from fractals (Mandelbrot set, Julia sets).
- **Install:** Download from GitHub releases
- **License:** MIT
- **Notes:** Maps fractal mathematics to musical parameters. The resulting music has self-similar structure at different time scales -- a direct translation of fractal geometry to sound.

---

### Markov Chain Generators (various)

Several projects implement Markov chain-based music generation:

- **mnagel/markov:** https://github.com/mnagel/markov -- Generate music (and text) using Markov chains
- **adegani/Markovex:** https://github.com/adegani/Markovex -- Reads MIDI files, extracts Markov chains, generates new music. Usage: `markovex [options] <file.mid>`
- **kstar/markov-music:** https://github.com/kstar/markov-music -- Trained on Bach violin concertos
- **Zunawe/markov-chain-music-generator:** https://github.com/Zunawe/markov-chain-music-generator -- Higher-order multivariate Markov chains for piano music

---

## 20. Music Library Management & Metadata

### Beets

- **GitHub:** https://github.com/beetbox/beets
- **Website:** https://beets.io
- **What:** The music geek's media organizer. A command-line music library manager with auto-tagging, metadata correction, and an extensible plugin system.
- **Install:** `pip install beets`
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Import music (auto-tag with MusicBrainz)
  beet import /path/to/music/

  # List all tracks
  beet ls

  # Search library
  beet ls artist:radiohead album:ok

  # Show stats
  beet stats

  # Fetch album art
  beet fetchart

  # Calculate ReplayGain
  beet replaygain

  # Fetch lyrics
  beet lyrics

  # Acoustic fingerprint identification
  beet fingerprint
  ```
- **Notes:** The plugin system is vast: album art, lyrics, ReplayGain, acoustic fingerprinting (Chromaprint), last.fm integration, duplicate detection, format conversion, web interface. MusicBrainz and Discogs as metadata sources. Probably the most comprehensive music library management tool available.

---

### lltag

- **GitHub:** https://github.com/bgoglin/lltag
- **What:** Automatic command-line MP3/OGG/FLAC file tagger and renamer. Parse filenames to extract metadata, or apply tags from format strings.
- **License:** GPL-2.0
- **CLI Examples:**
  ```bash
  # Auto-tag from filename pattern
  lltag --yes -F '%n - %t' *.mp3

  # Rename files based on tags
  lltag --rename '%a - %t' *.flac
  ```

---

## 21. Terminal DAW Projects

### Jackdaw

- **GitHub:** https://github.com/chvolow24/jackdaw
- **What:** A keyboard-focused digital audio workstation written in C, using SDL2 for rendering. Takes design cues from non-linear video editors like Avid. Work in progress but functional.
- **Install:** Build from source
- **License:** GPL-3.0
- **Features:**
  - Multi-track recording and playback
  - Up to 16 effects per track
  - Keyboard-driven (hit spacebar for command autocomplete)
  - Mouse support as alternative
  - Open .jdaw file format
  - Built-in effects processing
- **Notes:** The Hackaday article "Terminal DAW Does It In Style" highlighted this as a standout project. The spacebar-triggered command palette (similar to VS Code's command palette) makes it discoverable despite being keyboard-first. Active development.

---

### termdaw

- **GitHub:** https://github.com/codybloemhard/termdaw
- **What:** A terminal, graph-based programmable pipeline DAW written in Rust. Designed to be friendly to automation and algorithmic composition.
- **Install:** Build from source (Rust)
- **License:** GPL-3.0
- **Notes:** Graph-based audio pipeline in the terminal. Designed for programmers who want DAW functionality without leaving the terminal. Early stage but conceptually interesting.

---

### ttdaw

- **GitHub:** https://github.com/mitjafelicijan/ttdaw
- **What:** A tiny terminal-based digital audio workstation made for fun, experimentation, and learning about audio, MIDI, and terminal applications.
- **Install:** Build from source
- **License:** Not specified
- **Notes:** Educational project focused on understanding audio processing fundamentals. Minimal but instructive.

---

### Ecasound

- **GitHub:** https://github.com/kaivehmanen/ecasound
- **Website:** https://ecasound.seul.org
- **What:** A command-line multitrack audio recorder and effects processor. Pure CLI -- no native GUI. Supports JACK and LADSPA effects plugins.
- **Install:** Build from source (or `brew install ecasound` if available)
- **License:** GPL-2.0
- **CLI Examples:**
  ```bash
  # Record from mic to file
  ecasound -i alsa -o output.wav

  # Play a file through an effect chain
  ecasound -i input.wav -o alsa -el:ladspa_reverb,0.5

  # Mix two files
  ecasound -a:1 -i file1.wav -a:2 -i file2.wav -a:all -o output.wav

  # Real-time effects processing
  ecasound -i alsa -o alsa -ef3,1000,1.5,0.9
  ```
- **Notes:** The concept of "chains" (like patch cables in a modular synth) is the core abstraction. GUI frontends exist (Nama, EcaEnveloptor) but the CLI is the primary interface. One of the oldest and most battle-tested CLI audio processing tools. Supports JACK, LADSPA, and real-time controllable oscillators.

---

## 22. Terminal Music Players

### musikcube

- **GitHub:** https://github.com/clangen/musikcube
- **Website:** https://musikcube.com
- **What:** A cross-platform, terminal-based audio engine, library, player, and server written in C++. Supports libraries with 250,000+ tracks.
- **Install:** `brew install musikcube`
- **License:** BSD-3-Clause
- **Features:**
  - File scanning and tag indexing
  - Gapless and crossfading playback
  - Play queue management and playlists
  - Built-in streaming audio server (WebSocket + HTTP)
  - Extensible plugin architecture
  - ncurses terminal UI
- **Notes:** Not just a player -- it is a full music server. Stream from one machine to another. The plugin system supports custom decoders, DSP, and output handlers. 4000+ GitHub stars.

---

### cmus

- **GitHub:** https://github.com/cmus/cmus
- **Website:** https://cmus.github.io
- **What:** A small, fast, and powerful console music player for Unix-like operating systems. Supports MP3, OGG, FLAC, Opus, and many more formats.
- **Install:** `brew install cmus`
- **License:** GPL-2.0
- **Notes:** Vim-like keybindings. Can be controlled remotely via `cmus-remote`. Multiple view modes. Last.fm and ListenBrainz scrobbling. Lightweight. The classic terminal music player.

---

### kew

- **GitHub:** https://github.com/ravachol/kew
- **What:** A terminal music player with full-color album art (in sixel-capable terminals) and a built-in audio visualizer.
- **Install:** Build from source
- **License:** GPL-2.0
- **Notes:** Displays album covers in the terminal using sixel graphics. The visualizer has various modes. Searches your music library and creates playlists automatically. Modern and visually striking.

---

## 23. Additional Esoteric & Notable Tools

### Seq80x25

- **GitHub:** https://github.com/frangedev/Seq80x25
- **What:** A retro-inspired, terminal-based music sequencer that mimics DOS-style interfaces. Built to run in an 80x25 terminal grid for chiptune-style composition.
- **Install:** Clone and run with Python
- **License:** Not specified
- **Features:**
  - 80x25 terminal grid with ASCII-based visuals
  - 8 built-in musical patterns (scales, arpeggios, blues, chiptune)
  - Multiple export formats (JSON, WAV, MIDI, text, CSV)
  - 8 professional effects types
  - Cross-platform (Python)

---

### SunVox

- **Website:** https://warmplace.ru/soft/sunvox/
- **What:** A fast, powerful modular synthesizer with a pattern-based sequencer. Free for desktop, can run headless. Extremely portable -- runs on everything from Raspberry Pi to Windows to macOS.
- **Install:** Download from website (free for desktop)
- **License:** Proprietary (but free for desktop use)
- **Notes:** Not strictly CLI but can run headless via configuration. The modular synthesis engine is professional-grade. Pattern-based sequencer familiar to tracker users. One of the smallest fully-featured music production tools in existence.

---

### LilyPond

- **Website:** https://lilypond.org
- **GitHub:** https://gitlab.com/lilypond/lilypond
- **What:** A text-based music engraving program. Write music notation as text; LilyPond compiles it to beautifully typeset sheet music (PDF, SVG) and MIDI files.
- **Install:** `brew install lilypond`
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Compile to PDF and MIDI
  lilypond myscore.ly

  # Output PNG instead of PDF
  lilypond --png myscore.ly

  # Specify output format
  lilypond --pdf -o output myscore.ly

  # Example .ly file content:
  # \relative c' { c4 d e f | g2 g | a4 a a a | g1 | }
  ```
- **Notes:** The gold standard for music engraving. Output quality rivals Finale and Sibelius. The text-based input means scores can be version-controlled with Git. Extensive macro system. Can generate MIDI output for playback.

---

### Gwion

- **GitHub:** https://github.com/Gwion/Gwion
- **What:** A strongly-timed musical programming language inspired by ChucK, adding high-level features like templates, first-class functions, and generics. Aims to be simple, small, fast, extendable, and embeddable.
- **Install:** Build from source
- **License:** MIT
- **Notes:** If you like ChucK's time-based model but want more modern language features, Gwion is worth exploring. Plugin-based architecture where sound-making capabilities come from loadable modules. Actively developed.

---

### Music Suite (Haskell)

- **GitHub:** https://github.com/music-suite/music-suite
- **Website:** https://music-suite.github.io/docs/ref/
- **What:** A Haskell library for describing music. Represents and manipulates music in a very general sense, compatible with standard notation.
- **Install:** Available via Hackage
- **License:** BSD-3-Clause
- **CLI Examples:**
  ```bash
  # Convert a music expression to PDF
  music2pdf composition.music

  # Convert to MIDI
  music2midi composition.music

  # Convert to LilyPond
  music2ly composition.music
  ```
- **Notes:** Leverages Haskell's type system for musical representation. Supports LilyPond, MusicXML, and ABC notation output. Deep mathematical foundations. The `music2...` utilities compile musical expressions into various formats.

---

### Strudel

- **Website:** https://strudel.cc
- **What:** A JavaScript port of TidalCycles' pattern language for live coding in the browser. Includes a REPL that runs entirely in the browser.
- **License:** AGPL-3.0
- **Notes:** Not strictly CLI but the REPL interface is text-based. Can connect to SuperCollider via OSC or to hardware via MIDI. The mini-notation for patterns is identical to TidalCycles. Good for quick experimentation without installing anything.

---

### OpenAI Jukebox

- **GitHub:** https://github.com/openai/jukebox
- **What:** A neural network that generates music (including rudimentary singing) as raw audio. Trained on 1.2 million songs.
- **Install:** `pip install git+https://github.com/openai/jukebox.git`
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Generate a sample
  python jukebox/sample.py --model=5b_lyrics --name=sample_5b \
    --levels=3 --sample_length_in_seconds=20

  # Multi-GPU
  mpiexec -n 4 python jukebox/sample.py --model=5b_lyrics ...
  ```
- **Notes:** Requires significant GPU resources. The generated audio is lo-fi but recognizably musical, including approximations of singing. Historically significant as an early large-scale neural music generator. Research tool, not production-ready.

---

## Awesome Lists & Resource Collections

For further exploration, these curated lists are invaluable:

| List | URL | Focus |
|------|-----|-------|
| awesome-music-production | https://github.com/ad-si/awesome-music-production | Software, services, resources for music creation |
| awesome-music | https://github.com/noteflakes/awesome-music | Music libraries, tools, frameworks |
| awesome-audio-dsp | https://github.com/BillyDM/Awesome-Audio-DSP | Audio DSP and plugin development |
| awesome-python-scientific-audio | https://github.com/faroit/awesome-python-scientific-audio | Python audio research tools |
| awesome-linuxaudio | https://github.com/nodiscc/awesome-linuxaudio | Linux audio production |
| awesome-livecoding | https://github.com/toplap/awesome-livecoding | Live coding tools and resources |
| awesome-musicdsp | https://github.com/olilarkin/awesome-musicdsp | Music DSP programming resources |
| awesome-audio (DolbyIO) | https://github.com/DolbyIO/awesome-audio | Audio technology for developers |
| Rust Audio Link Collection | https://gist.github.com/WeirdConstructor/276f7e0555b2dbe83614268b59a7a998 | Rust audio ecosystem |

---

## Recommended Starting Points

**Quickest path to sound from terminal:**
1. `brew install sox` then `play -n synth 2 sine 440` -- instant tone
2. `brew install chuck` then write a `.ck` file -- instant real-time synthesis
3. `brew install alda` then `alda play -c "piano: c d e f g"` -- instant music

**For live coding / performance:**
1. TidalCycles (pattern-based, Haskell) -- industry standard
2. Sardine (Python) -- most accessible if you know Python
3. Glicol (Rust, file-watching) -- edit a text file, hear changes

**For deep sound design / DSP:**
1. Csound -- most opcodes, most documentation, most powerful
2. SuperCollider -- most flexible real-time engine
3. Faust -- best for creating optimized DSP code

**For audio analysis:**
1. Aubio -- CLI beat/pitch/onset detection, no setup required
2. Essentia -- comprehensive MIR (music information retrieval)
3. Sonic Annotator + Vamp plugins -- extensible analysis framework

**For stem separation / AI:**
1. Demucs -- best quality vocal/drum/bass separation
2. Spleeter -- faster, with unique 5-stem model
3. CREPE -- state-of-the-art pitch tracking via neural network

**For maximum weirdness:**
1. Bytebeat -- one-line mathematical compositions
2. Orca -- 2D grid programming language for sequencing
3. Sporth -- stack-based modular synthesis in text
4. Celltone -- cellular automata driving MIDI
5. athenaCL -- L-systems, genetic algorithms, Xenakis sieves

**For algorithmic composition:**
1. isobar (Python) -- Markov chains, Euclidean rhythms, L-systems
2. athenaCL -- 80+ algorithmic models, multi-format output
3. Polyrhythmix -- polyrhythmic MIDI drum generation

**For music library management:**
1. Beets -- auto-tagging, metadata correction, plugin ecosystem
2. r128gain / loudgain -- loudness normalization
3. Chromaprint/fpcalc -- acoustic fingerprinting

**For scripting / automation:**
1. SoX -- pipe audio, chain effects, generate tones in bash scripts
2. FFmpeg -- universal conversion, loudness analysis, visualization
3. FluidSynth -- render MIDI to audio programmatically
4. Csound -- batch render complex scores

**For terminal aesthetics:**
1. CAVA -- gorgeous bar spectrum visualizer
2. Cursynth -- full synth in ncurses
3. Orca -- animated 2D code grid
4. PLEBTracker -- tracker interface in the terminal
5. musikcube -- full music player/server with ncurses UI
