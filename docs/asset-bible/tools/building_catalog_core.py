# Каталог строений CORE — набор «по умолчанию» для рас без собственных
# китов зданий. Референсы: refs/buildings/core/*.
#
# Состав: 14 планетарных BuildingType (ascendancy-remake,
# model/colony/BuildingType.java; SKY_NET и TERRAFORMING без рефов —
# спроектированы в стиле набора) + 4 наземных спецпозиции из рефов
# оригинальной Ascendancy (пока вне BuildingType) + 15 орбитальных
# конструкций (OrbitalCatalog, как у humans; рефы OrbitalDocks/
# OrbitalShipyard/OrbitalShield_1..3/OrbitalLaser/OrbitalMissileBase)
# + 6 пропсов.
#
# ПОРЯДОК ЗАПИСЕЙ = индекс узла в GLB. Существующий порядок не менять,
# новые записи только добавлять в конец (как в building_catalog.py).
#
# display_name — имена строений оригинальной Ascendancy 1995, где они
# отличаются от BuildingType (Agriplot, Industrial Megafacility,
# Hyperpower Plant, Lush Growth Bomb).

# (id, display_name, recipe, level, kind)
RECIPES = [
    # -------- планетарные здания (BuildingType), level не используется
    ("COLONY_BASE", "Colony Base",               'colony_base', 0, 'building'),
    ("FACTORY", "Factory",                       'factory', 0, 'building'),
    ("OUTPOST", "Outpost",                       'outpost', 0, 'building'),
    ("FARM", "Agriplot",                         'farm', 0, 'building'),
    ("LABORATORY", "Laboratory",                 'laboratory', 0, 'building'),
    ("RESEARCH_CAMPUS", "Research Campus",       'research_campus', 0, 'building'),
    ("MEGAFACTORY", "Industrial Megafacility",   'megafactory', 0, 'building'),
    ("HABITAT", "Habitat",                       'habitat', 0, 'building'),
    ("ARTIFICAL_HYDROPONIFIER", "Artificial Hydroponifier",
                                                 'hydroponifier', 0, 'building'),
    ("METROPLEX", "Metroplex",                   'metroplex', 0, 'building'),
    ("POWER_PLANT", "Hyperpower Plant",          'power_plant', 0, 'building'),
    ("SKY_NET", "Sky Net",                       'sky_net', 0, 'building'),
    ("ECO_BOOSTER", "Lush Growth Bomb",          'eco_booster', 0, 'building'),
    ("TERRAFORMING", "Terraforming",             'terraforming', 0, 'building'),
    # -------- наземные спецпозиции по рефам (вне BuildingType)
    ("ENGINEERING_RETREAT", "Engineering Retreat",
                                                 'engineering_retreat', 0, 'building'),
    ("SURFACE_SHIELD", "Surface Shield",         'surface_shield', 0, 'building'),
    ("SURFACE_MEGA_SHIELD", "Surface Megashield",
                                                 'surface_mega_shield', 0, 'building'),
    ("ALIEN_RUINS", "Alien Ruins",               'alien_ruins', 0, 'building'),
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
