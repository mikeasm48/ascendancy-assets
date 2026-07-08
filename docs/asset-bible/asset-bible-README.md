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
| [races/humans.md](races/humans.md) | Стилевой кит расы Humans |
| [races/shuffie.md](races/shuffie.md) | Стилевой кит расы Shuffie |
| [races/_template.md](races/_template.md) | Шаблон — копируется при добавлении новой расы |
| [tools/geonodes_scaffold.py](tools/geonodes_scaffold.py) | Скрипт: создаёт каркас нод-групп в .blend |
| [tools/render_device_set.py](tools/render_device_set.py) | Batch-рендер набора устройств в PNG |

## Quick start

```bash
# 1. Создать каркас нод-групп в новом .blend
blender -b -P tools/geonodes_scaffold.py -- --out blends/devices.blend

# 2. Наполнить стилевые киты вручную в Blender (см. races/*.md)

# 3. Отрендерить полный набор устройств расы
blender -b blends/devices.blend -P tools/render_device_set.py -- \
    --race humans --seeds 8 --out renders/humans/
```

## Добавление новой расы

1. Скопировать `races/_template.md` → `races/<race>.md`, заполнить.
2. В .blend создать нод-группу `GN_Style_<Race>` по интерфейсу из `00-pipeline.md`.
3. Добавить расу в enum `Race Style` мастер-группы `GN_Device_Master`.
4. Прогнать `render_device_set.py --race <race>` и приложить контрольный лист
   рендеров к странице расы.

Ничего в существующих расах при этом не трогается — стилевые киты изолированы.
