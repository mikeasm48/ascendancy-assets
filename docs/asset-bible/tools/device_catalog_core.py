# Каталог устройств CORE v3 — по обновлённым референсам
# refs/devices/core/ (формат имени: <Тип>_core_<Название>_<версия>).
#
# Набор отражает устройства оригинальной Ascendancy 1995 и СОЗНАТЕЛЬНО не
# привязан к спецификациям ascendancy-remake и поколениям устройств —
# маппинг на спецификации выполняется вручную отдельно. Ни уровней, ни
# tech_level здесь нет: одна модель = один референс.
#
# Имя узла в GLB = node (формат <Тип>_<Название>). Платформа-постамент —
# отдельный child-меш <node>_platform (в игре можно скрыть); вид плиты
# задаёт поле plate (см. device_recipes_core.platform). plate=None — для
# устройств с геометрией из готового импортированного референса, у
# которых собственная плита уже часть меша: общая плита не строится.
#
# ПОРЯДОК ЗАПИСЕЙ = индекс узла в GLB. Существующий порядок не менять,
# новые записи только добавлять в конец.

# (node, display_name, device_type, recipe, plate)
RECIPES = [
    # -------- engines
    ("Engine_TonklinMotor", "Tonklin Motor", "engine",
     'engine_tonklin_motor', 'silver'),
    ("Engine_IonBanger", "Ion Banger", "engine",
     'engine_ion_banger', 'silver'),
    # -------- star lane drives
    ("StarLaneDrive", "Star Lane Drive", "star_lane_drive",
     'star_lane_drive', None),
    ("StarLaneDrive_HyperDrive", "Star Lane Hyperdrive", "star_lane_drive",
     'star_lane_hyperdrive', 'silver'),
    # -------- generators
    ("Generator_ProtonShaver", "Proton Shaver", "generator",
     'generator_proton_shaver', 'silver'),
    ("Generator_SubatomicScoop", "Subatomic Scoop", "generator",
     'generator_subatomic_scoop', 'silver'),
    ("Generator_QuarkExpress", "Quark Express", "generator",
     'generator_quark_express', 'silver'),
    ("Generator_VanCreegHypersplicer", "Van Creeg Hypersplicer", "generator",
     'generator_van_creeg', 'fins'),
    ("Generator_Nanotwirler", "Nanotwirler", "generator",
     'generator_nanotwirler', 'fins'),
    # -------- scanners
    ("Scanner_TonklinFrequencyAnalizer", "Tonklin Frequency Analizer",
     "scanner", 'scanner_tonklin_freq', 'circuit'),
    ("Scanner_SubspacePhaseArray", "Subspace Phase Array", "scanner",
     'scanner_subspace_phase_array', 'lattice'),
    ("Scanner_AuralCloudConstructor", "Aural Cloud Constructor", "scanner",
     'scanner_aural_cloud', 'silver'),
    ("Scanner_HyperwaveTympanum", "Hyperwave Tympanum", "scanner",
     'scanner_hyperwave_tympanum', 'dark'),
    ("Scanner_NanowaveDecouplingNet", "Nanowave Decoupling Net", "scanner",
     'scanner_nanowave_net', 'silver'),
    # -------- shields
    ("Shield_ion_wrap", "Ion Wrap", "shield",
     'shield_ion_wrap', 'dark'),
    ("Shield_deactotron", "Deactotron", "shield",
     'shield_deactotron', 'dark'),
    ("Shield_wave_scatterer", "Wave Scatterer", "shield",
     'shield_wave_scatterer', 'silver'),
    ("Shield_conclusion", "Conclusion", "shield",
     'shield_conclusion', 'silver'),
    # -------- weapons
    ("Weapon_Ueberlaser", "Ueberlaser", "weapon",
     'weapon_ueberlaser', 'silver'),
    ("Weapon_Plasmatron", "Plasmatron", "weapon",
     'weapon_plasmatron', 'silver'),
    ("Weapon_HypersphereDriver", "Hypersphere Driver", "weapon",
     'weapon_hypersphere_driver', 'dark'),
    ("Weapon_Nanomanipulator", "Nanomanipulator", "weapon",
     'weapon_nanomanipulator', 'silver'),
    # -------- aux
    ("Aux_Colonizer", "Colonizer", "aux",
     'aux_colonizer', 'silver'),
    ("Aux_InvasionModule", "Invasion Module", "aux",
     'aux_invasion_module', None),
    ("Aux_LaneMagnetron", "Lane Magnetron", "aux",
     'aux_lane_magnetron', None),
    ("Aux_Colonizer_New", "Colonizer (New)", "aux",
     'aux_colonizer_new', None),
]


def build(mod, recipe, seed=0):
    fn = getattr(mod, recipe, None)
    if fn is None:
        raise ValueError(f"{mod.__name__}: нет рецепта '{recipe}'")
    return fn(seed)
