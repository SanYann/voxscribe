#!/usr/bin/env bash
#
# voxscribe — one-shot installer for macOS.
# Installs everything needed to transcribe voice notes locally, then (optionally)
# plugs voxscribe into Claude. Safe to re-run.
#
#   curl -fsSL https://raw.githubusercontent.com/SanYann/voxscribe/main/install.sh | bash
#
set -euo pipefail

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
info() { printf "  \033[34m•\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }

bold "voxscribe installer"
echo

if [[ "$(uname)" != "Darwin" ]]; then
  warn "This script targets macOS. On Linux, see the README for manual steps."
  exit 1
fi

# 1. Homebrew --------------------------------------------------------------
if ! command -v brew >/dev/null 2>&1; then
  info "Homebrew (the macOS app installer) is missing — installing it now."
  info "You may be asked for your Mac password. That's normal."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Make brew available in this session (Apple Silicon + Intel paths).
  if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
  if [[ -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi
ok "Homebrew ready"

# 2. Native tools ----------------------------------------------------------
info "Installing audio + transcription engines (ffmpeg, whisper.cpp)…"
brew install ffmpeg whisper-cpp pipx >/dev/null
pipx ensurepath >/dev/null 2>&1 || true
ok "ffmpeg, whisper.cpp, pipx installed"

# 3. voxscribe -------------------------------------------------------------
info "Installing voxscribe…"
# Try PyPI first (once published); otherwise install straight from GitHub.
pipx install --force "voxscribe[mcp]" >/dev/null 2>&1 \
  || pipx install --force "voxscribe[mcp] @ git+https://github.com/SanYann/voxscribe.git" >/dev/null
ok "voxscribe installed"

# 4. Connect to Claude (optional) -----------------------------------------
if command -v claude >/dev/null 2>&1; then
  if claude mcp add voxscribe -- voxscribe-mcp >/dev/null 2>&1; then
    ok "Connected to Claude Code — ask Claude to \"transcribe my voice note\""
  else
    info "Claude Code already has voxscribe (or add it later with: claude mcp add voxscribe -- voxscribe-mcp)"
  fi
else
  info "Claude Code not detected — that's fine, the 'voxscribe' command still works on its own."
fi

echo
bold "Done! 🎉"
echo
echo "Try it now (open a NEW Terminal window first so the command is found):"
echo "    voxscribe ~/Downloads/your-voice-note.opus -l fr"
echo
echo "First run downloads a small AI model (~140 MB) — that only happens once."
