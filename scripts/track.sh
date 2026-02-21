#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$PROJECT_ROOT/state"
TRACKS_FILE="$STATE_DIR/tracks.json"
EFFECTS_FILE="$STATE_DIR/effects.json"
PROJECT_FILE="$STATE_DIR/project.json"

usage() {
    cat <<'HELP'
Usage: track.sh <command> [options]

Manage tracks in the current Cornwall project.

Commands:
  add       Add a new track
  list      List all tracks
  remove    Remove a track
  solo      Solo a track (unsolo all others)
  unsolo    Unsolo a track
  mute      Mute a track
  unmute    Unmute a track
  volume    Set track volume
  pan       Set track pan
  rename    Rename a track
  info      Show detailed track info
  import    Import an audio file to a track

track.sh add [options]
  --name <name>         Track name (required)
  --type <type>         Track type: audio, midi, synth (default: audio)

track.sh list
  List all tracks with status (mute/solo/volume/pan).
  --json    Output as raw JSON

track.sh remove <id>
  Remove track by ID number.

track.sh solo <id>
  Solo a track. Other tracks are silenced during playback.

track.sh unsolo <id>
  Remove solo from a track.

track.sh mute <id>
  Mute a track.

track.sh unmute <id>
  Unmute a track.

track.sh volume <id> <0.0-2.0>
  Set track volume. 1.0 = unity gain.

track.sh pan <id> <-1.0 to 1.0>
  Set track pan. -1.0 = hard left, 0.0 = center, 1.0 = hard right.

track.sh rename <id> <new-name>
  Rename a track.

track.sh info <id>
  Show detailed info for a track.
  --json    Output as raw JSON

track.sh import <id> <file>
  Import an audio file as the source for a track.

Examples:
  track.sh add --name "mandolin" --type audio
  track.sh add --name "banjo" --type audio
  track.sh list
  track.sh solo 1
  track.sh volume 2 0.8
  track.sh pan 1 -0.3
  track.sh import 1 ~/samples/mandolin-riff.wav
HELP
}

require_project() {
    if [[ ! -f "$PROJECT_FILE" ]]; then
        echo "Error: No project loaded. Run 'project.sh create' first." >&2
        exit 1
    fi
}

ensure_tracks_file() {
    if [[ ! -f "$TRACKS_FILE" ]]; then
        echo '[]' > "$TRACKS_FILE"
    fi
}

next_id() {
    local max_id
    max_id=$(jq 'if length == 0 then 0 else [.[].id] | max end' "$TRACKS_FILE")
    echo $((max_id + 1))
}

get_project_dir() {
    local proj_name
    proj_name=$(jq -r '.project_dir // .name' "$PROJECT_FILE")
    echo "$PROJECT_ROOT/projects/$proj_name"
}

add_track() {
    local name="" type="audio"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name) name="$2"; shift 2 ;;
            --type) type="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done

    if [[ -z "$name" ]]; then
        echo "Error: --name is required" >&2
        exit 1
    fi

    case "$type" in
        audio|midi|synth) ;;
        *) echo "Error: --type must be audio, midi, or synth" >&2; exit 1 ;;
    esac

    require_project
    ensure_tracks_file

    local id
    id=$(next_id)

    jq --argjson id "$id" \
       --arg name "$name" \
       --arg type "$type" \
       '. + [{
            id: $id,
            name: $name,
            type: $type,
            source: null,
            volume: 1.0,
            pan: 0.0,
            mute: false,
            solo: false
        }]' "$TRACKS_FILE" > "$TRACKS_FILE.tmp" && mv "$TRACKS_FILE.tmp" "$TRACKS_FILE"

    # Initialize empty effects chain for this track
    jq --arg id "$id" '. + {($id): []}' "$EFFECTS_FILE" > "$EFFECTS_FILE.tmp" && mv "$EFFECTS_FILE.tmp" "$EFFECTS_FILE"

    echo "Added track $id: '$name' ($type)"
}

list_tracks() {
    require_project
    ensure_tracks_file

    if [[ "${1:-}" == "--json" ]]; then
        cat "$TRACKS_FILE"
        return
    fi

    local count
    count=$(jq 'length' "$TRACKS_FILE")

    if [[ "$count" -eq 0 ]]; then
        echo "No tracks. Use 'track.sh add --name <name>' to add one."
        return
    fi

    printf "%-4s %-20s %-6s %-6s %-5s %-5s %-5s %s\n" "ID" "Name" "Type" "Vol" "Pan" "Mute" "Solo" "Source"
    printf "%-4s %-20s %-6s %-6s %-5s %-5s %-5s %s\n" "---" "----" "----" "---" "---" "----" "----" "------"

    jq -r '.[] | [
        .id,
        .name,
        .type,
        .volume,
        .pan,
        (if .mute then "M" else "-" end),
        (if .solo then "S" else "-" end),
        (.source // "(empty)")
    ] | @tsv' "$TRACKS_FILE" | while IFS=$'\t' read -r id name type vol pan mute solo source; do
        printf "%-4s %-20s %-6s %-6s %-5s %-5s %-5s %s\n" "$id" "$name" "$type" "$vol" "$pan" "$mute" "$solo" "$source"
    done
}

remove_track() {
    local id="$1"
    require_project
    ensure_tracks_file

    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name // empty' "$TRACKS_FILE")

    if [[ -z "$name" ]]; then
        echo "Error: Track $id not found" >&2
        exit 1
    fi

    jq --argjson id "$id" 'map(select(.id != $id))' "$TRACKS_FILE" > "$TRACKS_FILE.tmp" && mv "$TRACKS_FILE.tmp" "$TRACKS_FILE"

    # Remove effects chain
    jq --arg id "$id" 'del(.[$id])' "$EFFECTS_FILE" > "$EFFECTS_FILE.tmp" && mv "$EFFECTS_FILE.tmp" "$EFFECTS_FILE"

    echo "Removed track $id: '$name'"
}

