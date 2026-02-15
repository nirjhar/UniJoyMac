# CONTEXT

This file captures the current technical context of the `UniJoyMac` project so future debugging is fast.

## Project goal

Convert Avro keyboard layout source (`ub.avrolayout`) into a macOS custom keyboard layout that can be enabled via:

- System Settings -> Keyboard -> Input Sources -> Others

## Current architecture

- Source format: `ub.avrolayout` (Avro keyboard XML-like format)
- Converter: `tools/avro_to_keylayout.py`
- Output layout: `dist/UniJoyMac.keylayout` (XML 1.1)
- Bundle metadata: `dist/UniJoyMac.bundle/Contents/Info.plist`
- Language: `bn` (Bengali, matches Apple's Bangla keyboards)

### Keylayout structure (8 keymaps)

- Index 0: Normal (Bengali) — `modifier keys=""`
- Index 1: Shift (Bengali) — `modifier keys="anyShift"`
- Index 2: Option/AltGr (Bengali) — `modifier keys="anyOption"`
- Index 3: Shift+Option (Bengali) — `modifier keys="anyShift anyOption"`
- Index 4: Command (QWERTY) — `modifier keys="command"`
- Index 5: Shift+Command (QWERTY shifted) — `modifier keys="anyShift command"`
- Index 6: Option+Command (QWERTY) — `modifier keys="anyOption command"`
- Index 7: Shift+Option+Command (QWERTY shifted) — `modifier keys="anyShift anyOption command"`

### Layout element

```xml
<layout first="0" last="17" mapSet="mapset_0" modifiers="modifiers_0" />
<layout first="18" last="18" mapSet="mapset_0" modifiers="modifiers_0" />
```

Covers all ANSI keyboard types (0-17) and JIS (18), matching working third-party layouts.

### Key code 51 (backspace) and `&#x0008;`

Key code 51 is mapped to `&#x0008;` (U+0008, BS) in all 8 keymaps.

- XML 1.1 declaration is required: `&#x0008;` is not a legal XML 1.0 character reference
- Python ET can't serialize U+0008; uses PUA sentinel U+E000, replaced after serialization
- `verify.sh` downgrades XML 1.1→1.0 and substitutes `&#x0008;`→`&#x0009;` for xmllint/ET validation

### Command keymap rules

- Command keymaps use ONLY `output` attributes, NEVER `action`
- Must use `command` (not `anyCommand`) — macOS 26.3 silently rejects `anyCommand`
- `anyShift` and `anyOption` still work fine with `command`

### Virama dead-key state machine

The converter generates `<actions>` and `<terminators>` elements implementing a UniJoy-style virama (`্`) state. Pressing virama enters `state_virama`; pressing a dependent vowel sign in that state emits the corresponding independent vowel.

## Important IDs and names

- Display/layout name: `UniJoyMac`
- Bundle id: `pro.lonesock.keyboardlayout.unijoymac`
- Keyboard ID: `-28676`
- Keyboard group: `126`
- Plist layout info key: `KLInfo_UniJoyMac` (must match `name` attribute in keylayout)
- Language: `bn` (Bengali)

## macOS 26.3 compatibility findings

Confirmed by bisection testing (2026-02-15):

1. **`anyCommand` is silently rejected.** A keylayout containing `anyCommand` in any modifier key will not appear in Input Sources. Use `command` instead.
2. **XML 1.1 works fine.** Previous belief that XML 1.1 was rejected was wrong — `anyCommand` was the actual cause.
3. **`&#x0008;` works with XML 1.1.** Previous belief that `&#x0008;` was rejected was wrong — `anyCommand` was the actual cause.
4. **`first="0" last="0"` is too restrictive.** Use `first="0" last="17"` for ANSI + `first="18" last="18"` for JIS.
5. **Rejection is completely silent.** No Console logs, no errors. Keyboard just doesn't appear.
6. **Force TIS rescan:** `killall TextInputMenuAgent cfprefsd` (no restart needed for testing).

## Known issue: Backspace in Microsoft Word

Backspace from third-party `.keylayout` files does not work in Microsoft Word on macOS. This affects ALL third-party keylayouts, not just UniJoyMac.

Tested approaches (all failed in Word):
- `output="&#x0008;"` (direct output)
- `output="&#x007F;"` (DEL character)
- `action` element with `&#x0008;` output
- No key code 51 mapping at all

Root cause: macOS TSM routes key code 51 from third-party keylayouts through `insertText:` with U+0008. Word doesn't interpret this as a backspace command. System keylayouts use a different path that Word handles correctly.

Apple's Bangla QWERTY (system keylayout) produces identical UCKeyTranslate output (U+0008 for key code 51) but works in Word — confirming the difference is in the event delivery path, not the character.

## Fast debug commands

```bash
# Full rebuild + install + test cycle
python3 tools/avro_to_keylayout.py ub.avrolayout dist/UniJoyMac.keylayout --layout-name UniJoyMac
cp dist/UniJoyMac.keylayout dist/UniJoyMac.bundle/Contents/Resources/UniJoyMac.keylayout
sudo cp dist/UniJoyMac.keylayout "/Library/Keyboard Layouts/UniJoyMac.bundle/Contents/Resources/UniJoyMac.keylayout"
sudo touch "/Library/Keyboard Layouts/"
killall TextInputMenuAgent cfprefsd
sleep 3
swift /tmp/list_keyboards.swift | grep -i unijoy

# Validate keylayout (substitute control chars for strict parsers)
TMPXML="$(mktemp)" && sed -e 's/version="1\.1"/version="1.0"/' -e 's/\&#x0008;/\&#x0009;/g' dist/UniJoyMac.keylayout > "$TMPXML" && xmllint --noout --valid "$TMPXML" && rm -f "$TMPXML"

# Check UCKeyTranslate output for key code 51
swift /tmp/check_unijoy_delete.swift
```
