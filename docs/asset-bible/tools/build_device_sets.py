# build_device_sets.py — сборка наборов моделей устройств (Blender 4.2+/5.x)
#
# Геометрия строится чистым Python/numpy (device_meshes.py + device_recipes_*.py,
# силуэты согласованы по референсам из refs/devices), Blender используется
# только для материалов, шейдинга и экспорта GLB. Никаких хрупких нод.
#
# Запуск:
#   blender -b -P tools/build_device_sets.py -- \
#       --races humans[,core] \
#       --assets-dir ~/.ascendancy/assets/races \
#       [--out blends/devices_gen.blend] [--no-export]
#
# Выход per race:
#   humans -> <assets-dir>/humans/devices/device_constructor.glb
#             (device_catalog.RECIPES: 36 устройств с tech_level)
#   core   -> <assets-dir>/core/devices/device_constructor.glb
#             (device_catalog_core.RECIPES: 25 моделей по рефам
#              refs/devices/core БЕЗ уровней/поколений; имя узла =
#              <Тип>_<Название>; платформа — отдельный child-меш
#              <node>_platform, в игре её можно скрыть)
#
# Extras: humans — device_id, display_name, tech_level;
#         core   — device_id (= имя узла), display_name, device_type.

import os
import sys
import math

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import device_recipes_humans
import device_recipes_core
from device_catalog import RECIPES, build
from device_catalog_core import RECIPES as RECIPES_CORE
from device_catalog_core import build as build_core

RACE_MODULES = {"humans": device_recipes_humans, "core": device_recipes_core}
RACE_FOLDERS = {"humans": "humans", "core": "core"}

