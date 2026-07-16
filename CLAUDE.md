# ascendancy-assets — контекст проекта

Репозиторий ассетов для игры ascendancy-remake (Java, отдельный репо в
`~/java/`). Здесь: Asset Bible (единый источник правды по визуальному стилю)
и пайплайн процедурной генерации моделей устройств.

## Прямые коммиты в main запрещены

Все изменения — через feature-ветку и Pull Request, без исключений.
Не пушить и не коммитить напрямую в `main`. Это касается и
`tools/release.sh`: бамп `VERSION` идёт через `release/v<version>` +
`gh pr create`, не прямым push (см. «Публикация релизов ассетов»
ниже).

## Ключевые документы — читать перед задачами по генерации

- `docs/asset-bible/02-device-set.md` — архитектура генератора устройств,
  команды запуска, маппинг каталога
- `docs/asset-bible/03-building-set.md` — генератор зданий (BuildingType) и
  орбитальных конструкций (OrbitalCatalog): Humans в 2 стилях
  industrial/scifi + наземный набор core «по умолчанию» + пропсы
- `docs/asset-bible/races/humans.md`, `races/shuffie.md` — стилевые киты рас
  (палитры/геометрия сверены с фактическими GLB игры)
- `docs/asset-bible/refs/devices/README.md` — политика референсов

## Пайплайн генерации устройств (главное)

- Геометрия строится **чистым Python/numpy** в `docs/asset-bible/tools/`:
  `device_meshes.py` (примитивы: revolve, tube, torus, helix_coil, loft),
  `device_recipes_humans.py` + `device_catalog.py` (36 устройств humans с
  поколениями), `device_recipes_core.py` + `device_catalog_core.py`
  (25 устройств core v3 по рефам, БЕЗ поколений и привязки к
  спецификациям — маппинг вручную отдельно; узлы `<Тип>_<Название>`),
  `build_device_sets.py` (bpy-глю: материалы, шейдинг, экспорт).
  Порядок записей каталогов = индекс узла в GLB — НЕ МЕНЯТЬ существующий
  порядок, только добавлять в конец.
- Blender используется ТОЛЬКО для материалов/шейдинга/экспорта. Geometry
  Nodes сознательно не используем: первая GN-версия сломалась о разницу
  раскладки сокетов между Blender 4.2 и 5.1 (`build_device_library.py`
  оставлен как эксперимент). Обращаться к сокетам нод — только по имени+типу,
  никогда по индексам.
- Запуск (Blender 4.2+/5.x, проверено на 5.1):
  `blender -b -P tools/build_device_sets.py -- --races humans,core --assets-dir ~/.ascendancy/assets/races`
- Выход: `<assets>/<race>/devices/device_constructor.glb`;
  extras каждого узла: `device_id`, `display_name`, `tech_level`.
  Папки рас в ассетах: humans, core; раса shuffie в игре лежит в `bionics/`.

## Конвенции рецептов

- Ось Z вверх; «лицо» устройства (сопла, стволы, жерла) смотрит в **+Y**.
- Части тегируются материалами (см. MATS в `build_device_sets.py`):
  свечения — `accent` (оранжевый), `bglow` (синий), `flame`, `redline`.
- Категорийные цвета: двигатели — красные катушки + пламя, star lane — синий,
  генераторы/щиты — цвет поколения (blue→teal→gold→accent→coil по уровням),
  сканеры humans — графит + красные канты, оружие — светящиеся дула.
- Shade smooth + EdgeSplit 42° на всём, КРОМЕ щитов (гекс-сфера гранёная).
- Core-набор: плита-постамент (5 видов: silver/dark/fins/circuit/lattice)
  — отдельный child-меш `<node>_platform`.
- Быстрое превью без Blender: рецепты чистый numpy, рендерится matplotlib
  (см. историю в `renders/preview/approval_*.png` — эталоны вида).

## Референсы

