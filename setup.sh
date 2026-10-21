#!/usr/bin/env bash
#
# Install RSI-Anything skills into supported coding agents.
# Safe defaults: only detected agents are changed, existing entries are backed
# up, and the source repository is never modified.

set -euo pipefail

DRY_RUN=0
MODE="symlink"

usage() {
  cat <<'EOF'
Usage: ./setup.sh [setup] [--dry-run] [--copy] [--help]

  setup       Optional command accepted for `npx rsi-anything setup`
  --dry-run   Print the changes without touching the filesystem
  --copy      Copy skill directories instead of creating symbolic links
  --help      Show this help
EOF
}

for arg in "$@"; do
  case "$arg" in
    setup) ;;
    --dry-run) DRY_RUN=1 ;;
    --copy) MODE="copy" ;;
    -h|--help) usage; exit 0 ;;
    *)
      printf 'Error: unknown argument: %s\n\n' "$arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

# Follow an npm-created bin symlink, if present, to find the packaged skills.
SCRIPT_PATH="${BASH_SOURCE[0]}"
while [[ -L "$SCRIPT_PATH" ]]; do
  LINK_TARGET="$(readlink "$SCRIPT_PATH")"
  if [[ "$LINK_TARGET" == /* ]]; then
    SCRIPT_PATH="$LINK_TARGET"
  else
    SCRIPT_PATH="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)/$LINK_TARGET"
  fi
done
ROOT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SOURCE_DIR="$ROOT_DIR/skills"

if [[ ! -d "$SOURCE_DIR" ]]; then
  printf 'Error: skills directory not found at %s\n' "$SOURCE_DIR" >&2
  exit 1
fi

shopt -s nullglob
SKILLS=("$SOURCE_DIR"/*)
if [[ ${#SKILLS[@]} -eq 0 ]]; then
  printf 'Error: no skills found in %s\n' "$SOURCE_DIR" >&2
  exit 1
fi

AGENT_NAMES=("Claude Code" "Cursor" "Codex")
AGENT_ROOTS=("$HOME/.claude" "$HOME/.cursor" "$HOME/.codex")
AGENT_SKILL_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.cursor/skills"
  "$HOME/.codex/skills"
)

detected=0
installed=0
backed_up=0
unchanged=0
planned=0
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '  DRY-RUN:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

next_backup_path() {
  local target="$1"
  local backup="${target}.backup-${timestamp}"
  local suffix=1
  while [[ -e "$backup" || -L "$backup" ]]; do
    backup="${target}.backup-${timestamp}-${suffix}"
    suffix=$((suffix + 1))
  done
  printf '%s' "$backup"
}

printf 'RSI-Anything skill installer\n'
printf 'Source: %s\nMode: %s%s\n\n' \
  "$SOURCE_DIR" "$MODE" "$([[ "$DRY_RUN" -eq 1 ]] && printf ' (dry run)')"

for i in "${!AGENT_NAMES[@]}"; do
  agent="${AGENT_NAMES[$i]}"
  agent_root="${AGENT_ROOTS[$i]}"
  target_root="${AGENT_SKILL_DIRS[$i]}"

  # An existing agent config root or skills directory counts as installed.
  if [[ ! -d "$agent_root" && ! -d "$target_root" ]]; then
    printf '○ %-12s not detected (%s)\n' "$agent" "$agent_root"
    continue
  fi

  detected=$((detected + 1))
  printf '● %-12s detected\n' "$agent"
  run mkdir -p "$target_root"

  for source in "${SKILLS[@]}"; do
    [[ -d "$source" ]] || continue
    skill_name="$(basename "$source")"
    target="$target_root/$skill_name"

    if [[ "$MODE" == "symlink" && -L "$target" ]] &&
       [[ "$(readlink "$target")" == "$source" ]]; then
      printf '  ✓ %s already linked\n' "$skill_name"
      unchanged=$((unchanged + 1))
      continue
    fi

    if [[ -e "$target" || -L "$target" ]]; then
      backup="$(next_backup_path "$target")"
      printf '  ↳ backing up %s to %s\n' "$skill_name" "$(basename "$backup")"
      run mv "$target" "$backup"
      backed_up=$((backed_up + 1))
    fi

    if [[ "$MODE" == "copy" ]]; then
      printf '  + copying %s\n' "$skill_name"
      run cp -R "$source" "$target"
    else
      printf '  + linking %s\n' "$skill_name"
      run ln -s "$source" "$target"
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
      planned=$((planned + 1))
    else
      installed=$((installed + 1))
    fi
  done
  printf '\n'
done

printf '%s\n' '────────────────────────────────────────'
if [[ "$detected" -eq 0 ]]; then
  printf 'No supported coding agents detected; nothing changed.\n'
  printf 'Install Claude Code, Cursor, or Codex, then run this again.\n'
elif [[ "$DRY_RUN" -eq 1 ]]; then
  printf 'Dry run complete: %d agent(s), %d skill install(s), %d backup(s) planned.\n' \
    "$detected" "$planned" "$backed_up"
else
  printf 'Setup complete: %d agent(s), %d skill(s) installed, %d unchanged, %d backup(s).\n' \
    "$detected" "$installed" "$unchanged" "$backed_up"
fi
