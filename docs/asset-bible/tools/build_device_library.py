# build_device_library.py — полная генерация наборов устройств (Blender 4.2+)
#
# Реализует пайплайн Asset Bible (00-pipeline.md) целиком:
#   * архетипы GN_Arch_* с атрибутами part_id / greeble_slot / panel_density
#   * стилевые киты GN_Style_Humans / GN_Style_Shuffie по races/*.md
#     (палитры и геометрический язык сверены с фактическими GLB-ассетами)
#   * мастер-группа GN_Device_Master
#   * объекты DEV_<race>_<id> для всех устройств из tools/devices.json
#     (каталог извлечён из DefaultTechCatalog.java)
#   * экспорт device_constructor.glb для каждой расы
#
# Запуск:
#   blender -b -P tools/build_device_library.py -- \
#       --out blends/devices.blend \
#       --assets-dir ~/.ascendancy/assets/races \
#       [--races humans,shuffie] [--no-export]
#
# Папки рас в assets-dir: humans -> humans/, shuffie -> bionics/ (см. devices.json).

import bpy
import json
import math
import os
import sys

# ----------------------------------------------------------------------------
# Аргументы и каталог устройств
# ----------------------------------------------------------------------------

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"out": "blends/devices.blend",
         "assets_dir": os.path.expanduser("~/.ascendancy/assets/races"),
         "races": ["humans", "shuffie"],
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


def load_catalog():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "devices.json"), encoding="utf-8") as f:
        return json.load(f)


DEVICE_TYPES = ["engine", "generator", "shield", "weapon_beam",
                "weapon_launcher", "scanner", "special"]
RACES = ["humans", "shuffie"]  # порядок = индекс Race Style в мастер-группе

# ----------------------------------------------------------------------------
# Палитры — фактические значения из races/humans.md и races/shuffie.md
# (сверены с shipyard_constructor.glb обеих рас 2026-07-08)
# ----------------------------------------------------------------------------

def srgb(hexcode):
    """#RRGGBB -> linear RGBA (Blender хранит цвета в linear)."""
    h = hexcode.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


PAL = {
    "humans": {
        # корабли Humans: Mat_Main / Mat_Seco / Mat_MetalD / Glow_Ora / Glow_Blu
        "hull":      {"col": srgb("#818184"), "metal": 0.48, "rough": 0.80},
        "hull_b":    {"col": srgb("#BFBFC2"), "metal": 0.00, "rough": 0.70},
        "detail":    {"col": srgb("#595959"), "metal": 1.00, "rough": 0.40},
        "dark":      {"col": srgb("#191919"), "metal": 0.00, "rough": 1.00},
        "emissive":  {"col": srgb("#FF6C27"), "strength": 4.0},   # главный акцент
        "emissive_b": {"col": srgb("#4B95FF"), "strength": 2.0},  # служебный
        "accent_default": srgb("#FF6C27"),
    },
    "shuffie": {
        # корабли Shuffie: белый «фарфор» + графитовые врезки; золото — из зданий
        "hull":      {"col": srgb("#F2F2F2"), "metal": 0.30, "rough": 0.15},
        "hull_b":    {"col": srgb("#E7E7E7"), "metal": 1.00, "rough": 0.20},
        "detail":    {"col": srgb("#3C3C3C"), "metal": 0.00, "rough": 0.45},
        "dark":      {"col": srgb("#5E6470"), "metal": 0.00, "rough": 0.30},
        "emissive":  {"col": srgb("#BFEFFF"), "strength": 2.0},   # резерв (в углубления)
        "emissive_b": {"col": srgb("#F0C37D"), "strength": 1.5},  # золото (орбитальные)
        "accent_default": srgb("#BFEFFF"),
    },
}

# ----------------------------------------------------------------------------
# Материалы. Эмиссия читает color-атрибут "AccentCol", который пишет стилевой
# кит (вход Accent Col) — контракт из races/*.md §4.
# ----------------------------------------------------------------------------

def make_materials():
    for race, pal in PAL.items():
        for role in ("hull", "hull_b", "detail", "dark"):
            name = f"MAT_{race}_{role}"
            if name in bpy.data.materials:
                continue
            m = bpy.data.materials.new(name)
            m.use_nodes = True
            b = m.node_tree.nodes.get("Principled BSDF")
            b.inputs["Base Color"].default_value = pal[role]["col"]
            b.inputs["Metallic"].default_value = pal[role]["metal"]
            b.inputs["Roughness"].default_value = pal[role]["rough"]
        for role in ("emissive", "emissive_b"):
            name = f"MAT_{race}_{role}"
            if name in bpy.data.materials:
                continue
            m = bpy.data.materials.new(name)
            m.use_nodes = True
            nt = m.node_tree
            b = nt.nodes.get("Principled BSDF")
            b.inputs["Base Color"].default_value = pal[role]["col"]
            b.inputs["Emission Strength"].default_value = pal[role]["strength"]
            attr = nt.nodes.new("ShaderNodeAttribute")
            attr.attribute_name = "AccentCol"
            attr.location = (-400, -300)
            nt.links.new(attr.outputs["Color"], b.inputs["Emission Color"])

# ----------------------------------------------------------------------------
# Утилиты построения нод-групп
# ----------------------------------------------------------------------------

def fresh_group(name):
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT",
                            socket_type="NodeSocketGeometry")
    return ng


def in_sock(ng, name, stype, default=None, min_=None, max_=None):
    s = ng.interface.new_socket(name, in_out="INPUT", socket_type=stype)
    if default is not None:
        s.default_value = default
    if min_ is not None:
        s.min_value = min_
    if max_ is not None:
        s.max_value = max_
    return s


def io_nodes(ng):
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    gi.location, go.location = (-900, 0), (900, 0)
    return gi, go


