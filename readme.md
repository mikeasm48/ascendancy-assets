# ascendancy-assets

Ассеты игры [ascendancy-remake](https://github.com/mikeasm48/ascendancy-remake):
Asset Bible, пайплайн процедурной генерации моделей и публикация релизов
бандла моделей.

- `docs/asset-bible/` — стиль, рецепты, инструменты генерации
- `assets/` — снимок актуального содержимого бандла (`~/.ascendancy/assets`)
- `VERSION` — semver текущего релиза бандла
- `tools/sync_assets.sh` — синхронизация локального кэша в `assets/`
- `tools/build_release_zip.sh` — локальная сборка релизного архива

Релиз публикуется автоматически: PR с обновлённым `assets/` и бампом
`VERSION` → merge в main → workflow `release-assets.yml` создаёт GitHub
Release `v<VERSION>` с `models_v<VERSION>.zip` и `assets-manifest.json`.
Подробности — в `CLAUDE.md`.
