# build_building_sets.py — сборка наборов зданий Humans + Core
# (Blender 4.2+/5.x)
#
# Геометрия строится чистым Python/numpy (building_meshes.py +
# building_recipes_humans_{industrial,scifi}.py / building_recipes_core.py,
# силуэты согласованы по refs/buildings), Blender используется только для
# материалов, шейдинга и экспорта GLB — как в build_device_sets.py.
#
# Запуск:
#   blender -b -P tools/build_building_sets.py -- \
#       --styles industrial[,scifi][,core] \
#       --assets-dir ~/.ascendancy/assets/races \
#       [--out blends/buildings_gen.blend] [--no-export]
#
# Выход per style (старый building_constructor.glb Humans НЕ трогаем):
#   industrial -> <assets-dir>/humans/buildings/building_constructor_industrial.glb
#   scifi      -> <assets-dir>/humans/buildings/building_constructor_scifi.glb
#   core       -> <assets-dir>/core/buildings/building_constructor.glb
#
# Каждый объект несёт glTF-extras: building_id, display_name, style,
# kind (building / orbital / prop), level. Порядок узлов фиксирован
# каталогом набора (building_catalog.RECIPES / building_catalog_core.RECIPES).

import os
import sys
import math

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import building_recipes_humans_industrial
import building_recipes_humans_scifi
import building_recipes_core
from building_catalog import RECIPES, build
from building_catalog_core import RECIPES as RECIPES_CORE

# style -> (модуль рецептов, каталог, раса, имя GLB)
SETS = {
    "industrial": (building_recipes_humans_industrial, RECIPES, "humans",
                   "building_constructor_industrial.glb"),
    "scifi": (building_recipes_humans_scifi, RECIPES, "humans",
              "building_constructor_scifi.glb"),
    "core": (building_recipes_core, RECIPES_CORE, "core",
             "building_constructor.glb"),
}

# ----------------------------------------------------------------------------
# Материалы: tag -> (hex, metallic, roughness, emission_strength)
# Палитра синхронизирована с preview_buildings.PALETTE и races/humans.md
# ----------------------------------------------------------------------------
MATS = {
    "conc":    ("#9AA0A6", 0.10, 0.75, 0),
    "conc_l":  ("#C2C7CC", 0.10, 0.70, 0),
    "conc_d":  ("#62686E", 0.15, 0.75, 0),
    "steel":   ("#7E8890", 0.85, 0.40, 0),
    "dark":    ("#363B41", 0.40, 0.55, 0),
    "rust":    ("#A85C2E", 0.30, 0.60, 0),
    "glass":   ("#9FC4D8", 0.30, 0.10, 0),
    "glass_g": ("#AEDCC2", 0.20, 0.15, 0),
    "green":   ("#4E7A3C", 0.05, 0.80, 0),
    "screen":  ("#35C8DC", 0.00, 0.40, 2.5),
    "accent":  ("#E06A2B", 0.00, 0.40, 3.0),
    "redline": ("#C43B2A", 0.30, 0.30, 1.5),
    "white":   ("#E2E6E9", 0.55, 0.30, 0),
    "silver":  ("#B9C2CA", 0.95, 0.20, 0),
    "bglow":   ("#4FC3FF", 0.00, 0.40, 4.0),
    "gglow":   ("#7CE87C", 0.00, 0.40, 2.5),
    "pglow":   ("#A97BFF", 0.00, 0.40, 3.0),
    # --- дополнения набора core (синхронизировано с preview_buildings)
    "plate":   ("#D5DADF", 0.20, 0.60, 0),
    "grass":   ("#5F9E44", 0.00, 0.90, 0),
    "soil":    ("#6B4A2F", 0.00, 0.90, 0),
    "red":     ("#C0392B", 0.20, 0.50, 0),
    "sand":    ("#C9B48A", 0.10, 0.80, 0),
    "copper":  ("#B87333", 0.80, 0.35, 0),
    "solar":   ("#2B3D66", 0.40, 0.30, 0),
    "pink":    ("#C79AA6", 0.10, 0.70, 0),
    "gold":    ("#C89B3C", 0.70, 0.35, 0),
    "teal":    ("#3E9A92", 0.30, 0.50, 0),
    "blue":    ("#4A6FA5", 0.30, 0.50, 0),
    "ygreen":  ("#A8B23A", 0.20, 0.60, 0),
    "dgreen":  ("#39543F", 0.20, 0.60, 0),
    "graph":   ("#3A3F45", 0.50, 0.35, 0),
}
GLASS_ALPHA = {"glass": 0.45, "glass_g": 0.55}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"styles": ["industrial", "scifi"],
         "assets_dir": os.path.expanduser("~/.ascendancy/assets/races"),
         "out": "blends/buildings_gen.blend",
         "export": True}
    i = 0
    while i < len(argv):
        k = argv[i].lstrip("-").replace("-", "_")
        if k == "no_export":
            a["export"] = False
            i += 1
            continue
        v = argv[i + 1]
        if k == "styles":
            a["styles"] = [s.strip() for s in v.split(",")]
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
        name = f"MAT_bld_{tag}"
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
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
            if tag in GLASS_ALPHA:
                b.inputs["Alpha"].default_value = GLASS_ALPHA[tag]
                m.blend_method = "BLEND"
        mats[tag] = m
    return mats


def mesh_from_parts(name, V, F, tags, mats, smooth=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F])
    mesh.validate()
    mesh.update()
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
    else:  # validate() мог отбросить дегенеративные грани
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


def build_style(style, mats, off_y=0.0):
    """off_y разносит сетки нескольких стилей в одном .blend; при сборке
    одного стиля раскладка начинается от начала координат."""
    module, recipes, race, _ = SETS[style]
    coll = bpy.data.collections.new(f"COL_buildings_{race}_{style}")
    bpy.context.scene.collection.children.link(coll)
    objs = []
    for i, (bld_id, disp, recipe, lvl, kind) in enumerate(recipes):
        V, F, tags = build(module, recipe, lvl, seed=i)
        mesh = mesh_from_parts(f"BLD_{style}_{bld_id}", V, F, tags, mats)
        obj = bpy.data.objects.new(f"{i:03d}_{style}_{bld_id}", mesh)
        coll.objects.link(obj)
        row, col_i = divmod(i, 6)
        obj.location = (col_i * 6.0, off_y + row * 6.0, 0.0)
        add_edge_split(obj)
        obj["building_id"] = bld_id
        obj["display_name"] = disp
        obj["style"] = style
        obj["kind"] = kind
        obj["level"] = lvl
        objs.append(obj)
    return objs


def export_glb(style, objs, assets_dir):
    _, _, race, fname = SETS[style]
    out_dir = os.path.join(assets_dir, race, "buildings")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname)
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
    print(f"[building-sets] экспорт: {path} ({len(objs)} узлов)")


def main():
    a = parse_args()
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    mats = make_materials()
    made = {}
    for style in a["styles"]:
        if style not in SETS:
            print(f"[building-sets] неизвестный стиль: {style} — пропуск")
            continue
        made[style] = build_style(style, mats, off_y=60.0 * len(made))
        print(f"[building-sets] {style}: {len(made[style])} объектов")
    out = os.path.abspath(a["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"[building-sets] сохранено: {out}")
    if a["export"]:
        for style, objs in made.items():
            export_glb(style, objs, os.path.expanduser(a["assets_dir"]))


if __name__ == "__main__":
    main()
