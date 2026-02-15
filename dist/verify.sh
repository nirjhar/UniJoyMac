#!/usr/bin/env bash
set -euo pipefail

LAYOUT_NAME="UniJoyMac"
USER_INSTALL_DIR="$HOME/Library/Keyboard Layouts"
SYSTEM_INSTALL_DIR="/Library/Keyboard Layouts"
BUNDLE_NAME="${LAYOUT_NAME}.bundle"
KEYLAYOUT_FILE="UniJoyMac.keylayout"

INSTALL_SCOPE="user"
if [[ "${1:-}" == "--system" ]]; then
  INSTALL_SCOPE="system"
fi

if [[ "$INSTALL_SCOPE" == "system" ]]; then
  TARGET_DIR="$SYSTEM_INSTALL_DIR"
else
  TARGET_DIR="$USER_INSTALL_DIR"
fi

BUNDLE_PATH="$TARGET_DIR/$BUNDLE_NAME"
KEYLAYOUT_PATH="$BUNDLE_PATH/Contents/Resources/$KEYLAYOUT_FILE"
PLIST_PATH="$BUNDLE_PATH/Contents/Info.plist"

echo "== UniJoyMac Verification =="
echo "Scope: $INSTALL_SCOPE"
echo "Target: $BUNDLE_PATH"

if [[ ! -d "$BUNDLE_PATH" ]]; then
  echo "ERROR: Bundle not found: $BUNDLE_PATH"
  echo "Install first: cp -R dist/$BUNDLE_NAME \"$TARGET_DIR/\""
  exit 1
fi

if [[ ! -f "$KEYLAYOUT_PATH" ]]; then
  echo "ERROR: Missing keylayout in bundle: $KEYLAYOUT_PATH"
  exit 1
fi

if [[ ! -f "$PLIST_PATH" ]]; then
  echo "ERROR: Missing Info.plist: $PLIST_PATH"
  exit 1
fi

echo "- Bundle exists"
echo "- keylayout present"

if command -v plutil >/dev/null 2>&1; then
  plutil -lint "$PLIST_PATH"
else
  echo "WARN: plutil not available, skipping Info.plist lint"
fi

if command -v xmllint >/dev/null 2>&1; then
  # The keylayout uses XML 1.1 (required for &#x0008; backspace character
  # reference).  xmllint only supports XML 1.0, so we downgrade the
  # declaration and substitute &#x0008; with &#x0009; for validation.
  TMPXML="$(mktemp)"
  sed -e 's/version="1\.1"/version="1.0"/' \
      -e 's/\&#x0008;/\&#x0009;/g' "$KEYLAYOUT_PATH" > "$TMPXML"
  xmllint --noout "$TMPXML"
  xmllint --noout --valid "$TMPXML"
  rm -f "$TMPXML"
  echo "- keylayout XML and DTD validation passed"
else
  echo "WARN: xmllint not available, skipping XML validation"
fi

python3 - <<PY
import xml.etree.ElementTree as ET

keylayout_path = """$KEYLAYOUT_PATH"""
# The keylayout uses XML 1.1 for &#x0008; support.  Python's ET only
# handles XML 1.0, so downgrade the declaration and substitute the
# backspace char ref for parsing.
raw = open(keylayout_path, 'r', encoding='utf-8').read()
safe = raw.replace('version="1.1"', 'version="1.0"').replace('&#x0008;', '&#x0009;')
root = ET.fromstring(safe)

maps = {}
actions = {}

for action in root.findall(".//actions/action"):
    action_id = action.attrib.get("id")
    if not action_id:
        continue
    by_state = {}
    for when in action.findall("when"):
        state = when.attrib.get("state", "none")
        output = when.attrib.get("output")
        if output is not None:
            by_state[state] = output
    actions[action_id] = by_state

for key_map in root.findall(".//keyMap"):
    idx = int(key_map.attrib["index"])
    resolved = {}
    for key in key_map.findall("key"):
        code = int(key.attrib["code"])
        output = key.attrib.get("output")
        if output is None:
            action_id = key.attrib.get("action", "")
            output = actions.get(action_id, {}).get("none", "")
        resolved[code] = output
    maps[idx] = resolved

checks = [
    ("normal", 0, 12, "ং"),
    ("normal", 0, 3, "া"),
    ("normal", 0, 35, "ড়"),
    ("normal", 0, 50, "\u200c"),
    ("shift", 1, 12, "ঙ"),
    ("shift", 1, 19, "ঁ"),
    ("shift", 1, 5, "।"),
    ("shift", 1, 35, "ঢ়"),
    ("option", 2, 0, "ঋ"),
    ("option", 2, 7, "ও"),
    ("option+shift", 3, 1, "ঊ"),
    ("option+shift", 3, 8, "ঐ"),
]

errors = []
for layer_name, map_index, keycode, expected in checks:
    actual = maps.get(map_index, {}).get(keycode, None)
    if actual != expected:
        errors.append((layer_name, map_index, keycode, expected, actual))

if errors:
    print("ERROR: Mapping mismatches detected:")
    for layer_name, map_index, keycode, expected, actual in errors:
        print(f"  layer={layer_name} map={map_index} code={keycode} expected={expected!r} actual={actual!r}")
    raise SystemExit(1)

print("- Sample mapping checks passed for normal/shift/option/option+shift")
PY

if defaults read com.apple.HIToolbox AppleEnabledInputSources >/dev/null 2>&1; then
  echo "- HIToolbox input source preferences are readable"
fi

echo
echo "If the layout is still not visible in Input Sources:"
echo "1) Run: touch \"$TARGET_DIR\""
echo "2) Restart macOS (preferred) or log out and back in"
echo "3) Open System Settings -> Keyboard -> Input Sources -> + -> Others or Bengali"
echo "Verification complete."
