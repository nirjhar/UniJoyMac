# UniJoyMac (macOS) Install Guide

This package contains:

- `UniJoyMac.bundle` (recommended)
- `UniJoyMac-Installer.pkg` (recommended if available)
- `UniJoyMac.keylayout` (raw XML layout)
- `UniJoyMac.icns` (bundle icon)
- `verify.sh` (post-install verification)

## Recommended install via `.pkg`

If `UniJoyMac-Installer.pkg` is present:

```bash
open "dist/UniJoyMac-Installer.pkg"
```

The installer installs to `/Library/Keyboard Layouts/`, refreshes keyboard layout discovery, prompts you to log out, and initiates logout when you confirm.

To build a signed package before sharing:

```bash
UNIJOYMAC_SIGN_IDENTITY="Developer ID Installer: YOUR NAME (TEAMID)" bash "tools/build_installer.sh"
```

Then:

1. Open **System Settings -> Keyboard -> Input Sources**
2. Click **+**
3. Look under **Others**
4. Add **UniJoyMac**

## Verify installation

User scope:

```bash
bash "dist/verify.sh"
```

System scope:

```bash
bash "dist/verify.sh" --system
```

If you chose **Later** in the installer prompt, log out and back in before adding the layout.

If it still does not appear, run the installer again and choose **Log Out Now** when prompted.

## Manual test checklist (TextEdit)

Switch input to **UniJoyMac** and test:

1. `q` -> `ং`
2. `Q` -> `ঙ`
3. `f` -> `া`
4. `Shift+g` -> `।`
5. `1` -> `১`
6. `Shift+2` -> `ঁ`
7. `Option+a` -> `ঋ`
8. `Option+x` -> `ও`
9. `Option+Shift+s` -> `ঊ`
10. `Option+Shift+c` -> `ঐ`

## Notes

- This is a positional conversion from Avro static key maps.
- Dynamic phonetic composition rules are not implemented in macOS `.keylayout` (not supported natively).
