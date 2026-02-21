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

## Vision

In this framework, Claude acts as the conversational user interface for a completely headless DAW, translating your natural language prompts into executable scripts that manipulate JSON state files representing your tracks, effects, and mix. At the foundation of this system, audio routing and playback are handled seamlessly in the background so you can constantly hear the loop you are working on. Simple playback is executed using SoX's `play` command or the native macOS `afplay` utility, while more complex, zero-latency audio routing between different background applications is managed by virtual loopback drivers like BlackHole and the JACK2 audio server. 

When you ask Claude to create or modify musical clips, the system relies on specialized command-line tools to handle MIDI and text-based notation. If you prompt the DAW to write a folk melody using ABC notation, Claude can use `abc2midi` to instantly compile that compact text into a functional MIDI file. For algorithmic "note FX" like generating Euclidean rhythms, applying complex arpeggios, or utilizing Markov chains to generate new melodies, Claude can invoke the Python library `isobar` to programmatically manipulate the MIDI data. To ensure this generated MIDI data flows correctly between your virtual tracks and instruments, utilities like `SendMIDI` and `ReceiveMIDI` function as the invisible MIDI cables of the DAW.

To convert those MIDI clips into actual audio, Claude orchestrates a variety of command-line synthesizers and samplers depending on the sound you request. For traditional instrument sounds, `FluidSynth` serves as a highly efficient engine for rendering MIDI through SoundFonts, while `LinuxSampler` can operate as a background server to handle large, streaming sample libraries. If you ask for deep, experimental sound design, Claude can generate text-based instrument definitions and render them using heavyweight synthesis engines like `Csound` or `SuperCollider`. When you specifically request your own third-party virtual instruments, Python libraries like `Pedalboard` or `DawDreamer` are invoked to headlessly load your VST3 and AU plugins and render the MIDI notes into audio tracks.

For the final stages of building FX chains, mixing, and routing, the DAW heavily relies on headless plugin hosts and foundational Unix audio utilities. `Pedalboard` acts as the primary workhorse here, efficiently loading external VST3 and AU effects plugins and processing your audio tracks through complex effect chains entirely via Python scripts. If you need to utilize CLAP plugins or require a modular patchbay architecture, Claude can spin up `Carla` in its headless mode. For built-in effects, EQ, and the final mixdown, `SoX` and `FFmpeg` serve as the ultimate mixing engine, handling everything from basic reverb to EBU R128 loudness normalization. Furthermore, if you ask Claude to manipulate a sampled loop, it can deploy specialized tools like `Rubber Band` for high-quality time-stretching and pitch-shifting, or `Demucs` to isolate and extract specific stems like vocals or drums before looping the updated mix back into your headphones.

## Tool Tour

One highly intriguing open-source command-line tool is **Orca**, which functions as an esoteric 2D programming language built specifically for procedural sequencing. In this unique environment, **every single letter of the alphabet acts as an operator**, and your code takes the form of a visually mesmerizing grid of characters that dynamically animates in the terminal as the sequencer runs. While Orca does not generate audio on its own, it is incredibly useful for algorithmic composition because it sends MIDI, OSC, or UDP messages to control other software or hardware synthesizers. Created by the collective Hundred Rabbits, the tool offers a deeply weird and compelling approach to making music that radiates what the documentation describes as maximum Aphex Twin energy. 

On the purely useful side of the spectrum is **SoX** (Sound eXchange), universally regarded as the **Swiss Army knife of command-line audio processing**. This foundational Unix workhorse allows users to seamlessly convert, record, play, and generate audio entirely from the terminal. It features a highly capable built-in synthesizer that can generate sine, square, and sawtooth waves alongside various noise profiles, and it can chain multiple audio effects like reverb, echo, chorus, and overdrive. Because **SoX scripts beautifully**, users can construct entire musical pieces or automate extensive audio batch-processing workflows directly from bash scripts, making it arguably the single most essential and reliable CLI audio tool available.

