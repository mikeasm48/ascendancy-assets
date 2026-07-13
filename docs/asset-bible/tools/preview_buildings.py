# preview_buildings.py — контрольный лист зданий без Blender (numpy+matplotlib).
# Быстрая итерация по силуэтам; палитра синхронизирована с build_building_sets.
#
#   python preview_buildings.py --style industrial \
#       --out ../renders/preview/approval_buildings_humans_industrial_v1.png

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

from building_catalog import build  # noqa: E402

# tag -> (hex, emissive)  — цвета согласованы с MATS в build_building_sets.py
PALETTE = {
    "conc":   ("#9AA0A6", 0), "conc_l": ("#C2C7CC", 0), "conc_d": ("#62686E", 0),
    "steel":  ("#7E8890", 0), "dark":   ("#363B41", 0), "rust":   ("#A85C2E", 0),
    "glass":  ("#9FC4D8", 0), "glass_g": ("#AEDCC2", 0), "green":  ("#4E7A3C", 0),
    "screen": ("#35C8DC", 1), "accent": ("#E06A2B", 1), "redline": ("#C43B2A", 1),
    "white":  ("#E2E6E9", 0), "silver": ("#B9C2CA", 0), "bglow":  ("#4FC3FF", 1),
    "gglow":  ("#7CE87C", 1), "pglow":  ("#A97BFF", 1),
    # --- дополнения набора core
    "plate":  ("#D5DADF", 0), "grass":  ("#5F9E44", 0), "soil":   ("#6B4A2F", 0),
    "red":    ("#C0392B", 0), "sand":   ("#C9B48A", 0), "copper": ("#B87333", 0),
    "solar":  ("#2B3D66", 0), "pink":   ("#C79AA6", 0), "gold":   ("#C89B3C", 0),
    "teal":   ("#3E9A92", 0), "blue":   ("#4A6FA5", 0), "ygreen": ("#A8B23A", 0),
    "dgreen": ("#39543F", 0), "graph":  ("#3A3F45", 0),
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
    # единый масштаб по максимальному габариту
    c = (V.max(0) + V.min(0)) / 2
    r = (V.max(0) - V.min(0)).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(max(c[2] - r, -0.2), c[2] + r)
    ax.set_proj_type('ortho')
    ax.view_init(elev=24, azim=-54)
    ax.set_axis_off()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="industrial",
                    choices=("industrial", "scifi", "core"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.style == "industrial":
        import building_recipes_humans_industrial as mod
        from building_catalog import RECIPES
        race = "HUMANS"
    elif args.style == "scifi":
        import building_recipes_humans_scifi as mod
        from building_catalog import RECIPES
        race = "HUMANS"
    else:
        import building_recipes_core as mod
        from building_catalog_core import RECIPES
        race = "CORE"

    n = len(RECIPES)
    cols = 6
    rows = math.ceil(n / cols)
    fig = plt.figure(figsize=(cols * 3.0, rows * 3.0), facecolor="#14161a")
    for i, (bid, name, recipe, lvl, kind) in enumerate(RECIPES):
        ax = fig.add_subplot(rows, cols, i + 1, projection='3d',
                             facecolor="#14161a")
        V, F, tags = build(mod, recipe, lvl, seed=i)
        draw(ax, V, F, tags)
        ax.set_title(f"{bid}", color="#c8cdd2", fontsize=7, pad=0)
    fig.suptitle(f"{race} buildings — {args.style}", color="#e8ecef",
                 fontsize=13, y=0.995)
    default_name = (f"approval_buildings_core_v1.png" if args.style == "core"
                    else f"approval_buildings_humans_{args.style}_v1.png")
    out = args.out or os.path.join(HERE, "..", "renders", "preview",
                                   default_name)
    fig.tight_layout()
    fig.savefig(out, dpi=105, facecolor=fig.get_facecolor())
    print("saved:", os.path.abspath(out))


if __name__ == "__main__":
    main()
