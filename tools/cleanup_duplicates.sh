#!/usr/bin/env bash
set -euo pipefail

LAYOUT_NAME="UniJoyMac"
USER_DIR="$HOME/Library/Keyboard Layouts"
SYSTEM_DIR="/Library/Keyboard Layouts"

clean_user() {
  /bin/mkdir -p "$USER_DIR"
  /bin/rm -f "$USER_DIR/${LAYOUT_NAME}.keylayout" "$USER_DIR/${LAYOUT_NAME}.icns"
  /usr/bin/touch "$USER_DIR"
  echo "Cleaned user-local loose files in: $USER_DIR"
}

clean_system() {
  if [[ "$(/usr/bin/id -u)" -eq 0 ]]; then
    /bin/rm -rf "$SYSTEM_DIR/${LAYOUT_NAME}.bundle"
    /bin/rm -f "$SYSTEM_DIR/${LAYOUT_NAME}.keylayout" "$SYSTEM_DIR/${LAYOUT_NAME}.icns"
    /usr/bin/touch "$SYSTEM_DIR"
  else
    /usr/bin/sudo /bin/rm -rf "$SYSTEM_DIR/${LAYOUT_NAME}.bundle"
    /usr/bin/sudo /bin/rm -f "$SYSTEM_DIR/${LAYOUT_NAME}.keylayout" "$SYSTEM_DIR/${LAYOUT_NAME}.icns"
    /usr/bin/sudo /usr/bin/touch "$SYSTEM_DIR"
  fi
  echo "Removed system-wide install in: $SYSTEM_DIR"
}

MODE="user"
if [[ "${1:-}" == "--all" ]]; then
  MODE="all"
fi

if [[ "$MODE" == "all" ]]; then
  clean_user
  clean_system
else
  clean_user
fi

/usr/bin/killall TextInputMenuAgent >/dev/null 2>&1 || true
/usr/bin/killall cfprefsd >/dev/null 2>&1 || true

echo "Done. Log out and log back in, then re-add UniJoyMac once in Input Sources."
