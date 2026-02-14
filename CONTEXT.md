# CONTEXT

This file captures the current technical context of the `UniJoyMac` project so future debugging is fast.

## Project goal

Convert Avro keyboard layout source (`ub.avrolayout`) into a macOS custom keyboard layout that can be enabled via:

- System Settings -> Keyboard -> Input Sources -> Others

Deliverables are generated under `dist/` as:

- `UniJoyMac.keylayout`
- `UniJoyMac.icns`
- `UniJoyMac.bundle`
- `UniJoyMac-Installer.pkg`
- `INSTALL.md`
- `verify.sh`
- `mapping_report.md`

## Current architecture

- Source format: `ub.avrolayout` (Avro keyboard XML-like format)
- Converter: `tools/avro_to_keylayout.py`
- Output layout: `dist/UniJoyMac.keylayout`
- Bundle metadata: `dist/UniJoyMac.bundle/Contents/Info.plist`

### Why custom parsing was used

`ub.avrolayout` is XML-like but not strictly XML for generic parsers because it contains numeric tag names, for example:

- `<1_Normal>...</1_Normal>`

`xml.etree.ElementTree.parse()` fails on that. The converter therefore:

1. Reads raw file text
2. Extracts `<KeyData>...</KeyData>` with regex
3. Extracts `<KEY_(Normal|Shift|AltGr|ShiftAltGr)>value</...>` fields with regex
4. Preserves Avro source code points exactly (no NFC normalization) so letters like ড়/ঢ়/য় stay in their source form

## Mapping model

Implemented layers (8 keyMaps total):

- `Normal` -> macOS no modifier (index 0)
- `Shift` -> macOS Shift (index 1)
- `AltGr` -> macOS Option (index 2)
- `ShiftAltGr` -> macOS Option+Shift (index 3)
- `Command` -> passes through US QWERTY so Cmd+C/V/X etc. work (indices 4-7)

Virama state machine: the converter generates `<actions>` and `<terminators>` elements implementing a UniJoy-style virama (`্`) state. Pressing virama enters `state_virama`; pressing a dependent vowel sign in that state emits the corresponding independent vowel (e.g. া→আ, ি→ই).

Key coverage (main ANSI set):

- Letters: `A-Z`
- Digits: `0-9`
- OEM/punctuation: `` OEM3 MINUS PLUS OEM4 OEM6 OEM5 OEM1 OEM7 COMMA PERIOD OEM2 ``

Numpad entries (`Num1`, etc.) are present in source but currently not emitted in `.keylayout`.

## Important IDs and names

- Display/layout name: `UniJoyMac`
- Bundle id in plist: `pro.lonesock.keyboardlayout.unijoymac`
- Keyboard ID in `.keylayout`: `-28676`
- Keyboard group in `.keylayout`: `126`
- Plist layout info key: `KLInfo_UniJoyMac` (must match the `name` attribute in `.keylayout`)

## Install behavior

Preferred install path:

- Open `dist/UniJoyMac-Installer.pkg`

Installer behavior:

- installs bundle only to `/Library/Keyboard Layouts/UniJoyMac.bundle`
- removes standalone `.keylayout` and `.icns` from `/Library/Keyboard Layouts/` to prevent duplicate Input Sources entries
- removes user-level copies from `~/Library/Keyboard Layouts/` so only the system bundle is active
- clears extended attributes (`com.apple.quarantine`, `com.apple.provenance`) on installed keyboard files
- refreshes keyboard discovery (`touch` + `TextInputMenuAgent`/`cfprefsd` restart)
- prompts user to save work and choose **Restart Now**, **Log Out Now**, or **Later**
- restart is now the recommended refresh action on recent macOS versions

System install path:

- `/Library/Keyboard Layouts/UniJoyMac.bundle` (bundle only — no standalone files)

Supported installation flow is installer-only (`UniJoyMac-Installer.pkg`), followed by restart (preferred) or logout/login.

## Verification behavior

Script: `dist/verify.sh`

Checks:

- bundle exists
- keylayout exists in bundle resources
- plist lint via `plutil`
- keylayout XML syntax and DTD validation via `xmllint --valid`
- sample key mapping assertions across 4 layers

If verify fails:

1. Confirm file names in bundle match expected `UniJoyMac.*`
2. Confirm `Info.plist` keys point to `UniJoyMac.icns`
3. Confirm `dist/UniJoyMac.keylayout` is copied into bundle resources
4. Reinstall and touch keyboard layouts directory

If verify passes but layout is not visible in Input Sources:

1. Restart macOS (preferred on newer versions)
2. Check both categories in Input Sources picker: `Others` and `Bengali`
3. Re-run installer to refresh both system and user layout directories

## Known limitations

- Static positional mapping only
- No phonetic/dynamic composition engine in native `.keylayout`
- Option and Option+Shift are sparse because source layout has many empty values in those layers
- Key code 51 (delete/backspace) is omitted from the keylayout — macOS handles it natively, and U+0008 (BS) is not valid XML 1.0 (its presence caused macOS to silently reject the entire keylayout file)
- The `Info.plist` key `KLInfo_<name>` must use the layout name (e.g. `KLInfo_UniJoyMac`), not a numeric index — macOS 26 (Tahoe) does not discover the bundle with `KLInfo_0`

## Fast debug commands

Regenerate layout:

```bash
python3 "tools/avro_to_keylayout.py" "ub.avrolayout" "dist/UniJoyMac.keylayout" --layout-name "UniJoyMac"
```

Rebuild bundle resources after regeneration:

```bash
cp "dist/UniJoyMac.keylayout" "dist/UniJoyMac.bundle/Contents/Resources/UniJoyMac.keylayout"
cp "dist/UniJoyMac.icns" "dist/UniJoyMac.bundle/Contents/Resources/UniJoyMac.icns"
```

Reinstall with installer and verify:

```bash
bash "tools/build_installer.sh"
open "dist/UniJoyMac-Installer.pkg"
bash "dist/verify.sh"
```

Validate keylayout XML manually:

```bash
xmllint --noout --valid "dist/UniJoyMac.keylayout"
```
