# Каталог зданий/орбитальных конструкций/пропсов -> рецепты.
#
# Источники списков (ascendancy-remake):
#   планетарные — enum BuildingType (model/colony/BuildingType.java)
#   орбитальные — OrbitalCatalog (model/colony/OrbitalCatalog.java)
#
# Каждая запись строится в ДВУХ стилевых вариантах (industrial / scifi),
# стили не смешиваются внутри модели. Пропсы — мелкие группы-расширители
# (аналог "Random blocks" старого city-set): игра комбинирует одну
# доминанту + несколько пропсов для эффекта занимаемой площади.
#
# ПОРЯДОК ЗАПИСЕЙ = индекс узла в GLB. Существующий порядок не менять,
# новые записи только добавлять в конец (как в device_catalog.py).

# (id, display_name, recipe, level, kind)
RECIPES = [
    # -------- планетарные здания (BuildingType), level не используется
    ("COLONY_BASE", "Colony Base",               'colony_base', 0, 'building'),
    ("FACTORY", "Factory",                       'factory', 0, 'building'),
    ("OUTPOST", "Outpost",                       'outpost', 0, 'building'),
    ("FARM", "Farm",                             'farm', 0, 'building'),
    ("LABORATORY", "Laboratory",                 'laboratory', 0, 'building'),
    ("RESEARCH_CAMPUS", "Research Campus",       'research_campus', 0, 'building'),
    ("MEGAFACTORY", "Megafactory",               'megafactory', 0, 'building'),
    ("HABITAT", "Habitat",                       'habitat', 0, 'building'),
    ("ARTIFICAL_HYDROPONIFIER", "Artificial Hydroponifier",
                                                 'hydroponifier', 0, 'building'),
    ("METROPLEX", "Metroplex",                   'metroplex', 0, 'building'),
    ("POWER_PLANT", "Power Plant",               'power_plant', 0, 'building'),
    ("SKY_NET", "Sky Net",                       'sky_net', 0, 'building'),
    ("ECO_BOOSTER", "Eco Booster",               'eco_booster', 0, 'building'),
    ("TERRAFORMING", "Terraforming",             'terraforming', 0, 'building'),
    # -------- орбитальные конструкции (OrbitalCatalog)
    ("SPACE_DOCK_SMALL", "Small Orbital Dock",   'orb_dock', 1, 'orbital'),
    ("SPACE_DOCK_MEDIUM", "Medium Orbital Dock", 'orb_dock', 2, 'orbital'),
    ("SPACE_DOCK_LARGE", "Large Orbital Dock",   'orb_dock', 3, 'orbital'),
    ("SPACE_DOCK_HUGE", "Huge Orbital Dock",     'orb_dock', 4, 'orbital'),
    ("SPACE_SHIELD_1", "Orbital Shield",         'orb_shield', 1, 'orbital'),
    ("SPACE_SHIELD_2", "Advanced Orbital Shield", 'orb_shield', 2, 'orbital'),
    ("SPACE_SHIELD_3", "Hyper Orbital Shield",   'orb_shield', 3, 'orbital'),
    ("ORBITAL_LASER_1", "Orbital Lazer",         'orb_laser', 1, 'orbital'),
    ("ORBITAL_LASER_2", "Advanced Orbital Lazer", 'orb_laser', 2, 'orbital'),
    ("ORBITAL_LASER_3", "Hyper Orbital Lazer",   'orb_laser', 3, 'orbital'),
    ("ORBITAL_PHAZER_1", "Orbital Phazer",       'orb_phazer', 1, 'orbital'),
    ("ORBITAL_PHAZER_2", "Advanced Orbital Phazer", 'orb_phazer', 2, 'orbital'),
    ("ORBITAL_PHAZER_3", "Hyper Orbital Phazer", 'orb_phazer', 3, 'orbital'),
    ("ORBITAL_PHAZER_RAPID_1", "Orbital Rapid Phazer",
                                                 'orb_phazer_rapid', 1, 'orbital'),
    ("ORBITAL_PHAZER_RAPID_2", "Advanced Orbital Rapid Phazer",
                                                 'orb_phazer_rapid', 2, 'orbital'),
    # -------- пропсы-расширители (level = вариант)
    ("PROP_BLOCKS_1", "Random blocks 1",         'prop_blocks', 1, 'prop'),
    ("PROP_BLOCKS_2", "Random blocks 2",         'prop_blocks', 2, 'prop'),
    ("PROP_TANKS", "Storage tanks",              'prop_tanks', 0, 'prop'),
    ("PROP_PIPES", "Pipe run",                   'prop_pipes', 0, 'prop'),
    ("PROP_MAST", "Comm mast",                   'prop_mast', 0, 'prop'),
    ("PROP_PAD", "Landing pad",                  'prop_pad', 0, 'prop'),
]

STYLES = ("industrial", "scifi")


def build(mod, recipe, level, seed=0, **kw):
    """Диспетчер: у каждого стилевого модуля одинаковый интерфейс —
    функция <recipe>(level, seed)."""
    fn = getattr(mod, recipe, None)
    if fn is None:
        raise ValueError(f"{mod.__name__}: нет рецепта '{recipe}'")
    return fn(level, seed, **kw)
