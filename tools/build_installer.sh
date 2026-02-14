#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
LAYOUT_NAME="UniJoyMac"
BUNDLE_NAME="${LAYOUT_NAME}.bundle"
INPUT_BUNDLE="$DIST_DIR/$BUNDLE_NAME"
PKG_ID="pro.lonesock.keyboard.unijoymac.installer"
PKG_VERSION="1.0.0"
OUTPUT_PKG="$DIST_DIR/${LAYOUT_NAME}-Installer.pkg"
SIGNED_PKG="$DIST_DIR/${LAYOUT_NAME}-Installer-signed.pkg"
SIGN_IDENTITY="${UNIJOYMAC_SIGN_IDENTITY:-}"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/unijoymac-pkg.XXXXXX")"
PKG_ROOT="$WORK_DIR/root"
SCRIPTS_DIR="$ROOT_DIR/packaging/scripts"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if [[ ! -d "$INPUT_BUNDLE" ]]; then
  echo "ERROR: Missing bundle: $INPUT_BUNDLE"
  echo "Build or copy the bundle into dist/ first."
  exit 1
fi

if ! command -v pkgbuild >/dev/null 2>&1; then
  echo "ERROR: pkgbuild is not available. Install Xcode Command Line Tools."
  exit 1
fi

if [[ -n "$SIGN_IDENTITY" ]] && ! command -v productsign >/dev/null 2>&1; then
  echo "ERROR: productsign is not available but signing was requested."
  exit 1
fi

if [[ ! -d "$SCRIPTS_DIR" ]]; then
  echo "ERROR: Missing installer scripts directory: $SCRIPTS_DIR"
  exit 1
fi

mkdir -p "$PKG_ROOT/Library/Keyboard Layouts"
COPYFILE_DISABLE=1 /usr/bin/ditto --norsrc "$INPUT_BUNDLE" "$PKG_ROOT/Library/Keyboard Layouts/$BUNDLE_NAME"
/usr/bin/xattr -cr "$PKG_ROOT" >/dev/null 2>&1 || true
/usr/bin/dot_clean -m "$PKG_ROOT" >/dev/null 2>&1 || true

pkgbuild \
  --root "$PKG_ROOT" \
  --scripts "$SCRIPTS_DIR" \
  --identifier "$PKG_ID" \
  --version "$PKG_VERSION" \
  "$OUTPUT_PKG"

echo "Built installer: $OUTPUT_PKG"
echo "This package works on both Apple Silicon and Intel Macs (data-only keyboard bundle)."

if [[ -n "$SIGN_IDENTITY" ]]; then
  productsign \
    --sign "$SIGN_IDENTITY" \
    "$OUTPUT_PKG" \
    "$SIGNED_PKG"
  mv "$SIGNED_PKG" "$OUTPUT_PKG"
  echo "Signed installer with identity: $SIGN_IDENTITY"
  pkgutil --check-signature "$OUTPUT_PKG" || true
else
  echo "Unsigned package (set UNIJOYMAC_SIGN_IDENTITY to sign)."
fi
