# render_device_set.py — batch-рендер набора устройств одной расы
#
# Запуск:
#   blender -b blends/devices.blend -P tools/render_device_set.py -- \
#       --race humans --seeds 8 --out renders/humans/ [--types engine,shield]
#       [--res 1024] [--size 2]
#
# Итог: PNG по конвенции  <out>/<type>_s<seed:03d>_<size>.png
# и контрольный лист contact_sheet.png (если установлен PIL — опционально).

import bpy
import sys
import os

DEVICE_TYPES = ["engine", "generator", "shield", "weapon_beam",
                "weapon_launcher", "scanner", "special"]
RACES = ["humans", "shuffie"]  # порядок = индексы Race Style в мастер-группе
SIZE_TAG = {1: "s", 2: "m", 3: "l"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"race": "humans", "seeds": 8, "out": "renders/out",
         "types": DEVICE_TYPES, "res": 1024, "size": 2}
    i = 0
    while i < len(argv):
        k = argv[i].lstrip("-")
        v = argv[i + 1]
        if k == "types":
            a["types"] = [t.strip() for t in v.split(",")]
        elif k in ("seeds", "res", "size"):
            a[k] = int(v)
        else:
            a[k] = v
        i += 2
    return a


def find_device_object():
    preview = bpy.data.objects.get("DEV_preview")
    candidates = ([preview] if preview else []) + list(bpy.data.objects)
    for obj in candidates:
        for mod in obj.modifiers:
            if mod.type == "NODES" and mod.node_group \
                    and mod.node_group.name == "GN_Device_Master":
                return obj, mod
    raise RuntimeError("Не найден объект с модификатором GN_Device_Master")


def socket_ids(node_group):
    """имя входа -> identifier для modifier[...]"""
    return {s.name: s.identifier
            for s in node_group.interface.items_tree
            if getattr(s, "in_out", None) == "INPUT"}


def main():
    a = parse_args()
    obj, mod = find_device_object()
    sid = socket_ids(mod.node_group)
    race_idx = RACES.index(a["race"])

    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = a["res"]
    out_dir = os.path.abspath(a["out"])
    os.makedirs(out_dir, exist_ok=True)

    mod[sid["Race Style"]] = race_idx
    mod[sid["Size Class"]] = a["size"]
    mod[sid["Detail"]] = 1.0

    total = 0
    for dtype in a["types"]:
        mod[sid["Device Type"]] = DEVICE_TYPES.index(dtype)
        for seed in range(a["seeds"]):
            mod[sid["Seed"]] = seed
            obj.update_tag()
            bpy.context.view_layer.update()
            name = f"{dtype}_s{seed:03d}_{SIZE_TAG[a['size']]}.png"
            sc.render.filepath = os.path.join(out_dir, name)
            bpy.ops.render.render(write_still=True)
            total += 1
            print(f"[render] {a['race']}/{name}")

    print(f"[done] {total} изображений -> {out_dir}")


if __name__ == "__main__":
    main()
