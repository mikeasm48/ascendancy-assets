# ascendancy-assets — контекст проекта

Репозиторий ассетов для игры ascendancy-remake (Java, отдельный репо в
`~/java/`). Здесь: Asset Bible (единый источник правды по визуальному стилю)
и пайплайн процедурной генерации моделей устройств.

## Ключевые документы — читать перед задачами по генерации

- `docs/asset-bible/02-device-set.md` — архитектура генератора устройств,
  команды запуска, маппинг каталога
- `docs/asset-bible/03-building-set.md` — генератор зданий (BuildingType) и
  орбитальных конструкций (OrbitalCatalog): 2 стиля industrial/scifi + пропсы
- `docs/asset-bible/races/humans.md`, `races/shuffie.md` — стилевые киты рас
  (палитры/геометрия сверены с фактическими GLB игры)
- `docs/asset-bible/refs/devices/README.md` — политика референсов

## Пайплайн генерации устройств (главное)

- Геометрия строится **чистым Python/numpy** в `docs/asset-bible/tools/`:
  `device_meshes.py` (примитивы: revolve, tube, torus, helix_coil, loft),
  `device_recipes_humans.py`, `device_recipes_core.py` (рецепты 36 устройств),
  `device_catalog.py` (порядок = индекс узла в GLB — НЕ МЕНЯТЬ существующий
  порядок, только добавлять в конец), `build_device_sets.py` (bpy-глю:
  материалы, шейдинг, экспорт).
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
- Core-набор: платформа-постамент — отдельный child-меш `<id>_platform`.
- Быстрое превью без Blender: рецепты чистый numpy, рендерится matplotlib
  (см. историю в `renders/preview/approval_*.png` — эталоны вида).

## Референсы

- `docs/asset-bible/refs/devices/`, `refs/buildings/` — ужатые копии
  (≤1024px, GLB заменены `*_preview.png`). Полноразмерные оригиналы:
  `~/java/ascendancy-refs-originals/{devices,buildings}/` (вне git).
  Скриншоты `*_core*.png` — оригиналы Ascendancy 1995, не трогать.

## Не коммитить

- `blends/`, `*.blend` — артефакты сборки (в .gitignore)
- сгенерированные GLB уходят в `~/.ascendancy/assets/` (вне репо)

## Состояние и следующие задачи (на 2026-07-11)

- [x] Наборы устройств humans + core: 36 корабельных, сгенерированы и
  согласованы (эталоны: `renders/preview/approval_humans_v14.png` — плюс
  более поздние правки оружия/aux в рецептах, `approval_core_v4.png`)
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
- [ ] Набор устройств для расы Shuffie (папка ассетов — `bionics/`;
  стиль: races/shuffie.md — белый «фарфор», непрерывная кривизна, акцент
  только в углублениях)
- [ ] Интеграция device_constructor.glb в игру (адресация по индексу или
  extras.device_id)
- [ ] Интеграция building_constructor_<style>.glb в игру: на BuildingType -
  комбинация "доминанта + несколько PROP_*" (пропсы отдельными узлами)
