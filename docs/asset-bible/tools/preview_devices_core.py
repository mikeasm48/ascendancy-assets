# preview_devices_core.py — контрольный лист устройств core без Blender
# (numpy+matplotlib). Палитра синхронизирована с MATS build_device_sets.py.
#
#   python preview_devices_core.py \
#       --out ../renders/preview/approval_devices_core_v3.png

import argparse
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from device_catalog_core import RECIPES, build  # noqa: E402
import device_recipes_core as mod  # noqa: E402

# tag -> (hex, emissive) — цвета согласованы с MATS в build_device_sets.py
PALETTE = {
    "plat":   ("#6E7A86", 0), "hull":   ("#9AA3AB", 0), "hull_b": ("#C4CBD1", 0),
    "detail": ("#5E666E", 0), "coil":   ("#B3372B", 0), "coil2":  ("#A9803A", 0),
    "blue":   ("#4A6FA5", 0), "teal":   ("#3E9A92", 0), "gold":   ("#B08D3C", 0),
    "glass":  ("#9FC4D8", 0), "dark":   ("#33383E", 0), "green":  ("#6B8F3E", 0),
    "white":  ("#D8D8D8", 0), "accent": ("#E06A2B", 1), "pink":   ("#B56A9A", 0),
    "flame":  ("#FF9A3C", 1), "graph":  ("#3A3F45", 0), "redline": ("#C43B2A", 1),
    "ygreen": ("#A8B23A", 0), "dgreen": ("#39543F", 0), "silver": ("#C0C7CC", 0),
    "wood":   ("#B99A5E", 0), "bottle": ("#3FA34D", 0), "bglow":  ("#4FC3FF", 1),
    "gun":    ("#8E969E", 0), "gun_d":  ("#4C545C", 0),
    "copper": ("#B87333", 0), "pearl":  ("#E8DFEA", 0), "yellow": ("#D9C04B", 0),
    "pglow":  ("#E570C0", 1), "yglow":  ("#C6E24A", 1),
    "tan":    ("#F2DD9B", 0), "redbright": ("#DE211E", 0), "invgray": ("#8E988E", 0),
    "colgray": ("#B2B4AC", 0), "colgreen": ("#A8C7A6", 0),
    "coltan": ("#DCC9A4", 0), "colgold": ("#CCB27A", 0),
    "lmgray": ("#BCBEBB", 0), "lmtan": ("#D5C5A0", 0), "lmbrass": ("#998C66", 0),
    "lmteal": ("#3689A4", 0), "lmglow": ("#F2F470", 1), "lmgreen": ("#7CA379", 0),
    "sldwhite": ("#ECE7E6", 0), "sldgray": ("#BCBDBB", 0), "sldpeach": ("#F7DCCF", 0),
    "sldblue": ("#94B3C9", 0), "sldnavy": ("#084C7E", 0),
    "hdsilver": ("#BFBCBD", 0), "hdred": ("#A3485E", 0), "hdrose": ("#A88486", 0),
}
LIGHT = np.array([0.4, -0.65, 0.65])
LIGHT_N = LIGHT / np.linalg.norm(LIGHT)


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def draw(ax, V, F, tags):
    V = np.asarray(V, float)
    tris = V[np.asarray(F, int)]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    lam = np.clip(n @ LIGHT_N, 0, 1)
    cols = []
    for k, t in enumerate(tags):
        base, emis = PALETTE[t]
        c = hex2rgb(base)
        if emis:
            c = np.clip(c * 1.15 + 0.1, 0, 1)
        else:
            c = c * (0.35 + 0.65 * lam[k])
        cols.append((*c, 1.0))
    pc = Poly3DCollection(tris, facecolors=cols, edgecolors='none')
    ax.add_collection3d(pc)
    c = (V.max(0) + V.min(0)) / 2
    r = (V.max(0) - V.min(0)).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(max(c[2] - r, -0.1), c[2] + r)
    ax.set_proj_type('ortho')
    ax.view_init(elev=24, azim=-54)
    ax.set_axis_off()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    n = len(RECIPES)
    cols = 5
    rows = math.ceil(n / cols)
    fig = plt.figure(figsize=(cols * 3.2, rows * 3.2), facecolor="#14161a")
    for i, (node, disp, dtype, recipe, plate) in enumerate(RECIPES):
        ax = fig.add_subplot(rows, cols, i + 1, projection='3d',
                             facecolor="#14161a")
        V, F, tags = build(mod, recipe, seed=i)
        if plate is not None:
            pV, pF, ptags = mod.merge(mod.platform(plate))
            allV = np.vstack([V, pV])
            allF = np.vstack([np.asarray(F, int),
                              np.asarray(pF, int) + len(V)])
            allTags = list(tags) + list(ptags)
        else:
            allV, allF, allTags = V, np.asarray(F, int), list(tags)
        draw(ax, allV, allF, allTags)
        ax.set_title(node, color="#c8cdd2", fontsize=7, pad=0)
    fig.suptitle("CORE devices — v3 (по рефам, без поколений)",
                 color="#e8ecef", fontsize=13, y=0.995)
    out = args.out or os.path.join(HERE, "..", "renders", "preview",
                                   "approval_devices_core_v3.png")
    fig.tight_layout()
    fig.savefig(out, dpi=105, facecolor=fig.get_facecolor())
    print("saved:", os.path.abspath(out))


if __name__ == "__main__":
    main()
