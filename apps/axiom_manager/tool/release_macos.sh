#!/usr/bin/env bash
set -euo pipefail

MODE="unsigned"
BUILD_NAME="1.0.0"
BUILD_NUMBER="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --build-name)
      BUILD_NAME="$2"
      shift 2
      ;;
    --build-number)
      BUILD_NUMBER="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ "$MODE" != "unsigned" && "$MODE" != "signed" ]]; then
  echo "Invalid mode: $MODE (allowed: unsigned|signed)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RELEASE_DIR="$PROJECT_ROOT/dist/macos/$MODE"
BUNDLE_DIR="$RELEASE_DIR/axiom-manager-macos-$MODE"

echo "[1/4] flutter pub get"
(
  cd "$PROJECT_ROOT"
  flutter pub get
)

echo "[2/4] build macos release"
(
  cd "$PROJECT_ROOT"
  flutter build macos --release --build-name "$BUILD_NAME" --build-number "$BUILD_NUMBER"
)

SOURCE_DIR="$PROJECT_ROOT/build/macos/Build/Products/Release"
APP_PATH="$(find "$SOURCE_DIR" -maxdepth 1 -type d -name "*.app" | head -n 1 || true)"
if [[ -z "$APP_PATH" ]]; then
  echo "Build output not found in $SOURCE_DIR"
  exit 1
fi

echo "[3/4] prepare dist directory"
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
cp -R "$APP_PATH" "$BUNDLE_DIR/"

if [[ "$MODE" == "signed" ]]; then
  echo "[WARN] signed 模式需要你自行在此脚本接入 codesign/notarytool。当前仅完成构建与打包。"
fi

APP_NAME="$(basename "$APP_PATH")"
ZIP_PATH="$RELEASE_DIR/axiom-manager-macos-$MODE.zip"

echo "[4/4] create zip"
mkdir -p "$RELEASE_DIR"
rm -f "$ZIP_PATH"
(
  cd "$BUNDLE_DIR"
  ditto -c -k --sequesterRsrc --keepParent "$APP_NAME" "$ZIP_PATH"
)

echo "Done"
echo "Bundle: $BUNDLE_DIR/$APP_NAME"
echo "Zip:    $ZIP_PATH"
