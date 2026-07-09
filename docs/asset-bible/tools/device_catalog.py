# Маппинг: 36 корабельных устройств (без Orbital_/Space_) -> рецепты
RECIPES = [
 ("ENGINE_1", "Tonklin Motor",                'engine', 1),
 ("ENGINE_2", "Ion Banger",                   'engine', 2),
 ("ENGINE_3", "Graviton Projector",           'engine', 3),
 ("INTERSTELLAR_ENGINE_1", "Star Lane Drive", 'star_lane', 1),
 ("INTERSTELLAR_ENGINE_2", "Star Lane Adv. Drive", 'star_lane', 2),
 ("INTERSTELLAR_ENGINE_3", "Star Lane Hyper Drive", 'star_lane', 3),
 ("ENGINE_INERTIA_NEGATOR", "Inertia Negator", 'inertia', 0),
 ("GENERATOR_1", "Proton Shaver",             'generator', 1),
 ("GENERATOR_2", "Subatomic Scoop",           'generator', 2),
 ("GENERATOR_3", "Quark Express",             'generator', 3),
 ("GENERATOR_4", "Van Creeg Hypersplicer",    'generator', 4),
 ("GENERATOR_5", "Nanotwirler",               'generator', 5),
 ("SHIELD_1", "Ion Wrap",                     'shield', 1),
 ("SHIELD_SMART_1", "Deactotron",             'shield', 2),
 ("SHIELD_TIME_1", "Wave Scatterer",          'shield', 3),
 ("SHIELD_SMART_2", "Hyperwave Nullifier",    'shield', 4),
 ("SHIELD_TIME_2", "Nanoshield",              'shield', 5),
 ("SCANNER_1", "Tonklin Frequency Analyzer",  'scanner', 1),
 ("SCANNER_2", "Subspace Phase Array",        'scanner', 2),
 ("SCANNER_3", "Aural Cloud Constructor",     'scanner', 3),
 ("SCANNER_4", "Hyperwave Tympanum",          'scanner', 4),
 ("SCANNER_5", "Nanowave Decoupling Net",     'scanner', 5),
 ("WEAPON_LAZER_BEAM_1", "Lazer Gun",         'beam:lazer', 1),
 ("WEAPON_LAZER_BEAM_2", "Advanced Lazer Gun",'beam:lazer', 2),
 ("WEAPON_LAZER_BEAM_3", "Hyper Lazer (Ueberlaser)", 'beam:lazer', 3),
 ("WEAPON_PHAZER_BEAM_1", "Phazer (Plasmatron)", 'beam:phazer', 1),
 ("WEAPON_PHAZER_BEAM_2", "Advanced Phazer",  'beam:phazer', 2),
 ("WEAPON_PHAZER_BEAM_3", "Hyper Phazer",     'beam:phazer', 3),
 ("WEAPON_LAZER_RAPID_1", "Lazer Turret (Hypersphere)", 'rapid:lazer', 1),
 ("WEAPON_LAZER_RAPID_2", "Adv. Lazer Turret",'rapid:lazer', 2),
 ("WEAPON_LAZER_RAPID_3", "Hyper Lazer Turret",'rapid:lazer', 3),
 ("WEAPON_PHAZER_RAPID_1", "Phazer Rapid",    'rapid:phazer', 1),
 ("WEAPON_PHAZER_RAPID_2", "Adv. Phazer Rapid", 'rapid:phazer', 2),
 ("WEAPON_PHAZER_RAPID_3", "Nanomanipulator", 'rapid:phazer', 3),
 ("AUX_COLONY_BASE", "Colony Base (Colonizer)", 'aux:colony', 0),
 ("AUX_INVASION_MODULE", "Invasion Module",   'aux:invasion', 0),
]

def build(mod, recipe, lvl, seed=0, **kw):
    if recipe == 'engine': return mod.engine(lvl, seed, **kw)
    if recipe == 'star_lane': return mod.star_lane(lvl, seed, **kw)
    if recipe == 'generator': return mod.generator(lvl, seed, **kw)
    if recipe == 'shield': return mod.shield(lvl, seed, **kw)
    if recipe == 'scanner': return mod.scanner(lvl, seed, **kw)
    if recipe.startswith('beam:'): return mod.weapon_beam(lvl, recipe.split(':')[1], seed, **kw)
    if recipe.startswith('rapid:'): return mod.weapon_rapid(lvl, recipe.split(':')[1], seed, **kw)
    if recipe.startswith('aux:'): return mod.aux(recipe.split(':')[1], seed, **kw)
    if recipe == 'inertia': return mod.inertia_negator(seed, **kw)
    raise ValueError(recipe)