- `docs/asset-bible/refs/devices/`, `refs/buildings/` — ужатые копии
  (≤1024px jpeg q85, GLB заменены `*_preview.png`). Полноразмерные
  оригиналы: `~/java/ascendancy-refs-originals/{devices,buildings}/`
  (вне git). Раскладка refs/devices — по расам: `devices/core/`
  (формат имени `<Тип>_core_<Название>_<версия>`), `devices/humans/`
  (по категориям устройств).

## Публикация релизов ассетов

Источник правды по содержимому — локальная папка `~/.ascendancy/assets`
(туда пишут генераторы). Версия — semver в файле `VERSION`.

**`ascendancy_release/` НЕ трекается git** (см. .gitignore) — рабочая
копия для сборки архива, только на диске локально. Причина: GLB-экспорт
из Blender почти всегда меняется побайтово даже для «того же» ассета
(зашитые таймстемпы/метаданные генератора), поэтому каждый релиз
добавлял бы в git-историю почти полный объём бандла (>100 МБ), а
бинарники (GLB/PNG) уже сжаты и не дельта-сжимаются packfile'ом.
История `.git` за первый же релиз доросла до ~200 МБ (расчищено
`git filter-repo` 2026-07-16). Дублировать эти же байты в git
бессмысленно и опасно для размера репо: они и так навсегда живут как
GitHub Release asset (см. следующий раздел про политику хранения
релизов).

Выпуск релиза — **одна команда, локально**:

```bash
tools/release.sh <version> ["заметки к релизу"]
```

Что она делает (см. `tools/release.sh`), идемпотентно — повторный
запуск с той же версией падает с понятной ошибкой на первом же шаге,
ничего не создавая наполовину:
1. Проверяет, что нет незакоммиченных изменений и что релиза с такой
   версией ещё нет (`gh release view`).
2. `tools/sync_assets.sh` — синхронизирует `~/.ascendancy/assets` →
   `ascendancy_release/` (rsync --delete; `version.txt` и мусор macOS
   исключаются).
3. `tools/build_release_zip.sh` — собирает `models_v<version>.zip`
   (всё под префиксом `models/` — так требует AssetDownloader игры)
   и `assets-manifest.json`.
4. `gh release create` — публикует GitHub Release `v<version>` с
   архивом и манифестом.
5. Бампает `VERSION` в ветке `release/v<version>` (пересоздаётся
   force-push при каждом запуске, чтобы стейл-ветка от отклонённого
   PR не мешала повторному запуску той же версии) и открывает PR —
   `gh pr create`, без прямого push в main.

Версия сравнивается дословно с локальным `version.txt` игрока — не
поднять её значит релиз не подхватится. Semver: patch — фиксы
моделей, minor — новый контент без ломающих изменений, major —
переименования/удаления путей.

После публикации релиза срабатывает `release-assets.yml` (событие
`release: published`) и запускает `update-assets.yml` в
ascendancy-remake: тот скачивает архив, пересчитает sha256/размер (не
доверяет чужому манифесту), обновит
`src/main/resources/assets-manifest.json` и откроет PR. Секрет
`REMAKE_TRIGGER_TOKEN` уже настроен (PAT с правами Actions:write +
Metadata:read только на ascendancy-remake). Итого один запуск
`tools/release.sh` даёт **2 PR** (бамп VERSION в этом репо + манифест
в ascendancy-remake) — оба смержить руками после проверки.

Проверка идемпотентности: отклонить оба PR и удалить релиз
(`gh release delete v<version> --repo mikeasm48/ascendancy-assets
--cleanup-tag --yes`) → повторный `tools/release.sh <version>`
должен пройти чисто с нуля.

Ручной запуск, если автотриггер не сработал (`--ref main` обязателен
— без него `gh workflow run` пытается определить default branch через
GraphQL, а токену намеренно не даны права на это):
`gh workflow run update-assets.yml -R mikeasm48/ascendancy-remake --ref main -f version=<VERSION>`

### Политика хранения GitHub Releases