def node(ng, btype, loc=(0, 0), props=None, **sockets):
    """Создать ноду; sockets: имя_входа=константа | NodeSocket (линк)."""
    n = ng.nodes.new(btype)
    n.location = loc
    for k, v in (props or {}).items():
        setattr(n, k, v)
    for key, val in sockets.items():
        name = key.replace("_", " ")
        sock = n.inputs.get(name)
        if sock is None:
            raise RuntimeError(f"{btype}: нет входа '{name}'")
        if hasattr(val, "is_output") and val.is_output:
            ng.links.new(val, sock)
        else:
            sock.default_value = val
    return n


def nmath(ng, op, a, b=None, loc=(0, 0)):
    n = ng.nodes.new("ShaderNodeMath")
    n.operation = op
    n.location = loc
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if hasattr(v, "is_output") and v.is_output:
            ng.links.new(v, n.inputs[i])
        else:
            n.inputs[i].default_value = v
    return n.outputs[0]


def _rand(ng, dtype, lo, hi, seed, offset, loc, id_sock):
    """Random Value с выбором сокетов по имени+типу (не по индексам!).

    Раскладка сокетов Random Value различается между Blender 4.2 и 5.x —
    обращение по индексам молча пишет значения не туда (баг: все случайные
    размеры = 0). Ищем сокеты Min/Max нужного типа; если типизированных
    нет (динамический интерфейс новых версий) — берём единственные Min/Max.
    """
    n = ng.nodes.new("FunctionNodeRandomValue")
    n.data_type = dtype
    n.location = loc
    want = "VALUE" if dtype == "FLOAT" else dtype
    mins = [s for s in n.inputs if s.name == "Min" and s.type == want]
    maxs = [s for s in n.inputs if s.name == "Max" and s.type == want]
    if not mins:
        mins = [s for s in n.inputs if s.name == "Min"]
    if not maxs:
        maxs = [s for s in n.inputs if s.name == "Max"]
    if not mins or not maxs:
        raise RuntimeError("Random Value: не найдены сокеты Min/Max — "
                           "неизвестная версия Blender, поправьте _rand()")
    cast = float if dtype == "FLOAT" else int
    mins[0].default_value = cast(lo)
    maxs[0].default_value = cast(hi)
    if id_sock is not None:
        ng.links.new(id_sock, n.inputs["ID"])
    if hasattr(seed, "is_output"):
        if offset:
            seed = nmath(ng, "ADD", seed, offset, (loc[0] - 160, loc[1]))
        ng.links.new(seed, n.inputs["Seed"])
    else:
        n.inputs["Seed"].default_value = int(seed) + offset
    outs = [s for s in n.outputs if s.name == "Value" and s.type == want]
    if not outs:
        outs = [s for s in n.outputs if s.name == "Value"]
    return outs[0]


def rand_float(ng, lo, hi, seed, offset=0, loc=(0, 0), id_sock=None):
    """Random Value(FLOAT). seed — сокет или число; offset разводит каналы."""
    return _rand(ng, "FLOAT", lo, hi, seed, offset, loc, id_sock)


def rand_int(ng, lo, hi, seed, offset=0, loc=(0, 0), id_sock=None):
    return _rand(ng, "INT", lo, hi, seed, offset, loc, id_sock)


def store_attr(ng, geo, name, value, data_type="FLOAT", domain="FACE",
               selection=None, loc=(0, 0)):
    n = ng.nodes.new("GeometryNodeStoreNamedAttribute")
    n.data_type = data_type
    n.domain = domain
    n.location = loc
    ng.links.new(geo, n.inputs["Geometry"])
    n.inputs["Name"].default_value = name
    v = n.inputs["Value"]
    if hasattr(value, "is_output"):
        ng.links.new(value, v)
    else:
        v.default_value = value
    if selection is not None:
        ng.links.new(selection, n.inputs["Selection"])
    return n.outputs["Geometry"]


def named_attr(ng, name, data_type="FLOAT", loc=(0, 0)):
    n = ng.nodes.new("GeometryNodeInputNamedAttribute")
    n.data_type = data_type
    n.location = loc
    n.inputs["Name"].default_value = name
    return n.outputs["Attribute"]


def set_mat(ng, geo, mat_name, selection=None, loc=(0, 0)):
    n = ng.nodes.new("GeometryNodeSetMaterial")
    n.location = loc
    ng.links.new(geo, n.inputs["Geometry"])
    n.inputs["Material"].default_value = bpy.data.materials[mat_name]
    if selection is not None:
        ng.links.new(selection, n.inputs["Selection"])
    return n.outputs["Geometry"]


def transform(ng, geo, translation=None, rotation=None, scale=None, loc=(0, 0)):
    n = ng.nodes.new("GeometryNodeTransform")
    n.location = loc
    ng.links.new(geo, n.inputs["Geometry"])
    for key, val in (("Translation", translation), ("Rotation", rotation),
                     ("Scale", scale)):
        if val is None:
            continue
        if hasattr(val, "is_output"):
            ng.links.new(val, n.inputs[key])
        else:
            n.inputs[key].default_value = val
    return n.outputs["Geometry"]


def join(ng, *geos, loc=(0, 0)):
    n = ng.nodes.new("GeometryNodeJoinGeometry")
    n.location = loc
    for g in geos:
        ng.links.new(g, n.inputs["Geometry"])
    return n.outputs["Geometry"]


def combine_xyz(ng, x, y, z, loc=(0, 0)):
    n = ng.nodes.new("ShaderNodeCombineXYZ")
    n.location = loc
    for i, v in enumerate((x, y, z)):
        if hasattr(v, "is_output"):
            ng.links.new(v, n.inputs[i])
        else:
            n.inputs[i].default_value = v
    return n.outputs[0]


def tag_part(ng, geo, part_id, greeble=0.0, panel=0.2, loc=(0, 0)):
    """Контракт архетипа: part_id / greeble_slot / panel_density на гранях."""
    g = store_attr(ng, geo, "part_id", float(part_id), loc=loc)
    g = store_attr(ng, g, "greeble_slot", float(greeble),
                   loc=(loc[0] + 40, loc[1] - 40))
    g = store_attr(ng, g, "panel_density", float(panel),
                   loc=(loc[0] + 80, loc[1] - 80))
    return g


