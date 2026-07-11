# Референсы зданий (Humans) — что сюда класть

> **Оригиналы:** полноразмерные версии всех референсов лежат вне
> репозитория — `~/java/ascendancy-refs-originals/buildings/` (включая
> варианты, не попавшие в эту папку). Здесь хранятся ужатые копии
> (≤1024px, jpeg q≈68) — их достаточно для сверки при доработке рецептов
> `tools/building_recipes_humans_*.py`. Для генерации GLB-наборов эта
> папка не требуется вовсе (см. `03-building-set.md`).

Именование: `<Здание><-|_>humans_<номер варианта>.jpg`. Примеры двух
видов — брутальный **industrial** и футуристический **scifi**; при
генерации стили НЕ смешиваются (см. `03-building-set.md`).

## Классификация

| Файл(ы) | Здание | Стиль |
|---|---|---|
| `ColonyBase_humans-1` | COLONY_BASE | industrial (пирамида-зиккурат) |
| `Factory_humans_1/2` | FACTORY / METROPLEX | industrial (башни, трубы, конвейеры) |
| `Outpost_humans_1` | OUTPOST | industrial (купола на платформах) |
| `Farm_humans_1` | FARM | industrial (стеклянные своды-теплицы) |
| `Laboratory_humans_1` | LABORATORY | industrial (модули с остеклением) |
| `Laboratory_humans_2` | LABORATORY | scifi (белый блок с куполом) |
| `ArtificalHidroponifier_humans_1` | ARTIFICAL_HYDROPONIFIER | scifi (башня-оранжерея) |
| `ArtificalHidroponifier_humans_2` | ARTIFICAL_HYDROPONIFIER / FARM | industrial (грядки под куполами) |
| `Metroplex_humans_1/4` | METROPLEX | scifi (шпили, алмазы-сады, эстакады) |
| `PowerPlant-humans_1/2` | POWER_PLANT | scifi (купол-реактор, чаши-канопе) |
| `ResearchCampus_humans_1` | RESEARCH_CAMPUS | scifi (шпиль + купола с мостами) |
| `SkyNet-humans_1` | SKY_NET | scifi (спиральная башня) |
| `EcoBooster_humans_1` | ECO_BOOSTER | scifi (лотос вокруг ядра) |
| `SpaceDock_humans_1/4` | SPACE_DOCK_* | industrial (гранёное кольцо-верфь) |
| `SpaceShield_humans_1/3` | SPACE_SHIELD_* | industrial (колесо; гекс-панели) |
| `OrbitalLaser_humans_1..3` | ORBITAL_LASER_1..3 | industrial (кольцо + красный луч) |
| `OrbitalPhaser_humans_1..3` | ORBITAL_PHAZER_1..3 | industrial (тяжёлые турели) |
| `OrbitalPhaserRapid_humans_1..3` | ORBITAL_PHAZER_RAPID_* | scifi (массив игл, фиолет) |

Для зданий без референса (MEGAFACTORY, HABITAT, TERRAFORMING) силуэты
экстраполированы из соседних рефов того же стиля — см. рецепты.

⚠️ Старый city-set `building_constructor.glb` (белая керамика) референсом
для Humans НЕ является — его модели переедут к другой расе.
