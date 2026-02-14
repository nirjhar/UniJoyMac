# UniJoyMac

UniJoyMac is a macOS Bangla keyboard layout package generated from Avro's `ub.avrolayout` static key map.

It provides a positional Bangla layout for macOS Input Sources and includes:

- a distributable `.bundle` for reliable discovery in System Settings
- a `.pkg` installer for Intel and Apple Silicon Macs
- the raw `.keylayout` XML
- a conversion tool from Avro layout format
- verification and installation helpers

## What this project contains

- `ub.avrolayout` - source Avro keyboard layout file
- `tools/avro_to_keylayout.py` - Avro-to-macOS converter
- `dist/UniJoyMac.keylayout` - generated macOS keyboard layout XML
- `dist/UniJoyMac.icns` - icon file used by the bundle
- `dist/UniJoyMac.bundle` - distributable keyboard layout bundle
- `dist/UniJoyMac-Installer.pkg` - macOS installer package (built locally)
- `dist/INSTALL.md` - step-by-step install and manual test checklist
- `dist/verify.sh` - install and mapping verification script
- `dist/mapping_report.md` - mapping coverage and assumptions

## macOS support

Tested in a modern macOS environment where custom keyboard layouts in `~/Library/Keyboard Layouts` appear under **System Settings -> Keyboard -> Input Sources -> Others**.

## Install

### Installer package (recommended)

Build installer:

```bash
bash "tools/build_installer.sh"
```

Build and sign installer (Developer ID Installer):

```bash
UNIJOYMAC_SIGN_IDENTITY="Developer ID Installer: YOUR NAME (TEAMID)" bash "tools/build_installer.sh"
```

Then run:

```bash
open "dist/UniJoyMac-Installer.pkg"
```

The installer places `UniJoyMac.bundle` in `/Library/Keyboard Layouts`, touches the keyboard layouts directory, and refreshes input-source daemons.
When signing is enabled, the script signs `dist/UniJoyMac-Installer.pkg` in-place and prints signature details.

Find available installer identities:

```bash
security find-identity -v -p basic
```

### User install (manual)

```bash
mkdir -p "$HOME/Library/Keyboard Layouts"
cp -R "dist/UniJoyMac.bundle" "$HOME/Library/Keyboard Layouts/"
touch "$HOME/Library/Keyboard Layouts"
```

Then add the input source from:

`System Settings -> Keyboard -> Input Sources -> + -> Others -> UniJoyMac`

### System-wide install (manual)

```bash
sudo mkdir -p "/Library/Keyboard Layouts"
sudo cp -R "dist/UniJoyMac.bundle" "/Library/Keyboard Layouts/"
sudo touch "/Library/Keyboard Layouts"
```

## Verify

Run:

```bash
bash "dist/verify.sh"
```

For system scope:

```bash
bash "dist/verify.sh" --system
```

The verification checks:

- bundle and keylayout presence
- `Info.plist` validity
- keylayout XML validity
- sample key mappings in all main layers: normal, Shift, Option, Option+Shift

## Mapping model and limitations

UniJoyMac is a static positional mapping.

- Implemented layers: no modifier, Shift, Option (AltGr), Option+Shift
- Unicode outputs are normalized with NFC during conversion
- Avro dynamic phonetic/composition rules are not implemented in native `.keylayout`

If you need phonetic behavior, use an IME/input method layer on top of this, not `.keylayout` alone.

## Regenerate keylayout

```bash
python3 "tools/avro_to_keylayout.py" "ub.avrolayout" "dist/UniJoyMac.keylayout" --layout-name "UniJoyMac"
```

## Maintainer

Lutfar Rahman Nirjhar
