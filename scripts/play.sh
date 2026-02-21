#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$PROJECT_ROOT/state"
PROJECT_FILE="$STATE_DIR/project.json"
TRACKS_FILE="$STATE_DIR/tracks.json"
EFFECTS_FILE="$STATE_DIR/effects.json"
MIX_FILE="$STATE_DIR/mix.json"
PID_FILE="$STATE_DIR/.playback.pid"

usage() {
    cat <<'HELP'
Usage: play.sh <command> [options]

Playback and rendering for Cornwall projects.

Commands:
  track <id>            Play a single track through headphones
  mix                   Render and play the full mix
  render                Render the mix to a file (no playback)
  loop <id|mix>         Loop a track or the mix continuously in background
  stop                  Stop background playback
  status                Check if something is playing
  file <path>           Play any audio file

play.sh track <id> [options]
  --start <seconds>     Start playback from this position
  --duration <seconds>  Play for this many seconds

play.sh mix [options]
  Render all unmuted tracks, apply effects, and play.
  --start <seconds>     Start from position
  --no-play             Render only, don't play

play.sh render [options]
  --output <path>       Output file (default: projects/<name>/mix.wav)
  --format <fmt>        Output format: wav, flac, mp3 (default: wav)

play.sh loop <id|mix>
  Start looping playback in the background. Use 'play.sh stop' to end it.
  Rendering changes and running 'play.sh loop' again hot-swaps the audio.

play.sh stop
  Stop any background playback.

play.sh status
  Show what's currently playing.

play.sh file <path>
  Play any audio file directly.

Examples:
  play.sh track 1
  play.sh mix
  play.sh loop 1
  play.sh loop mix
  play.sh stop
  play.sh file ~/samples/banjo.wav
HELP
}

require_project() {
    if [[ ! -f "$PROJECT_FILE" ]]; then
        echo "Error: No project loaded. Run 'project.sh create' first." >&2
        exit 1
    fi
}

get_project_dir() {
    local proj_name
    proj_name=$(jq -r '.project_dir // .name' "$PROJECT_FILE")
    echo "$PROJECT_ROOT/projects/$proj_name"
}

get_track_source() {
    local id="$1"
    jq -r --argjson id "$id" '.[] | select(.id == $id) | .source // empty' "$TRACKS_FILE"
}

get_track_name() {
    local id="$1"
    jq -r --argjson id "$id" '.[] | select(.id == $id) | .name // empty' "$TRACKS_FILE"
}

stop_playback() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            # Also kill any child processes (sox/play spawns children)
            pkill -P "$pid" 2>/dev/null || true
            echo "Stopped playback (pid $pid)"
        else
            echo "No active playback"
        fi
        rm -f "$PID_FILE"
    else
        # Try to kill any play/afplay processes we might have spawned
        echo "No tracked playback. Checking for stray audio processes..."
        local killed=false
        if pgrep -f "play.*cornwall" >/dev/null 2>&1; then
            pkill -f "play.*cornwall" 2>/dev/null || true
            killed=true
        fi
        if [[ "$killed" == "true" ]]; then
            echo "Stopped stray playback"
        else
            echo "Nothing playing"
        fi
    fi
}

check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Playing (pid $pid)"
            return 0
        else
            rm -f "$PID_FILE"
            echo "Not playing"
            return 1
        fi
    else
        echo "Not playing"
        return 1
    fi
}

play_file() {
    local file="$1"
    shift
    local start="" duration=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --start) start="$2"; shift 2 ;;
            --duration) duration="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        exit 1
    fi

    local cmd="play"
    local args=("$file")

    if [[ -n "$start" ]]; then
        args+=(trim "$start")
        if [[ -n "$duration" ]]; then
            args+=("$duration")
        fi
    fi

    echo "Playing: $file"
    "$cmd" "${args[@]}"
}

play_track() {
    local id="$1"
    shift

    require_project

    local source
    source=$(get_track_source "$id")

    if [[ -z "$source" ]]; then
        local name
        name=$(get_track_name "$id")
        if [[ -z "$name" ]]; then
            echo "Error: Track $id not found" >&2
        else
            echo "Error: Track $id '$name' has no audio source. Use 'track.sh import $id <file>' first." >&2
        fi
        exit 1
    fi

    local name
    name=$(get_track_name "$id")

    # Get volume and pan
    local vol pan
    vol=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .volume' "$TRACKS_FILE")
    pan=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .pan' "$TRACKS_FILE")

    echo "Playing track $id: '$name' (vol=$vol pan=$pan)"

    local args=("$source")

    # Apply volume via sox vol effect
    if [[ "$vol" != "1" && "$vol" != "1.0" ]]; then
        args+=(vol "$vol")
    fi

    play "${args[@]}"
}

