# geonodes_scaffold.py — создаёт каркас пайплайна Asset Bible в новом .blend
#
# Запуск:
#   blender -b -P tools/geonodes_scaffold.py -- --out blends/devices.blend
#
# Что создаёт:
#   * нод-группы архетипов GN_Arch_* с контрактным интерфейсом (заглушки)
#   * стилевые киты GN_Style_Humans / GN_Style_Shuffie (заглушки)
#   * мастер-группу GN_Device_Master (Device Type / Race Style / Seed /
#     Size Class / Detail) с switch-логикой архетипов и стилей
#   * материалы MAT_<race>_* по палитрам из races/*.md
#   * объект DEV_preview с модификатором + камеру, свет, настройки рендера
#
# Дальше киты и архетипы наполняются вручную в Blender — интерфейсы уже
# зафиксированы, контракт из 00-pipeline.md соблюдён.

import bpy
import sys
import os

DEVICE_TYPES = ["engine", "generator", "shield", "weapon_beam",
                "weapon_launcher", "scanner", "special"]
RACES = {
    "humans":  {"hull": (0.61, 0.64, 0.66), "accent": (0.25, 0.66, 1.00)},
    "shuffie": {"hull": (0.85, 0.81, 0.75), "accent": (0.49, 1.00, 0.37)},
}


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = "devices.blend"
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    return out


def _new_group(name):
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT",
                            socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT",
                            socket_type="NodeSocketGeometry")
    n_in = ng.nodes.new("NodeGroupInput")
    n_out = ng.nodes.new("NodeGroupOutput")
    n_in.location, n_out.location = (-400, 0), (400, 0)
    ng.links.new(n_in.outputs["Geometry"], n_out.inputs["Geometry"])
    return ng


def _sock(ng, name, stype, default=None, min_=None, max_=None):
    s = ng.interface.new_socket(name, in_out="INPUT", socket_type=stype)
    if default is not None:
        s.default_value = default
    if min_ is not None:
        s.min_value = min_
    if max_ is not None:
        s.max_value = max_
    return s


def make_materials():
    for race, pal in RACES.items():
        for role, col in (("hull", pal["hull"]), ("emissive", pal["accent"])):
            name = f"MAT_{race}_{role}"
            if name in bpy.data.materials:
                continue
            m = bpy.data.materials.new(name)
            m.use_nodes = True
            bsdf = m.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            if role == "emissive":
                bsdf.inputs["Emission Color"].default_value = (*col, 1.0)
                bsdf.inputs["Emission Strength"].default_value = 5.0
            else:
                bsdf.inputs["Metallic"].default_value = 0.8
                bsdf.inputs["Roughness"].default_value = 0.45


def make_archetypes():
    for t in DEVICE_TYPES:
        ng = _new_group(f"GN_Arch_{t}")
        # контрактные входы архетипа
        for nm, st, dv in (("Seed", "NodeSocketInt", 0),
                           ("Size Class", "NodeSocketInt", 2)):
            if nm not in [s.name for s in ng.interface.items_tree]:
                _sock(ng, nm, st, dv)
        # TODO вручную: база формы + атрибуты part_id / greeble_slot /
        # panel_density / mount_point (Store Named Attribute)


def make_style_kits():
    for race in RACES:
        ng = _new_group(f"GN_Style_{race.capitalize()}")
        for nm, st, dv in (("Seed", "NodeSocketInt", 0),
                           ("Detail", "NodeSocketFloat", 1.0)):
            if nm not in [s.name for s in ng.interface.items_tree]:
                _sock(ng, nm, st, dv)
        _sock(ng, "Accent Col", "NodeSocketColor",
              (*RACES[race]["accent"], 1.0))
        # TODO вручную: панелизация/рельеф, гриблы, назначение материалов


