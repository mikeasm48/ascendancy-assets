# 03 — Набор зданий: планетарные строения и орбитальные конструкции (Humans, Core)

Источники списков (ascendancy-remake):

- планетарные здания — enum `BuildingType`
  (`src/main/java/com/ascendancy/model/colony/BuildingType.java`), 14 шт.;
- орбитальные конструкции — `OrbitalCatalog`
  (`.../model/colony/OrbitalCatalog.java`), 15 шт. (4 дока, 3 щита,
  3 лазера, 3 фазера, 2 скорострельных фазера).

Референсы — `refs/buildings/humans/`. Примеры там двух видов, поэтому
каждая позиция генерируется в **двух несмешиваемых стилевых вариантах**:

- **industrial** — брутальный индустриальный (рефы Factory_1, ColonyBase_1,
  Laboratory_1, Farm_1, орбитальные SpaceDock/OrbitalLaser/OrbitalPhaser):
  серый бетон и сталь, ступенчатые башни-зиккураты, трубы с ржавыми
  поясами, решётчатые фермы, конвейерные мосты, бирюзовые экраны
  (`screen`), оранжевые техно-свечения (`accent`), красные габаритные
  огни (`redline`).
- **scifi** — футуристическое техно (рефы PowerPlant_1/2, Metroplex_1,
  SkyNet_1, EcoBooster_1, ResearchCampus_1, ArtificalHidroponifier_1,
  OrbitalPhaserRapid_1): белый металл и стекло, шпили, торы-кольца,
  купола, чаши-канопе, арочные пилоны; свечения синие (`bglow`), зелёные
  био (`gglow`), фиолетовые у орбитальных фазеров (`pglow`).

Стили не смешиваются внутри одной модели; игра берёт набор целиком.

## Пропсы-расширители

Кроме доминант в каждом наборе есть 6 мелких групп-пропсов (аналог
"Random blocks 1/2" старого city-set): `PROP_BLOCKS_1/2` (хаотичные
контейнеры), `PROP_TANKS`, `PROP_PIPES`, `PROP_MAST`, `PROP_PAD`.
Средствами ascendancy-remake каждый `BuildingType` собирается как
комбинация «одна узнаваемая доминанта + несколько пропсов» — так модель
визуально занимает площадь. Пропсы — отдельные узлы GLB, заранее в
доминанты не вкомбинированы.

## Архитектура генерации

Та же схема, что у устройств (`02-device-set.md`): геометрия — чистый
Python/numpy, Blender только материалы/шейдинг/экспорт.

| Файл | Роль |
|---|---|
| `tools/building_meshes.py` | помощники поверх `device_meshes.py`: frustum, loft_z, hbarrel (свод-теплица), cooling_tower, lattice_mast, geodome, dish_mesh, chimney, box_ring, spire, octahedron, scatter_boxes |
| `tools/building_recipes_humans_industrial.py` | 35 рецептов industrial |
| `tools/building_recipes_humans_scifi.py` | 35 рецептов scifi (тот же интерфейс) |
| `tools/building_catalog.py` | каталог `RECIPES`: id → рецепт/уровень/kind; **порядок = индекс узла в GLB, не менять** |
| `tools/build_building_sets.py` | bpy-глю: меши → материалы `MAT_bld_*` → EdgeSplit 42° → GLB |
| `tools/preview_buildings.py` | контрольный лист без Blender (numpy+matplotlib) |

Конвенции: земля z=0, здания растут в +Z; орбитальные конструкции —
центр ~z=1, «рабочее» направление орудий +Y (как у устройств). Габарит
доминанты ≤ ~3.5 юнита, пропсы ≤ ~1.3.

## Запуск

```bash
# Оба стиля
blender -b -P tools/build_building_sets.py -- \
    --styles industrial,scifi --assets-dir ~/.ascendancy/assets/races

# Быстрое превью без Blender (venv с numpy+matplotlib)
python tools/preview_buildings.py --style industrial
python tools/preview_buildings.py --style scifi
```

Выход (старый временный `building_constructor.glb` не перезаписывается —
его модели переедут к другой расе):

```
~/.ascendancy/assets/races/humans/buildings/building_constructor_industrial.glb
~/.ascendancy/assets/races/humans/buildings/building_constructor_scifi.glb
```

По 35 узлов в файле: 14 зданий + 15 орбиталей + 6 пропсов. Каждый узел
несёт glTF-`extras`: `building_id` (= имя константы BuildingType /
OrbitalCatalog, у пропсов `PROP_*`), `display_name`, `style`, `kind`
(`building`/`orbital`/`prop`), `level`. Адресация из игры — по
`building_id` или индексу (порядок фиксирован каталогом).

