#!/usr/bin/env bash
# Полный локальный релиз ассетов: sync -> build zip -> publish GitHub
# Release -> PR с бампом VERSION.
#
# Единственная команда, которую нужно запустить для релиза:
#   tools/release.sh <version> ["notes"]
#
# Идемпотентно: повторный запуск с той же версией падает с понятной
# ошибкой (релиз уже существует). После reject PR-а и удаления релиза
# (gh release delete v<version> --cleanup-tag) можно запускать заново
# с тем же именем версии - ветка релиза каждый раз пересоздаётся
# заново (force-push), а не переиспользуется, так что стейл-ветка от
# отклонённого PR этому не мешает.
#
# ascendancy_release/ (рабочая копия ~/.ascendancy/assets для сборки
# архива) НЕ трекается git - см. .gitignore и CLAUDE.md.
#
# Требует: gh (авторизован), zip, rsync.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:?Использование: tools/release.sh <version> [notes]}"
NOTES="${2:-Бандл моделей v${VERSION}.}"
REPO="mikeasm48/ascendancy-assets"
TAG="v${VERSION}"
BRANCH="release/v${VERSION}"

if git -C "$REPO_ROOT" status --porcelain --untracked-files=no | grep -q .; then
    echo "В репозитории есть незакоммиченные изменения отслеживаемых файлов - закоммитьте или отложите их перед релизом." >&2
    git -C "$REPO_ROOT" status --short >&2
    exit 1
fi

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    echo "Релиз ${TAG} уже существует - поднимите версию, либо удалите его:" >&2
    echo "  gh release delete ${TAG} --repo ${REPO} --cleanup-tag --yes" >&2
    exit 1
fi

echo "==> Синхронизация ~/.ascendancy/assets -> ascendancy_release/"
"$REPO_ROOT/tools/sync_assets.sh"

echo "==> Сборка архива"
"$REPO_ROOT/tools/build_release_zip.sh" "$VERSION" "$REPO_ROOT/build"

echo "==> Публикация GitHub Release ${TAG}"
gh release create "$TAG" \
    "$REPO_ROOT/build/models_v${VERSION}.zip" \
    "$REPO_ROOT/build/assets-manifest.json" \
    --repo "$REPO" \
    --title "Assets ${VERSION}" \
    --notes "$NOTES"

echo "==> PR с бампом VERSION"
git -C "$REPO_ROOT" fetch origin main
# Ветка релиза пересоздаётся заново при каждом запуске (force), а не
# переиспользуется - иначе повторный прогон после reject-нутого PR
# наткнулся бы на стейл-ветку с чужой историей.
git -C "$REPO_ROOT" push origin --delete "$BRANCH" 2>/dev/null || true
git -C "$REPO_ROOT" checkout -B "$BRANCH" origin/main
echo "$VERSION" > "$REPO_ROOT/VERSION"
git -C "$REPO_ROOT" add VERSION
git -C "$REPO_ROOT" commit -m "Release assets v${VERSION}"
git -C "$REPO_ROOT" push --force -u origin "$BRANCH"
gh pr create --repo "$REPO" \
    --title "Release assets v${VERSION}" \
    --body "Публикует релиз [${TAG}](https://github.com/${REPO}/releases/tag/${TAG})." \
    --base main --head "$BRANCH"
git -C "$REPO_ROOT" checkout main

echo
echo "Готово: релиз ${TAG} опубликован, PR с бампом VERSION открыт."
echo "GitHub Actions (событие release: published) сам должен открыть PR в ascendancy-remake."