def size_scale(ng, gi, loc=(0, 0)):
    """Size Class 1..3 -> общий масштаб 0.7 / 1.0 / 1.4."""
    n = ng.nodes.new("ShaderNodeMapRange")
    n.location = loc
    ng.links.new(gi.outputs["Size Class"], n.inputs["Value"])
    n.inputs["From Min"].default_value = 1.0
    n.inputs["From Max"].default_value = 3.0
    n.inputs["To Min"].default_value = 0.7
    n.inputs["To Max"].default_value = 1.4
    return n.outputs["Result"]

# ----------------------------------------------------------------------------
# Архетипы (общие для рас). Ось устройства — Y: «нос»/эмиттер в +Y, сопло в -Y.
# part_id: 0 = корпус, 1 = акцентная зона («сердце» — правило 2 таксономии).
# ----------------------------------------------------------------------------

def arch_group(name):
    ng = fresh_group(name)
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Size Class", "NodeSocketInt", 2, 1, 3)
    gi, go = io_nodes(ng)
    return ng, gi, go


def finish_arch(ng, gi, go, geo):
    scl = size_scale(ng, gi, (500, -300))
    out = transform(ng, geo, scale=combine_xyz(
        ng, scl, scl, scl, (560, -220)), loc=(640, 0))
    ng.links.new(out, go.inputs["Geometry"])


def make_arch_engine():
    ng, gi, go = arch_group("GN_Arch_engine")
    seed = gi.outputs["Seed"]
    length = rand_float(ng, 1.6, 2.6, seed, 1, (-700, 300))
    radius = rand_float(ng, 0.45, 0.7, seed, 2, (-700, 160))
    # корпус — восьмигранная призма вдоль Y (фасочный язык Humans закладывается
    # архетипом как нейтральная база, кит Shuffie её сгладит)
    body = node(ng, "GeometryNodeMeshCylinder", (-450, 300),
                {"fill_type": "NGON"},
                Vertices=8, Radius=radius, Depth=length)
    body_g = transform(ng, body.outputs["Mesh"],
                       rotation=(1.5707963, 0, 0),
                       loc=(-260, 300))
    body_g = tag_part(ng, body_g, 0, greeble=1.0, panel=1.0, loc=(-80, 300))
    # сопло — усечённый конус в -Y, акцент
    noz_r = nmath(ng, "MULTIPLY", radius, 1.25, (-700, 0))
    noz = node(ng, "GeometryNodeMeshCone", (-450, 0),
               {"fill_type": "NGON"},
               Vertices=16, Radius_Top=radius, Radius_Bottom=noz_r,
               Depth=0.7)
    noz_y = nmath(ng, "MULTIPLY", length, -0.62, (-450, -160))
    noz_g = transform(ng, noz.outputs["Mesh"], rotation=(-1.5707963, 0, 0),
                      loc=(-260, 0))
    noz_g = transform(ng, noz_g,
                      translation=combine_xyz(ng, 0, noz_y, 0, (-260, -160)),
                      loc=(-100, 0))
    noz_g = tag_part(ng, noz_g, 1, loc=(60, 0))
    # топливный бак сверху
    tank = node(ng, "GeometryNodeMeshUVSphere", (-450, -320),
                Segments=16, Rings=8, Radius=0.32)
    tank_g = transform(ng, tank.outputs["Mesh"],
                       translation=(0, 0.3, 0.55),
                       scale=(1, 1.8, 1), loc=(-260, -320))
    tank_g = tag_part(ng, tank_g, 0, greeble=0.0, panel=0.0, loc=(-80, -320))
    finish_arch(ng, gi, go, join(ng, body_g, noz_g, tank_g, loc=(320, 100)))


def make_arch_generator():
    ng, gi, go = arch_group("GN_Arch_generator")
    seed = gi.outputs["Seed"]
    core_r = rand_float(ng, 0.5, 0.75, seed, 1, (-700, 300))
    core = node(ng, "GeometryNodeMeshUVSphere", (-450, 300),
                Segments=24, Rings=12, Radius=core_r)
    core_g = tag_part(ng, core.outputs["Mesh"], 1, loc=(-260, 300))
    # радиаторы — 4 плоских бокса радиально
    fins = []
    n_f = 4
    for i in range(n_f):
        ang = i * (2 * 3.14159265 / n_f)
        fin = node(ng, "GeometryNodeMeshCube", (-450, 100 - i * 90),
                   Size=(0.12, 0.9, 1.1))
        f_g = transform(ng, fin.outputs["Mesh"],
                        translation=(0.75 * math.cos(ang), 0,
                                     0.75 * math.sin(ang)),
                        rotation=(0, -ang, 0), loc=(-260, 100 - i * 90))
        fins.append(tag_part(ng, f_g, 0, greeble=1.0, panel=0.6,
                             loc=(-100, 100 - i * 90)))
    # несущая рама — куб вокруг ядра
    frame = node(ng, "GeometryNodeMeshCube", (-450, -300),
                 Size=(0.9, 0.9, 0.9))
    fr_g = tag_part(ng, frame.outputs["Mesh"], 0, greeble=1.0, panel=1.0,
                    loc=(-260, -300))
    finish_arch(ng, gi, go, join(ng, core_g, fr_g, *fins, loc=(320, 100)))