**Demucs** is a state-of-the-art open-source tool developed by Meta's Facebook Research team that utilizes deep learning models for music source separation. From the command line, it can process a mixed audio track and automatically separate it into four distinct stems, isolating the vocals, drums, bass, and other musical elements into individual, high-quality WAV files. This remarkable capability makes it a genuinely revolutionary utility for music producers and remixers who need to extract a specific drum pattern or isolate a pristine vocal track from a fully mastered recording. 

Another fascinating option is **Cursynth**, a polyphonic and MIDI-enabled subtractive synthesizer that operates entirely within a terminal window. Instead of relying on a modern graphical user interface, this GNU project utilizes the ncurses library to provide a full ASCII-based visual environment where users can play music and manipulate oscillators, filters, and volume envelopes using their computer keyboard. Because it automatically connects to all available MIDI devices on your system, it serves as a highly functional, real-time musical instrument while maintaining a deeply retro, pure text-based aesthetic.

If you are looking for something deeply experimental, **Bytebeat** offers a fascinating approach to audio generation known as one-liner music. Instead of relying on traditional sequencing or synthesis, Bytebeat uses a single mathematical expression, typically written in C, to define a waveform as a function of time. By processing this mathematical formula thousands of times per second, users can generate surprisingly complex rhythmic and melodic patterns from just a few characters of code. The resulting raw audio data can then be piped directly to your speakers, producing chaotic, alien-sounding compositions that represent a brilliant intersection of pure mathematics and music.

On the highly practical side is **Pedalboard**, an open-source tool developed by Spotify's Audio Intelligence Lab. It serves as a remarkably useful Python library for loading external VST3 and AU plugins, processing audio effects, and rendering MIDI instruments entirely from the command line without a graphical interface. Because it releases the Python Global Interpreter Lock for multi-threaded processing and includes dozens of its own built-in effects, it operates at exceptional speeds. This makes it arguably the most ergonomic and efficient option available for producers who need to script complex batch-processing workflows or automate extensive plugin effect chains across large numbers of audio files.

If you are drawn to the performance art of live coding, **TidalCycles** serves as an incredibly intriguing option. Operating as a domain-specific language embedded within Haskell, it is widely considered the gold standard for live coding musical patterns. Users interact with an extraordinarily expressive mini-notation system to manipulate complex rhythmic and melodic sequences on the fly, utilizing SuperCollider's SuperDirt as its underlying audio engine. Because it allows you to dynamically alter deeply intricate musical structures in real time, it offers a powerful environment for algorithmic composition and live electronic performance that frequently touches upon glitchy, Aphex Twin-esque aesthetic territories.

On the highly analytical and practical side, **Aubio** is a remarkably useful command-line toolset dedicated to audio feature extraction and labeling. Rather than acting as a simple wrapper around a background library, it provides first-class, purpose-built terminal utilities for tasks like onset detection, beat tracking, pitch detection, tempo estimation, and note transcription. Because each of its subcommands functions as a complete analysis pipeline that outputs raw plain text, it is perfectly designed to have its data piped directly into other shell scripts or programs. This makes it an invaluable building block for developers and musicians who need to programmatically analyze the contents of an audio file without ever opening a graphical interface.

For those interested in deeply experimental generative music, **Celltone** is one of the weirdest and most fascinating command-line tools available. It functions as a unique programming language that utilizes cellular automata for musical composition. Users define specific rules, allowing the mathematical automata to evolve over time, and these changing states are directly mapped to musical outputs. This creates emergent, self-evolving musical structures that produce unpredictable and genuinely alien-sounding results, making it an incredible resource for exploring deep generative audio territories.

On the highly practical side of command-line utilities, **Beets** stands out as the ultimate media organizer for music enthusiasts. Operating as a comprehensive music library manager, it offers powerful features like auto-tagging and metadata correction entirely from the terminal. What makes it particularly useful is its vast, extensible plugin system, which can automatically handle everything from fetching album art and lyrics to applying loudness normalization and performing acoustic fingerprinting. By leveraging robust databases like MusicBrainz and Discogs as metadata sources, it serves as arguably the most capable and efficient tool available for organizing large digital music collections.