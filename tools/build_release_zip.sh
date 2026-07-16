#!/usr/bin/env bash
# Собирает релизный архив models_v<version>.zip из папки assets/ и кладёт
# рядом assets-manifest.json (формат, который читает ascendancy-remake).
#
# Внутри архива всё лежит под префиксом models/ - этого требует
# AssetDownloader в ascendancy-remake (записи без префикса он игнорирует).
#
# Использование:
#   tools/build_release_zip.sh [version] [out_dir]
#   version - по умолчанию содержимое файла VERSION
#   out_dir - по умолчанию build/
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-$(tr -d '[:space:]' < "$REPO_ROOT/VERSION")}"
OUT_DIR="${2:-$REPO_ROOT/build}"
SRC="$REPO_ROOT/assets"

if [ ! -d "$SRC" ]; then
    echo "Папка assets/ не найдена - сначала запустите tools/sync_assets.sh" >&2
    exit 1
fi
if [ -z "$VERSION" ]; then
    echo "Пустая версия (файл VERSION?)" >&2
    exit 1
fi

ZIP_NAME="models_v${VERSION}.zip"
ZIP_PATH="$OUT_DIR/$ZIP_NAME"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$OUT_DIR" "$STAGE/models"
rsync -a \
    --exclude 'version.txt' \
    --exclude '.DS_Store' \
    --exclude '._*' \
    "$SRC/" "$STAGE/models/"

rm -f "$ZIP_PATH"
(cd "$STAGE" && find models -type f | LC_ALL=C sort | zip -X -q "$ZIP_PATH" -@)

# stat и sha256 различаются на macOS и Linux - поддерживаем оба.
if stat -c%s "$ZIP_PATH" >/dev/null 2>&1; then
    SIZE_BYTES="$(stat -c%s "$ZIP_PATH")"
else
    SIZE_BYTES="$(stat -f%z "$ZIP_PATH")"
fi
if command -v sha256sum >/dev/null 2>&1; then
    SHA256="$(sha256sum "$ZIP_PATH" | cut -d' ' -f1)"
else
    SHA256="$(shasum -a 256 "$ZIP_PATH" | cut -d' ' -f1)"
fi

ARCHIVE_URL="https://github.com/mikeasm48/ascendancy-assets/releases/download/v${VERSION}/${ZIP_NAME}"

cat > "$OUT_DIR/assets-manifest.json" <<EOF
{
  "version":    "${VERSION}",
  "archiveUrl": "${ARCHIVE_URL}",
  "sizeBytes":  ${SIZE_BYTES},
  "sha256":     "${SHA256}"
}
EOF

echo "Архив:    $ZIP_PATH"
echo "Размер:   $SIZE_BYTES байт"
echo "SHA-256:  $SHA256"
echo "Манифест: $OUT_DIR/assets-manifest.json"