def make_arch_shield():
    ng, gi, go = arch_group("GN_Arch_shield")
    seed = gi.outputs["Seed"]
    base_r = rand_float(ng, 0.55, 0.8, seed, 1, (-700, 300))
    base = node(ng, "GeometryNodeMeshCylinder", (-450, 300),
                {"fill_type": "NGON"},
                Vertices=12, Radius=base_r, Depth=0.5)
    base_g = tag_part(ng, base.outputs["Mesh"], 0, greeble=1.0, panel=1.0,
                      loc=(-260, 300))
    # эмиттер — сфера на пилоне
    emit = node(ng, "GeometryNodeMeshUVSphere", (-450, 100),
                Segments=20, Rings=10, Radius=0.3)
    emit_g = transform(ng, emit.outputs["Mesh"], translation=(0, 0, 0.85),
                       loc=(-260, 100))
    emit_g = tag_part(ng, emit_g, 1, loc=(-100, 100))
    pylon = node(ng, "GeometryNodeMeshCylinder", (-450, -80),
                 {"fill_type": "NGON"},
                 Vertices=8, Radius=0.09, Depth=0.7)
    py_g = transform(ng, pylon.outputs["Mesh"], translation=(0, 0, 0.45),
                     loc=(-260, -80))
    py_g = tag_part(ng, py_g, 0, loc=(-100, -80))
    # дуга проекции — полукольцо из кривой
    arc = node(ng, "GeometryNodeCurveArc", (-450, -260),
               Resolution=24, Radius=1.05,
               Start_Angle=0.4, Sweep_Angle=2.35)
    prof = node(ng, "GeometryNodeCurvePrimitiveCircle", (-450, -420),
                Resolution=8, Radius=0.05)
    arc_m = node(ng, "GeometryNodeCurveToMesh", (-260, -260),
                 Curve=arc.outputs["Curve"],
                 Profile_Curve=prof.outputs["Curve"])
    arc_g = transform(ng, arc_m.outputs["Mesh"],
                      rotation=(1.5707963, 0, 0),
                      translation=(0, 0, 0.85), loc=(-100, -260))
    arc_g = tag_part(ng, arc_g, 1, loc=(60, -260))
    finish_arch(ng, gi, go, join(ng, base_g, emit_g, py_g, arc_g,
                                 loc=(320, 100)))


def make_arch_weapon_beam():
    ng, gi, go = arch_group("GN_Arch_weapon_beam")
    seed = gi.outputs["Seed"]
    barrel_l = rand_float(ng, 1.6, 2.6, seed, 1, (-700, 300))
    # казённик — бокс
    base = node(ng, "GeometryNodeMeshCube", (-450, 300),
                Size=(0.7, 0.9, 0.6))
    base_g = tag_part(ng, base.outputs["Mesh"], 0, greeble=1.0, panel=1.0,
                      loc=(-260, 300))
    # ствол вдоль +Y
    barrel = node(ng, "GeometryNodeMeshCylinder", (-450, 80),
                  {"fill_type": "NGON"},
                  Vertices=12, Radius=0.14, Depth=barrel_l)
    b_y = nmath(ng, "MULTIPLY", barrel_l, 0.5, (-450, -60))
    bar_g = transform(ng, barrel.outputs["Mesh"], rotation=(1.5707963, 0, 0),
                      loc=(-260, 80))
    bar_g = transform(ng, bar_g,
                      translation=combine_xyz(ng, 0, b_y, 0, (-260, -60)),
                      loc=(-100, 80))
    bar_g = tag_part(ng, bar_g, 0, panel=0.0, loc=(60, 80))
    # фокусатор на срезе ствола — акцент
    tip_y = nmath(ng, "ADD", barrel_l, 0.15, (-450, -220))
    tip = node(ng, "GeometryNodeMeshUVSphere", (-450, -320),
               Segments=16, Rings=8, Radius=0.22)
    tip_g = transform(ng, tip.outputs["Mesh"],
                      translation=combine_xyz(ng, 0, tip_y, 0, (-260, -220)),
                      scale=(1, 1.4, 1), loc=(-260, -320))
    tip_g = tag_part(ng, tip_g, 1, loc=(-80, -320))
    finish_arch(ng, gi, go, join(ng, base_g, bar_g, tip_g, loc=(320, 100)))


def make_arch_weapon_launcher():
    ng, gi, go = arch_group("GN_Arch_weapon_launcher")
    seed = gi.outputs["Seed"]
    # корпус-кассета
    body = node(ng, "GeometryNodeMeshCube", (-450, 300),
                Size=(1.1, 1.0, 0.8))
    body_g = tag_part(ng, body.outputs["Mesh"], 0, greeble=1.0, panel=1.0,
                      loc=(-260, 300))
    # ячейки: сетка точек на фронтальной плоскости, инстансы стволиков
    cells = rand_int(ng, 2, 4, seed, 1, (-700, 60))
    grid = node(ng, "GeometryNodeMeshGrid", (-450, 60),
                Size_X=0.8, Size_Y=0.55,
                Vertices_X=cells, Vertices_Y=cells)
    pts = node(ng, "GeometryNodeMeshToPoints", (-260, 60),
               {"mode": "VERTICES"},
               Mesh=grid.outputs["Mesh"], Radius=0.0)
    tube = node(ng, "GeometryNodeMeshCylinder", (-450, -160),
                {"fill_type": "NGON"},
                Vertices=8, Radius=0.09, Depth=0.5)
    tube_g = transform(ng, tube.outputs["Mesh"], rotation=(1.5707963, 0, 0),
                       loc=(-260, -160))
    tube_g = tag_part(ng, tube_g, 1, loc=(-100, -160))
    inst = node(ng, "GeometryNodeInstanceOnPoints", (-60, 60),
                Points=pts.outputs["Points"], Instance=tube_g)
    real = node(ng, "GeometryNodeRealizeInstances", (120, 60),
                Geometry=inst.outputs["Instances"])
    cells_g = transform(ng, real.outputs["Geometry"],
                        rotation=(1.5707963, 0, 0),
                        translation=(0, 0.55, 0.1), loc=(300, 60))
    finish_arch(ng, gi, go, join(ng, body_g, cells_g, loc=(420, 200)))


