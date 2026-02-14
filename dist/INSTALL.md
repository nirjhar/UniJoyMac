# UniJoyMac (macOS) Install Guide

This package contains:

- `UniJoyMac.bundle` (recommended)
- `UniJoyMac.keylayout` (raw XML layout)
- `UniJoyMac.icns` (bundle icon)
- `verify.sh` (post-install verification)

## User install (current user)

```bash
mkdir -p "$HOME/Library/Keyboard Layouts"
cp -R "dist/UniJoyMac.bundle" "$HOME/Library/Keyboard Layouts/"
touch "$HOME/Library/Keyboard Layouts"
```

Then:

1. Open **System Settings -> Keyboard -> Input Sources**
2. Click **+**
3. Look under **Others**
4. Add **UniJoyMac**

## System-wide install (all users)

```bash
sudo mkdir -p "/Library/Keyboard Layouts"
sudo cp -R "dist/UniJoyMac.bundle" "/Library/Keyboard Layouts/"
sudo touch "/Library/Keyboard Layouts"
```

## Verify installation

User scope:

```bash
bash "dist/verify.sh"
```

System scope:

```bash
bash "dist/verify.sh" --system
```

If the layout does not appear, log out and log back in.

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
