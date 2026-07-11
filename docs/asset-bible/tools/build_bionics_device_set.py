# build_bionics_device_set.py — набор устройств Shuffie/bionics из частей
# конструктора кораблей (Blender 4.2+/5.x, headless).
#
# Идея: все 36 устройств DeviceCatalog заимствуются из
# bionics/ships/shipyard_constructor.glb — флот остаётся эталоном стиля:
#   оружие      — те же модели, что орбитальное оружие зданий v2
#                 (Laser turret / Wave cannon / Gauss cannon);
#   двигатели   — Engine 1..3, инерционный компенсатор — Engine 4;
#   star lane   — Hull 8;  генератор — Hull 2;  сканер — Antenna;
#   щит         — Panel 4, развёрнутая вертикально;
#   colony base — Saucer сверху + Conjunction 2 снизу;
#   invasion    — Shuttle 1.001.
# Поколения одного устройства различаются РАЗМЕРОМ (масштаб узла) и
# ЦВЕТОМ (категорийный multiply-тинт поверх фарфоровой текстуры, сила
# тинта растёт с уровнем; паттерн Mix-Multiply экспортируется в
# baseColorFactor glTF).
#
# Запуск:
#   blender -b -P tools/build_bionics_device_set.py -- \
#       [--assets-dir ~/.ascendancy/assets/races] [--out blends/bionics_devices.blend]
#
# Выход: <assets-dir>/bionics/devices/device_constructor.glb — 36 узлов
# в порядке device_catalog.RECIPES (адресация по индексу или
# extras.device_id, как у humans/core).

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from device_catalog import RECIPES
from build_shuffie_building_set import (import_glb, find_groups,
                                        mesh_children, downscale_images)

SRC_SHIPS = "~/.ascendancy/assets/races/bionics/ships/shipyard_constructor.glb"
PI = math.pi

MAX_TEX = 512
MAX_TEX_DATA = 256

# recipe -> (группа|{level: группа}, категорийный цвет тинта, базовый
#            габарит (макс. измерение при level=1), rx, rz)
MAP = {
    "engine": ({1: "Engine 1_44", 2: "Engine 2_30", 3: "Engine 3_42"},
               (1.0, 0.62, 0.52), 1.15, 0, 0),
    "inertia": ("Engine 4_43", (1.0, 0.85, 0.55), 1.2, 0, 0),
    "star_lane": ("Hull 8_20", (0.55, 0.75, 1.0), 1.35, 0, 0),
    "generator": ("Hull 2_26", (0.5, 0.95, 0.95), 1.35, 0, 0),
    "shield": ("Panel 4_14", (0.75, 1.0, 0.6), 1.35, PI / 2, 0),
    "scanner": ("Antenna_38", (0.82, 0.66, 1.0), 1.25, 0, 0),
    "beam:lazer": ("Laser turret_36", (1.0, 0.8, 0.5), 1.25, 0, 0),
    "beam:phazer": ("Wave cannon_35", (0.5, 0.9, 1.0), 1.35, 0, 0),
    "rapid:lazer": ("Gauss cannon_45", (1.0, 0.65, 0.45), 1.55, 0, 0),
    "rapid:phazer": ("Gauss cannon_45", (0.8, 0.6, 1.0), 1.55, 0, 0),
    "aux:invasion": ("Shuttle 1.001_54", None, 1.5, 0, 0),
    "aux:colony": (None, None, 1.6, 0, 0),  # комбо Saucer + Conjunction 2
}
LEVEL_SCALE = {1: 0.84, 2: 1.0, 3: 1.16, 4: 1.3, 5: 1.44}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"assets_dir": os.path.expanduser("~/.ascendancy/assets/races"),
         "out": "blends/bionics_devices.blend"}
    i = 0
    while i < len(argv):
        a[argv[i].lstrip("-").replace("-", "_")] = argv[i + 1]
        i += 2
    return a


def tint_material(base, name, rgb, t):
    """Копия материала с multiply-тинтом lerp(white, rgb, t) поверх
    baseColor-текстуры; экспортируется как baseColorFactor."""
    if rgb is None or t <= 0:
        return base
    col = tuple(1.0 + (c - 1.0) * t for c in rgb)
    m = base.copy()
    m.name = name
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    link = b.inputs["Base Color"].links[0]
    tex_out = link.from_socket
    nt.links.remove(link)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    sock_a = next(s for s in mix.inputs if s.identifier == "A_Color")
    sock_b = next(s for s in mix.inputs if s.identifier == "B_Color")
    sock_out = next(s for s in mix.outputs if s.identifier == "Result_Color")
    nt.links.new(tex_out, sock_a)
    sock_b.default_value = (*col, 1.0)
    nt.links.new(sock_out, b.inputs["Base Color"])
    return m