def make_arch_scanner():
    ng, gi, go = arch_group("GN_Arch_scanner")
    seed = gi.outputs["Seed"]
    dish_r = rand_float(ng, 0.6, 0.95, seed, 1, (-700, 300))
    # мачта
    mast = node(ng, "GeometryNodeMeshCylinder", (-450, 300),
                {"fill_type": "NGON"},
                Vertices=8, Radius=0.08, Depth=1.2)
    mast_g = transform(ng, mast.outputs["Mesh"], translation=(0, 0, 0.6),
                       loc=(-260, 300))
    mast_g = tag_part(ng, mast_g, 0, loc=(-100, 300))
    # тарелка — усечённый конус «блюдцем» вверх
    dish = node(ng, "GeometryNodeMeshCone", (-450, 100),
                {"fill_type": "NGON"},
                Vertices=24, Radius_Top=dish_r, Radius_Bottom=0.12,
                Depth=0.35)
    dish_g = transform(ng, dish.outputs["Mesh"], translation=(0, 0, 1.35),
                       loc=(-260, 100))
    dish_g = tag_part(ng, dish_g, 0, greeble=0.0, panel=0.3, loc=(-100, 100))
    # сенсор в фокусе — акцент
    sens = node(ng, "GeometryNodeMeshUVSphere", (-450, -100),
                Segments=16, Rings=8, Radius=0.14)
    sens_g = transform(ng, sens.outputs["Mesh"], translation=(0, 0, 1.65),
                       loc=(-260, -100))
    sens_g = tag_part(ng, sens_g, 1, loc=(-100, -100))
    # основание
    base = node(ng, "GeometryNodeMeshCube", (-450, -300),
                Size=(0.7, 0.7, 0.35))
    base_g = tag_part(ng, base.outputs["Mesh"], 0, greeble=1.0, panel=1.0,
                      loc=(-260, -300))
    finish_arch(ng, gi, go, join(ng, mast_g, dish_g, sens_g, base_g,
                                 loc=(320, 100)))


def make_arch_special():
    ng, gi, go = arch_group("GN_Arch_special")
    seed = gi.outputs["Seed"]
    # нестандартный силуэт: кольцо + ядро + несимметричный блок (по seed)
    ring_r = rand_float(ng, 0.8, 1.15, seed, 1, (-700, 300))
    circ = node(ng, "GeometryNodeCurvePrimitiveCircle", (-450, 300),
                Resolution=32, Radius=ring_r)
    prof = node(ng, "GeometryNodeCurvePrimitiveCircle", (-450, 160),
                Resolution=8, Radius=0.12)
    ring = node(ng, "GeometryNodeCurveToMesh", (-260, 300),
                Curve=circ.outputs["Curve"],
                Profile_Curve=prof.outputs["Curve"])
    ring_g = transform(ng, ring.outputs["Mesh"], rotation=(1.5707963, 0, 0),
                       loc=(-100, 300))
    ring_g = tag_part(ng, ring_g, 0, panel=0.0, loc=(60, 300))
    core = node(ng, "GeometryNodeMeshUVSphere", (-450, 0),
                Segments=20, Rings=10, Radius=0.45)
    core_g = tag_part(ng, core.outputs["Mesh"], 1, loc=(-260, 0))
    off_x = rand_float(ng, -0.6, 0.6, seed, 2, (-700, -200))
    blk = node(ng, "GeometryNodeMeshCube", (-450, -200),
               Size=(0.6, 0.8, 0.5))
    blk_g = transform(ng, blk.outputs["Mesh"],
                      translation=combine_xyz(ng, off_x, 0, -0.7,
                                              (-450, -340)),
                      loc=(-260, -200))
    blk_g = tag_part(ng, blk_g, 0, greeble=1.0, panel=1.0, loc=(-100, -200))
    finish_arch(ng, gi, go, join(ng, ring_g, core_g, blk_g, loc=(320, 100)))

# ----------------------------------------------------------------------------
# Стилевой кит Humans (races/humans.md):
# гранёный шейдинг, панелизация с рандомным смещением плит, гриблы из
# примитивов (баки/вентблоки/октопризмы), палитра #818184 + глоу #FF6C27.
# ----------------------------------------------------------------------------

def make_humans_panels():
    ng = fresh_group("GN_Style_Humans_Panels")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    gi, go = io_nodes(ng)
    dens = named_attr(ng, "panel_density", loc=(-700, -100))
    sel = nmath(ng, "GREATER_THAN", dens, 0.5, (-520, -100))
    idx = ng.nodes.new("GeometryNodeInputIndex")
    idx.location = (-700, -260)
    depth = rand_float(ng, 0.015, 0.05, gi.outputs["Seed"], 3, (-520, -260),
                       id_sock=idx.outputs[0])
    depth = nmath(ng, "MULTIPLY", depth, gi.outputs["Detail"], (-360, -260))
    ext = node(ng, "GeometryNodeExtrudeMesh", (-200, 0),
               {"mode": "FACES"},
               Mesh=gi.outputs["Geometry"], Individual=True)
    ng.links.new(sel, ext.inputs["Selection"])
    ng.links.new(depth, ext.inputs["Offset Scale"])
    shr = node(ng, "GeometryNodeScaleElements", (100, 0),
               {"domain": "FACE"},
               Geometry=ext.outputs["Mesh"], Scale=0.88)
    ng.links.new(ext.outputs["Top"], shr.inputs["Selection"])
    ng.links.new(shr.outputs["Geometry"], go.inputs["Geometry"])
    return ng