def make_master():
    ng = _new_group("GN_Device_Master")
    for nm, dv, mn, mx in (("Device Type", 0, 0, len(DEVICE_TYPES) - 1),
                           ("Race Style", 0, 0, len(RACES) - 1),
                           ("Seed", 0, 0, 10**6),
                           ("Size Class", 2, 1, 3)):
        if nm not in [s.name for s in ng.interface.items_tree]:
            _sock(ng, nm, "NodeSocketInt", dv, mn, mx)
    if "Detail" not in [s.name for s in ng.interface.items_tree]:
        _sock(ng, "Detail", "NodeSocketFloat", 1.0, 0.0, 1.0)

    n_in = next(n for n in ng.nodes if n.type == "GROUP_INPUT")
    n_out = next(n for n in ng.nodes if n.type == "GROUP_OUTPUT")
    for l in list(ng.links):
        ng.links.remove(l)

    # switch по архетипам
    sw_arch = ng.nodes.new("GeometryNodeIndexSwitch")
    sw_arch.data_type = "GEOMETRY"
    sw_arch.location = (-100, 0)
    while len(sw_arch.index_switch_items) < len(DEVICE_TYPES):
        sw_arch.index_switch_items.new()
    ng.links.new(n_in.outputs["Device Type"], sw_arch.inputs["Index"])
    for i, t in enumerate(DEVICE_TYPES):
        g = ng.nodes.new("GeometryNodeGroup")
        g.node_tree = bpy.data.node_groups[f"GN_Arch_{t}"]
        g.location = (-350, 250 - i * 130)
        ng.links.new(n_in.outputs["Seed"], g.inputs["Seed"])
        ng.links.new(n_in.outputs["Size Class"], g.inputs["Size Class"])
        ng.links.new(g.outputs["Geometry"], sw_arch.inputs[i + 1])

    # switch по стилевым китам
    sw_style = ng.nodes.new("GeometryNodeIndexSwitch")
    sw_style.data_type = "GEOMETRY"
    sw_style.location = (250, 0)
    while len(sw_style.index_switch_items) < len(RACES):
        sw_style.index_switch_items.new()
    ng.links.new(n_in.outputs["Race Style"], sw_style.inputs["Index"])
    for i, race in enumerate(RACES):
        g = ng.nodes.new("GeometryNodeGroup")
        g.node_tree = bpy.data.node_groups[f"GN_Style_{race.capitalize()}"]
        g.location = (80, 200 - i * 160)
        ng.links.new(sw_arch.outputs[0], g.inputs["Geometry"])
        ng.links.new(n_in.outputs["Seed"], g.inputs["Seed"])
        ng.links.new(n_in.outputs["Detail"], g.inputs["Detail"])
        ng.links.new(g.outputs["Geometry"], sw_style.inputs[i + 1])
    ng.links.new(sw_style.outputs[0], n_out.inputs["Geometry"])
    return ng


def make_scene(master):
    sc = bpy.context.scene
    for ob in list(sc.collection.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    mesh = bpy.data.meshes.new("DEV_preview")
    obj = bpy.data.objects.new("DEV_preview", mesh)
    sc.collection.objects.link(obj)
    mod = obj.modifiers.new("Device", "NODES")
    mod.node_group = master

    cam = bpy.data.objects.new("CAM_icon", bpy.data.cameras.new("CAM_icon"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.0
    cam.location, cam.rotation_euler = (4, -4, 3), (1.0, 0, 0.785)
    sc.collection.objects.link(cam)
    sc.camera = cam

    for nm, loc, e in (("key", (4, -2, 5), 1000),
                       ("fill", (-4, -3, 2), 300),
                       ("rim", (-2, 5, 4), 600)):
        ld = bpy.data.lights.new(f"L_{nm}", "AREA")
        ld.energy = e
        lo = bpy.data.objects.new(f"L_{nm}", ld)
        lo.location = loc
        sc.collection.objects.link(lo)

    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 1024
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"


if __name__ == "__main__":
    out = _args()
    make_materials()
    make_archetypes()
    make_style_kits()
    master = make_master()
    make_scene(master)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out))
    print(f"[scaffold] сохранено: {out}")
