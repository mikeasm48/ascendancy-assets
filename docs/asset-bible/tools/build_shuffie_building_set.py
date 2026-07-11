# build_shuffie_building_set.py — объединённый набор зданий Shuffie
# (Blender 4.2+/5.x, headless).
#
# Творческое слияние двух готовых city-set'ов (см. 03-building-set.md §Shuffie):
#   A) текущий Shuffie:  ~/.ascendancy/assets/races/bionics/buildings/
#      building_constructor.glb (31 здание, металл/стекло) — основа доминант;
#   B) deprecated Humans: ~/.ascendancy/assets/races/humans/buildings/
#      building_constructor.glb (белая керамика + бирюза/лайм, бионические
#      формы) — мелкие групповые пропсы, «инопланетные» доминанты, цвета;
#   C) refs/buildings/Shuffie/SpaceDock_shuffie_1.glb, SpaceShield_shuffie_1.glb
#      — орбитальные док и щит (форма как есть, цвета гармонизируются).
#
# Гармонизация под флот Shuffie (shipyard_constructor.glb — ЭТАЛОН, не трогаем):
# флот ахроматичен (белый глянец + графитовые врезки), поэтому золото сета A
# заменяется бирюзой сета B, стекло тонируется в бирюзу, серый уводится в
# графит; текстуры сета B (белый + бирюза + лайм) сохраняются, добавляется
# глянец; оранжевая линза щита перекрашивается в бирюзу.
#
# Запуск:
#   blender -b -P tools/build_shuffie_building_set.py -- \
#       [--assets-dir ~/.ascendancy/assets/races] [--out blends/shuffie_buildings.blend]
#
# Выход (текущий building_constructor.glb НЕ перезаписывается):
#   <assets-dir>/bionics/buildings/building_constructor_v2.glb
#
# Узлы: 14 доминант (BuildingType) + 8 пропсов + 15 орбитальных
# (4 дока: 2 органических DOCK2 + 2 верфи DOCK; 3 щита размерами;
# 8 орудий из корабельных Laser turret / Wave cannon / Gauss cannon
# в серебре палитры строений) + 31 вариант (kind=variant). Extras:
# building_id, display_name, kind, level, source. Бюджет размера:
# текстуры <=512px, децимация тяжёлых мешей (DECIMATE_CAP).

import os
import sys
import math

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REFS_SHUFFIE = os.path.normpath(os.path.join(HERE, "..", "refs", "buildings",
                                             "Shuffie"))

SRC_A = "~/.ascendancy/assets/races/bionics/buildings/building_constructor.glb"
SRC_B = "~/.ascendancy/assets/races/humans/buildings/building_constructor.glb"
SRC_SHIPS = "~/.ascendancy/assets/races/bionics/ships/shipyard_constructor.glb"
SRC_DOCK = os.path.join(REFS_SHUFFIE, "SpaceDock_shuffie_1.glb")
SRC_DOCK2 = os.path.join(REFS_SHUFFIE, "SpaceShield_shuffie_2.glb")  # органический док
SRC_SHIELD = os.path.join(REFS_SHUFFIE, "SpaceShield_shuffie_1.glb")

MAX_TEX = 512          # даунскейл цветовых текстур (бюджет размера GLB)
MAX_TEX_DATA = 256     # normal/MR и прочие Non-Color карты

# Децимация по ИСТОЧНИКУ: (потолок треугольников, нижний порог ratio).
# Плотная органика (B, купол щита) терпит сильный collapse; тонкие
# многослойные оболочки сета A при ratio<0.5 разрушаются — им floor выше.
DECIMATE = {
    "A": (8000, 0.5), "B": (6000, 0.1), "DOCK": (9000, 0.1),
    "DOCK2": (9000, 0.2), "SHIELD": (9000, 0.1), "SHIPS": (4000, 0.5),
}
VARIANT_CAP_MUL = 0.6  # запасные варианты можно жать сильнее
# нетекстурированные источники: UV-слои не нужны (экономия ~8 байт/вершина)
NO_UV_SRC = {"A", "DOCK", "DOCK2", "SHIPS"}