def make_humans_greebles():
    ng = fresh_group("GN_Style_Humans_Greebles")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    gi, go = io_nodes(ng)
    slot = named_attr(ng, "greeble_slot", loc=(-700, -140))
    sel = nmath(ng, "GREATER_THAN", slot, 0.5, (-520, -140))
    dens = nmath(ng, "MULTIPLY", gi.outputs["Detail"], 7.0, (-520, -280))
    dist = node(ng, "GeometryNodeDistributePointsOnFaces", (-320, 0),
                Mesh=gi.outputs["Geometry"])
    ng.links.new(sel, dist.inputs["Selection"])
    ng.links.new(dens, dist.inputs["Density"])
    ng.links.new(gi.outputs["Seed"], dist.inputs["Seed"])
    # три примитива-грибла: бак / вентблок / октопризма (язык реальных частей
    # Tank / Vent_Block / hull_angle из shipyard_constructor.glb)
    g1 = node(ng, "GeometryNodeMeshCube", (-320, -220), Size=(0.1, 0.1, 0.08))
    g2 = node(ng, "GeometryNodeMeshCylinder", (-320, -360),
              {"fill_type": "NGON"}, Vertices=8, Radius=0.05, Depth=0.12)
    g3 = node(ng, "GeometryNodeMeshUVSphere", (-320, -500),
              Segments=8, Rings=4, Radius=0.06)
    packs = []
    for i, gg in enumerate((g1, g2, g3)):
        out = gg.outputs.get("Mesh")
        m = set_mat(ng, out, "MAT_humans_detail", loc=(-160, -220 - i * 140))
        packs.append(m)
    pack = node(ng, "GeometryNodeGeometryToInstance", (0, -300))
    for p in packs:
        ng.links.new(p, pack.inputs["Geometry"])
    pick = rand_int(ng, 0, 2, gi.outputs["Seed"], 5, (0, -460))
    scl = rand_float(ng, 0.7, 1.6, gi.outputs["Seed"], 6, (0, -600))
    inst = node(ng, "GeometryNodeInstanceOnPoints", (200, 0),
                Points=dist.outputs["Points"],
                Instance=pack.outputs["Instances"],
                Pick_Instance=True)
    ng.links.new(pick, inst.inputs["Instance Index"])
    ng.links.new(dist.outputs["Rotation"], inst.inputs["Rotation"])
    ng.links.new(scl, inst.inputs["Scale"])
    real = node(ng, "GeometryNodeRealizeInstances", (400, 0),
                Geometry=inst.outputs["Instances"])
    out = join(ng, gi.outputs["Geometry"], real.outputs["Geometry"],
               loc=(580, 0))
    ng.links.new(out, go.inputs["Geometry"])
    return ng


def make_style_humans():
    make_humans_panels()
    make_humans_greebles()
    ng = fresh_group("GN_Style_Humans")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    in_sock(ng, "Accent Col", "NodeSocketColor", PAL["humans"]["accent_default"])
    gi, go = io_nodes(ng)
    # корпус
    g = set_mat(ng, gi.outputs["Geometry"], "MAT_humans_hull", loc=(-600, 0))
    # панелизация
    pnl = node(ng, "GeometryNodeGroup", (-420, 0))
    pnl.node_tree = bpy.data.node_groups["GN_Style_Humans_Panels"]
    ng.links.new(g, pnl.inputs["Geometry"])
    ng.links.new(gi.outputs["Seed"], pnl.inputs["Seed"])
    ng.links.new(gi.outputs["Detail"], pnl.inputs["Detail"])
    # гриблы
    grb = node(ng, "GeometryNodeGroup", (-240, 0))
    grb.node_tree = bpy.data.node_groups["GN_Style_Humans_Greebles"]
    ng.links.new(pnl.outputs["Geometry"], grb.inputs["Geometry"])
    ng.links.new(gi.outputs["Seed"], grb.inputs["Seed"])
    ng.links.new(gi.outputs["Detail"], grb.inputs["Detail"])
    # акцентная зона part_id==1 -> эмиссия
    pid = named_attr(ng, "part_id", loc=(-240, -260))
    acc_sel = nmath(ng, "GREATER_THAN", pid, 0.5, (-60, -260))
    g = set_mat(ng, grb.outputs["Geometry"], "MAT_humans_emissive",
                selection=acc_sel, loc=(60, 0))
    g = store_attr(ng, g, "AccentCol", gi.outputs["Accent Col"],
                   data_type="FLOAT_COLOR", domain="POINT", loc=(240, 0))
    # гранёный шейдинг — корабли Humans не сглаживаются
    flat = node(ng, "GeometryNodeSetShadeSmooth", (420, 0),
                Geometry=g, Shade_Smooth=False)
    ng.links.new(flat.outputs["Geometry"], go.inputs["Geometry"])
    return ng

# ----------------------------------------------------------------------------
# Стилевой кит Shuffie (races/shuffie.md):
# smooth + subdivision, утопленные графитовые кольца вместо панелей,
# редкие крупные капли-наросты, ахроматичный белый «фарфор», акцент —
# только в углублениях/эмиттерах.
# ----------------------------------------------------------------------------

def make_shuffie_skin():
    ng = fresh_group("GN_Style_Shuffie_Skin")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    gi, go = io_nodes(ng)
    # сглаживание: приём из races/shuffie.md §5 — Subdivision + Smooth
    lvl = nmath(ng, "MULTIPLY", gi.outputs["Detail"], 2.0, (-700, -140))
    lvl = nmath(ng, "ADD", lvl, 1.0, (-540, -140))
    lvl = nmath(ng, "ROUND", lvl, None, (-380, -140))
    sub = node(ng, "GeometryNodeSubdivisionSurface", (-220, 0),
               Mesh=gi.outputs["Geometry"])
    ng.links.new(lvl, sub.inputs["Level"])
    smo = node(ng, "GeometryNodeSetShadeSmooth", (-40, 0),
               Geometry=sub.outputs["Mesh"], Shade_Smooth=True)
    # утопленные тёмные кольца: полосы по Z (sin), только на корпусе part_id==0
    pos = ng.nodes.new("GeometryNodeInputPosition")
    pos.location = (-700, -320)
    sep = ng.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-540, -320)
    ng.links.new(pos.outputs[0], sep.inputs[0])
    ph = nmath(ng, "MULTIPLY", sep.outputs["Z"], 9.0, (-380, -320))
    ph = nmath(ng, "ADD", ph, gi.outputs["Seed"], (-220, -320))
    band = nmath(ng, "SINE", ph, None, (-60, -320))
    band_sel = nmath(ng, "GREATER_THAN", band, 0.86, (100, -320))
    pid = named_attr(ng, "part_id", loc=(-60, -460))
    body = nmath(ng, "LESS_THAN", pid, 0.5, (100, -460))
    both = nmath(ng, "MULTIPLY", band_sel, body, (260, -380))
    # лёгкое утапливание полосы внутрь по нормали
    nrm = ng.nodes.new("GeometryNodeInputNormal")
    nrm.location = (100, -600)
    vm = ng.nodes.new("ShaderNodeVectorMath")
    vm.operation = "SCALE"
    vm.location = (260, -600)
    ng.links.new(nrm.outputs[0], vm.inputs[0])
    vm.inputs["Scale"].default_value = -0.02
    setp = node(ng, "GeometryNodeSetPosition", (420, 0),
                Geometry=smo.outputs["Geometry"])
    ng.links.new(both, setp.inputs["Selection"])
    ng.links.new(vm.outputs[0], setp.inputs["Offset"])
    g = set_mat(ng, setp.outputs["Geometry"], "MAT_shuffie_detail",
                selection=both, loc=(600, 0))
    ng.links.new(g, go.inputs["Geometry"])
    return ng


