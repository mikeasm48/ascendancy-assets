# Asset Bible — ascendancy-remake

Единый источник правды по визуальному стилю и процедурной генерации ассетов
(корабли, здания, устройства) для всех рас проекта.

**Ключевой принцип:** *что* генерируется (функциональная форма устройства) отделено
от того, *как это выглядит* (стилевой кит расы). Одна и та же нод-группа
`GN_Device_Engine` даёт человеческий двигатель и двигатель Shuffie — меняется
только подключённый Race Style Kit.

## Структура

| Файл | Что внутри |
|---|---|
| [00-pipeline.md](00-pipeline.md) | Архитектура Geometry Nodes, naming conventions, рендер-пайплайн |
| [01-device-taxonomy.md](01-device-taxonomy.md) | Общая таксономия устройств — одинакова для всех рас |
| [02-device-set.md](02-device-set.md) | Генерация набора устройств из DefaultTechCatalog для Humans/Shuffie |
| [03-building-set.md](03-building-set.md) | Генерация зданий (BuildingType) и орбитальных конструкций (OrbitalCatalog), стили industrial/scifi |
| [04-ui-style.md](04-ui-style.md) | Стиль "Ascendancy Neo" 2D-интерфейса — цветовые/геометрические токены, типографика, каталог компонентов, assets vs код |
| [races/humans.md](races/humans.md) | Стилевой кит расы Humans |
| [races/shuffie.md](races/shuffie.md) | Стилевой кит расы Shuffie |
| [races/_template.md](races/_template.md) | Шаблон — копируется при добавлении новой расы |
| [tools/geonodes_scaffold.py](tools/geonodes_scaffold.py) | Скрипт: создаёт каркас нод-групп в .blend (заглушки, для ручного наполнения) |
| [tools/build_device_library.py](tools/build_device_library.py) | Скрипт: полная генерация наборов устройств + экспорт GLB per race |
| [tools/devices.json](tools/devices.json) | Каталог устройств (из DefaultTechCatalog.java) |
| [tools/render_device_set.py](tools/render_device_set.py) | Batch-рендер набора устройств в PNG |

## Quick start

```bash
# Сгенерировать наборы устройств (36 корабельных × humans/core)
# и экспортировать device_constructor.glb в ассеты игры
blender -b -P tools/build_device_sets.py -- \
    --races humans,core --assets-dir ~/.ascendancy/assets/races

# Сгенерировать наборы зданий и орбитальных конструкций Humans
# (industrial + scifi) в building_constructor_<style>.glb
blender -b -P tools/build_building_sets.py -- \
    --styles industrial,scifi --assets-dir ~/.ascendancy/assets/races
```

Подробности и маппинг Java-каталога — в [02-device-set.md](02-device-set.md)
и [03-building-set.md](03-building-set.md).
Ручной путь (каркас-заглушки + наполнение в Blender) — `tools/geonodes_scaffold.py`.

## Добавление новой расы

1. Скопировать `races/_template.md` → `races/<race>.md`, заполнить.
2. В .blend создать нод-группу `GN_Style_<Race>` по интерфейсу из `00-pipeline.md`.
3. Добавить расу в enum `Race Style` мастер-группы `GN_Device_Master`.
4. Прогнать `render_device_set.py --race <race>` и приложить контрольный лист
   рендеров к странице расы.

Ничего в существующих расах при этом не трогается — стилевые киты изолированы.
