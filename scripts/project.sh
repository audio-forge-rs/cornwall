#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$PROJECT_ROOT/state"
PROJECTS_DIR="$PROJECT_ROOT/projects"
PROJECT_FILE="$STATE_DIR/project.json"

usage() {
    cat <<'HELP'
Usage: project.sh <command> [options]

Manage Cornwall projects.

Commands:
  create    Create a new project
  info      Show current project info
  set       Change a project setting
  open      Open (switch to) an existing project

project.sh create [options]
  --name <name>         Project name (required)
  --bpm <number>        Tempo in BPM (default: 120)
  --sample-rate <rate>  Sample rate in Hz (default: 44100)
  --time-sig <n/d>      Time signature (default: 4/4)

project.sh info
  Print current project settings as formatted text.
  --json    Output as raw JSON

project.sh set <key> <value>
  Change a project setting. Keys: name, bpm, sample-rate, time-sig

project.sh open <name>
  Switch to an existing project by name.

Examples:
  project.sh create --name "folk-session" --bpm 110
  project.sh info
  project.sh set bpm 140
  project.sh set time-sig 3/4
HELP
}

ensure_state_dir() {
    mkdir -p "$STATE_DIR"
    mkdir -p "$PROJECTS_DIR"
}

create_project() {
    local name="" bpm=120 sample_rate=44100 time_sig="4/4"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name) name="$2"; shift 2 ;;
            --bpm) bpm="$2"; shift 2 ;;
            --sample-rate) sample_rate="$2"; shift 2 ;;
            --time-sig) time_sig="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done

    if [[ -z "$name" ]]; then
        echo "Error: --name is required" >&2
        exit 1
    fi

    ensure_state_dir

    local project_dir="$PROJECTS_DIR/$name"
    mkdir -p "$project_dir"

    jq -n \
        --arg name "$name" \
        --argjson bpm "$bpm" \
        --argjson sample_rate "$sample_rate" \
        --arg time_sig "$time_sig" \
        --arg created "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            name: $name,
            bpm: $bpm,
            sample_rate: $sample_rate,
            time_sig: $time_sig,
            created: $created,
            project_dir: $name
        }' > "$PROJECT_FILE"

    # Initialize empty tracks and effects state
    echo '[]' > "$STATE_DIR/tracks.json"
    jq -n '{}' > "$STATE_DIR/effects.json"
    jq -n '{master_volume: 1.0, output_format: "wav", output_file: "mix.wav"}' > "$STATE_DIR/mix.json"

    echo "Created project '$name' at ${bpm} BPM, ${sample_rate}Hz, ${time_sig}"
    echo "Project directory: $project_dir"
}

show_info() {
    if [[ ! -f "$PROJECT_FILE" ]]; then
        echo "No project loaded. Use 'project.sh create' first." >&2
        exit 1
    fi

    if [[ "${1:-}" == "--json" ]]; then
        cat "$PROJECT_FILE"
    else
        local name bpm sr ts created
        name=$(jq -r '.name' "$PROJECT_FILE")
        bpm=$(jq -r '.bpm' "$PROJECT_FILE")
        sr=$(jq -r '.sample_rate' "$PROJECT_FILE")
        ts=$(jq -r '.time_sig' "$PROJECT_FILE")
        created=$(jq -r '.created' "$PROJECT_FILE")

        echo "Project: $name"
        echo "BPM:     $bpm"
        echo "Rate:    ${sr}Hz"
        echo "Time:    $ts"
        echo "Created: $created"

        if [[ -f "$STATE_DIR/tracks.json" ]]; then
            local track_count
            track_count=$(jq 'length' "$STATE_DIR/tracks.json")
            echo "Tracks:  $track_count"
        fi
    fi
}

set_value() {
    if [[ ! -f "$PROJECT_FILE" ]]; then
        echo "No project loaded. Use 'project.sh create' first." >&2
        exit 1
    fi

    local key="$1" value="$2"

    case "$key" in
        name)
            jq --arg v "$value" '.name = $v' "$PROJECT_FILE" > "$PROJECT_FILE.tmp" && mv "$PROJECT_FILE.tmp" "$PROJECT_FILE"
            ;;
        bpm)
            jq --argjson v "$value" '.bpm = $v' "$PROJECT_FILE" > "$PROJECT_FILE.tmp" && mv "$PROJECT_FILE.tmp" "$PROJECT_FILE"
            ;;
        sample-rate)
            jq --argjson v "$value" '.sample_rate = $v' "$PROJECT_FILE" > "$PROJECT_FILE.tmp" && mv "$PROJECT_FILE.tmp" "$PROJECT_FILE"
            ;;
        time-sig)
            jq --arg v "$value" '.time_sig = $v' "$PROJECT_FILE" > "$PROJECT_FILE.tmp" && mv "$PROJECT_FILE.tmp" "$PROJECT_FILE"
            ;;
        *)
            echo "Unknown key: $key. Valid keys: name, bpm, sample-rate, time-sig" >&2
            exit 1
            ;;
    esac

    echo "Set $key = $value"
}

open_project() {
    local name="$1"
    # For now, open just verifies the project exists and loads its state
    if [[ ! -d "$PROJECTS_DIR/$name" ]]; then
        echo "Project '$name' not found in $PROJECTS_DIR/" >&2
        echo "Available projects:"
        ls "$PROJECTS_DIR/" 2>/dev/null || echo "  (none)"
        exit 1
    fi

    echo "Opened project '$name'"
    show_info
}

# Main dispatch
case "${1:-}" in
    create) shift; create_project "$@" ;;
    info)   shift; show_info "$@" ;;
    set)
        shift
        if [[ $# -lt 2 ]]; then
            echo "Usage: project.sh set <key> <value>" >&2
            exit 1
        fi
        set_value "$1" "$2"
        ;;
    open)
        shift
        if [[ $# -lt 1 ]]; then
            echo "Usage: project.sh open <name>" >&2
            exit 1
        fi
        open_project "$1"
        ;;
    --help|-h|"") usage ;;
    *)
        echo "Unknown command: $1" >&2
        usage >&2
        exit 1
        ;;
esac
