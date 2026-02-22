use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    ExecutableCommand,
};
use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::CrosstermBackend,
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
    Frame, Terminal,
};
use rodio::{Decoder, OutputStream, OutputStreamHandle, Sink};
use serde::{Deserialize, Serialize};
use std::{
    env,
    fs,
    io::{self, BufReader, Cursor},
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

// --- State structures (mirror Cornwall's JSON) ---

#[derive(Deserialize, Default, Clone)]
struct ProjectState {
    name: String,
    bpm: f64,
    #[allow(dead_code)]
    sample_rate: u32,
    time_sig: String,
}

#[derive(Deserialize, Default, Clone)]
struct TrackState {
    id: u32,
    name: String,
    #[allow(dead_code)]
    #[serde(rename = "type")]
    track_type: String,
    source: Option<String>,
    volume: f64,
    pan: f64,
    mute: bool,
    solo: bool,
}

#[derive(Serialize)]
struct PlayerStatus {
    playing: bool,
    position_secs: f64,
    bar: u32,
    beat: u32,
    bpm: f64,
    time_sig: String,
    level_l: f64,
    level_r: f64,
    file: String,
}

// --- Audio level metering via pre-scanned peaks ---

struct LevelMeter {
    levels_l: Vec<f64>,
    levels_r: Vec<f64>,
    chunk_duration: f64,
    current_l: f64,
    current_r: f64,
}

impl LevelMeter {
    fn from_wav(path: &Path, chunk_ms: u32) -> Self {
        let reader = hound::WavReader::open(path).expect("Failed to read WAV for metering");
        let spec = reader.spec();
        let channels = spec.channels as usize;
        let sample_rate = spec.sample_rate as usize;
        let chunk_samples = (sample_rate * chunk_ms as usize) / 1000;

        let samples: Vec<f64> = if spec.bits_per_sample <= 16 {
            reader
                .into_samples::<i16>()
                .filter_map(|s| s.ok())
                .map(|s| s as f64 / 32768.0)
                .collect()
        } else {
            reader
                .into_samples::<i32>()
                .filter_map(|s| s.ok())
                .map(|s| s as f64 / 2147483648.0)
                .collect()
        };

        let frames = samples.len() / channels.max(1);
        let mut levels_l = Vec::new();
        let mut levels_r = Vec::new();

        let mut i = 0;
        while i < frames {
            let end = (i + chunk_samples).min(frames);
            let mut sum_l = 0.0_f64;
            let mut sum_r = 0.0_f64;
            let count = (end - i) as f64;

            for f in i..end {
                let l = samples[f * channels];
                let r = if channels > 1 {
                    samples[f * channels + 1]
                } else {
                    l
                };
                sum_l += l * l;
                sum_r += r * r;
            }

            levels_l.push((sum_l / count).sqrt());
            levels_r.push((sum_r / count).sqrt());
            i = end;
        }

        LevelMeter {
            levels_l,
            levels_r,
            chunk_duration: chunk_ms as f64 / 1000.0,
            current_l: 0.0,
            current_r: 0.0,
        }
    }

    fn update(&mut self, position_secs: f64) {
        let idx = (position_secs / self.chunk_duration) as usize;
        self.current_l = self.levels_l.get(idx).copied().unwrap_or(0.0);
        self.current_r = self.levels_r.get(idx).copied().unwrap_or(0.0);
    }
}

// --- App state ---

struct App {
    project: ProjectState,
    tracks: Vec<TrackState>,
    audio_file: PathBuf,
    audio_data: Vec<u8>,
    audio_duration: f64,
    playing: bool,
    position: f64,
    play_started: Option<Instant>,
    play_offset: f64,
    meter: LevelMeter,
    beats_per_bar: u32,
    state_dir: PathBuf,
    _stream: OutputStream,
    stream_handle: OutputStreamHandle,
    sink: Sink,
    looping: bool,
}

impl App {
    fn new(state_dir: PathBuf, audio_file: PathBuf) -> Self {
        let project: ProjectState = fs::read_to_string(state_dir.join("project.json"))
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();

        let tracks: Vec<TrackState> = fs::read_to_string(state_dir.join("tracks.json"))
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();

        let beats_per_bar: u32 = project
            .time_sig
            .split('/')
            .next()
            .and_then(|s| s.parse().ok())
            .unwrap_or(4);

        let reader = hound::WavReader::open(&audio_file).expect("Cannot open WAV file");
        let spec = reader.spec();
        let total_samples = reader.len() as f64;
        let audio_duration = total_samples / (spec.sample_rate as f64 * spec.channels as f64);

        let meter = LevelMeter::from_wav(&audio_file, 50);
        let audio_data = fs::read(&audio_file).expect("Cannot read audio file");

        let (_stream, stream_handle) =
            OutputStream::try_default().expect("Cannot open audio output");
        let sink = Sink::try_new(&stream_handle).expect("Cannot create audio sink");
        sink.pause();

        App {
            project,
            tracks,
            audio_file,
            audio_data,
            audio_duration,
            playing: false,
            position: 0.0,
            play_started: None,
            play_offset: 0.0,
            meter,
            beats_per_bar,
            state_dir,
            _stream,
            stream_handle,
            sink,
            looping: true,
        }
    }

    fn toggle_play(&mut self) {
        if self.playing {
            self.stop();
        } else {
            self.play();
        }
    }

    fn play(&mut self) {
        self.playing = true;
        self.play_offset = 0.0;
        self.position = 0.0;
        self.play_started = Some(Instant::now());

        self.sink.stop();
        self.sink = Sink::try_new(&self.stream_handle).expect("Cannot create audio sink");

        let cursor = Cursor::new(self.audio_data.clone());
        let source = Decoder::new(BufReader::new(cursor)).expect("Cannot decode audio");
        self.sink.append(source);
        self.sink.play();
    }

    fn stop(&mut self) {
        self.playing = false;
        self.position = 0.0;
        self.play_started = None;
        self.sink.stop();
        self.sink = Sink::try_new(&self.stream_handle).expect("Cannot create audio sink");
        self.meter.current_l = 0.0;
        self.meter.current_r = 0.0;
    }

    fn tick(&mut self) {
        if self.playing {
            if let Some(started) = self.play_started {
                self.position = self.play_offset + started.elapsed().as_secs_f64();

                if self.position >= self.audio_duration {
                    if self.looping {
                        self.play();
                    } else {
                        self.stop();
                    }
                    return;
                }

                self.meter.update(self.position);
            }

            self.write_status();
        }
    }

    fn current_bar(&self) -> u32 {
        if self.project.bpm <= 0.0 {
            return 1;
        }
        let beat = self.position * self.project.bpm / 60.0;
        (beat / self.beats_per_bar as f64) as u32 + 1
    }

    fn current_beat(&self) -> u32 {
        if self.project.bpm <= 0.0 {
            return 1;
        }
        let beat = self.position * self.project.bpm / 60.0;
        (beat % self.beats_per_bar as f64) as u32 + 1
    }

    fn write_status(&self) {
        let status = PlayerStatus {
            playing: self.playing,
            position_secs: self.position,
            bar: self.current_bar(),
            beat: self.current_beat(),
            bpm: self.project.bpm,
            time_sig: self.project.time_sig.clone(),
            level_l: self.meter.current_l,
            level_r: self.meter.current_r,
            file: self.audio_file.to_string_lossy().to_string(),
        };
        let json = serde_json::to_string(&status).unwrap_or_default();
        let _ = fs::write(self.state_dir.join(".player.json"), json);
    }

    fn clear_status(&self) {
        let _ = fs::remove_file(self.state_dir.join(".player.json"));
    }
}

// --- UI rendering ---

fn render_meter_bar(level: f64, width: u16) -> Vec<Span<'static>> {
    let filled = ((level * 3.0).min(1.0) * width as f64) as u16;
    let mut spans = Vec::new();

    for i in 0..width {
        if i < filled {
            let ratio = i as f64 / width as f64;
            let color = if ratio < 0.6 {
                Color::Green
            } else if ratio < 0.85 {
                Color::Yellow
            } else {
                Color::Red
            };
            spans.push(Span::styled("█", Style::default().fg(color)));
        } else {
            spans.push(Span::styled("░", Style::default().fg(Color::DarkGray)));
        }
    }
    spans
}