# (building_id, display_name, source, имя группы в GLB, kind, level, scale)
MAPPING = [
    ("COLONY_BASE", "Colony Base", "A", "Building_02_18", "building", 0, 1.0),
    ("FACTORY", "Factory", "A", "Building_03_24", "building", 0, 1.0),
    ("OUTPOST", "Outpost", "B", "Mushroom-like building_7", "building", 0, 1.0),
    ("FARM", "Farm", "A", "Building_02.002_4", "building", 0, 1.0),
    ("LABORATORY", "Laboratory", "A", "Building_09_25", "building", 0, 1.0),
    ("RESEARCH_CAMPUS", "Research Campus", "A", "Building_05_30", "building", 0, 0.7),
    ("MEGAFACTORY", "Megafactory", "A", "Building_07.001_16", "building", 0, 1.4),
    ("HABITAT", "Habitat", "B", "Skyscraper 5_20", "building", 0, 1.0),
    ("ARTIFICAL_HYDROPONIFIER", "Artificial Hydroponifier", "A",
     "Building_08_17", "building", 0, 1.0),
    ("METROPLEX", "Metroplex", "A", "Building_14_20", "building", 0, 1.0),
    ("POWER_PLANT", "Power Plant", "A", "Building_10_22", "building", 0, 1.0),
    ("SKY_NET", "Sky Net", "B", "Droadcast center_13", "building", 0, 1.6),
    ("ECO_BOOSTER", "Eco Booster", "B", "Ringed building_9", "building", 0, 1.3),
    ("TERRAFORMING", "Terraforming", "B", "Skyscraper 4_12", "building", 0, 1.0),
    # пропсы-расширители (мелкие группы большой площади — из deprecated B)
    ("PROP_BLOCKS_1", "Random blocks 1", "B", "Random blocks 1_6", "prop", 1, 1.0),
    ("PROP_BLOCKS_2", "Random blocks 2", "B", "Random blocks 2_11", "prop", 2, 1.0),
    ("PROP_HOUSING", "Social housing", "B", "Social housing_14", "prop", 0, 1.0),
    ("PROP_HIGHWAY", "Highway section", "B", "Highway section_19", "prop", 0, 1.0),
    ("PROP_CANOPY", "Canopy", "B", "Canopy 1_18", "prop", 0, 1.0),
    ("PROP_SPIRE", "Spire", "B", "Spire_0", "prop", 0, 1.0),
    ("PROP_FACILITY", "Facility", "B", "Facility 4_2", "prop", 0, 1.0),
    ("PROP_PYLON", "Pylon", "A", "Building_04.001_6", "prop", 0, 1.0),
    # орбитальные доки: 2 малых — органический кластер (DOCK2),
    # 2 больших — верфь-ферма (DOCK); размеры растут с уровнем
    ("SPACE_DOCK_SMALL", "Small Orbital Dock", "DOCK2", "Mball.192_0",
     "orbital", 1, 0.052),
    ("SPACE_DOCK_MEDIUM", "Medium Orbital Dock", "DOCK2", "Mball.192_0",
     "orbital", 2, 0.072),
    ("SPACE_DOCK_LARGE", "Large Orbital Dock", "DOCK", "Colonial Shipyard",
     "orbital", 3, 0.032),
    ("SPACE_DOCK_HUGE", "Huge Orbital Dock", "DOCK", "Colonial Shipyard",
     "orbital", 4, 0.041),
    # щиты: 3 уровня размером
    ("SPACE_SHIELD_1", "Orbital Shield", "SHIELD",
     "Weighted_Sphere.obj.cleaner.materialmerger.gles", "orbital", 1, 0.00065),
    ("SPACE_SHIELD_2", "Advanced Orbital Shield", "SHIELD",
     "Weighted_Sphere.obj.cleaner.materialmerger.gles", "orbital", 2, 0.00085),
    ("SPACE_SHIELD_3", "Hyper Orbital Shield", "SHIELD",
     "Weighted_Sphere.obj.cleaner.materialmerger.gles", "orbital", 3, 0.00105),
    # орбитальное оружие: корабельные орудия флота, но в общей палитре
    # строений (серебро) — цвета кораблей специально не переносим
    ("ORBITAL_LASER_1", "Orbital Lazer", "SHIPS", "Laser turret_36",
     "orbital", 1, 1.2),
    ("ORBITAL_LASER_2", "Advanced Orbital Lazer", "SHIPS", "Laser turret_36",
     "orbital", 2, 1.55),
    ("ORBITAL_LASER_3", "Hyper Orbital Lazer", "SHIPS", "Laser turret_36",
     "orbital", 3, 1.9),
    ("ORBITAL_PHAZER_1", "Orbital Phazer", "SHIPS", "Wave cannon_35",
     "orbital", 1, 1.1),
    ("ORBITAL_PHAZER_2", "Advanced Orbital Phazer", "SHIPS", "Wave cannon_35",
     "orbital", 2, 1.4),
    ("ORBITAL_PHAZER_3", "Hyper Orbital Phazer", "SHIPS", "Wave cannon_35",
     "orbital", 3, 1.75),
    ("ORBITAL_PHAZER_RAPID_1", "Orbital Rapid Phazer", "SHIPS",
     "Gauss cannon_45", "orbital", 1, 0.55),
    ("ORBITAL_PHAZER_RAPID_2", "Advanced Orbital Rapid Phazer", "SHIPS",
     "Gauss cannon_45", "orbital", 2, 0.7),
]
# источники, чьим узлам назначается общий материал строений (серебро)
SILVER_OVERRIDE_SRC = {"SHIPS"}
EXCLUDE = {"Mercury-class"}  # пристыкованный корабль из dock-рефа не берём