def merge_group(group_empty, rx=0.0, rz=0.0):
    """Копии мешей группы -> один объект; ориентация rx/rz; центр (0,0),
    низ на z=0."""
    parts = []
    for o in mesh_children(group_empty):
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        mw = o.matrix_world.copy()
        c.parent = None
        c.matrix_world = mw
        parts.append(c)
    target = parts[0]
    if len(parts) > 1:
        with bpy.context.temp_override(active_object=target,
                                       selected_editable_objects=parts):
            bpy.ops.object.join()
    rot = Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(rx, 4, "X")
    target.data.transform(rot @ target.matrix_world)
    target.matrix_world = Matrix.Identity(4)
    xs = [v.co for v in target.data.vertices]
    lo = Vector((min(v.x for v in xs), min(v.y for v in xs),
                 min(v.z for v in xs)))
    hi = Vector((max(v.x for v in xs), max(v.y for v in xs),
                 max(v.z for v in xs)))
    c = (lo + hi) / 2
    target.data.transform(Matrix.Translation((-c.x, -c.y, -lo.z)))
    return target, (hi - lo)


def normalize(obj, ext, base_size):
    """Отмасштабировать меш так, чтобы max-габарит = base_size (масштаб
    уровня добавляется трансформом узла)."""
    s = base_size / max(ext.x, ext.y, ext.z)
    obj.data.transform(Matrix.Scale(s, 4))
    return obj


def colony_combo(groups, base_size):
    """AUX_COLONY_BASE: Saucer сверху + Conjunction 2 снизу."""
    conj, cext = merge_group(groups["Conjunction 2_31"])
    sauc, sext = merge_group(groups["Saucer_13"])
    normalize(conj, cext, base_size)
    # блюдце заметно уже развилки (лучи должны читаться) и сидит на её верхе
    normalize(sauc, sext, base_size * 0.68)
    ch = max(v.co.z for v in conj.data.vertices)
    sauc.data.transform(Matrix.Translation((0, 0, ch * 0.92)))
    with bpy.context.temp_override(active_object=conj,
                                   selected_editable_objects=[conj, sauc]):
        bpy.ops.object.join()
    return conj


def main():
    a = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs, mats = import_glb(SRC_SHIPS)
    groups = find_groups(objs)
    downscale_images(MAX_TEX, MAX_TEX_DATA)
    base_mat = next(m for m in mats if m.name.startswith("Base"))

    out_objs = []
    mat_cache = {}
    for i, (dev_id, disp, recipe, lvl) in enumerate(RECIPES):
        gspec, family, base_size, rx, rz = MAP[recipe]
        if recipe == "aux:colony":
            obj = colony_combo(groups, base_size)
        else:
            gname = gspec[lvl] if isinstance(gspec, dict) else gspec
            g = groups.get(gname)
            if g is None:
                raise RuntimeError(f"группа не найдена: {gname}")
            obj, ext = merge_group(g, rx=rx, rz=rz)
            normalize(obj, ext, base_size)
        # категорийный тинт, сила растёт с поколением
        t = 0.0 if lvl == 0 else 0.14 + 0.13 * lvl
        if recipe == "inertia":
            t = 0.45
        key = (recipe, lvl)
        if key not in mat_cache:
            mat_cache[key] = tint_material(base_mat,
                                           f"Base_{recipe.replace(':', '_')}_l{lvl}",
                                           family, t)
        for slot in obj.material_slots:
            slot.material = mat_cache[key]
        obj.name = f"{i:03d}_{dev_id}"
        row, col = divmod(i, 8)
        obj.location = (col * 3.0, row * 3.0, 0.0)
        s = LEVEL_SCALE.get(lvl, 1.0)
        obj.scale = (s, s, s)
        obj["device_id"] = dev_id
        obj["display_name"] = disp
        obj["tech_level"] = lvl
        obj["style"] = "shuffie"
        out_objs.append(obj)

    for ob in list(bpy.data.objects):
        if ob not in out_objs:
            bpy.data.objects.remove(ob, do_unlink=True)

    out = os.path.abspath(a["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"[bionics-devices] сохранено: {out}")

    out_dir = os.path.join(os.path.expanduser(a["assets_dir"]),
                           "bionics", "devices")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "device_constructor.glb")
    for o in bpy.data.objects:
        o.select_set(o in out_objs)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB",
                              use_selection=True, export_apply=True,
                              export_extras=True, export_yup=True)
    print(f"[bionics-devices] экспорт: {path} ({len(out_objs)} узлов)")


if __name__ == "__main__":
    main()