# ----------------------------------------------------------------------------
# Материалы: tag -> (hex, metallic, roughness, emission_strength)
# Синхронизировано с палитрой превью (render_iso.MATS) и races/humans.md
# ----------------------------------------------------------------------------
MATS = {
    "plat":    ("#6E7A86", 0.7, 0.45, 0),
    "hull":    ("#9AA3AB", 0.8, 0.40, 0),
    "hull_b":  ("#C4CBD1", 0.5, 0.50, 0),
    "detail":  ("#5E666E", 0.9, 0.35, 0),
    "coil":    ("#B3372B", 0.6, 0.30, 0),
    "coil2":   ("#A9803A", 0.8, 0.30, 0),
    "blue":    ("#4A6FA5", 0.6, 0.35, 0),
    "teal":    ("#3E9A92", 0.5, 0.40, 0),
    "gold":    ("#B08D3C", 0.9, 0.25, 0),
    "glass":   ("#9FC4D8", 0.3, 0.10, 0),
    "dark":    ("#33383E", 0.4, 0.50, 0),
    "green":   ("#6B8F3E", 0.4, 0.50, 0),
    "white":   ("#D8D8D8", 0.4, 0.35, 0),
    "accent":  ("#E06A2B", 0.0, 0.40, 4.0),
    "pink":    ("#B56A9A", 0.5, 0.35, 0),
    "flame":   ("#FF9A3C", 0.0, 0.60, 6.0),
    "graph":   ("#3A3F45", 0.5, 0.35, 0),
    "redline": ("#C43B2A", 0.4, 0.25, 1.5),
    "ygreen":  ("#A8B23A", 0.3, 0.45, 0),
    "dgreen":  ("#39543F", 0.4, 0.40, 0),
    "silver":  ("#C0C7CC", 1.0, 0.15, 0),
    "wood":    ("#B99A5E", 0.1, 0.80, 0),
    "bottle":  ("#3FA34D", 0.2, 0.12, 0),
    "bglow":   ("#4FC3FF", 0.0, 0.40, 4.0),
    "gun":     ("#8E969E", 0.85, 0.35, 0),
    "gun_d":   ("#4C545C", 0.7, 0.40, 0),
    # --- дополнения core v3 (по обновлённым рефам refs/devices/core)
    "copper":  ("#B87333", 0.9, 0.30, 0),
    "pearl":   ("#E8DFEA", 0.4, 0.15, 0),
    "yellow":  ("#D9C04B", 0.3, 0.50, 0),
    "pglow":   ("#E570C0", 0.0, 0.40, 3.0),
    "yglow":   ("#C6E24A", 0.0, 0.40, 3.0),
    # --- InvasionModule (перенос цвета с эталонного референса, см.
    # device_recipes_core.aux_invasion_module)
    "tan":       ("#F2DD9B", 0.2, 0.55, 0),
    "redbright": ("#DE211E", 0.1, 0.35, 0),
    "invgray":   ("#8E988E", 0.5, 0.45, 0),
    # --- Colonizer_New (перенос цвета с эталонного референса, см.
    # device_recipes_core.aux_colonizer_new)
    "colgray":   ("#B2B4AC", 0.3, 0.55, 0),
    "colgreen":  ("#A8C7A6", 0.2, 0.55, 0),
    "coltan":    ("#DCC9A4", 0.2, 0.55, 0),
    "colgold":   ("#CCB27A", 0.3, 0.45, 0),
    # --- LaneMagnetron (перенос цвета с эталонного референса, см.
    # device_recipes_core.aux_lane_magnetron)
    "lmgray":    ("#BCBEBB", 0.6, 0.40, 0),
    "lmtan":     ("#D5C5A0", 0.2, 0.55, 0),
    "lmbrass":   ("#998C66", 0.7, 0.35, 0),
    "lmteal":    ("#3689A4", 0.5, 0.35, 0),
    "lmglow":    ("#F2F470", 0.0, 0.40, 3.0),
    "lmgreen":   ("#7CA379", 0.3, 0.50, 0),
    # --- StarLaneDrive (перенос цвета с эталонного референса, см.
    # device_recipes_core.star_lane_drive)
    "sldwhite":  ("#ECE7E6", 0.3, 0.45, 0),
    "sldgray":   ("#BCBDBB", 0.5, 0.40, 0),
    "sldpeach":  ("#F7DCCF", 0.2, 0.55, 0),
    "sldblue":   ("#94B3C9", 0.4, 0.40, 0),
    "sldnavy":   ("#084C7E", 0.4, 0.35, 0),
    # --- StarLaneDrive_HyperDrive (перенос цвета с эталонного референса,
    # см. device_recipes_core.star_lane_hyperdrive)
    "hdsilver":  ("#BFBCBD", 0.8, 0.35, 0),
    "hdred":     ("#A3485E", 0.3, 0.50, 0),
    "hdrose":    ("#A88486", 0.3, 0.55, 0),
    # --- Nanomanipulator (перенос цвета с эталонного референса, см.
    # device_recipes_core.weapon_nanomanipulator)
    "nmgun":     ("#6E6B70", 0.85, 0.40, 0),
    "nmglow":    ("#E29ABD", 0.0, 0.40, 2.5),
    # --- HypersphereDriver (перенос цвета с эталонного референса, см.
    # device_recipes_core.weapon_hypersphere_driver; корпус — общий nmgun)
    "hsbrass":   ("#B69C7F", 0.9, 0.30, 0),
    "hsglow":    ("#3C83A4", 0.0, 0.40, 2.5),
    # --- Plasmatron (перенос цвета с эталонного референса, см.
    # device_recipes_core.weapon_plasmatron)
    "plwhite":   ("#B9B3B3", 0.3, 0.40, 0),
    "plbronze":  ("#85696B", 0.8, 0.35, 0),
    "plglow":    ("#D54C3D", 0.0, 0.40, 3.0),
    # --- Ueberlaser (перенос цвета с эталонного референса, см.
    # device_recipes_core.weapon_ueberlaser)
    "ubsilver":  ("#A4A4A4", 0.8, 0.35, 0),
    "ubyellow":  ("#DBCD71", 0.3, 0.50, 0),
    "ubgreen":   ("#99BE79", 0.3, 0.50, 0),
    "ubglow":    ("#95C9C8", 0.0, 0.40, 2.5),
    # --- IonBanger (перенос цвета с эталонного референса, см.
    # device_recipes_core.engine_ion_banger)
    "ibsilver":  ("#A8A2A4", 0.7, 0.40, 0),
    "ibred":     ("#B05052", 0.3, 0.45, 0),
    "ibyellow":  ("#E9D176", 0.3, 0.50, 0),
    "ibglow":    ("#7AA5C4", 0.0, 0.40, 2.5),
    # --- TonklinMotor (перенос цвета с эталонного референса, см.
    # device_recipes_core.engine_tonklin_motor)
    "tmsteel":   ("#98908B", 0.8, 0.45, 0),
    "tmred":     ("#9A4348", 0.4, 0.45, 0),
    # --- генераторы (перенос цвета с эталонных референсов, см.
    # device_recipes_core.generator_*)
    "ntsilver":  ("#B2B0AB", 0.7, 0.40, 0),
    "ntdark":    ("#5A5C56", 0.6, 0.45, 0),
    "ntgold":    ("#C8B084", 0.9, 0.30, 0),
    "ntred":     ("#E82C37", 0.0, 0.40, 3.0),
    "ntblue":    ("#6B90AF", 0.0, 0.40, 2.0),
    "pssilver":  ("#ABA9A8", 0.7, 0.40, 0),
    "psblue":    ("#7695A9", 0.5, 0.40, 0),
    "psbrass":   ("#E0C996", 0.8, 0.35, 0),
    "pscoil":    ("#AC5038", 0.6, 0.35, 0),
    "qeblue":    ("#8C9FAD", 0.5, 0.40, 0),
    "qegold":    ("#C6BC9D", 0.8, 0.35, 0),
    "qegreen":   ("#57B550", 0.3, 0.45, 0),
    "qeglow":    ("#DB4B58", 0.0, 0.40, 2.5),
    "sssilver":  ("#99999A", 0.7, 0.40, 0),
    "ssblue":    ("#5885A3", 0.5, 0.40, 0),
    "ssorange":  ("#A8897F", 0.4, 0.50, 0),
    "ssglow":    ("#E0785F", 0.0, 0.40, 2.0),
    "ssteal":    ("#5FD9CE", 0.0, 0.40, 2.5),
    "vcsteel":   ("#AAACAA", 0.8, 0.35, 0),
    "vcgold":    ("#E4D0A2", 0.9, 0.30, 0),
    "vcglow":    ("#4F91AE", 0.0, 0.40, 2.5),
    # --- щиты (перенос цвета с эталонных референсов, см.
    # device_recipes_core.shield_*)
    "dtsteel":   ("#888D90", 0.8, 0.35, 0),
    "dtblue":    ("#3F6FB0", 0.5, 0.40, 0),
    "dtgold":    ("#C8A24A", 0.9, 0.30, 0),
    "dtglow":    ("#2EA8E8", 0.0, 0.40, 3.0),
    "iwcopper":  ("#A2917F", 0.85, 0.35, 0),
    "iwred":     ("#DB111D", 0.3, 0.35, 0),
    "iwteal":    ("#8FC0BE", 0.4, 0.45, 0),
    "wssteel":   ("#8791A0", 0.7, 0.40, 0),
    "wsblue":    ("#2F4B79", 0.6, 0.40, 0),
    "wscrystal": ("#E1E6E8", 0.2, 0.20, 0),
    "wsgreen":   ("#7FB56A", 0.4, 0.45, 0),
    "wspurple":  ("#7A3E9A", 0.0, 0.40, 2.0),
    "wsglow":    ("#3AAEE0", 0.0, 0.40, 2.8),
    # --- Shield_conclusion (перенос цвета с эталонного референса, см.
    # device_recipes_core.shield_conclusion)
    "cnsteel":   ("#6E7376", 0.8, 0.40, 0),
    "cnbubble":  ("#C7D2DE", 0.2, 0.12, 0),
    "cnteal":    ("#5FA394", 0.3, 0.45, 0),
}