# Перекраска материалов сета A: tag -> (rgb 0..1, metallic, roughness)
# бирюза вместо золота — цветовой мост к текстурам сета B
RECOLOR_A = {
    "Concrete_01": ((0.855, 0.87, 0.88), 0.0, 0.25),   # белый фарфор
    "Silver_01":   ((0.82, 0.84, 0.86), 1.0, 0.18),    # серебро (как было)
    "Gold_01":     ((0.16, 0.6, 0.66), 0.75, 0.25),    # бирюзовый металл
    "Glass_01":    ((0.26, 0.54, 0.6), 0.8, 0.15),     # стекло в бирюзу
    "Gray_01":     ((0.055, 0.065, 0.075), 0.0, 0.35), # графит врезок флота
}
RECOLOR_DOCK = {"Hull": ((0.72, 0.75, 0.78), 0.9, 0.32)}
GLOSS_B = 0.22  # глянец для керамики сета B (текстуры сохраняются)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"assets_dir": os.path.expanduser("~/.ascendancy/assets/races"),
         "out": "blends/shuffie_buildings.blend"}
    i = 0
    while i < len(argv):
        a[argv[i].lstrip("-").replace("-", "_")] = argv[i + 1]
        i += 2
    return a


def import_glb(path):
    before_obj = set(bpy.data.objects)
    before_mat = set(bpy.data.materials)
    bpy.ops.import_scene.gltf(filepath=os.path.expanduser(path))
    return (set(bpy.data.objects) - before_obj,
            set(bpy.data.materials) - before_mat)


def mesh_children(ob):
    out = []
    def walk(o):
        if o.type == "MESH":
            out.append(o)
        for c in o.children:
            walk(c)
    walk(ob)
    return out


def find_groups(objs):
    """Эмпти нижнего уровня с меш-детьми (группа-здание) по имени."""
    groups = {}
    for ob in objs:
        if ob.type != "EMPTY":
            continue
        child_empties = [c for c in ob.children
                         if c.type == "EMPTY" and mesh_children(c)]
        if mesh_children(ob) and not child_empties:
            groups[ob.name] = ob
    return groups


def recolor(materials, table):
    for m in materials:
        spec = table.get(m.name.split(".0")[0] if m.name not in table else m.name)
        if spec is None:
            spec = table.get(m.name)
        if spec is None:
            continue
        rgb, metal, rough = spec
        b = m.node_tree.nodes.get("Principled BSDF")
        # рвём текстурные связи, красим плоским цветом
        for link in list(b.inputs["Base Color"].links):
            m.node_tree.links.remove(link)
        b.inputs["Base Color"].default_value = (*rgb, 1.0)
        b.inputs["Metallic"].default_value = metal
        b.inputs["Roughness"].default_value = rough


def gloss_textured(materials, roughness):
    """Сет B: текстуры остаются, добавляем фарфоровый глянец."""
    for m in materials:
        b = m.node_tree.nodes.get("Principled BSDF")
        if b is None:
            continue
        for link in list(b.inputs["Roughness"].links):
            m.node_tree.links.remove(link)
        b.inputs["Roughness"].default_value = roughness


