# CLI Audio Plugin Hosts, Effects Processors & Audio Routing Tools

Comprehensive survey of open-source, command-line tools for hosting AU/VST/VST3/CLAP plugins,
processing audio with effects, sampling, audio routing, and MIDI tooling on macOS.

**Key focus:** Loading existing AU, VST, VST3, and CLAP plugins from the command line,
sending MIDI to instrument plugins, capturing audio output, and batch processing audio
through effect chains -- all without a GUI.

---

## Table of Contents

1. [CLI Plugin Hosts (Load & Run Plugins from Terminal)](#1-cli-plugin-hosts)
2. [Python-Based Plugin Hosts](#2-python-based-plugin-hosts)
3. [Full-Featured Plugin Hosts with Headless/CLI Modes](#3-full-featured-plugin-hosts-with-headlesscli-modes)
4. [Plugin Validation & Inspection CLI Tools](#4-plugin-validation--inspection-cli-tools)
5. [CLI Audio Effects Processors](#5-cli-audio-effects-processors)
6. [CLI Samplers & Sample Tools](#6-cli-samplers--sample-tools)
7. [SoX Audio Processing Capabilities](#7-sox-audio-processing-capabilities)
8. [FFmpeg Audio Capabilities](#8-ffmpeg-audio-capabilities)
9. [Audio Routing on macOS](#9-audio-routing-on-macos)
10. [JACK Audio on macOS](#10-jack-audio-on-macos)
11. [CLI Audio Recording & Playback](#11-cli-audio-recording--playback)
12. [CLI MIDI Tools](#12-cli-midi-tools)
13. [macOS Built-in Audio CLI Tools](#13-macos-built-in-audio-cli-tools)
14. [LV2 Plugin CLI Tools](#14-lv2-plugin-cli-tools)
15. [Quick Reference Matrix](#15-quick-reference-matrix)
16. [Recommended Workflows](#16-recommended-workflows)

---

## 1. CLI Plugin Hosts

These tools load AU/VST/VST3/CLAP plugins and process audio or render MIDI -- all from the command line.

### Plugalyzer

- **GitHub:** https://github.com/CrushedPixel/Plugalyzer
- **What:** A command-line VST3, AU, LADSPA, and LV2 plugin host for non-realtime audio processing. Designed to make it easy to run plugins outside a DAW for debugging, batch processing, or automation. Processes audio and/or MIDI from input files, writes processed output to a file.
- **Plugin Formats:** VST3, AU, LADSPA, LV2 (no CLAP, no VST2)
- **Install:** Build from source (CMake). No pre-built binaries.
  ```bash
  git clone https://github.com/CrushedPixel/Plugalyzer
  cd Plugalyzer
  mkdir build && cd build
  cmake ..
  make
  ```
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Process audio through a VST3 effect
  plugalyzer process --plugin=/path/to/MyEffect.vst3 \
      --input=input.wav --output=output.wav

  # Render MIDI through a VST3 instrument
  plugalyzer process --plugin=/path/to/MySynth.vst3 \
      --midiInput=melody.mid --output=rendered.wav

  # Set plugin parameters
  plugalyzer process --plugin=/path/to/MyEffect.vst3 \
      --input=input.wav --output=output.wav \
      --param="Mix:0.5" --param="Decay:3.2"

  # Use a parameter automation JSON file
  plugalyzer process --plugin=/path/to/MyEffect.vst3 \
      --input=input.wav --output=output.wav \
      --paramFile=automation.json

  # Load a VST3 preset
  plugalyzer process --plugin=/path/to/MySynth.vst3 \
      --midiInput=melody.mid --output=rendered.wav \
      --preset=my_preset.vstpreset

  # Set sample rate, block size, bit depth
  plugalyzer process --plugin=/path/to/MyEffect.vst3 \
      --input=input.wav --output=output.wav \
      --sampleRate=48000 --blockSize=512 --bitDepth=24

  # Sidechain input (multiple input buses)
  plugalyzer process --plugin=/path/to/Compressor.vst3 \
      --input=main.wav --input=sidechain.wav --output=output.wav

  # List plugin parameters
  plugalyzer list-params --plugin=/path/to/MyEffect.vst3
  ```
- **Key Features:**
  - Sidechain / multi-bus input support
  - Parameter automation via JSON keyframes (samples, seconds, or percentage)
  - VST3 preset file loading
  - Configurable sample rate, block size, bit depth, output channels
- **Notes:** This is arguably the most capable modern CLI plugin host. The JSON automation system allows complex parameter changes over time. CLAP and VST2 are not supported. JUCE-based, so AU support works on macOS.

---

### Vstility

- **GitHub:** https://github.com/OpenAnime/vstility
- **What:** A simple CLI tool that uses JUCE to apply audio plugins to audio files. Minimal, focused on "run one plugin on one file."
- **Plugin Formats:** VST3 (fully supported), VST 1-2 (WIP), LADSPA (WIP)
- **Install:** Build from source (CMake + JUCE)
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Apply a VST3 plugin to an audio file
  vstility --input=input.wav --output=output.wav --vst3=/path/to/plugin.vst3

  # Overwrite output without prompting
  vstility --input=input.wav --output=output.wav --vst3=/path/to/plugin.vst3 --y
  ```
- **Notes:** Very simple interface. Plugin dependencies must be available or the app will crash. Good for quick one-off processing.

---

### MrsWatson (Archived)

- **GitHub:** https://github.com/teragonaudio/MrsWatson
- **What:** A command-line audio plugin host. Takes audio and/or MIDI file as input, processes through one or more VST plugins, writes output. Was the original tool in this space.
- **Plugin Formats:** VST2 only (no VST3, no AU, no CLAP)
- **Install:** Download pre-built binaries from teragonaudio.com/MrsWatson or build from source
- **License:** BSD
- **CLI Examples:**
  ```bash
  # Process audio through a VST effect
  mrswatson --input input.wav --output out.wav --plugin myplugin

  # Render MIDI through an instrument with a preset
  mrswatson --midi-file mysong.mid --output out.wav --plugin piano,soft.fxp

  # Chain multiple plugins (semicolon-separated)
  mrswatson --input input.wav --output out.wav \
      --plugin "compressor;eq;reverb"

  # List available plugins
  mrswatson --list-plugins

  # Verbose output with error reporting
  mrswatson --input input.wav --output out.wav --plugin myplugin --verbose

  # Full help
  mrswatson --help full
  ```
- **Notes:** **PROJECT IS ARCHIVED** -- no longer maintained. VST2 only, which is increasingly problematic since Steinberg has discontinued the VST2 SDK. Separate 32-bit and 64-bit executables. Historical significance as the original CLI plugin host, but Plugalyzer and Pedalboard are better choices today.

---

### Sushi (Elk Audio)

- **GitHub:** https://github.com/elk-audio/sushi
- **What:** A headless, track-based DAW / plugin host. Originally built for Elk Audio OS (embedded Linux audio), but since v1.0 builds natively on macOS with Core Audio. Configuration-driven via JSON. Controllable at runtime via gRPC, OSC, MIDI, and Ableton Link.
- **Plugin Formats:** VST 2.x, VST 3.x, LV2 (LV2 not available on macOS)
- **Install:** Build from source (C++17, CMake + vcpkg)
  ```bash
  git clone --recursive https://github.com/elk-audio/sushi
  cd sushi
  mkdir build && cd build
  cmake -DCMAKE_TOOLCHAIN_FILE=../third-party/vcpkg/scripts/buildsystems/vcpkg.cmake ..
  make
  ```
- **License:** AGPL-3.0
- **CLI Examples:**
  ```bash
  # Offline rendering (process audio file through plugin chain)
  sushi -o -i input.wav -c config.json

  # Real-time with Core Audio on macOS
  sushi --coreaudio -c config.json

  # Real-time with JACK
  sushi -j -c config.json

  # Show all options
  sushi -h
  ```
- **Key Features:**
  - JSON configuration defines tracks, plugins, MIDI routing, sequencing
  - gRPC API for full runtime control (parameter changes, plugin loading, etc.)
  - OSC control interface
  - Ableton Link sync
  - Can also be embedded as a C++ library
  - MIDI support via RtMidi (CoreMIDI on macOS)
- **Notes:** The most "DAW-like" of the CLI tools. The JSON config approach is powerful for reproducible setups. The gRPC API means you can control everything programmatically from any language. AGPL license is restrictive for commercial use. No CLAP or AU support.

---

### RenderMan

- **GitHub:** https://github.com/fedden/RenderMan
- **What:** A command-line C++ and Python VSTi host library for rendering audio from instrument plugins. Designed for machine learning researchers who need to render large datasets of synthesizer audio.
- **Plugin Formats:** VST2 (via JUCE)
- **Install:** Build from source (requires JUCE, Maximilian)
- **License:** MIT (implied from repo structure)
- **Key Features:**
  - Load VST instruments and set/get parameters
  - Send MIDI notes, render patches to WAV
  - Extract audio features (MFCC, FFT, RMS)
  - Python bindings for scripting
  - Generate and render random patches
- **Notes:** Purpose-built for ML audio datasets. The Python bindings make it scriptable. VST2-only is a limitation. Good for batch rendering large numbers of synth presets.

---

## 2. Python-Based Plugin Hosts

### Pedalboard (Spotify)

- **GitHub:** https://github.com/spotify/pedalboard
- **What:** A Python library for audio processing that can load VST3 and AU plugins. Built by Spotify's Audio Intelligence Lab. Includes 20+ built-in effects and supports loading external plugins for both effects processing and instrument rendering (with MIDI).
- **Plugin Formats:** VST3, AU (macOS) -- no VST2, no CLAP
- **Install:** `pip install pedalboard`
- **License:** GPL-3.0
- **CLI / Script Examples:**
  ```python
  from pedalboard import Pedalboard, Reverb, Chorus, Delay, load_plugin
  from pedalboard.io import AudioFile

  # Load a VST3 or AU plugin
  effect = load_plugin("/Library/Audio/Plug-Ins/VST3/FabFilter Pro-R.vst3")
  instrument = load_plugin("/Library/Audio/Plug-Ins/Components/Diva.component")

  # See and set plugin parameters
  print(effect.parameters.keys())
  effect.mix = 0.5
  effect.decay = 3.0

  # Process audio through a plugin
  with AudioFile("input.wav") as f:
      audio = f.read(f.frames)
      sr = f.samplerate

  processed = effect(audio, sr)

  with AudioFile("output.wav", "w", sr, audio.shape[0]) as f:
      f.write(processed)

  # Chain built-in + external effects
  board = Pedalboard([
      load_plugin("./MyCompressor.vst3"),
      Reverb(room_size=0.8),
      Chorus(rate_hz=1.5),
  ])
  processed = board(audio, sr)

  # Render MIDI through an instrument plugin
  from mido import Message
  audio = instrument(
      [Message("note_on", note=60), Message("note_off", note=60, time=5)],
      duration=5,
      sample_rate=44100,
  )

  # Load a VST3 preset
  effect.load_vst3_preset("my_preset.vstpreset")
  ```
- **Built-in Effects:**
  - Dynamics: Compressor, Gain, Limiter, NoiseGate
  - Filters: HighpassFilter, LowpassFilter, LadderFilter, HighShelfFilter, LowShelfFilter, PeakFilter
  - Spatial: Convolution, Delay, Reverb
  - Modulation: Chorus, Phaser
  - Distortion: Distortion, Clipping, Bitcrush
  - Pitch: PitchShift
  - Codecs: MP3Compressor, GSMFullRateCompressor
  - Utility: Resample, Invert, Mix
- **Key Features:**
  - 300x faster than pySoX, 4x faster file reading than librosa
  - Releases Python GIL for multi-threaded processing
  - TensorFlow integration for ML pipelines
  - Streaming / real-time capable via AudioStream
  - Cross-platform (macOS, Windows, Linux)
- **Notes:** The best option if you want Python-scriptable plugin hosting. The combination of built-in effects + external plugin loading + MIDI instrument rendering makes this extremely versatile. Actively maintained by Spotify. The pedalboard-pluginary companion tool (https://github.com/twardoch/pedalboard-pluginary) adds CLI plugin discovery and management.

---

### DawDreamer

- **GitHub:** https://github.com/DBraun/DawDreamer
- **What:** A full Digital Audio Workstation in Python. Composable audio processor graphs, VST instrument/effect hosting, Faust DSP integration, MIDI support, time-stretching, parameter automation.
- **Plugin Formats:** VST2, VST3, AU (.component on macOS) -- no CLAP
- **Install:** `pip install dawdreamer` (Python 3.11-3.14, macOS Apple Silicon 11.0+)
- **License:** GPL-3.0
- **CLI / Script Examples:**
  ```python
  import dawdreamer as daw

  engine = daw.RenderEngine(sample_rate=44100, block_size=512)

  # Load a VST instrument
  synth = engine.make_plugin_processor("synth", "/path/to/Synth.vst3")
  synth.add_midi_note(60, 127, 0.0, 2.0)  # note, velocity, start, duration
  synth.add_midi_note(64, 100, 0.5, 1.5)

  # Load a VST effect
  reverb = engine.make_plugin_processor("reverb", "/path/to/Reverb.vst3")

  # Load presets
  synth.load_vst3_preset("/path/to/preset.vstpreset")

  # Build the processing graph
  graph = [
      (synth, []),
      (reverb, ["synth"]),
  ]
  engine.load_graph(graph)
  engine.render(5.0)  # render 5 seconds

  # Get audio output
  audio = engine.get_audio()

  # Parameter automation
  synth.set_automation("Cutoff", [0.0, 0.5, 1.0])  # automate over time
  ```
- **Key Features:**
  - DAG-based audio processor routing (like a DAW mixer)
  - MIDI playback (programmatic note-by-note or MIDI file loading)
  - MIDI file export
  - Faust DSP code compilation and execution
  - Time-stretching / pitch-shifting via RubberBand
  - Ableton Live warp marker support
  - Parameter automation at audio-rate or PPQN-rate
  - Multi-processor parallel rendering
- **Notes:** The most "DAW-like" Python tool. Build complex signal processing graphs with multiple instruments and effects. The Faust integration means you can write custom DSP in Faust syntax directly. On macOS, AU (.component) plugins generally work well; some .vst3 plugins may have issues.

---

## 3. Full-Featured Plugin Hosts with Headless/CLI Modes

### Carla

- **GitHub:** https://github.com/falkTX/Carla
- **Website:** https://kx.studio/Applications:Carla
- **What:** A fully-featured, modular audio plugin host. Supports virtually every plugin format. Can run headless with `--no-gui` flag. Multiple processing modes (Rack, Patchbay, Single, Multi-Client). Includes `carla-single` for running individual plugins as standalone JACK clients.
- **Plugin Formats:** LADSPA, DSSI, LV2, VST2, VST3, AU, CLAP, JSFX, SF2/SF3, SFZ
- **Install:** Download from https://kx.studio/Applications:Carla or build from source
- **License:** GPL-2.0+
- **CLI Examples:**
  ```bash
  # Run Carla headless with a saved session
  carla --no-gui my_session.carxp

  # Set client name for headless operation
  CARLA_CLIENT_NAME=my_host carla --no-gui my_session.carxp

  # Run a single plugin as a standalone JACK client (carla-single)
  carla-single native vst3 /path/to/plugin.vst3
  carla-single native au /path/to/plugin.component
  carla-single native clap /path/to/plugin.clap
  carla-single native lv2 http://plugin.uri
  carla-single native sf2 /path/to/soundfont.sf2

  # carla-single supported architectures:
  #   native, posix32, posix64, mac32, mac64, win32, win64

  # carla-single supported formats:
  #   internal, ladspa, dssi, lv2, vst, vst2, vst3, au, clap, jsfx, sf2, sfz
  ```
- **Key Features:**
  - CLAP support (one of the few hosts that supports all major formats including CLAP)
  - Rack mode (serial effect chain) and Patchbay mode (modular routing)
  - OSC remote control
  - MIDI automation
  - Plugin bridging (run 32-bit plugins in 64-bit host, etc.)
  - JACK application hosting (wrap non-plugin audio apps)
  - JACK, CoreAudio, and other audio driver support
- **Notes:** Carla is the **only tool in this list that supports all of AU, VST2, VST3, and CLAP** from CLI. The `carla-single` script is particularly useful -- it turns any plugin into a standalone JACK client that you can wire up with other audio tools. Requires JACK for `carla-single`. The `--no-gui` mode with a saved `.carxp` session file enables fully headless operation.

---

### Element

- **GitHub:** https://github.com/kushview/element
- **Website:** https://kushview.net/element/
- **What:** A modular audio plugin host application. Primarily GUI-based but supports all major plugin formats.
- **Plugin Formats:** AU, VST, VST3, LV2, CLAP
- **Install:** Download from kushview.net or build from source
- **License:** GPL-3.0
- **Notes:** Element is primarily a GUI application. Listed here because it supports all major formats and could potentially be scripted or extended. Not a true CLI tool.

---

### AudioGridder

- **GitHub:** https://github.com/apohl79/audiogridder
- **What:** A network-based plugin host that offloads DSP processing to remote machines. Run the AudioGridder Server on any Mac/Windows machine, and use plugins from that machine over the network.
- **Plugin Formats:** VST2, VST3, AU (macOS)
- **Install:** Download from https://audiogridder.com or build from source
- **License:** MIT
- **Key Features:**
  - Network-transparent plugin hosting
  - Stream plugin UIs over network
  - Unlimited remote effect chains
  - Latency compensation
  - Server runs as tray application (background process)
- **Notes:** Not exactly a CLI tool, but the server component runs headless and could be useful for remote plugin processing scenarios. Open source (MIT license) is a plus.

---

## 4. Plugin Validation & Inspection CLI Tools

### pluginval (Tracktion)

- **GitHub:** https://github.com/Tracktion/pluginval
- **What:** A cross-platform plugin validation and testing tool. Loads plugins and runs comprehensive test suites to check for crashes, conformity, and stability. Runs in both GUI and CLI modes.
- **Plugin Formats:** VST2, VST3, AU
- **Install:** Download from GitHub releases
  ```bash
  curl -L https://github.com/Tracktion/pluginval/releases/latest/download/pluginval_macOS.zip -o pluginval.zip
  unzip pluginval.zip
  cp pluginval.app/Contents/MacOS/pluginval /usr/local/bin/
  ```
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Validate a VST3 plugin
  pluginval --validate /path/to/plugin.vst3

  # Validate an AU plugin
  pluginval --validate /path/to/plugin.component

  # Set strictness level (1-10, 5 is recommended minimum)
  pluginval --validate /path/to/plugin.vst3 --strictness-level 5

  # Verbose output
  pluginval --validate /path/to/plugin.vst3 --verbose

  # Exit code: 0 = all tests pass, 1 = failures
  ```
- **Notes:** Excellent for CI pipelines. Strictness levels 1-4 are quick crash tests; level 5+ includes parameter fuzzing and state restoration tests. Exit code makes it scriptable.

---

### auvaltool / auval (macOS Built-in)

- **What:** Apple's built-in Audio Unit validation tool. Ships with macOS. Tests AU plugins for conformity and correctness.
- **Plugin Formats:** AU (AUv2 and AUv3)
- **Install:** Pre-installed on macOS (part of Xcode Command Line Tools)
- **License:** Proprietary (Apple)
- **CLI Examples:**
  ```bash
  # List all installed Audio Units
  auval -a

  # Validate a specific Audio Unit (by type, subtype, manufacturer)
  auval -v aufx MyFX Mfgr
  auval -v aumu MySyn Mfgr
  auval -v aumf MyMid Mfgr

  # Types: aufx=effect, aumu=instrument, aumf=MIDI processor,
  #        aufc=format converter, aumx=mixer, aupn=panner,
  #        augn=generator, auol=offline
  ```
- **Notes:** The canonical way to check if an AU plugin is correctly implemented. Every AU developer uses this. The `-a` flag is useful for listing all installed Audio Units on your system.

---

### Steinberg VST3 Validator

- **GitHub:** https://github.com/steinbergmedia/vst3sdk (part of SDK)
- **What:** A command-line test host for checking VST3 plugin conformity. Part of the VST3 SDK.
- **Plugin Formats:** VST3 only
- **Install:** Build from VST3 SDK source (located at `public.sdk/samples/vst-hosting/validator`)
- **License:** Steinberg VST3 License (proprietary, free to use)
- **Notes:** Useful for VST3 plugin developers. Can run custom test code for CI integration.

---

### clap-info

- **GitHub:** https://github.com/free-audio/clap-info
- **What:** A CLI tool to list and inspect CLAP plugins. Shows descriptors, ports, parameters, and extension information.
- **Plugin Formats:** CLAP only
- **Install:** Build from source (CMake)
- **License:** MIT
- **CLI Examples:**
  ```bash
  # List all installed CLAP plugins
  clap-info -l

  # Scan and print descriptors for all CLAPs
  clap-info -s

  # Show detailed info for a specific CLAP plugin
  clap-info /path/to/plugin.clap
  ```

---

### clap-validator

- **GitHub:** https://github.com/free-audio/clap-validator
- **What:** An automatic validation and test suite for CLAP plugins. Tests for common bugs and incorrect behavior.
- **Plugin Formats:** CLAP only
- **Install:** `cargo install` from source, or download pre-built binaries
- **License:** MIT (implied -- part of free-audio project)
- **CLI Examples:**
  ```bash
  # Validate a CLAP plugin
  clap-validator validate /path/to/plugin.clap

  # List all available tests
  clap-validator list tests

  # Show only failed tests
  clap-validator validate /path/to/plugin.clap --only-failed
  ```
- **Notes:** Tests run in separate processes by default so plugin crashes do not take down the validator.

---

## 5. CLI Audio Effects Processors

### Ecasound

- **GitHub:** https://github.com/kaivehmanen/ecasound
- **Website:** https://ecasound.sourceforge.net/ecasound/
- **What:** A multitrack-capable audio recorder and effect processor. Fully command-line driven. Supports LADSPA plugins, JACK, and its own effect library. Think of it as a CLI DAW.
- **Install:** Build from source, or check package managers
- **License:** GPL-2.0
- **CLI Examples:**
  ```bash
  # Apply effects to an audio file
  ecasound -i input.wav -o output.wav -ef reverb

  # Multitrack mixing with effects
  ecasound -a:1 -i track1.wav -ea:80 \
           -a:2 -i track2.wav -ea:120 \
           -a:3 -i track3.wav -etr:60,0.3 \
           -a:all -o all_tracks.wav

  # Apply LADSPA plugin
  ecasound -i input.wav -o output.wav -el:plugin_id,param1,param2

  # Real-time processing via JACK
  ecasound -i jack -o jack -ef reverb

  # Interactive mode (control effects in real-time)
  ecasound -c -i input.wav -o jack -ef:delay,0.5,0.3
  ```
- **Key Features:**
  - Multitrack mixing and recording
  - LADSPA plugin hosting
  - JACK integration for real-time routing
  - Scriptable (no GUI at all)
  - MIDI control of effects parameters
  - Chain-based architecture (chains = tracks with inputs, outputs, and effects)
- **Notes:** Ecasound is one of the oldest and most capable CLI audio tools. Its chain-based architecture is flexible -- you can build complex routing and effect chains entirely from the command line. Works on macOS. The interactive mode (`-c` flag) allows real-time parameter control.

---

### Rubber Band

- **GitHub:** https://github.com/breakfastquay/rubberband
- **Website:** https://breakfastquay.com/rubberband/
- **What:** A high-quality library and command-line tool for audio time-stretching and pitch-shifting. Used by many DAWs internally.
- **Install:** `brew install rubberband`
- **License:** GPL-2.0 (open source), commercial license available
- **CLI Examples:**
  ```bash
  # Time-stretch to 150% duration, pitch-shift up 2 semitones
  rubberband -t 1.5 -p 2.0 input.wav output.wav

  # Just change tempo (no pitch change)
  rubberband -t 0.8 input.wav faster.wav

  # Just change pitch (no tempo change)
  rubberband -p -3.0 input.wav lower.wav

  # Use higher-quality R3 engine
  rubberband -3 -t 1.5 -p 2.0 input.wav output.wav

  # Preserve formants (keep vocal timbre natural)
  rubberband -p 5.0 --formant input.wav output.wav

  # Show help
  rubberband -h
  ```
- **Notes:** Professional quality. The R3 engine produces excellent results, especially for vocals and complex material. The formant preservation option is key for pitch-shifting vocals without the chipmunk effect.

---

### Guitarix (Headless Mode)

- **GitHub:** https://github.com/brummer10/guitarix
- **What:** A virtual guitar amplifier for Linux/macOS. Over 25 built-in effects modules (compression, distortion, modulation, reverb, delay, EQ). Can run headless on devices like Raspberry Pi.
- **Plugin Formats:** Also available as VST3 and LV2 plugins
- **Install:** Build from source (primarily Linux; macOS support varies)
- **License:** GPL-2.0+
- **Notes:** The effects modules are high quality. Even if the standalone GUI app is Linux-centric, the LV2/VST3 plugin versions of Guitarix effects can be loaded in other CLI plugin hosts on macOS.

---

## 6. CLI Samplers & Sample Tools

### LinuxSampler

- **Website:** https://www.linuxsampler.org/
- **What:** A modular, streaming-capable sampler that supports Gigasampler (.gig), SoundFont (.sf2), and SFZ (.sfz) formats. Runs as a headless server process controllable via the LSCP protocol from the command line.
- **Plugin Formats:** Available as VST, AU, DSSI, LV2, and standalone
- **Install:** Download macOS installer from linuxsampler.org or build from source
- **License:** GPL-2.0
- **CLI Examples:**
  ```bash
  # Start the sampler as a background process
  linuxsampler

  # Connect to it via the LSCP shell
  lscp

  # LSCP commands:
  # CREATE AUDIO_OUTPUT_DEVICE COREAUDIO
  # CREATE MIDI_INPUT_DEVICE COREMIDI
  # ADD CHANNEL
  # LOAD ENGINE SFZ 0
  # LOAD INSTRUMENT '/path/to/instrument.sfz' 0 0
  # SET CHANNEL AUDIO_OUTPUT_DEVICE 0 0
  # SET CHANNEL MIDI_INPUT_DEVICE 0 0
  ```
- **Key Features:**
  - SFZ v2, SF2, Gigasampler format support
  - CoreAudio and CoreMIDI on macOS
  - Headless server architecture (no GUI needed)
  - LSCP protocol for full programmatic control
  - Streaming from disk (handles large sample libraries)
- **Notes:** True headless sampler. The LSCP protocol means you can automate everything. On macOS, uses CoreAudio and CoreMIDI natively. Good for setting up a programmable sample playback server.

---

### FluidSynth (as a Sampler)

- **GitHub:** https://github.com/FluidSynth/fluidsynth
- **What:** While primarily a SoundFont synthesizer, FluidSynth is effectively a command-line sampler. Load a SoundFont, send MIDI notes, get audio out.
- **Install:** `brew install fluid-synth`
- **License:** LGPL-2.1+
- **CLI Examples:**
  ```bash
  # Start FluidSynth with a SoundFont, listening for MIDI
  fluidsynth -a coreaudio -m coremidi /path/to/soundfont.sf2

  # Render MIDI file to audio (offline, fast)
  fluidsynth -a file -F output.wav /path/to/soundfont.sf2 song.mid

  # Non-interactive rendering (no shell, no MIDI input)
  fluidsynth -ni /path/to/soundfont.sf2 song.mid -F output.wav

  # Interactive shell with direct note control
  fluidsynth -i /path/to/soundfont.sf2
  # > noteon 0 60 100
  # > noteon 0 64 80
  # > noteoff 0 60
  # > prog 0 25    (change program/instrument)
  ```
- **Notes:** See the full FluidSynth entry in the companion document (cli-synth-research.md). The `midi2audio` Python wrapper (`pip install midi2audio`) provides an even simpler CLI: `midi2audio input.mid output.wav`.

---

### BBC audiowaveform

- **GitHub:** https://github.com/bbc/audiowaveform
- **What:** A C++ command-line tool for generating waveform data and rendered waveform images from audio files. Not a sampler, but essential for sample management and visualization.
- **Install:** `brew install audiowaveform`
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Generate waveform data (JSON) from an audio file
  audiowaveform -i input.mp3 -o waveform.json -z 256 -b 8

  # Generate waveform data (binary)
  audiowaveform -i input.wav -o waveform.dat -z 256

  # Render waveform as PNG image
  audiowaveform -i input.wav -o waveform.png --width 800 --height 200
  ```
- **Notes:** Useful for building audio file browsers, visualizing samples, or creating waveform displays for web apps. Supports MP3, WAV, FLAC, Ogg Vorbis, and Opus.

---

## 7. SoX Audio Processing Capabilities

SoX (Sound eXchange) is the Swiss Army knife of CLI audio processing. A comprehensive effects reference.

- **GitHub:** https://sourceforge.net/projects/sox/
- **Install:** `brew install sox`
- **License:** GPL-2.0+

### Full Effects List

```bash
# === DYNAMICS ===
# Compand (compressor/expander/limiter)
sox input.wav output.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2

# Noise gate
sox input.wav output.wav compand 0.1,0.3 -inf,-50.1,-inf,-50,-50 0 -90 0.1

# === EQUALIZATION & FILTERING ===
# High-pass filter (remove below 200Hz)
sox input.wav output.wav highpass 200

# Low-pass filter (remove above 5000Hz)
sox input.wav output.wav lowpass 5000

# Band-pass filter (center 1000Hz, width 200Hz)
sox input.wav output.wav bandpass 1000 200

# Parametric EQ (center freq, bandwidth, gain in dB)
sox input.wav output.wav equalizer 1000 200 6

# Bass boost
sox input.wav output.wav bass +6 100

# Treble boost
sox input.wav output.wav treble +3 5000

# === TIME/PITCH ===
# Change speed (and pitch) -- 1.5x faster
sox input.wav output.wav speed 1.5

# Change tempo only (no pitch change)
sox input.wav output.wav tempo 1.5

# Change pitch only (no tempo change) -- up 200 cents
sox input.wav output.wav pitch 200

# === SPATIAL / REVERB ===
# Reverb (reverberance%, HF-damping%, room-scale%, stereo-depth%)
sox input.wav output.wav reverb 80 50 100 100

# Echo (gain-in, gain-out, delay-ms, decay)
sox input.wav output.wav echo 0.8 0.88 500 0.4

# Delay (milliseconds per channel)
sox input.wav output.wav delay 0.5

# === MODULATION ===
# Chorus
sox input.wav output.wav chorus 0.5 0.9 50 0.4 0.25 2 -t

# Flanger
sox input.wav output.wav flanger

# Phaser
sox input.wav output.wav phaser 0.8 0.74 3 0.4 0.5 -t

# Tremolo (speed-Hz, depth-%)
sox input.wav output.wav tremolo 5 50

# === DISTORTION ===
# Overdrive (gain-dB, colour)
sox input.wav output.wav overdrive 20

# === UTILITY ===
# Normalize to 0dB
sox input.wav output.wav norm

# Fade in/out (type, fade-in-length, stop-position, fade-out-length)
sox input.wav output.wav fade t 0.5 0 0.5

# Trim (start, duration)
sox input.wav output.wav trim 1.5 3.0

# Reverse
sox input.wav output.wav reverse

# Repeat
sox input.wav output.wav repeat 3

# Pad with silence (before, after in seconds)
sox input.wav output.wav pad 1.0 2.0

# Convert sample rate
sox input.wav -r 48000 output.wav

# Convert channels (stereo to mono, etc.)
sox input.wav output.wav channels 1

# Concatenate files
sox file1.wav file2.wav file3.wav combined.wav

# Mix files (overlay)
sox -m file1.wav file2.wav mixed.wav

# === CHAIN MULTIPLE EFFECTS ===
sox input.wav output.wav \
    highpass 100 \
    compand 0.3,1 6:-70,-60,-20 -5 -90 0.2 \
    reverb 60 50 80 \
    norm

# === SYNTHESIS ===
# See cli-synth-research.md for full synth capabilities
play -n synth 2 sine 440
sox -n output.wav synth 2 sine 300 reverb 80

# === RECORDING ===
rec output.wav                        # record from default input
rec -c 1 -r 44100 -b 16 output.wav   # mono, 44.1kHz, 16-bit

# === FILE INFO ===
soxi input.wav   # show file details (sample rate, channels, duration, etc.)
```

### SoX Batch Processing (sox-tricks)

- **GitHub:** https://github.com/madskjeldgaard/sox-tricks
- **What:** A collection of shell functions for batch audio processing with SoX.
- **Install:**
  ```bash
  cd ~/ && wget https://raw.githubusercontent.com/datamads/sox-tricks/master/.sox_tricks
  source ~/.sox_tricks
  ```
- **Notes:** Provides single-word commands for common batch operations like normalizing a folder of sounds, converting formats, etc.

---

## 8. FFmpeg Audio Capabilities

FFmpeg ships with 120+ audio filters. A comprehensive reference for audio-specific usage.

- **GitHub:** https://github.com/FFmpeg/FFmpeg
- **Install:** `brew install ffmpeg`
- **License:** LGPL-2.1+ / GPL-2.0+ (depending on build configuration)

### Audio Effects & Filters

```bash
# === FORMAT CONVERSION ===
ffmpeg -i input.wav output.mp3
ffmpeg -i input.mp3 -ar 44100 -ac 2 -sample_fmt s16 output.wav

# === DYNAMICS ===
# Compressor
ffmpeg -i input.wav -af "acompressor=threshold=-20dB:ratio=4:attack=5:release=50" output.wav

# Limiter
ffmpeg -i input.wav -af "alimiter=limit=0.9:attack=5:release=50" output.wav

# Noise gate
ffmpeg -i input.wav -af "agate=threshold=-40dB:attack=5:release=50" output.wav

# Loudness normalization (EBU R128)
ffmpeg -i input.wav -af "loudnorm=I=-14:TP=-1:LRA=11" output.wav

# De-esser
ffmpeg -i input.wav -af "deesser=i=0.4:m=0.5:f=5500:s=o" output.wav

# === EQUALIZATION ===
# Parametric EQ
ffmpeg -i input.wav -af "equalizer=f=1000:t=q:w=1:g=6" output.wav

# High-pass filter
ffmpeg -i input.wav -af "highpass=f=200" output.wav

# Low-pass filter
ffmpeg -i input.wav -af "lowpass=f=5000" output.wav

# Band-pass filter
ffmpeg -i input.wav -af "bandpass=f=1000:width_type=h:w=200" output.wav

# Superequalizer (18-band)
ffmpeg -i input.wav -af "superequalizer=1b=1:2b=1:3b=1.2:4b=1.5" output.wav

# === SPATIAL / REVERB ===
# Echo
ffmpeg -i input.wav -af "aecho=0.8:0.9:500:0.3" output.wav

# Chorus
ffmpeg -i input.wav -af "chorus=0.5:0.9:50|60:0.4|0.32:0.25|0.4:2|2.3" output.wav

# Phaser
ffmpeg -i input.wav -af "aphaser=in_gain=0.4:out_gain=0.74:delay=3:decay=0.4:speed=0.5" output.wav

# === PITCH / TEMPO ===
# Change tempo without affecting pitch (atempo: 0.5 to 100.0)
ffmpeg -i input.wav -af "atempo=1.5" output.wav

# Change pitch (via rubberband filter, if compiled with librubberband)
ffmpeg -i input.wav -af "rubberband=pitch=1.5" output.wav

# === FADE / VOLUME ===
# Fade in (first 2 seconds) and fade out (last 3 seconds)
ffmpeg -i input.wav -af "afade=t=in:st=0:d=2,afade=t=out:st=57:d=3" output.wav

# Volume adjustment
ffmpeg -i input.wav -af "volume=0.5" output.wav

# === NOISE / ANALYSIS ===
# Remove silence
ffmpeg -i input.wav -af "silenceremove=start_periods=1:start_threshold=-50dB" output.wav

# Noise reduction (via afftdn)
ffmpeg -i input.wav -af "afftdn=nf=-20" output.wav

# === TRIMMING ===
# Trim (start at 10s, duration 30s)
ffmpeg -ss 10 -t 30 -i input.wav output.wav

# === MIXING ===
# Mix two audio files
ffmpeg -i file1.wav -i file2.wav -filter_complex "amix=inputs=2:duration=longest" output.wav

# Concatenate audio files
ffmpeg -i "concat:file1.wav|file2.wav" -acodec copy output.wav

# === CHAINING EFFECTS ===
ffmpeg -i input.wav -af "highpass=f=100,acompressor=threshold=-20dB:ratio=4,equalizer=f=3000:t=q:w=2:g=3,aecho=0.8:0.9:500:0.3,loudnorm=I=-14" output.wav

# === ANALYSIS ===
# Get audio file info
ffprobe -v quiet -print_format json -show_format -show_streams input.wav

# Show audio levels / loudness
ffmpeg -i input.wav -af "volumedetect" -f null -

# EBU R128 loudness measurement
ffmpeg -i input.wav -af "ebur128" -f null -

# Play audio from command line
ffplay -nodisp -autoexit input.wav
```

---

## 9. Audio Routing on macOS

### BlackHole

- **GitHub:** https://github.com/ExistentialAudio/BlackHole
- **Website:** https://existential.audio/blackhole/
- **What:** A modern macOS audio loopback driver. Creates virtual audio devices that pass audio between applications with zero additional latency.
- **Install:**
  ```bash
  brew install blackhole-2ch     # 2-channel version
  brew install blackhole-16ch    # 16-channel version
  brew install blackhole-64ch    # 64-channel version
  ```
- **License:** MIT
- **Key Features:**
  - Zero additional latency
  - 2, 16, or 64 channel versions (customizable to 256+)
  - Supports 44.1/48/88.2/96/176.4/192 kHz sample rates
  - Works with any CoreAudio application
- **Usage with CLI tools:**
  ```bash
  # Route audio from one CLI tool to another via BlackHole:
  # 1. Set BlackHole as output device for tool A
  # 2. Set BlackHole as input device for tool B
  # 3. Use Multi-Output Device in Audio MIDI Setup to hear audio too

  # Record system audio via BlackHole + sox
  rec -d "BlackHole 2ch" output.wav

  # Record system audio via BlackHole + ffmpeg
  ffmpeg -f avfoundation -i ":BlackHole 2ch" output.wav
  ```

---

### switchaudio-osx

- **GitHub:** https://github.com/deweller/switchaudio-osx
- **What:** A command-line utility to switch macOS audio input/output devices. Essential for scripting audio routing.
- **Install:** `brew install switchaudio-osx`
- **License:** MIT
- **CLI Examples:**
  ```bash
  # List all audio devices
  SwitchAudioSource -a

  # Show current output device
  SwitchAudioSource -c

  # Switch output to BlackHole
  SwitchAudioSource -s "BlackHole 2ch"

  # Switch input device
  SwitchAudioSource -t input -s "BlackHole 2ch"

  # Cycle to next output device
  SwitchAudioSource -n

  # Switch by device ID
  SwitchAudioSource -i 42

  # Show current device in specific format
  SwitchAudioSource -c -f json
  ```
- **Notes:** Essential companion tool for BlackHole. Scriptable audio device switching enables complex routing scenarios from shell scripts.

---

### Background Music

- **GitHub:** https://github.com/kyleneideck/BackgroundMusic
- **What:** A macOS audio utility for per-application volume control and system audio recording. Installs a virtual audio device.
- **Install:** `brew install --cask background-music`
- **License:** GPL-2.0
- **CLI Control (via AppleScript):**
  ```bash
  # Set per-app volume from command line
  osascript -e 'tell application "Background Music" to setappvolume bundle "com.spotify.client" volume 0.5 end tell'
  ```
- **Notes:** Per-app volume control from CLI via AppleScript. The virtual audio device can be used for system audio capture.

---

### vpcm

- **GitHub:** https://github.com/SimulPiscator/vpcm
- **What:** Creates virtual audio devices on macOS from the command line. Unlike BlackHole (which uses a fixed set of devices), vpcm lets you create and delete virtual devices dynamically.
- **License:** Check repository
- **CLI Examples:**
  ```bash
  # Create a virtual audio device
  echo "create MyVirtualDevice 2 44100" > /dev/vpcm

  # Delete a virtual device
  echo "delete MyVirtualDevice" > /dev/vpcm
  ```
- **Notes:** Kernel extension -- requires reduced security on modern macOS. More flexible than BlackHole for dynamic device creation.

---

## 10. JACK Audio on macOS

### JACK2

- **Website:** https://jackaudio.org/
- **GitHub:** https://github.com/jackaudio/jack2
- **What:** The JACK Audio Connection Kit -- a professional sound server daemon for low-latency audio routing between applications. The standard inter-application audio routing system on Linux, also works on macOS.
- **Install:**
  ```bash
  # Via Homebrew (limited CLI tools -- may only include jackd)
  brew install jack

  # Via official installer (full CLI tools) -- RECOMMENDED
  # Download from https://jackaudio.org/downloads/
  # macOS installer includes all CLI tools
  ```
- **License:** GPL-2.0 / LGPL-2.1
- **CLI Tools (from full installer):**
  ```bash
  # Start the JACK server with CoreAudio
  jackd -d coreaudio

  # Start with specific settings
  jackd -d coreaudio -r 48000 -p 256

  # List all JACK ports
  jack_lsp

  # List ports with connections
  jack_lsp -c

  # Connect two ports
  jack_connect system:capture_1 myapp:input_1

  # Disconnect ports
  jack_disconnect system:capture_1 myapp:input_1

  # Monitor JACK connections in real-time
  jack_lsp -c -p

  # Show JACK server status
  jack_lsp -l   # show latency
  ```
- **Important Note:** The Homebrew `jack` formula may only install `jackd` without the CLI tools (`jack_connect`, `jack_lsp`, `jack_disconnect`, etc.). For the full set of CLI tools, use the official JACK2 macOS installer from jackaudio.org.
- **Notes:** JACK is the foundation that makes tools like Carla, jalv, mod-host, and Ecasound work together. On macOS, JACK bridges to CoreAudio. Essential for any serious CLI audio routing setup.

---

## 11. CLI Audio Recording & Playback

### SoX rec / play

```bash
# Record from default input
rec output.wav

# Record with specific format
rec -c 1 -r 44100 -b 16 output.wav   # mono, 44.1kHz, 16-bit

# Record with time limit
rec output.wav trim 0 30   # record 30 seconds

# Record with silence detection (stop when silent)
rec output.wav silence 1 0.1 3% 1 3.0 3%

# Play an audio file
play output.wav

# Play with effects
play output.wav reverb 50 speed 0.8
```

### FFmpeg Recording

```bash
# Record from macOS audio input (avfoundation)
ffmpeg -f avfoundation -i ":0" output.wav

# Record from specific device (list devices first)
ffmpeg -f avfoundation -list_devices true -i ""
ffmpeg -f avfoundation -i ":BlackHole 2ch" output.wav

# Record with format options
ffmpeg -f avfoundation -ar 48000 -ac 2 -i ":0" -acodec pcm_s24le output.wav
```

### macOS Built-in

```bash
# Play audio file
afplay output.wav

# Play with volume (0-255, default 1)
afplay -v 0.5 output.wav

# Play with rate (playback speed)
afplay -r 1.5 output.wav

# Text-to-speech
say "hello world"
say -v Cellos "doo doo doo"
say -o output.aiff "save to file"
```

---

## 12. CLI MIDI Tools

### SendMIDI

- **GitHub:** https://github.com/gbevin/SendMIDI
- **What:** A multi-platform command-line tool to send MIDI messages to any MIDI device or virtual port.
- **Install:** `brew install sendmidi`
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # List MIDI output devices
  sendmidi list

  # Send a note
  sendmidi dev "My Synth" on 60 127

  # Send a note with duration
  sendmidi dev "My Synth" on 60 100 sleep 500 off 60

  # Send CC message
  sendmidi dev "My Synth" cc 1 64

  # Send program change
  sendmidi dev "My Synth" pc 42

  # Send pitch bend
  sendmidi dev "My Synth" pb 8192

  # Chain multiple messages
  sendmidi dev "My Synth" ch 1 on 60 100 sleep 250 on 64 100 sleep 250 on 67 100 sleep 500 off 60 off 64 off 67
  ```

---

### ReceiveMIDI

- **GitHub:** https://github.com/gbevin/ReceiveMIDI
- **What:** A multi-platform command-line tool to monitor and receive MIDI messages. Output is compatible with SendMIDI for recording/playback.
- **Install:** `brew install receivemidi`
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # List MIDI input devices
  receivemidi list

  # Monitor all MIDI from a device
  receivemidi dev "My Controller"

  # Filter for specific message types
  receivemidi dev "My Controller" nn   # note on only
  receivemidi dev "My Controller" cc   # CC only

  # Record MIDI and pipe to SendMIDI for playback
  receivemidi dev "My Controller" > recorded.txt
  sendmidi dev "My Synth" < recorded.txt

  # Forward MIDI from one device to another (live)
  receivemidi dev "Controller" | sendmidi dev "Synth"
  ```

---

### midi2audio

- **GitHub:** https://github.com/bzamecnik/midi2audio
- **What:** Python/CLI wrapper around FluidSynth for rendering MIDI files to audio.
- **Install:** `pip install midi2audio` (requires FluidSynth and a SoundFont)
- **License:** MIT
- **CLI Examples:**
  ```bash
  # Render MIDI to WAV
  midi2audio input.mid output.wav

  # Render to FLAC
  midi2audio input.mid output.flac

  # Use custom SoundFont
  midi2audio -s /path/to/soundfont.sf2 input.mid output.wav

  # Custom sample rate
  midi2audio -r 48000 input.mid output.wav
  ```

---

## 13. macOS Built-in Audio CLI Tools

These tools ship with macOS and require no installation.

### afplay

```bash
# Play an audio file
afplay song.wav

# Set volume (0 = silent, 1 = normal, up to 255)
afplay -v 0.5 song.wav

# Set playback rate
afplay -r 2.0 song.wav   # 2x speed

# Set start time (seconds)
afplay -t 10 song.wav     # start 10 seconds in
```

### afinfo

```bash
# Show audio file information
afinfo song.wav
# Output includes: format, sample rate, channels, bit depth,
# duration, estimated size, etc.
```

### afconvert

```bash
# Convert WAV to AAC
afconvert input.wav output.m4a -d aac -f m4af

# Convert to AIFF
afconvert input.wav output.aiff -f AIFF

# Convert to Apple Lossless
afconvert input.wav output.m4a -d alac -f m4af

# Convert sample rate
afconvert input.wav output.wav -d LEI16 -r 48000

# List available formats
afconvert -hf
```

### auvaltool / auval

```bash
# List all installed Audio Units
auval -a

# Validate a specific AU (type subtype manufacturer)
auval -v aufx MyFX Mfgr    # effect
auval -v aumu MySyn Mfgr   # instrument
```

### coreaudiod

```bash
# Restart Core Audio daemon (fixes stuck audio devices)
sudo launchctl kickstart -kp system/com.apple.audio.coreaudiod
```

---

## 14. LV2 Plugin CLI Tools

### lilv-utils (lv2ls, lv2info, lv2apply)

- **GitHub:** https://github.com/lv2/lilv
- **What:** Command-line utilities for working with LV2 plugins.
- **Install:** `brew install lilv` (or build from source)
- **License:** ISC

```bash
# List all installed LV2 plugins
lv2ls

# List plugins by name (instead of URI)
lv2ls -n

# Show detailed info about an LV2 plugin
lv2info http://plugin.uri

# Apply an LV2 plugin to an audio file
lv2apply -i input.wav -o output.wav http://plugin.uri

# Set control port values
lv2apply -i input.wav -o output.wav -c control_port=0.5 http://plugin.uri
```

---

### jalv (JACK LV2 Host)

- **GitHub:** https://github.com/drobilla/jalv
- **What:** A simple host that runs a single LV2 plugin as a JACK client with an interactive CLI.
- **Install:** Build from source (requires JACK, lilv)
- **License:** ISC
- **CLI Examples:**
  ```bash
  # Run an LV2 plugin by URI
  jalv http://calf.sourceforge.net/plugins/Reverb

  # Set control values at startup
  jalv -c vol=0.8 -c decay=3.0 http://plugin.uri

  # Use custom JACK client name
  jalv -n my_reverb http://plugin.uri

  # Run non-interactively (no stdin)
  jalv -x http://plugin.uri
  ```

---

### mod-host

- **GitHub:** https://github.com/mod-audio/mod-host
- **What:** An LV2 host for JACK, controllable via socket or interactive command line. Designed for the MOD audio pedal platform. Supports dynamic loading/unloading of plugins and parameter control.
- **Install:** Build from source (`make && make install`)
- **License:** GPL-3.0
- **CLI Examples:**
  ```bash
  # Start in interactive mode
  mod-host -i

  # Interactive commands:
  # add <lv2_uri> <instance_id>
  add http://calf.sourceforge.net/plugins/Reverb 0

  # connect <origin_port> <destination_port>
  connect system:capture_1 effect_0:in

  # Set parameter
  param_set 0 decay 3.0

  # Remove effect
  remove 0

  # Start as daemon (socket mode, default port 5555)
  mod-host -p 5555

  # Send commands via socket
  echo "add http://plugin.uri 0" | nc localhost 5555
  ```
- **Notes:** The socket mode is powerful -- you can control the effects chain from any programming language by sending text commands to the TCP socket. Think of it as a scriptable guitar pedalboard server.

---

### LADSPA SDK (applyplugin, analyseplugin, listplugins)

- **Website:** https://www.ladspa.org/
- **What:** The original Linux audio plugin SDK includes basic CLI hosting tools.
- **Install:** `brew install ladspa-sdk` (or build from source)
- **License:** LGPL-2.1

```bash
# List all installed LADSPA plugins
listplugins

# Analyse a specific plugin library
analyseplugin /path/to/plugin.so

# Apply a LADSPA plugin to an audio file
applyplugin input.wav output.wav /path/to/plugin.so plugin_label param1 param2

# Set LADSPA search path
export LADSPA_PATH=/usr/local/lib/ladspa:/opt/ladspa
```

---

## 15. Quick Reference Matrix

### Plugin Hosts

| Tool | AU | VST2 | VST3 | CLAP | LV2 | LADSPA | MIDI In | Offline Render | License |
|------|:--:|:----:|:----:|:----:|:---:|:------:|:-------:|:--------------:|---------|
| **Plugalyzer** | Yes | - | Yes | - | Yes | Yes | Yes | Yes | GPL-3.0 |
| **Pedalboard** | Yes | - | Yes | - | - | - | Yes | Yes | GPL-3.0 |
| **DawDreamer** | Yes | Yes | Yes | - | - | - | Yes | Yes | GPL-3.0 |
| **Carla** | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Session | GPL-2.0 |
| **Sushi** | - | Yes | Yes | - | Yes* | - | Yes | Yes | AGPL-3.0 |
| **MrsWatson** | - | Yes | - | - | - | - | Yes | Yes | BSD |
| **Vstility** | - | WIP | Yes | - | - | WIP | - | Yes | MIT |
| **RenderMan** | - | Yes | - | - | - | - | Yes | Yes | MIT |

*LV2 on Linux only for Sushi

### Plugin Inspection/Validation

| Tool | Formats | Purpose |
|------|---------|---------|
| **pluginval** | VST2, VST3, AU | Comprehensive validation suite |
| **auval/auvaltool** | AU | Apple's official AU validator |
| **VST3 Validator** | VST3 | Steinberg's conformity checker |
| **clap-info** | CLAP | List/inspect CLAP plugins |
| **clap-validator** | CLAP | Automatic CLAP testing |
| **lv2ls/lv2info** | LV2 | List/inspect LV2 plugins |

### Effects Processors

| Tool | Plugin Support | Real-time | Offline | Key Strength |
|------|---------------|:---------:|:-------:|-------------|
| **SoX** | None (built-in) | Yes | Yes | Universal, scriptable |
| **FFmpeg** | None (built-in) | Yes | Yes | Format conversion + effects |
| **Ecasound** | LADSPA | Yes (JACK) | Yes | CLI multitrack DAW |
| **Rubber Band** | N/A | - | Yes | Pro time-stretch/pitch-shift |

---

## 16. Recommended Workflows

### Workflow 1: Render MIDI Through a VST3 Synth Plugin

```bash
# Option A: Plugalyzer (pure CLI, C++)
plugalyzer process --plugin=/path/to/Synth.vst3 \
    --midiInput=melody.mid --output=rendered.wav --sampleRate=48000

# Option B: Pedalboard (Python script)
python3 -c "
from pedalboard import load_plugin
from pedalboard.io import AudioFile
from mido import Message

synth = load_plugin('/path/to/Synth.vst3')
audio = synth([Message('note_on', note=60), Message('note_off', note=60, time=4)],
              duration=4, sample_rate=44100)
with AudioFile('rendered.wav', 'w', 44100, 1) as f:
    f.write(audio)
"

# Option C: DawDreamer (Python, DAW-style graph)
python3 -c "
import dawdreamer as daw
engine = daw.RenderEngine(44100, 512)
synth = engine.make_plugin_processor('synth', '/path/to/Synth.vst3')
synth.add_midi_note(60, 127, 0.0, 4.0)
engine.load_graph([(synth, [])])
engine.render(5.0)
import soundfile as sf
sf.write('rendered.wav', engine.get_audio().T, 44100)
"
```

### Workflow 2: Batch Process Audio Files Through a Plugin

```bash
# Using Pedalboard in a script
python3 << 'EOF'
from pedalboard import load_plugin
from pedalboard.io import AudioFile
import glob

effect = load_plugin("/Library/Audio/Plug-Ins/VST3/FabFilter Pro-R.vst3")
effect.mix = 0.3

for input_file in glob.glob("inputs/*.wav"):
    with AudioFile(input_file) as f:
        audio = f.read(f.frames)
        sr = f.samplerate
    processed = effect(audio, sr)
    output_file = input_file.replace("inputs/", "outputs/")
    with AudioFile(output_file, "w", sr, audio.shape[0]) as f:
        f.write(processed)
EOF
```

### Workflow 3: Chain Multiple Plugins (CLI Only)

```bash
# Plugalyzer doesn't support chaining natively -- use temp files
plugalyzer process --plugin=Compressor.vst3 --input=raw.wav --output=temp1.wav
plugalyzer process --plugin=EQ.vst3 --input=temp1.wav --output=temp2.wav
plugalyzer process --plugin=Reverb.vst3 --input=temp2.wav --output=final.wav
rm temp1.wav temp2.wav

# Or use Pedalboard for native chaining
python3 -c "
from pedalboard import Pedalboard, load_plugin
from pedalboard.io import AudioFile

board = Pedalboard([
    load_plugin('Compressor.vst3'),
    load_plugin('EQ.vst3'),
    load_plugin('Reverb.vst3'),
])
with AudioFile('raw.wav') as f:
    audio = f.read(f.frames)
processed = board(audio, 44100)
with AudioFile('final.wav', 'w', 44100, audio.shape[0]) as f:
    f.write(processed)
"
```

### Workflow 4: Live Plugin Hosting with JACK + Carla

```bash
# Start JACK
jackd -d coreaudio -r 48000 -p 256 &

# Load a CLAP plugin as a standalone JACK client
carla-single native clap /path/to/plugin.clap &

# Load a VST3 effect
carla-single native vst3 /path/to/effect.vst3 &

# Or load an AU instrument
carla-single native au /path/to/instrument.component &

# Connect them with JACK
jack_connect system:capture_1 effect:input_1
jack_connect effect:output_1 system:playback_1

# Send MIDI to the instrument
sendmidi dev "instrument" on 60 127
```

### Workflow 5: Record Plugin Output

```bash
# 1. Set up BlackHole as audio loopback
brew install blackhole-2ch

# 2. Route plugin output to BlackHole
SwitchAudioSource -s "BlackHole 2ch"

# 3. Record from BlackHole
rec -d "BlackHole 2ch" captured.wav

# Or with ffmpeg
ffmpeg -f avfoundation -i ":BlackHole 2ch" -acodec pcm_s24le captured.wav
```

### Workflow 6: Full CLI Effects Chain (No Plugins Needed)

```bash
# Pure SoX effects chain
sox input.wav output.wav \
    highpass 80 \
    compand 0.3,1 6:-70,-60,-20 -5 -90 0.2 \
    equalizer 3000 2 3 \
    overdrive 10 \
    reverb 60 50 80 100 \
    norm -1

# Pure FFmpeg effects chain
ffmpeg -i input.wav -af \
    "highpass=f=80,acompressor=threshold=-20dB:ratio=4,equalizer=f=3000:t=q:w=2:g=3,aecho=0.8:0.9:500:0.3,loudnorm=I=-14" \
    output.wav
```

---

## Key Takeaways

1. **For loading YOUR existing AU/VST3 plugins from CLI:** Use **Pedalboard** (Python, easiest) or **Plugalyzer** (C++, pure CLI). Both support VST3 and AU.

2. **For CLAP plugin hosting from CLI:** **Carla** with `--no-gui` or `carla-single` is currently the only option. No other CLI tool supports CLAP hosting.

3. **For VST2 plugins:** **DawDreamer** or **Carla** still support VST2. Most newer tools have dropped VST2.

4. **For MIDI-to-audio rendering through plugins:** **Pedalboard**, **DawDreamer**, or **Plugalyzer** can all render MIDI through instrument plugins offline.

5. **For built-in effects (no plugins needed):** **SoX** and **FFmpeg** together cover virtually every common audio effect.

6. **For real-time plugin hosting and routing:** **JACK** + **Carla** (`carla-single`) is the most capable setup on macOS.

7. **For batch processing:** Write a Python script using **Pedalboard** -- it is by far the most ergonomic option for processing many files through plugin chains.