# рецепты, которым НЕ включаем сглаживание (гекс-щит должен остаться гранёным)
FLAT_RECIPES = {"shield"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"races": ["humans"],
         "assets_dir": os.path.expanduser("~/.ascendancy/assets/races"),
         "out": "blends/devices_gen.blend",
         "export": True}
    i = 0
    while i < len(argv):
        k = argv[i].lstrip("-").replace("-", "_")
        if k == "no_export":
            a["export"] = False
            i += 1
            continue
        v = argv[i + 1]
        if k == "races":
            a["races"] = [r.strip() for r in v.split(",")]
        else:
            a[k] = v
        i += 2
    return a


def srgb(hexcode):
    h = hexcode.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def make_materials():
    mats = {}
    for tag, (hexc, metal, rough, emis) in MATS.items():
        name = f"MAT_dev_{tag}"
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
            # в 5.x материалы нодовые по умолчанию; ставим флаг только
            # при необходимости (иначе DeprecationWarning)
            if m.node_tree is None:
                m.use_nodes = True
            b = m.node_tree.nodes.get("Principled BSDF")
            col = srgb(hexc)
            b.inputs["Base Color"].default_value = col
            b.inputs["Metallic"].default_value = metal
            b.inputs["Roughness"].default_value = rough
            if emis:
                b.inputs["Emission Color"].default_value = col
                b.inputs["Emission Strength"].default_value = emis
            if tag == "glass":
                b.inputs["Alpha"].default_value = 0.45
                m.blend_method = "BLEND"
        mats[tag] = m
    return mats


