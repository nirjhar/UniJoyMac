# UniJoyMac

A macOS keyboard layout for typing Bengali using the UniJoy/Bijoy positional layout. Generated from Avro's `ub.avrolayout` static key map.

## Features

- Positional Bengali keyboard layout (UniJoy/Bijoy compatible)
- Virama dead-key state machine for typing independent vowels
- Command keymaps (Cmd+C/V/Z etc. produce correct QWERTY shortcuts)
- Backspace support via key code 51
## Requirements

- **macOS:** macOS 26 (Tahoe) or later
- **Architecture:** Intel (x86_64) and Apple Silicon (arm64)
- **Keyboard:** ANSI and JIS layouts supported

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

## Notes

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

1. **Additional key mappings** — Numpad keys, additional special characters
2. **Testing on different macOS versions**

Please open an issue to discuss before submitting large changes.

## Maintainer

Lutfar Rahman Nirjhar (nirjhar@nirjhar.com)
