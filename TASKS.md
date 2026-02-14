# TASKS

This file tracks practical maintenance/debug tasks for `UniJoyMac`.

## Current status

- [x] Convert `ub.avrolayout` to macOS `.keylayout`
- [x] Build distributable bundle `dist/UniJoyMac.bundle`
- [x] Build distributable installer `dist/UniJoyMac-Installer.pkg`
- [x] Include icon and `Info.plist`
- [x] Add install guide (`dist/INSTALL.md`)
- [x] Add verification script (`dist/verify.sh`)
- [x] Add mapping report (`dist/mapping_report.md`)
- [x] Add installer logout prompt + automatic logout initiation
- [x] Harden installer refresh path (xattr cleanup + restart/logout choice)
- [x] Add `.gitignore` and utility install/cleanup scripts
- [x] Publish repo as `UniJoyMac`
- [x] Add virama state machine for conjunct/independent vowel behavior
- [x] Add Command key passthrough layers (Cmd+C/V/X etc. emit US QWERTY)
- [x] Fix duplicate Input Sources entries (bundle-only install, remove standalone files)
- [x] Fix invalid XML character U+007F that caused layout to be rejected by macOS
- [x] Fix `KLInfo_0` → `KLInfo_UniJoyMac` in Info.plist so macOS 26 (Tahoe) discovers the bundle

## High-priority maintenance

- [ ] Add a small script to dump all mapped keys by layer from `dist/UniJoyMac.keylayout`
  - Why: faster visual diff/debug when user reports key mismatch
  - Suggested path: `tools/dump_keylayout_table.py`

- [ ] Add a deterministic regression test for converter output
  - Why: ensure future parser edits do not break mappings
  - Suggested approach:
    - regenerate to a temp file
    - assert key samples for all 4 layers
    - assert key count per keyMap is stable

- [ ] Ensure executable bits are intentional in repo
  - Verify `ub.avrolayout` mode (currently executable in git history) and normalize if needed

## Functional improvements

- [ ] Optional: include numpad mapping support in generated `.keylayout`
  - Source has `Num0..Num9` and arithmetic symbols
  - Needs explicit decision on macOS numpad key codes and layer behavior

- [ ] Optional: expose keyboard id/group via CLI defaults or config file
  - Current defaults: `keyboard id=-28676`, `group=126`

- [ ] Optional: add bundle build script for one-command release build
  - Suggested path: `tools/build_dist.sh`
  - Include: convert -> icon -> bundle copy -> lint -> verify

## Packaging/release tasks

- [ ] Create GitHub release (e.g. `v1.0.0`) with attached deliverables
  - Attach at minimum:
    - `dist/UniJoyMac-Installer.pkg`
    - `dist/UniJoyMac.bundle`
    - `dist/UniJoyMac.keylayout`
    - `dist/INSTALL.md`

- [ ] Add release notes template
  - Include compatibility notes and known limitation (no phonetic composition)

## Debug checklist when user reports issues

- [ ] Run:
  - `bash "dist/verify.sh"`
- [ ] Re-copy bundle resources from `dist/` if stale
- [ ] Rebuild and rerun `dist/UniJoyMac-Installer.pkg`
- [ ] Restart macOS (preferred) and check Input Sources -> Others and Bengali
- [ ] Validate failing key directly in `dist/UniJoyMac.keylayout`

## Nice-to-have documentation

- [ ] Add screenshots to README for Input Sources setup
- [ ] Add a compact “Top 20 key mappings” table to README
- [x] Add troubleshooting guidance for Sonoma/Sequoia cache behavior differences