def mesh_from_parts(name, V, F, tags, mats, smooth=True):
    """Создать mesh из numpy-данных с материалами по тегам граней."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F])
    mesh.validate()
    mesh.update()
    # материалы: уникальные теги в порядке появления
    uniq = []
    for t in tags:
        if t not in uniq:
            uniq.append(t)
    for t in uniq:
        mesh.materials.append(mats[t])
    idx = [uniq.index(t) for t in tags]
    n = len(mesh.polygons)
    if n == len(idx):
        mesh.polygons.foreach_set("material_index", idx)
    else:  # validate() мог отбросить дегенеративные грани — назначаем по одному
        for p in mesh.polygons:
            if p.index < len(idx):
                p.material_index = idx[p.index]
    mesh.polygons.foreach_set("use_smooth", [smooth] * n)
    mesh.update()
    return mesh


def add_edge_split(obj, angle_deg=42.0):
    mod = obj.modifiers.new("HardEdges", "EDGE_SPLIT")
    mod.split_angle = math.radians(angle_deg)
    mod.use_edge_angle = True
    mod.use_edge_sharp = False
    return mod


def build_race(race, mats):
    module = RACE_MODULES[race]
    coll = bpy.data.collections.new(f"COL_devices_{race}")
    bpy.context.scene.collection.children.link(coll)
    objs = []
    if race == "core":
        return build_race_core(module, coll, mats)
    for i, (dev_id, disp, recipe, lvl) in enumerate(RECIPES):
        V, F, tags = build(module, recipe, lvl, seed=i)
        smooth = recipe not in FLAT_RECIPES
        mesh = mesh_from_parts(f"DEV_{race}_{dev_id}", V, F, tags, mats, smooth)
        obj = bpy.data.objects.new(f"{i:03d}_{race}_{dev_id}", mesh)
        coll.objects.link(obj)
        row, col_i = divmod(i, 8)
        obj.location = (col_i * 3.0, row * 3.0, 0.0)
        if smooth:
            add_edge_split(obj)
        obj["device_id"] = dev_id
        obj["display_name"] = disp
        obj["tech_level"] = lvl
        objs.append(obj)
    return objs


def build_race_core(module, coll, mats):
    """Core v3: свой каталог (без уровней), имя узла = <Тип>_<Название>,
    плита-постамент по каталогу — отдельный child-меш <node>_platform."""
    objs = []
    for i, (node, disp, dtype, recipe, plate) in enumerate(RECIPES_CORE):
        V, F, tags = build_core(module, recipe, seed=i)
        mesh = mesh_from_parts(f"DEV_core_{node}", V, F, tags, mats)
        obj = bpy.data.objects.new(node, mesh)
        coll.objects.link(obj)
        row, col_i = divmod(i, 5)
        obj.location = (col_i * 3.0, row * 3.0, 0.0)
        add_edge_split(obj)
        obj["device_id"] = node
        obj["display_name"] = disp
        obj["device_type"] = dtype
        objs.append(obj)
        if plate is not None:
            pV, pF, ptags = module.merge(module.platform(plate))
            pmesh = mesh_from_parts(f"PLT_core_{node}", pV, pF, ptags, mats,
                                    smooth=False)
            pobj = bpy.data.objects.new(f"{node}_platform", pmesh)
            coll.objects.link(pobj)
            pobj.parent = obj
            pobj["device_id"] = node
            pobj["part"] = "platform"
            objs.append(pobj)
    return objs


def export_glb(race, objs, assets_dir):
    out_dir = os.path.join(assets_dir, RACE_FOLDERS[race], "devices")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "device_constructor.glb")
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_extras=True,
        export_yup=True,
    )
    print(f"[device-sets] экспорт: {path} ({len(objs)} узлов)")


def main():
    a = parse_args()
    # чистим стартовую сцену полностью (куб/камера/свет лежат в дочерней
    # коллекции "Collection", а не в корне сцены)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    mats = make_materials()
    made = {}
    for race in a["races"]:
        if race not in RACE_MODULES:
            print(f"[device-sets] неизвестная раса: {race} — пропуск")
            continue
        made[race] = build_race(race, mats)
        print(f"[device-sets] {race}: {len(made[race])} объектов")
    out = os.path.abspath(a["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"[device-sets] сохранено: {out}")
    if a["export"]:
        for race, objs in made.items():
            export_glb(race, objs, os.path.expanduser(a["assets_dir"]))


if __name__ == "__main__":
    main()
