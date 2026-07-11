# 02 — Набор устройств: генерация для Humans и Core

Источник списка устройств — `DefaultTechCatalog.java` (ascendancy-remake).
Генерируются **36 корабельных устройств**. Орбитальные конструкции
(`Orbital_*`, `Space_*`) и планетарные здания генерируются отдельным
пайплайном — см. `03-building-set.md`.

Два набора:

- **humans** — по референсам `refs/devices/**/*_humans*` (GLB + изображения);
  индустриальный металл, категорийные цвета, синее/оранжевое свечение.
- **core** — «1 в 1» по скриншотам Ascendancy 1995 (`*_core*`); используется
  как набор по умолчанию для рас без собственных моделей. Платформа-постамент —
  отдельный child-меш `<id>_platform` (в игре можно скрыть).

Силуэты обоих наборов согласованы по контрольным листам
`renders/preview/approval_*_v*.png` (итоговые: core v4, humans v14).

## Архитектура генерации

Геометрия строится **чистым Python/numpy** — без Geometry Nodes (первая
GN-версия оказалась хрупкой к версиям Blender: раскладка сокетов Random Value
сломала все случайные размеры в 5.1). Blender отвечает только за материалы,
шейдинг и экспорт.

| Файл | Роль |
|---|---|
| `tools/device_meshes.py` | примитивы: revolve, tube, torus, helix_coil, loft и т.д. |
| `tools/device_recipes_humans.py` | рецепты 36 устройств Humans |
| `tools/device_recipes_core.py` | рецепты 36 устройств Core + платформа |
| `tools/device_catalog.py` | каталог `RECIPES`: id → рецепт/уровень (порядок = индекс в GLB) |
| `tools/devices.json` | тот же каталог в JSON (для игры/инструментов) |
| `tools/build_device_sets.py` | bpy-скрипт: меши → материалы → шейдинг → GLB |

Рецепты редактируются и просматриваются без Blender (numpy-превью),
поэтому итерации по внешнему виду быстрые.

## Запуск

```bash
# Только Humans
blender -b -P tools/build_device_sets.py -- \
    --races humans --assets-dir ~/.ascendancy/assets/races

# Оба набора
blender -b -P tools/build_device_sets.py -- \
    --races humans,core --assets-dir ~/.ascendancy/assets/races
```

Требуется Blender 4.2+ (проверено на 5.1). Выход:

```
~/.ascendancy/assets/races/humans/devices/device_constructor.glb
~/.ascendancy/assets/races/core/devices/device_constructor.glb
```

Каждый узел несёт glTF-`extras`: `device_id`, `display_name`, `tech_level`;
адресация из игры — по индексу `device_constructor#<index>` (порядок
фиксирован каталогом) или по `device_id`.

## Материалы и шейдинг

- Палитра тегов (`MAT_dev_*`) синхронизирована с превью и стилями рас:
  металлик/шероховатость + эмиссия для свечений (`accent` — оранжевый,
  `bglow` — синий, `flame` — пламя сопел, `redline` — красные канты).
- Shade smooth на всех устройствах + Edge Split 42° (жёсткие рёбра);
  исключение — щиты (гекс-сфера остаётся гранёной по решению от 2026-07-09).
- `glass` — полупрозрачный (blend).

## Прежний GN-пайплайн

`tools/build_device_library.py` (Geometry Nodes: архетипы × стилевые киты)
оставлен как экспериментальный — для процедурной вариативности по seed.
Для продакшн-наборов используется `build_device_sets.py`.
