#!/usr/bin/env bash
# Синхронизирует живой кэш ассетов (~/.ascendancy/assets) в папку assets/
# репозитория. Запускать перед подготовкой релизного PR:
#
#   tools/sync_assets.sh
#   git status            # посмотреть, что изменилось
#
# version.txt намеренно исключён: его пишет AssetDownloader игры после
# распаковки, содержимым бандла он не является.
set -euo pipefail

SRC="${ASCENDANCY_ASSETS_DIR:-$HOME/.ascendancy/assets}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DST="$REPO_ROOT/assets"

if [ ! -d "$SRC" ]; then
    echo "Источник не найден: $SRC" >&2
    exit 1
fi

mkdir -p "$DST"
rsync -a --delete \
    --exclude 'version.txt' \
    --exclude '.DS_Store' \
    --exclude '._*' \
    "$SRC/" "$DST/"

echo "Синхронизировано: $SRC -> $DST"
echo "Файлов: $(find "$DST" -type f | wc -l | tr -d ' ')"
