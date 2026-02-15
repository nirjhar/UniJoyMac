# UniJoyMac

A macOS keyboard layout for typing Bengali using the UniJoy/Bijoy positional layout. Generated from Avro's `ub.avrolayout` static key map.

## Features

- Positional Bengali keyboard layout (UniJoy/Bijoy compatible)
- Virama dead-key state machine for typing independent vowels
- Command keymaps (Cmd+C/V/Z etc. produce correct QWERTY shortcuts)
- Backspace support via key code 51
- Works on macOS 26 (Tahoe) and later, Intel and Apple Silicon

## Install

### Download and run the installer

```bash
open "dist/UniJoyMac-Installer.pkg"
```

The installer places `UniJoyMac.bundle` in `/Library/Keyboard Layouts/` and prompts for restart.

After restarting, add the keyboard from:

**System Settings > Keyboard > Input Sources > + > Others (or Bengali) > UniJoyMac**

### Build installer from source

```bash
bash "tools/build_installer.sh"
open "dist/UniJoyMac-Installer.pkg"
```

Optionally sign the installer:

```bash
UNIJOYMAC_SIGN_IDENTITY="Developer ID Installer: YOUR NAME (TEAMID)" bash "tools/build_installer.sh"
```

## Keyboard layers

| Layer | Modifier | Content |
|-------|----------|---------|
| Normal | (none) | Bengali characters |
| Shift | Shift | Bengali shifted characters |
| Option | Option/AltGr | Bengali alternate characters |
| Shift+Option | Shift+Option | Bengali alternate shifted |
| Command | Cmd | US QWERTY (for shortcuts) |
| Shift+Command | Shift+Cmd | US QWERTY shifted |
| Option+Command | Option+Cmd | US QWERTY |
| Shift+Option+Command | Shift+Option+Cmd | US QWERTY shifted |

## Virama dead-key behavior

Pressing virama (`্`, G key) enters a dead-key state. Pressing a dependent vowel sign in this state produces the corresponding independent vowel:

| Dead-key sequence | Output |
|-------------------|--------|
| `্` then `া` | আ |
| `্` then `ি` | ই |
| `্` then `ু` | উ |
| `্` then `ে` | এ |
| `্` then `ো` | ও |
| (etc.) | |

## Regenerate keylayout from source

```bash
python3 "tools/avro_to_keylayout.py" "ub.avrolayout" "dist/UniJoyMac.keylayout" --layout-name "UniJoyMac"
cp "dist/UniJoyMac.keylayout" "dist/UniJoyMac.bundle/Contents/Resources/UniJoyMac.keylayout"
bash "tools/build_installer.sh"
```

## Verify installation

```bash
bash "dist/verify.sh" --system
```

Checks bundle presence, Info.plist validity, XML/DTD validation, and sample key mappings.

## Known issues

### Backspace does not work in Microsoft Word

Backspace works in all native macOS apps (TextEdit, Safari, Notes, etc.) but **not in Microsoft Word**. This is a limitation of how Word handles key events from third-party `.keylayout` files on macOS.

**Root cause:** macOS routes key code 51 (backspace) from third-party keylayouts through the text input `insertText:` path with U+0008. Word's text engine does not interpret this as a delete-backward command. Apple's built-in keyboard layouts use a different system-level path that Word handles correctly.

This affects **all** third-party `.keylayout` files in Word, not just UniJoyMac. Verified by testing a minimal keylayout containing only 3 keys + backspace.

**Workarounds:**
- Use **fn+Delete** (forward delete) in Word
- Switch to Apple's **Bangla QWERTY** keyboard for editing in Word
- Type in TextEdit and paste into Word

**Help wanted:** If you know how to make backspace work in Word with a third-party `.keylayout` (without converting to a full Input Method), please open an issue or PR. See [Contributing](#contributing).

### macOS 26.3 compatibility notes

macOS 26.3 introduced stricter validation for third-party keyboard layouts:

- **`anyCommand` modifier rejected:** Using `anyCommand` in modifier keymaps causes the entire keylayout to be silently rejected. Use `command` instead. (`anyShift` and `anyOption` still work.)
- **XML 1.1 required for backspace:** The backspace character `&#x0008;` is invalid in XML 1.0. XML 1.1 is required to include it as a legal character reference.
- **Silent rejection:** macOS provides no error messages when rejecting a keylayout. The keyboard simply doesn't appear in Input Sources.

### Other limitations

- Static positional mapping only (no phonetic/dynamic composition)
- Option and Option+Shift layers are sparse (source layout has many empty values)

## Project structure

```
ub.avrolayout                    # Source Avro keyboard layout
tools/avro_to_keylayout.py       # Converter: Avro → macOS keylayout
tools/build_installer.sh         # Builds .pkg installer
dist/UniJoyMac.keylayout         # Generated keylayout XML
dist/UniJoyMac.icns              # Keyboard icon
dist/UniJoyMac.bundle/           # macOS keyboard layout bundle
dist/UniJoyMac-Installer.pkg     # Installer package
dist/verify.sh                   # Installation verification script
packaging/scripts/postinstall    # Installer post-install script
```

## Contributing

Contributions are welcome, especially for:

1. **Fixing backspace in Microsoft Word** — The key challenge is making Word treat key code 51 from a third-party keylayout as a backspace command rather than text input. Potential approaches:
   - A lightweight Input Method wrapper around the keylayout
   - A macOS service/helper that intercepts backspace events
   - Discovering a keylayout-only solution that changes the TSM processing path

2. **Additional key mappings** — Numpad keys, additional special characters

3. **Testing on different macOS versions**

Please open an issue to discuss before submitting large changes.

## Maintainer

Lutfar Rahman Nirjhar
