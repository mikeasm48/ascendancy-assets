#!/usr/bin/env python3
"""Contact sheet of a constructor kit, rendered with a tiny software rasteriser.

There is no display in the agent sandbox and no Blender on the path, so this is
how a painted kit gets checked: it reads the GLB's own materials, flat-shades
every node and tiles them into one PNG.

Usage:
    preview_constructor_kit.py KIT.glb SHEET.png [--cols 6] [--size 280]
"""
import os, sys, argparse
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint_worms_constructors import Glb


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def rotm(yaw, pitch):
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    return np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ \
           np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])


def render_node(glb, node, size=300, yaw=0.6, pitch=0.30, bg=(28, 28, 30)):
    mesh = glb.json['meshes'][node['mesh']]
    mats = glb.json.get('materials', [])
    allpos, alltri, allcol, allemi = [], [], [], []
    base_v = 0
    for prim in mesh['primitives']:
        pos = glb.accessor(prim['attributes']['POSITION']).astype(np.float64)
        idx = glb.accessor(prim['indices']).astype(np.int64).reshape(-1, 3)
        mi = prim.get('material')
        if mi is None:
            col = np.array([0.75, 0.75, 0.75]); emi = np.zeros(3)
        else:
            m = mats[mi]
            col = np.array(m['pbrMetallicRoughness']['baseColorFactor'][:3])
            emi = np.array(m.get('emissiveFactor', [0, 0, 0]))
        allpos.append(pos); alltri.append(idx + base_v)
        allcol.append(np.tile(col, (len(idx), 1)))
        allemi.append(np.tile(emi, (len(idx), 1)))
        base_v += len(pos)
    P = np.vstack(allpos); T = np.vstack(alltri)
    C = np.vstack(allcol); E = np.vstack(allemi)

    R = rotm(yaw, pitch)
    V = P @ R.T
    lo, hi = V.min(0), V.max(0)
    V = (V - (lo + hi) / 2) / (hi - lo).max()
    W = H = size
    sx = (V[:, 0] * 0.86 + 0.5) * W
    sy = (0.5 - V[:, 1] * 0.86) * H
    sz = V[:, 2]

    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    n = np.cross(V[b] - V[a], V[c] - V[a])
    ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1; n /= ln[:, None]
    key = np.array([0.45, 0.65, 0.62]); key /= np.linalg.norm(key)
    fill = np.array([-0.55, 0.15, 0.35]); fill /= np.linalg.norm(fill)
    lam = np.clip(n @ key, 0, 1) * 0.72 + np.clip(n @ fill, 0, 1) * 0.18 + 0.10
    face = np.clip(C * lam[:, None] + E * 0.9, 0, 1)
    face = lin_to_srgb(face)

    img = np.zeros((H, W, 3), float) + np.array(bg) / 255
    zb = np.full((H, W), -1e9)
    for t in range(len(T)):
        x0, y0 = sx[a[t]], sy[a[t]]
        x1, y1 = sx[b[t]], sy[b[t]]
        x2, y2 = sx[c[t]], sy[c[t]]
        z = (sz[a[t]] + sz[b[t]] + sz[c[t]]) / 3
        mnx = int(max(0, np.floor(min(x0, x1, x2)))); mxx = int(min(W - 1, np.ceil(max(x0, x1, x2))))
        mny = int(max(0, np.floor(min(y0, y1, y2)))); mxy = int(min(H - 1, np.ceil(max(y0, y1, y2))))
        if mnx > mxx or mny > mxy:
            continue
        X, Y = np.meshgrid(np.arange(mnx, mxx + 1) + .5, np.arange(mny, mxy + 1) + .5)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(d) < 1e-9:
            continue
        w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / d
        w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / d
        m = (w0 >= 0) & (w1 >= 0) & ((1 - w0 - w1) >= 0)
        if not m.any():
            continue
        sub = zb[mny:mxy + 1, mnx:mxx + 1]
        m &= z > sub
        if not m.any():
            continue
        sub[m] = z
        img[mny:mxy + 1, mnx:mxx + 1][m] = face[t]
    return Image.fromarray((img * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('glb'); ap.add_argument('out')
    ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--size', type=int, default=280)
    ap.add_argument('--only', default=None, help='comma-separated node indices')
    args = ap.parse_args()
    glb = Glb(args.glb)
    nodes = [n for n in glb.json['nodes'] if 'mesh' in n]
    if args.only:
        want = {int(x) for x in args.only.split(',')}
        nodes = [n for i, n in enumerate(glb.json['nodes']) if i in want]
    cols = args.cols
    rows = (len(nodes) + cols - 1) // cols
    s = args.size
    sheet = Image.new('RGB', (cols * s, rows * (s + 16)), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    for i, node in enumerate(nodes):
        tile = render_node(glb, node, size=s)
        x, y = (i % cols) * s, (i // cols) * (s + 16)
        sheet.paste(tile, (x, y))
        draw.text((x + 4, y + s + 2), node.get('name', '?')[:40], fill=(190, 190, 190))
    sheet.save(args.out)
    print('wrote', args.out, sheet.size)


if __name__ == '__main__':
    main()