def teal_shift_orange(materials):
    """Щит: оранжево-красные пиксели цветовых текстур (Base Color И
    Emission Color — «глаз» линзы живёт в эмиссии) -> бирюза."""
    import numpy as np
    done = set()
    for m in materials:
        b = m.node_tree.nodes.get("Principled BSDF")
        if b is None:
            continue
        for sock in ("Base Color", "Emission Color"):
            if not b.inputs[sock].links:
                continue
            node = b.inputs[sock].links[0].from_node
            img = getattr(node, "image", None)
            if img is None or img.name in done:
                continue
            done.add(img.name)
            px = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
            img.pixels.foreach_get(px)
            rgba = px.reshape(-1, 4)
            r, g, bl = rgba[:, 0], rgba[:, 1], rgba[:, 2]
            mx = np.maximum(np.maximum(r, g), bl)
            mn = np.minimum(np.minimum(r, g), bl)
            sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
            warm = (sat > 0.2) & (r > g) & (g >= bl * 0.95)  # оранжевая зона
            # бирюза той же светлоты: g/b вверх, r вниз
            rgba[warm, 0] = mn[warm] * 0.6
            rgba[warm, 1] = mx[warm] * 0.85
            rgba[warm, 2] = mx[warm]
            # ВАЖНО: подменяем картинку новым generated-датаблоком.
            # Правка pixels + save()/pack() не работает: и glTF-экспортёр,
            # и Image.save() берут исходные упакованные байты PNG,
            # игнорируя отредактированный буфер.
            fresh = bpy.data.images.new(f"{img.name}_teal",
                                        img.size[0], img.size[1], alpha=True)
            fresh.colorspace_settings.name = img.colorspace_settings.name
            fresh.pixels.foreach_set(rgba.reshape(-1))
            fresh.update()
            node.image = fresh
        b.inputs["Roughness"].default_value = 0.3


def downscale_images(max_color, max_data):
    """Ужать текстуры: цветовые до max_color, Non-Color (normal/MR) до
    max_data. Отмасштабированный буфер подменяется свежим
    generated-датаблоком (см. teal_shift_orange): иначе экспортёр
    возьмёт исходные упакованные байты."""
    import numpy as np
    remap = {}
    for img in list(bpy.data.images):
        target = max_color if img.colorspace_settings.name == "sRGB" \
            else max_data
        if img.size[0] == 0 or max(img.size) <= target:
            continue
        img.scale(target, target)
        px = np.empty(target * target * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        fresh = bpy.data.images.new(f"{img.name}_s", target, target,
                                    alpha=True)
        fresh.colorspace_settings.name = img.colorspace_settings.name
        fresh.pixels.foreach_set(px)
        fresh.update()
        remap[img.name] = fresh
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image and n.image.name in remap:
                n.image = remap[n.image.name]


def assemble(group_empty):
    """Слить КОПИИ мешей группы в один объект (исходники не трогаем — одна
    группа используется в нескольких уровнях), посадить на z=0, центр (0,0).
    Масштаб уровня в меш НЕ запекается — уходит в трансформ узла, чтобы
    уровни одного источника делили один меш в GLB."""
    src = [o for o in mesh_children(group_empty) if o.name.split(".")[0]
           not in EXCLUDE]
    meshes = []
    for o in src:
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        mw = o.matrix_world.copy()
        c.parent = None       # сначала снять родителя,
        c.matrix_world = mw   # потом восстановить мировой трансформ
        meshes.append(c)
    target = meshes[0]
    if len(meshes) > 1:
        with bpy.context.temp_override(
                active_object=target,
                selected_editable_objects=meshes):
            bpy.ops.object.join()
    # мир -> меш (сплит-нормали исходников сохраняем — иначе «плавятся»
    # жёсткие пояса сета A и грани орудий)
    target.data.transform(target.matrix_world)
    target.matrix_world = Matrix.Identity(4)
    # bbox: центр XY в 0, низ на z=0
    xs = [v.co for v in target.data.vertices]
    lo = Vector((min(v.x for v in xs), min(v.y for v in xs),
                 min(v.z for v in xs)))
    hi = Vector((max(v.x for v in xs), max(v.y for v in xs),
                 max(v.z for v in xs)))
    c = (lo + hi) / 2
    target.data.transform(Matrix.Translation((-c.x, -c.y, -lo.z)))
    return target


def decimate_now(obj, cap, floor):
    """Сразу применить децимацию к мешу (не модификатором на экспорт),
    чтобы уровни могли делить один меш. floor защищает силуэт."""
    ntris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if ntris <= cap:
        return
    mod = obj.modifiers.new("Budget", "DECIMATE")
    mod.ratio = max(cap / ntris, floor)
    with bpy.context.temp_override(object=obj, active_object=obj):
        bpy.ops.object.modifier_apply(modifier=mod.name)


def strip_uvs(mesh):
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])