Релизы **не удаляются**. `archiveUrl` в манифесте remake — прямая
ссылка на конкретный тег; если у игрока старый `.jar` с манифестом на
`v1.0.0`, удаление этого релиза сломает ему скачивание насовсем.
Лимиты GitHub (2 ГБ на файл, без официального лимита на число
релизов/общий объём) далеко не проблема при текущих размерах бандла.
Удалять можно только явно мусорные/тестовые релизы, если точно
известно, что ни один манифест remake на них не ссылается.

## Не коммитить

- `blends/`, `*.blend` — артефакты сборки (в .gitignore)
- `build/` — локальная сборка релизного архива (в .gitignore)
- `ascendancy_release/` — снимок `~/.ascendancy/assets` для сборки
  релиза (в .gitignore); контент живёт только как GitHub Release
  asset, не в git-истории (см. «Публикация релизов ассетов» выше)

## Состояние и следующие задачи (на 2026-07-11)

- [x] Набор устройств humans: 36 корабельных, сгенерированы и согласованы
  (эталон: `renders/preview/approval_humans_v14.png` — плюс более поздние
  правки оружия/aux в рецептах)
- [x] Набор устройств core v3: 25 моделей строго по обновлённым рефам
  refs/devices/core (стилизация под иконки Ascendancy 1995, «прибор на
  плите-постаменте»), БЕЗ поколений и привязки к спецификациям (маппинг
  вручную отдельным PR) -> core/devices/device_constructor.glb (50 узлов:
  25 устройств `<Тип>_<Название>` + 25 плит `<node>_platform`, ~4.2MB;
  лист approval_devices_core_v3.png). Прежний core-набор v2 (36 устройств
  по device_catalog) признан неудачным и заменён
- [x] Здания + орбитальные конструкции Humans: 14 планетарных (BuildingType)
  + 15 орбитальных (OrbitalCatalog) + 6 пропсов, каждый в 2 стилях
  (industrial/scifi, не смешивать!) -> building_constructor_<style>.glb;
  контрольные листы renders/preview/approval_buildings_humans_*_v1.png.
  Старый временный buildings/building_constructor.glb для Humans больше
  не используется - его модели переедут к другой расе
- [x] Здания Shuffie: объединённый набор v2 (текущий сет bionics +
  бионический city-set экс-Humans + орбитальные док/щит из
  refs/buildings/Shuffie), гармонизирован с флотом ->
  bionics/buildings/building_constructor_v2.glb (68 узлов, <=10MB,
  весь орбитальный ряд: 4 дока/3 щита/8 орудий из корабельных турелей;
  tools/build_shuffie_building_set.py, лист approval_buildings_shuffie_v2.png)
- [x] Здания Core (набор «по умолчанию» для рас без своих китов, по
  refs/buildings/core): 14 BuildingType + 4 спецпозиции (Engineering
  Retreat, Surface Shield/Megashield, Alien Ruins) + 15 орбитальных
  (OrbitalCatalog, как у Humans) + 6 пропсов; наземные — «диорама на
  плите», орбитальные без плит -> core/buildings/building_constructor.glb
  (39 узлов, ~3.7MB; tools/building_recipes_core.py +
  building_catalog_core.py, сборка/превью общими скриптами со стилем core;
  лист approval_buildings_core_v1.png)
- [x] Набор устройств Shuffie: 36 устройств из частей конструктора
  кораблей (tools/build_bionics_device_set.py -> bionics/devices/
  device_constructor.glb; оружие = те же турели, что в орбитальном ряду
  зданий; поколения - размер + категорийный тинт baseColorFactor;
  лист approval_devices_bionics_v1.png)
- [ ] Интеграция device_constructor.glb в игру (адресация по индексу или
  extras.device_id)
- [ ] Интеграция building_constructor_<style>.glb в игру: на BuildingType -
  комбинация "доминанта + несколько PROP_*" (пропсы отдельными узлами)
