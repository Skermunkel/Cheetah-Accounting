#!/bin/sh
# Cheetah Accounting installer for macOS and Linux. In a terminal:
#   curl -LsSf https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.sh | sh
# Installs into ~/Cheetah: app/ (this repo) and workspace/ (your private files, never uploaded).
# Run it again at any time to repair or update.
set -eu
BASE="$HOME/Cheetah"
APP="$BASE/app"
export CHEETAH_WORKSPACE="$BASE/workspace"
REPO=https://github.com/Skermunkel/Cheetah-Accounting

echo '1/5 Python tools (uv)'
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    PATH="$HOME/.local/bin:$PATH"
fi

echo '2/5 Cheetah app'
mkdir -p "$BASE"
if [ -d "$APP/.git" ]; then
    git -C "$APP" pull --ff-only
elif command -v git >/dev/null 2>&1; then
    git clone "$REPO" "$APP"
else
    tmp=$(mktemp -d)
    curl -LsSf "$REPO/archive/refs/heads/main.zip" -o "$tmp/cheetah.zip"
    unzip -q "$tmp/cheetah.zip" -d "$tmp"
    mkdir -p "$APP"
    cp -R "$tmp/Cheetah-Accounting-main/." "$APP/"
fi

echo '3/5 Requirements (a few minutes the first time)'
uv --directory "$APP" sync

echo '4/5 Connect to Claude Desktop and build the skills'
uv --directory "$APP" run cheetah setup-claude
uv --directory "$APP" run cheetah build-skills

echo '5/5 Document-reading models (about 500 MB, once)'
uv --directory "$APP" run cheetah warm
uv --directory "$APP" run cheetah doctor || true

echo
echo 'Done. Next:'
echo '  1. Fully quit Claude Desktop and open it again.'
echo "  2. Settings > Capabilities: turn on code execution, then upload each zip in $APP/dist/skills"
echo '  3. In a new chat, type: cheetah-init'