def main():
    a = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)

    objs_a, mats_a = import_glb(SRC_A)
    objs_b, mats_b = import_glb(SRC_B)
    objs_d, mats_d = import_glb(SRC_DOCK)
    objs_d2, mats_d2 = import_glb(SRC_DOCK2)
    objs_s, mats_s = import_glb(SRC_SHIELD)
    objs_w, mats_w = import_glb(SRC_SHIPS)
    sources = {"A": objs_a, "B": objs_b, "DOCK": objs_d, "DOCK2": objs_d2,
               "SHIELD": objs_s, "SHIPS": objs_w}
    groups = {k: find_groups(v) for k, v in sources.items()}

    recolor(mats_a, RECOLOR_A)
    recolor(mats_d, RECOLOR_DOCK)
    gloss_textured(mats_b, GLOSS_B)
    teal_shift_orange(mats_s)
    downscale_images(MAX_TEX, MAX_TEX_DATA)
    silver = next(m for m in mats_a if m.name.startswith("Silver_01"))

    used = set()
    out_objs = []
    idx = 0

    mesh_cache = {}  # (src, gname) -> готовый декимированный меш

    def place(obj, bld_id, disp, kind, level, source, scale=1.0):
        nonlocal idx
        obj.name = f"{idx:03d}_{bld_id}"
        row, col = divmod(idx, 6)
        obj.location = (col * 12.0, row * 12.0, 0.0)
        obj.scale = (scale, scale, scale)
        obj["building_id"] = bld_id
        obj["display_name"] = disp
        obj["kind"] = kind
        obj["level"] = level
        obj["style"] = "shuffie"
        obj["source"] = source
        out_objs.append(obj)
        idx += 1

    def node_for(src, gname, kind):
        """Собрать (или переиспользовать) уникальный меш источника."""
        key = (src, gname)
        if key in mesh_cache:
            obj = bpy.data.objects.new("node", mesh_cache[key])
            bpy.context.scene.collection.objects.link(obj)
            return obj
        g = groups[src].get(gname)
        if g is None:
            raise RuntimeError(f"группа не найдена: {src}/{gname}")
        obj = assemble(g)
        cap, floor = DECIMATE[src]
        if kind == "variant":
            cap = int(cap * VARIANT_CAP_MUL)
        decimate_now(obj, cap, floor)
        if src in NO_UV_SRC:
            strip_uvs(obj.data)
        if src in SILVER_OVERRIDE_SRC:  # орудия — в общую палитру строений
            for slot in obj.material_slots:
                slot.material = silver
        mesh_cache[key] = obj.data
        return obj

    for bld_id, disp, src, gname, kind, level, scale in MAPPING:
        used.add((src, gname))
        place(node_for(src, gname, kind), bld_id, disp, kind, level, src,
              scale)

    # оставшиеся группы обоих сетов — вариантами (богатство набора)
    for src in ("A", "B"):
        for gname, g in sorted(groups[src].items()):
            if (src, gname) in used or gname.split(".")[0] in EXCLUDE:
                continue
            var_id = "VARIANT_" + gname.replace(" ", "_").replace(".", "_")
            place(node_for(src, gname, "variant"), var_id, gname,
                  "variant", 0, src)

    # выкидываем пустышки и неиспользованные меши (корабль из dock-рефа)
    for ob in list(bpy.data.objects):
        if ob not in out_objs:
            bpy.data.objects.remove(ob, do_unlink=True)
    for ob in out_objs:
        bpy.context.scene.collection.objects.link(ob) \
            if ob.name not in bpy.context.scene.collection.objects else None

    out = os.path.abspath(a["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"[shuffie-set] сохранено: {out}")

    out_dir = os.path.join(os.path.expanduser(a["assets_dir"]),
                           "bionics", "buildings")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "building_constructor_v2.glb")
    for o in bpy.data.objects:
        o.select_set(o in out_objs)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB",
                              use_selection=True, export_apply=True,
                              export_extras=True, export_yup=True)
    print(f"[shuffie-set] экспорт: {path} ({len(out_objs)} узлов)")


if __name__ == "__main__":
    main()
