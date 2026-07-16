#!/usr/bin/env bash
# Полный локальный релиз ассетов: sync -> build zip -> publish GitHub
# Release -> bump VERSION в git.
#
# Раньше архив собирался и релиз публиковался в CI из git-трекнутой
# assets/, но это раздувало историю репозитория на полный объём бандла
# (>100 МБ) на каждый релиз. Теперь assets/ игнорируется git (см.
# .gitignore) - в репозиторий коммитится только текстовый VERSION,
# а сам бандл живёт исключительно как GitHub Release asset.
#
# Использование:
#   tools/release.sh <version> ["notes"]
#
# Требует: gh (авторизован), zip, rsync.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:?Использование: tools/release.sh <version> [notes]}"
NOTES="${2:-Бандл моделей v${VERSION}.}"
REPO="mikeasm48/ascendancy-assets"

if git -C "$REPO_ROOT" status --porcelain | grep -qv '^??'; then
    echo "В репозитории есть незакоммиченные изменения (кроме assets/, он игнорируется) - закоммитьте или отложите их перед релизом." >&2
    git -C "$REPO_ROOT" status --short >&2
    exit 1
fi

if gh release view "v${VERSION}" --repo "$REPO" >/dev/null 2>&1; then
    echo "Релиз v${VERSION} уже существует - поднимите версию." >&2
    exit 1
fi

echo "==> Синхронизация ~/.ascendancy/assets -> assets/"
"$REPO_ROOT/tools/sync_assets.sh"

echo "==> Сборка архива"
"$REPO_ROOT/tools/build_release_zip.sh" "$VERSION" "$REPO_ROOT/build"

echo "==> Публикация GitHub Release v${VERSION}"
gh release create "v${VERSION}" \
    "$REPO_ROOT/build/models_v${VERSION}.zip" \
    "$REPO_ROOT/build/assets-manifest.json" \
    --repo "$REPO" \
    --title "Assets ${VERSION}" \
    --notes "$NOTES"

echo "==> Бамп VERSION и коммит"
echo "$VERSION" > "$REPO_ROOT/VERSION"
git -C "$REPO_ROOT" add VERSION
git -C "$REPO_ROOT" commit -m "Release assets v${VERSION}"
git -C "$REPO_ROOT" push origin main

echo
echo "Готово: релиз v${VERSION} опубликован, VERSION закоммичен и запушен."
echo "GitHub Actions (release: published) должен сам подтянуть update-assets.yml в ascendancy-remake."
