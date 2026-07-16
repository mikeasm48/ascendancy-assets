# ascendancy-assets

Ассеты игры [ascendancy-remake](https://github.com/mikeasm48/ascendancy-remake):
Asset Bible, пайплайн процедурной генерации моделей и публикация релизов
бандла моделей.

- `docs/asset-bible/` — стиль, рецепты, инструменты генерации
- `VERSION` — semver текущего релиза бандла
- `tools/release.sh` — полный локальный релиз (sync + build + publish + PR с бампом VERSION)
- `tools/sync_assets.sh` — синхронизация `~/.ascendancy/assets` → `ascendancy_release/`
- `tools/build_release_zip.sh` — локальная сборка релизного архива

Содержимое бандла (`ascendancy_release/`) не хранится в git-истории —
только как GitHub Release asset (иначе история распухала бы на полный
объём бандла с каждым релизом). Релиз: `tools/release.sh <version>` —
публикует Release и открывает PR с бампом VERSION здесь, а дальше
GitHub Actions сам открывает второй PR в ascendancy-remake. Подробности
— в `CLAUDE.md`.
