#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
USER_DIR="$HOME/Library/Keyboard Layouts"

mkdir -p "$USER_DIR"
rm -rf "$USER_DIR/UniJoyMac.bundle"
rm -f "$USER_DIR/UniJoyMac.keylayout" "$USER_DIR/UniJoyMac.icns"

cp -R "$DIST_DIR/UniJoyMac.bundle" "$USER_DIR/"
touch "$USER_DIR"

/usr/bin/killall TextInputMenuAgent >/dev/null 2>&1 || true
/usr/bin/killall cfprefsd >/dev/null 2>&1 || true

USER_UID="$(/usr/bin/id -u)"
/bin/launchctl kickstart -k "gui/$USER_UID/com.apple.TextInputMenuAgent" >/dev/null 2>&1 || true

echo "Installed UniJoyMac to $USER_DIR"
echo "Now log out and log back in, then add from Input Sources."