render_mix() {
    require_project

    local project_dir
    project_dir=$(get_project_dir)
    mkdir -p "$project_dir"

    local output="${project_dir}/mix.wav"
    local no_play=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --output) output="$2"; shift 2 ;;
            --no-play) no_play=true; shift ;;
            --format) shift 2 ;; # TODO: implement format conversion
            *) shift ;;
        esac
    done

    # Gather active tracks (not muted, and if any solo exists, only solo'd tracks)
    local has_solo
    has_solo=$(jq '[.[] | select(.solo == true)] | length' "$TRACKS_FILE")

    local active_tracks
    if [[ "$has_solo" -gt 0 ]]; then
        active_tracks=$(jq '[.[] | select(.solo == true and .source != null)]' "$TRACKS_FILE")
    else
        active_tracks=$(jq '[.[] | select(.mute == false and .source != null)]' "$TRACKS_FILE")
    fi

    local track_count
    track_count=$(echo "$active_tracks" | jq 'length')

    if [[ "$track_count" -eq 0 ]]; then
        echo "Error: No active tracks with audio sources to mix" >&2
        exit 1
    fi

    if [[ "$track_count" -eq 1 ]]; then
        # Single track - just copy with volume applied
        local source vol
        source=$(echo "$active_tracks" | jq -r '.[0].source')
        vol=$(echo "$active_tracks" | jq -r '.[0].volume')
        local name
        name=$(echo "$active_tracks" | jq -r '.[0].name')

        echo "Rendering track '$name' -> $output"
        sox "$source" "$output" vol "$vol"
    else
        # Multiple tracks - mix with sox
        echo "Mixing $track_count tracks -> $output"

        # Build sox mix command
        # sox -m applies equal mixing. We create intermediate volume-adjusted files.
        local tmpdir
        tmpdir=$(mktemp -d)
        local mix_inputs=()

        echo "$active_tracks" | jq -c '.[]' | while read -r track; do
            local tid source vol name
            tid=$(echo "$track" | jq -r '.id')
            source=$(echo "$track" | jq -r '.source')
            vol=$(echo "$track" | jq -r '.volume')
            name=$(echo "$track" | jq -r '.name')

            local tmp_file="$tmpdir/track_${tid}.wav"
            sox "$source" "$tmp_file" vol "$vol"
            echo "$tmp_file"
        done > "$tmpdir/file_list.txt"

        # Read the file list and mix
        local files=()
        while IFS= read -r f; do
            files+=("$f")
        done < "$tmpdir/file_list.txt"

        if [[ ${#files[@]} -gt 0 ]]; then
            sox -m "${files[@]}" "$output"
        fi

        rm -rf "$tmpdir"
    fi

    echo "Rendered: $output"

    if [[ "$no_play" == "false" ]]; then
        echo "Playing mix..."
        play "$output"
    fi
}

loop_audio() {
    local target="$1"
    require_project

    # Stop any existing playback
    stop_playback 2>/dev/null

    local file=""

    if [[ "$target" == "mix" ]]; then
        # Render the mix first
        local project_dir
        project_dir=$(get_project_dir)
        file="$project_dir/mix.wav"
        render_mix --no-play
    else
        # It's a track ID
        local source
        source=$(get_track_source "$target")
        if [[ -z "$source" ]]; then
            echo "Error: Track $target has no audio source" >&2
            exit 1
        fi
        file="$source"
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: No audio file to loop" >&2
        exit 1
    fi

    # Start looping in background
    play "$file" repeat 999 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo "Looping: $file (pid $pid)"
    echo "Use 'play.sh stop' to stop"
}

# Main dispatch
case "${1:-}" in
    track)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: play.sh track <id>" >&2; exit 1; }
        play_track "$@"
        ;;
    mix)
        shift
        render_mix "$@"
        ;;
    render)
        shift
        render_mix --no-play "$@"
        ;;
    loop)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: play.sh loop <id|mix>" >&2; exit 1; }
        loop_audio "$1"
        ;;
    stop)   stop_playback ;;
    status) check_status ;;
    file)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: play.sh file <path>" >&2; exit 1; }
        play_file "$@"
        ;;
    --help|-h|"") usage ;;
    *)
        echo "Unknown command: $1" >&2
        usage >&2
        exit 1
        ;;
esac