fn ui(f: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // header
            Constraint::Length(5),  // transport
            Constraint::Length(5),  // meters
            Constraint::Min(3),    // track list
            Constraint::Length(3), // footer
        ])
        .split(f.area());

    // --- Header ---
    let title = format!(
        "  C O R N W A L L   ─   {}",
        app.project.name.to_uppercase()
    );
    let header = Paragraph::new(Line::from(vec![Span::styled(
        title,
        Style::default()
            .fg(Color::White)
            .add_modifier(Modifier::BOLD),
    )]))
    .block(
        Block::default()
            .borders(Borders::BOTTOM)
            .border_style(Style::default().fg(Color::DarkGray)),
    );
    f.render_widget(header, chunks[0]);

    // --- Transport ---
    let state_indicator = if app.playing {
        Span::styled(
            "  ▶ PLAYING ",
            Style::default()
                .fg(Color::Black)
                .bg(Color::Green)
                .add_modifier(Modifier::BOLD),
        )
    } else {
        Span::styled(
            "  ■ STOPPED ",
            Style::default()
                .fg(Color::White)
                .bg(Color::DarkGray)
                .add_modifier(Modifier::BOLD),
        )
    };

    let bar_display = format!(
        "  BAR {:>3} . {}   ",
        app.current_bar(),
        app.current_beat()
    );

    let time_display = format!(
        "{:02}:{:02}.{:01}",
        (app.position as u32) / 60,
        (app.position as u32) % 60,
        ((app.position * 10.0) as u32) % 10
    );

    let tempo_display = format!("  {} BPM  {}  ", app.project.bpm, app.project.time_sig);

    let progress = if app.audio_duration > 0.0 {
        (app.position / app.audio_duration).min(1.0)
    } else {
        0.0
    };

    let transport_line1 = Line::from(vec![
        state_indicator,
        Span::raw("  "),
        Span::styled(
            bar_display,
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(time_display, Style::default().fg(Color::White)),
        Span::styled(tempo_display, Style::default().fg(Color::DarkGray)),
    ]);

    let prog_width = chunks[1].width.saturating_sub(4) as usize;
    let filled = (progress * prog_width as f64) as usize;
    let mut prog_spans = vec![Span::raw("  ")];
    for i in 0..prog_width {
        if i < filled {
            prog_spans.push(Span::styled("━", Style::default().fg(Color::Cyan)));
        } else if i == filled && app.playing {
            prog_spans.push(Span::styled("╸", Style::default().fg(Color::White)));
        } else {
            prog_spans.push(Span::styled("─", Style::default().fg(Color::DarkGray)));
        }
    }

    let transport = Paragraph::new(vec![
        Line::from(""),
        transport_line1,
        Line::from(""),
        Line::from(prog_spans),
    ])
    .block(
        Block::default()
            .borders(Borders::BOTTOM)
            .border_style(Style::default().fg(Color::DarkGray)),
    );
    f.render_widget(transport, chunks[1]);

    // --- Level Meters ---
    let meter_width = chunks[2].width.saturating_sub(8);
    let l_spans = render_meter_bar(app.meter.current_l, meter_width);
    let r_spans = render_meter_bar(app.meter.current_r, meter_width);

    let mut l_line = vec![Span::styled("  L ", Style::default().fg(Color::DarkGray))];
    l_line.extend(l_spans);

    let mut r_line = vec![Span::styled("  R ", Style::default().fg(Color::DarkGray))];
    r_line.extend(r_spans);

    let meters = Paragraph::new(vec![
        Line::from(""),
        Line::from(l_line),
        Line::from(""),
        Line::from(r_line),
    ])
    .block(
        Block::default()
            .borders(Borders::BOTTOM)
            .border_style(Style::default().fg(Color::DarkGray)),
    );
    f.render_widget(meters, chunks[2]);

    // --- Track List ---
    let mut track_lines = vec![Line::from("")];
    for t in &app.tracks {
        let mute_solo = match (t.mute, t.solo) {
            (_, true) => {
                Span::styled(" S ", Style::default().fg(Color::Black).bg(Color::Yellow))
            }
            (true, _) => Span::styled(" M ", Style::default().fg(Color::Black).bg(Color::Red)),
            _ => Span::styled("   ", Style::default()),
        };
        let source_name = t
            .source
            .as_ref()
            .map(|s| {
                Path::new(s)
                    .file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .to_string()
            })
            .unwrap_or_else(|| "(empty)".to_string());

        track_lines.push(Line::from(vec![
            Span::styled(format!("  {:>2} ", t.id), Style::default().fg(Color::DarkGray)),
            mute_solo,
            Span::raw(" "),
            Span::styled(format!("{:<16}", t.name), Style::default().fg(Color::White)),
            Span::styled(
                format!("  vol {:<4}", format!("{:.1}", t.volume)),
                Style::default().fg(Color::DarkGray),
            ),
            Span::styled(
                format!("  pan {:<5}", format!("{:.1}", t.pan)),
                Style::default().fg(Color::DarkGray),
            ),
            Span::styled(
                format!("  {}", source_name),
                Style::default().fg(Color::DarkGray),
            ),
        ]));
    }

    let tracks_widget = Paragraph::new(track_lines).block(
        Block::default()
            .borders(Borders::BOTTOM)
            .border_style(Style::default().fg(Color::DarkGray)),
    );
    f.render_widget(tracks_widget, chunks[3]);

    // --- Footer ---
    let footer = Paragraph::new(Line::from(vec![
        Span::styled(
            "  SPACE",
            Style::default()
                .fg(Color::White)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(" play/stop", Style::default().fg(Color::DarkGray)),
        Span::styled(
            "    q",
            Style::default()
                .fg(Color::White)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(" quit", Style::default().fg(Color::DarkGray)),
        Span::styled(
            "    L",
            Style::default()
                .fg(Color::White)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(
            if app.looping { " loop ◆" } else { " loop ◇" },
            Style::default().fg(if app.looping {
                Color::Cyan
            } else {
                Color::DarkGray
            }),
        ),
    ]));
    f.render_widget(footer, chunks[4]);
}

// --- Status query mode ---

fn print_status(state_dir: &Path) {
    let status_path = state_dir.join(".player.json");
    if status_path.exists() {
        let content = fs::read_to_string(&status_path).unwrap_or_default();
        println!("{}", content);
    } else {
        let status = PlayerStatus {
            playing: false,
            position_secs: 0.0,
            bar: 0,
            beat: 0,
            bpm: 0.0,
            time_sig: String::new(),
            level_l: 0.0,
            level_r: 0.0,
            file: String::new(),
        };
        println!("{}", serde_json::to_string(&status).unwrap());
    }
}

// --- Main ---

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();

    let state_dir = if args.len() > 1 && args[1] == "--status" {
        let dir = if args.len() > 2 {
            PathBuf::from(&args[2])
        } else {
            find_state_dir()
        };
        print_status(&dir);
        return Ok(());
    } else {
        find_state_dir()
    };

    let audio_file = if args.len() > 1 && args[1] != "--status" {
        PathBuf::from(&args[1])
    } else {
        let project: ProjectState = fs::read_to_string(state_dir.join("project.json"))
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();

        let project_dir = state_dir
            .parent()
            .unwrap()
            .join("projects")
            .join(&project.name);
        let mix = project_dir.join("mix.wav");
        if mix.exists() {
            mix
        } else {
            let tracks: Vec<TrackState> = fs::read_to_string(state_dir.join("tracks.json"))
                .ok()
                .and_then(|s| serde_json::from_str(&s).ok())
                .unwrap_or_default();

            tracks
                .iter()
                .filter_map(|t| t.source.as_ref())
                .map(PathBuf::from)
                .find(|p| p.exists())
                .expect(
                    "No audio file found. Pass a WAV file as argument or create a mix first.",
                )
        }
    };

    if !audio_file.exists() {
        eprintln!("Audio file not found: {}", audio_file.display());
        std::process::exit(1);
    }

    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(io::stdout());
    let mut terminal = Terminal::new(backend)?;

    let mut app = App::new(state_dir, audio_file);

    let tick_rate = Duration::from_millis(33);

    loop {
        terminal.draw(|f| ui(f, &app))?;

        if event::poll(tick_rate)? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char(' ') => app.toggle_play(),
                        KeyCode::Char('q') | KeyCode::Esc => break,
                        KeyCode::Char('l') | KeyCode::Char('L') => {
                            app.looping = !app.looping;
                        }
                        _ => {}
                    }
                }
            }
        }

        app.tick();
    }

    app.stop();
    app.clear_status();
    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;

    Ok(())
}

fn find_state_dir() -> PathBuf {
    let mut dir = env::current_dir().expect("Cannot get CWD");
    loop {
        let state = dir.join("state");
        if state.join("project.json").exists() {
            return state;
        }
        if !dir.pop() {
            break;
        }
    }
    PathBuf::from("state")
}