## Контрольные листы

- `renders/preview/approval_buildings_humans_industrial_v1.png`
- `renders/preview/approval_buildings_humans_scifi_v1.png`

## Материалы

Палитра `MAT_bld_*` (см. таблицу в `races/humans.md` §3): у industrial
бетон `#9AA0A6` + сталь + ржавые пояса, у scifi белый металл `#E2E6E9` +
серебро; стекло — blend с alpha 0.45/0.55, свечения — emission 1.5–4.
Shade smooth + EdgeSplit 42° на всех узлах.

## Core: наземный набор «по умолчанию»

Core — не раса, а набор для рас без собственных китов зданий. Референсы —
`refs/buildings/core/` (формат имени `<строение>_core[_<вариант>]`).

Стиль наземных: диорама на плите-основании (белый борт + газон или
техпокрытие), белый и серебристый металл, стеклянные купола и теплицы,
цветные трубы (`gold`/`teal`), серебристые чаны, красно-белые полосатые
дымовые трубы, солнечные панели (`solar`), свечения `accent`/`bglow`/
`gglow`. Орбитальные — без плит, центр ~z=1, орудия смотрят в +Y.

Состав (`tools/building_catalog_core.py`, порядок = индекс узла в GLB):

- 14 планетарных `BuildingType`; display_name — имена оригинальной
  Ascendancy 1995, где они отличаются (Agriplot, Industrial Megafacility,
  Hyperpower Plant, Lush Growth Bomb). SKY_NET и TERRAFORMING рефов не
  имеют — спроектированы в стиле набора.
- 4 наземных спецпозиции по рефам, пока вне `BuildingType`:
  ENGINEERING_RETREAT, SURFACE_SHIELD, SURFACE_MEGA_SHIELD, ALIEN_RUINS.
- 15 орбитальных конструкций `OrbitalCatalog` (те же id, что у Humans):
  доки — серые многоярусные эстакады с солнечным настилом и жёлтыми
  цистернами (рефы OrbitalDocks/OrbitalShipyard), щиты — зелёные платформы
  с парой геокуполов-клеток и синими ядрами (OrbitalShield_1..3), лазер —
  модульная платформа с фиолетовой линзой (OrbitalLaser, левый вариант),
  фазер — с плазменными трубами и роторным дулом (правый вариант),
  скорострельный — кассеты красных ракет с золотыми БЧ
  (OrbitalMissileBase).
- 6 пропсов-расширителей (те же id, что у Humans).

Файлы: `tools/building_recipes_core.py` (рецепты),
`tools/building_catalog_core.py` (каталог); сборка и превью — общими
`build_building_sets.py` / `preview_buildings.py` со стилем `core`:

```bash
blender -b -P tools/build_building_sets.py -- \
    --styles core --assets-dir ~/.ascendancy/assets/races
python tools/preview_buildings.py --style core
```

Выход: `~/.ascendancy/assets/races/core/buildings/building_constructor.glb`
(39 узлов, ~3.7MB; те же extras, kind=`building`/`orbital`/`prop`).
Контрольный лист — `renders/preview/approval_buildings_core_v1.png`.
Палитра — блок «дополнения набора core» в MATS `build_building_sets.py`.
Раскладка сетки в .blend начинается от начала координат (смещение +60 по Y
добавляется только следующим стилям при сборке нескольких за раз).

## Shuffie: объединённый набор v2

Для Shuffie здания НЕ генерируются процедурно — собираются из готовых
city-set'ов скриптом `tools/build_shuffie_building_set.py`: доминанты из
текущего сета bionics, мелкие групповые пропсы и «инопланетные» формы из
бионического city-set'а (ранее временно у Humans), орбитальные док и щит
из `refs/buildings/Shuffie/*.glb`, орбитальное оружие — корабельные
турели флота (Laser turret / Wave cannon / Gauss cannon) в серебре
палитры строений. Палитра гармонизирована с флотом (эталон): золото ->
бирюза, графитовые врезки; текстуры бирюза/лайм сохранены. Выход:
`bionics/buildings/building_constructor_v2.glb` (68 узлов, <=10MB:
текстуры ужаты, децимация по источнику, уровни делят меш; те же extras +
kind=variant у запасных групп). Подробный маппинг и палитра —
`races/shuffie.md` §5b; контрольный лист —
`renders/preview/approval_buildings_shuffie_v2.png`.