def make_shuffie_nodes():
    ng = fresh_group("GN_Style_Shuffie_Nodes")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    gi, go = io_nodes(ng)
    slot = named_attr(ng, "greeble_slot", loc=(-700, -140))
    sel = nmath(ng, "GREATER_THAN", slot, 0.5, (-520, -140))
    # редкие и крупные капли (по факту исходников — не «сыпь»)
    dens = nmath(ng, "MULTIPLY", gi.outputs["Detail"], 1.2, (-520, -280))
    dist = node(ng, "GeometryNodeDistributePointsOnFaces", (-320, 0),
                Mesh=gi.outputs["Geometry"])
    ng.links.new(sel, dist.inputs["Selection"])
    ng.links.new(dens, dist.inputs["Density"])
    ng.links.new(gi.outputs["Seed"], dist.inputs["Seed"])
    drop = node(ng, "GeometryNodeMeshIcoSphere", (-320, -240),
                Radius=0.16, Subdivisions=2)
    d_g = set_mat(ng, drop.outputs["Mesh"], "MAT_shuffie_hull",
                  loc=(-160, -240))
    d_sm = node(ng, "GeometryNodeSetShadeSmooth", (0, -240),
                Geometry=d_g, Shade_Smooth=True)
    scl = rand_float(ng, 0.6, 1.8, gi.outputs["Seed"], 7, (0, -400))
    inst = node(ng, "GeometryNodeInstanceOnPoints", (200, 0),
                Points=dist.outputs["Points"],
                Instance=d_sm.outputs["Geometry"])
    ng.links.new(dist.outputs["Rotation"], inst.inputs["Rotation"])
    ng.links.new(scl, inst.inputs["Scale"])
    real = node(ng, "GeometryNodeRealizeInstances", (400, 0),
                Geometry=inst.outputs["Instances"])
    out = join(ng, gi.outputs["Geometry"], real.outputs["Geometry"],
               loc=(580, 0))
    ng.links.new(out, go.inputs["Geometry"])
    return ng


def make_style_shuffie():
    make_shuffie_skin()
    make_shuffie_nodes()
    ng = fresh_group("GN_Style_Shuffie")
    in_sock(ng, "Geometry", "NodeSocketGeometry")
    in_sock(ng, "Seed", "NodeSocketInt", 0)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    in_sock(ng, "Accent Col", "NodeSocketColor", PAL["shuffie"]["accent_default"])
    gi, go = io_nodes(ng)
    g = set_mat(ng, gi.outputs["Geometry"], "MAT_shuffie_hull", loc=(-600, 0))
    nod = node(ng, "GeometryNodeGroup", (-420, 0))
    nod.node_tree = bpy.data.node_groups["GN_Style_Shuffie_Nodes"]
    ng.links.new(g, nod.inputs["Geometry"])
    ng.links.new(gi.outputs["Seed"], nod.inputs["Seed"])
    ng.links.new(gi.outputs["Detail"], nod.inputs["Detail"])
    skin = node(ng, "GeometryNodeGroup", (-240, 0))
    skin.node_tree = bpy.data.node_groups["GN_Style_Shuffie_Skin"]
    ng.links.new(nod.outputs["Geometry"], skin.inputs["Geometry"])
    ng.links.new(gi.outputs["Seed"], skin.inputs["Seed"])
    ng.links.new(gi.outputs["Detail"], skin.inputs["Detail"])
    # акцент — только «сердце» устройства (part_id==1), правило из shuffie.md §4
    pid = named_attr(ng, "part_id", loc=(-240, -260))
    acc_sel = nmath(ng, "GREATER_THAN", pid, 0.5, (-60, -260))
    g = set_mat(ng, skin.outputs["Geometry"], "MAT_shuffie_emissive",
                selection=acc_sel, loc=(120, 0))
    g = store_attr(ng, g, "AccentCol", gi.outputs["Accent Col"],
                   data_type="FLOAT_COLOR", domain="POINT", loc=(300, 0))
    ng.links.new(g, go.inputs["Geometry"])
    return ng

# ----------------------------------------------------------------------------
# Мастер-группа (контракт 00-pipeline.md)
# ----------------------------------------------------------------------------

