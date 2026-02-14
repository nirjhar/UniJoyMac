# Mapping Report: UniJoyMac

## Input analysis (`ub.avrolayout`)

- The file is XML-like but **not strict XML** for generic parsers because it uses numeric tag names like `<1_Normal>...</1_Normal>`.
- Top-level structure includes metadata and embedded base64 images:
  - `<Layout>`, `<AvroKeyboardVersion>`, `<LayoutName>`, developer fields
  - `<ImageNormalShift>` and `<ImageAltGrShift>` (base64 JPEG data)
  - `<KeyData>` containing the actual keyboard map
- Static key mappings are stored as tags in this form:
  - `<KEY_Normal>...`
  - `<KEY_Shift>...`
  - `<KEY_AltGr>...`
  - `<KEY_ShiftAltGr>...`

## What was mapped

- Parsed 47 physical keys from `KeyData`:
  - letters `A-Z`
  - digits `0-9`
  - punctuation/OEM keys (`OEM1..OEM7`, `MINUS`, `PLUS`, `COMMA`, `PERIOD`, `OEM2`)
- Converted Avro layers to macOS keylayout layers:
  - `Normal` -> no modifier
  - `Shift` -> Shift
  - `AltGr` -> Option
  - `ShiftAltGr` -> Option+Shift
- Preserved Avro Unicode code points exactly (no normalization rewrite), so letters like `ড়`, `ঢ়`, `য়` stay in their source form.
- Added a virama state-machine (`্`) in the generated `.keylayout` actions/terminators to improve UniJoy-style conjunct and vowel behavior.

Coverage summary from source `KeyData`:

- Normal: 47/47 non-empty
- Shift: 47/47 non-empty
- Option (AltGr): 6/47 non-empty
- Option+Shift (ShiftAltGr): 5/47 non-empty

## Representative mappings

- `q` -> `ং`, `Shift+q` -> `ঙ`
- `f` -> `া`, `Shift+f` -> `অ`, `Option+f` -> `আ`
- `a` -> `ৃ`, `Shift+a` -> `র্`, `Option+a` -> `ঋ`
- `x` -> `ো`, `Shift+x` -> `ৌ`, `Option+x` -> `ও`, `Option+Shift+x` -> `ঔ`
- `c` -> `ে`, `Shift+c` -> `ৈ`, `Option+c` -> `এ`, `Option+Shift+c` -> `ঐ`

## Assumptions and limitations

- Assumed ANSI US physical scan-code mapping for macOS key codes.
- For Option and Option+Shift keys where Avro provides empty values, the output is set to empty string in `.keylayout`.
- Avro phonetic/dynamic composition logic (if any) is not transferable to `.keylayout`; this output is a static positional layout.
- Numpad-specific mappings (`Num1`, `Num2`, etc.) are listed in source but not mapped in this conversion because the requested scope was main layers on standard keys.