set_track_field() {
    local id="$1" field="$2" value="$3" is_json="${4:-false}"
    require_project
    ensure_tracks_file

    local exists
    exists=$(jq --argjson id "$id" '[.[] | select(.id == $id)] | length' "$TRACKS_FILE")

    if [[ "$exists" -eq 0 ]]; then
        echo "Error: Track $id not found" >&2
        exit 1
    fi

    if [[ "$is_json" == "true" ]]; then
        jq --argjson id "$id" --argjson val "$value" \
            'map(if .id == $id then . + {'"$field"': $val} else . end)' \
            "$TRACKS_FILE" > "$TRACKS_FILE.tmp" && mv "$TRACKS_FILE.tmp" "$TRACKS_FILE"
    else
        jq --argjson id "$id" --arg val "$value" \
            'map(if .id == $id then . + {'"$field"': $val} else . end)' \
            "$TRACKS_FILE" > "$TRACKS_FILE.tmp" && mv "$TRACKS_FILE.tmp" "$TRACKS_FILE"
    fi
}

solo_track() {
    local id="$1"
    set_track_field "$id" "solo" "true" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Solo: track $id '$name'"
}

unsolo_track() {
    local id="$1"
    set_track_field "$id" "solo" "false" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Unsolo: track $id '$name'"
}

mute_track() {
    local id="$1"
    set_track_field "$id" "mute" "true" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Muted: track $id '$name'"
}

unmute_track() {
    local id="$1"
    set_track_field "$id" "mute" "false" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Unmuted: track $id '$name'"
}

set_volume() {
    local id="$1" vol="$2"
    set_track_field "$id" "volume" "$vol" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Volume: track $id '$name' = $vol"
}

set_pan() {
    local id="$1" pan="$2"
    set_track_field "$id" "pan" "$pan" "true"
    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Pan: track $id '$name' = $pan"
}

rename_track() {
    local id="$1" new_name="$2"
    set_track_field "$id" "name" "$new_name" "false"
    echo "Renamed: track $id -> '$new_name'"
}

track_info() {
    local id="$1"
    require_project
    ensure_tracks_file

    local track
    track=$(jq --argjson id "$id" '.[] | select(.id == $id)' "$TRACKS_FILE")

    if [[ -z "$track" ]]; then
        echo "Error: Track $id not found" >&2
        exit 1
    fi

    if [[ "${2:-}" == "--json" ]]; then
        echo "$track"
        return
    fi

    echo "$track" | jq -r '"Track:   \(.id)
Name:    \(.name)
Type:    \(.type)
Volume:  \(.volume)
Pan:     \(.pan)
Mute:    \(.mute)
Solo:    \(.solo)
Source:  \(.source // "(empty)")"'

    # Show effects chain
    local effects
    effects=$(jq -r --arg id "$id" '.[$id] // []' "$EFFECTS_FILE")
    local fx_count
    fx_count=$(echo "$effects" | jq 'length')

    if [[ "$fx_count" -gt 0 ]]; then
        echo "Effects:"
        echo "$effects" | jq -r '.[] | "  - \(.name) \(.params | to_entries | map("\(.key)=\(.value)") | join(" "))"'
    else
        echo "Effects: (none)"
    fi
}

import_audio() {
    local id="$1" file="$2"
    require_project

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        exit 1
    fi

    # Copy file into project directory
    local project_dir
    project_dir=$(get_project_dir)
    mkdir -p "$project_dir/audio"

    local basename
    basename=$(basename "$file")
    cp "$file" "$project_dir/audio/$basename"

    set_track_field "$id" "source" "$project_dir/audio/$basename" "false"

    local name
    name=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | .name' "$TRACKS_FILE")
    echo "Imported '$basename' to track $id '$name'"
}

# Main dispatch
case "${1:-}" in
    add)     shift; add_track "$@" ;;
    list)    shift; list_tracks "$@" ;;
    remove)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh remove <id>" >&2; exit 1; }
        remove_track "$1"
        ;;
    solo)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh solo <id>" >&2; exit 1; }
        solo_track "$1"
        ;;
    unsolo)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh unsolo <id>" >&2; exit 1; }
        unsolo_track "$1"
        ;;
    mute)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh mute <id>" >&2; exit 1; }
        mute_track "$1"
        ;;
    unmute)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh unmute <id>" >&2; exit 1; }
        unmute_track "$1"
        ;;
    volume)
        shift
        [[ $# -lt 2 ]] && { echo "Usage: track.sh volume <id> <0.0-2.0>" >&2; exit 1; }
        set_volume "$1" "$2"
        ;;
    pan)
        shift
        [[ $# -lt 2 ]] && { echo "Usage: track.sh pan <id> <-1.0 to 1.0>" >&2; exit 1; }
        set_pan "$1" "$2"
        ;;
    rename)
        shift
        [[ $# -lt 2 ]] && { echo "Usage: track.sh rename <id> <new-name>" >&2; exit 1; }
        rename_track "$1" "$2"
        ;;
    info)
        shift
        [[ $# -lt 1 ]] && { echo "Usage: track.sh info <id>" >&2; exit 1; }
        track_info "$@"
        ;;
    import)
        shift
        [[ $# -lt 2 ]] && { echo "Usage: track.sh import <id> <file>" >&2; exit 1; }
        import_audio "$1" "$2"
        ;;
    --help|-h|"") usage ;;
    *)
        echo "Unknown command: $1" >&2
        usage >&2
        exit 1
        ;;
esac