def make_master():
    ng = fresh_group("GN_Device_Master")
    in_sock(ng, "Device Type", "NodeSocketInt", 0, 0, len(DEVICE_TYPES) - 1)
    in_sock(ng, "Race Style", "NodeSocketInt", 0, 0, len(RACES) - 1)
    in_sock(ng, "Seed", "NodeSocketInt", 0, 0, 10 ** 6)
    in_sock(ng, "Size Class", "NodeSocketInt", 2, 1, 3)
    in_sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)
    gi, go = io_nodes(ng)

    sw_arch = ng.nodes.new("GeometryNodeIndexSwitch")
    sw_arch.data_type = "GEOMETRY"
    sw_arch.location = (-200, 0)
    while len(sw_arch.index_switch_items) < len(DEVICE_TYPES):
        sw_arch.index_switch_items.new()
    ng.links.new(gi.outputs["Device Type"], sw_arch.inputs["Index"])
    for i, t in enumerate(DEVICE_TYPES):
        g = ng.nodes.new("GeometryNodeGroup")
        g.node_tree = bpy.data.node_groups[f"GN_Arch_{t}"]
        g.location = (-500, 350 - i * 120)
        ng.links.new(gi.outputs["Seed"], g.inputs["Seed"])
        ng.links.new(gi.outputs["Size Class"], g.inputs["Size Class"])
        ng.links.new(g.outputs["Geometry"], sw_arch.inputs[i + 1])

    sw_style = ng.nodes.new("GeometryNodeIndexSwitch")
    sw_style.data_type = "GEOMETRY"
    sw_style.location = (300, 0)
    while len(sw_style.index_switch_items) < len(RACES):
        sw_style.index_switch_items.new()
    ng.links.new(gi.outputs["Race Style"], sw_style.inputs["Index"])
    for i, race in enumerate(RACES):
        g = ng.nodes.new("GeometryNodeGroup")
        g.node_tree = bpy.data.node_groups[f"GN_Style_{race.capitalize()}"]
        g.location = (100, 250 - i * 200)
        ng.links.new(sw_arch.outputs[0], g.inputs["Geometry"])
        ng.links.new(gi.outputs["Seed"], g.inputs["Seed"])
        ng.links.new(gi.outputs["Detail"], g.inputs["Detail"])
        ng.links.new(g.outputs["Geometry"], sw_style.inputs[i + 1])

    real = node(ng, "GeometryNodeRealizeInstances", (520, 0),
                Geometry=sw_style.outputs[0])
    ng.links.new(real.outputs["Geometry"], go.inputs["Geometry"])
    return ng

# ----------------------------------------------------------------------------
# Генерация DEV-объектов и экспорт
# ----------------------------------------------------------------------------

def socket_ids(ngroup):
    return {s.name: s.identifier for s in ngroup.interface.items_tree
            if getattr(s, "in_out", None) == "INPUT"}


def build_devices(catalog, races, master):
    sid = socket_ids(master)
    made = {}
    for r_i, race in enumerate(races):
        coll = bpy.data.collections.new(f"COL_devices_{race}")
        bpy.context.scene.collection.children.link(coll)
        objs = []
        for d_i, dev in enumerate(catalog["devices"]):
            mesh = bpy.data.meshes.new(f"DEV_{race}_{dev['id']}")
            obj = bpy.data.objects.new(f"{d_i:03d}_{race}_{dev['id']}", mesh)
            coll.objects.link(obj)
            row = DEVICE_TYPES.index(dev["type"])
            col_i = sum(1 for x in catalog["devices"][:d_i]
                        if x["type"] == dev["type"])
            obj.location = (col_i * 4.0, row * 6.0 + (0 if race == races[0]
                                                      else 70.0), 0.0)
            s = dev.get("scale", 1.0)
            obj.scale = (s, s, s)
            mod = obj.modifiers.new("Device", "NODES")
            mod.node_group = master
            mod[sid["Device Type"]] = DEVICE_TYPES.index(dev["type"])
            mod[sid["Race Style"]] = RACES.index(race)
            mod[sid["Seed"]] = int(dev["seed"])
            mod[sid["Size Class"]] = int(dev["size"])
            mod[sid["Detail"]] = 1.0
            obj["device_id"] = dev["id"]
            obj["display_name"] = dev["name"]
            obj["tech_level"] = dev["level"]
            obj["domain"] = dev["domain"]
            objs.append(obj)
        made[race] = objs
    return made


def export_glb(catalog, made, assets_dir):
    for race, objs in made.items():
        folder = catalog["races"].get(race, race)
        out_dir = os.path.join(assets_dir, folder, "devices")
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
            export_extras=True,   # device_id/display_name/tech_level в extras
            export_yup=True,
        )
        print(f"[device-lib] экспорт: {path} ({len(objs)} устройств)")


def make_preview_scene(master):
    """DEV_preview + камера/свет — чтобы render_device_set.py работал как есть."""
    sc = bpy.context.scene
    mesh = bpy.data.meshes.new("DEV_preview")
    obj = bpy.data.objects.new("DEV_preview", mesh)
    sc.collection.objects.link(obj)
    obj.location = (0, -20, 0)
    mod = obj.modifiers.new("Device", "NODES")
    mod.node_group = master

    cam = bpy.data.objects.new("CAM_icon", bpy.data.cameras.new("CAM_icon"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.0
    cam.location, cam.rotation_euler = (4, -24, 3), (1.0, 0, 0.785)
    sc.collection.objects.link(cam)
    sc.camera = cam
    for nm, loc, e in (("key", (4, -22, 5), 1000),
                       ("fill", (-4, -23, 2), 300),
                       ("rim", (-2, -15, 4), 600)):
        ld = bpy.data.lights.new(f"L_{nm}", "AREA")
        ld.energy = e
        lo = bpy.data.objects.new(f"L_{nm}", ld)
        lo.location = loc
        sc.collection.objects.link(lo)
    # 4.2: BLENDER_EEVEE_NEXT; 4.5+/5.x: снова BLENDER_EEVEE
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 1024


def main():
    a = parse_args()
    catalog = load_catalog()

    # чистая сцена
    for ob in list(bpy.context.scene.collection.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    make_materials()
    make_arch_engine()
    make_arch_generator()
    make_arch_shield()
    make_arch_weapon_beam()
    make_arch_weapon_launcher()
    make_arch_scanner()
    make_arch_special()
    make_style_humans()
    make_style_shuffie()
    master = make_master()
    make_preview_scene(master)

    made = build_devices(catalog, a["races"], master)
    total = sum(len(v) for v in made.values())
    print(f"[device-lib] создано {total} DEV-объектов "
          f"({', '.join(a['races'])})")

    out = os.path.abspath(a["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"[device-lib] сохранено: {out}")

    if a["export"]:
        export_glb(catalog, made, os.path.expanduser(a["assets_dir"]))


if __name__ == "__main__":
    main()
