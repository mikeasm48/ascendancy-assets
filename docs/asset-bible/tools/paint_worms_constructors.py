#!/usr/bin/env python3
"""Paint the Worms constructor kits.

The Worms building/ship constructors were exported as bare geometry: no
materials, no textures, only POSITION and NORMAL. Everything therefore renders
in the engine's default white. This tool gives them the palette of the
reference sheets in ``docs/asset-bible/refs/{buildings,ships}/Worms`` - dark
chitin, bone claws, glossy indigo eyes, shadowed crevices - without touching a
single vertex.

Zones are derived from geometry, because the meshes carry no other signal:

* ``medial radius``  - shrinking-ball half-thickness. Thin => claw / spine /
  tusk => bone. Thick => hull => chitin.
* ``occupancy AO``   - blurred voxel occupancy sampled above each vertex.
  Buried => crevice, mouth interior => dark chitin.
* ``sphere fit``     - a ball of geometry hanging off a much larger component
  is an eye orb.
* node names         - the ship kit labels its loose parts (``..._Eye_Orb``,
  ``..._stix``), and the two orbital shields need their caged core to glow.

Each mesh keeps its POSITION/NORMAL accessors; only the index buffer is
rewritten, split into one primitive per zone.

Usage:
    paint_worms_constructors.py IN.glb OUT.glb --kit buildings|ships [--report]
"""

from __future__ import annotations

import argparse
import json
import struct
import sys

import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

# --------------------------------------------------------------------- glb io

COMPONENT_TYPES = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}
TYPE_COUNTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


class Glb:
    """Minimal GLB reader - plain struct/numpy, no glTF library needed."""

    def __init__(self, path):
        data = open(path, 'rb').read()
        offset = 12
        self.json = None
        self.bin = b''
        while offset < len(data):
            length, kind = struct.unpack('<II', data[offset:offset + 8])
            chunk = data[offset + 8:offset + 8 + length]
            if kind == JSON_CHUNK:
                self.json = json.loads(chunk.decode('utf-8'))
            elif kind == BIN_CHUNK:
                self.bin = chunk
            offset += 8 + length

    def accessor(self, index):
        acc = self.json['accessors'][index]
        ncomp = TYPE_COUNTS[acc['type']]
        view = self.json['bufferViews'][acc['bufferView']]
        base = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        dtype = np.dtype('<' + COMPONENT_TYPES[acc['componentType']])
        count = acc['count']
        stride = view.get('byteStride')
        if stride and stride != ncomp * dtype.itemsize:
            raw = np.frombuffer(self.bin, dtype=np.uint8,
                                count=stride * (count - 1) + ncomp * dtype.itemsize,
                                offset=base)
            take = (np.arange(count)[:, None] * stride
                    + np.arange(ncomp * dtype.itemsize)[None, :]).ravel()
            arr = np.frombuffer(raw[take].tobytes(), dtype=dtype).reshape(count, ncomp)
        else:
            arr = np.frombuffer(self.bin, dtype=dtype, count=count * ncomp,
                                offset=base).reshape(count, ncomp)
        return arr if ncomp > 1 else arr.ravel()


def write_glb(path, gltf, blob):
    """Write a GLB, padding both chunks to the 4-byte alignment the spec wants."""
    js = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    blob += b'\x00' * ((4 - len(blob) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, 'wb') as fh:
        fh.write(struct.pack('<III', 0x46546C67, 2, total))
        fh.write(struct.pack('<II', len(js), JSON_CHUNK))
        fh.write(js)
        fh.write(struct.pack('<II', len(blob), BIN_CHUNK))
        fh.write(blob)


# ------------------------------------------------------------------- palette

def srgb_to_linear(hex_color):
    """glTF factors are linear; the reference colours were picked in sRGB."""
    c = np.array([int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def material(name, base_hex, roughness, metallic, emissive_hex=None,
             emissive_strength=1.0):
    mat = {
        'name': name,
        'doubleSided': True,
        'pbrMetallicRoughness': {
            'baseColorFactor': [round(float(v), 5) for v in srgb_to_linear(base_hex)] + [1.0],
            'metallicFactor': metallic,
            'roughnessFactor': roughness,
        },
    }
    if emissive_hex:
        e = srgb_to_linear(emissive_hex) * emissive_strength
        mat['emissiveFactor'] = [round(float(min(v, 1.0)), 5) for v in e]
    return mat


# Zone ids, in the order they become materials in the file.
CHITIN, CHITIN_LIGHT, CHITIN_DARK, BONE, EYE, GLOW = range(6)
ZONE_NAMES = ['chitin', 'chitin_light', 'chitin_dark', 'bone', 'eye', 'glow']

# Sampled off the reference sheets. The renders are far less saturated than a
# "brown chitin" instinct suggests - roughly 0.19 on the max-min/max scale,
# against 0.26 for a first guess - so these are pulled towards neutral on
# purpose. Buildings are earth-caked and warm; the ship hulls are the same
# chitin gone cold and grey.
PALETTES = {
    'buildings': [
        material('Worms_Chitin', '585149', 0.80, 0.00),
        material('Worms_Chitin_Light', '7c7466', 0.68, 0.00),
        material('Worms_Chitin_Dark', '221f1b', 0.88, 0.00),
        material('Worms_Bone', 'c2bba8', 0.42, 0.00),
        material('Worms_Eye', '342c4e', 0.10, 0.25),
        material('Worms_Glow', '6f63b4', 0.30, 0.00, 'a394ff', 1.0),
    ],
    # The ship sheets read a full stop lighter than the buildings - pale
    # weathered stone rather than wet earth - so the hull tones are raised.
    'ships': [
        material('Worms_Chitin', '6e6a64', 0.78, 0.05),
        material('Worms_Chitin_Light', '918d85', 0.66, 0.05),
        material('Worms_Chitin_Dark', '2a2926', 0.86, 0.00),
        material('Worms_Bone', 'd0cabb', 0.40, 0.00),
        material('Worms_Eye', '332b52', 0.10, 0.25),
        material('Worms_Glow', '6f63b4', 0.30, 0.00, 'a394ff', 1.0),
    ],
}

# Per-kit thresholds, as percentiles of the per-mesh signals. The ship hulls
# are spikier, so the same crevice percentile that reads as shading on a
# building turns them into camouflage; they get a tighter band.
TUNING = {
    'buildings': {'dark_pct': 90, 'light_pct': 18},
    'ships': {'dark_pct': 95, 'light_pct': 12},
}


# ------------------------------------------------------------------ geometry

def weld(pos, idx, tol=1e-5):
    """Merge the duplicated corners of a flat-shaded export into a topology.

    The exports carry ~3 unique vertices per triangle, so nothing is connected
    until identical positions are fused. Returns the welded vertices, the
    welded triangles, and the original-vertex -> welded-vertex map.
    """
    key = np.round(pos / tol).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    verts = np.zeros((len(uniq), 3))
    counts = np.bincount(inv, minlength=len(uniq))
    for axis in range(3):
        verts[:, axis] = np.bincount(inv, weights=pos[:, axis],
                                     minlength=len(uniq)) / counts
    faces = inv[idx.reshape(-1, 3)]
    keep = ((faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2])
            & (faces[:, 0] != faces[:, 2]))
    return verts, faces, inv, keep


def vertex_normals(verts, faces):
    e1 = verts[faces[:, 1]] - verts[faces[:, 0]]
    e2 = verts[faces[:, 2]] - verts[faces[:, 0]]
    fn = np.cross(e1, e2)
    normals = np.zeros_like(verts)
    for k in range(3):
        np.add.at(normals, faces[:, k], fn)
    length = np.linalg.norm(normals, axis=1)
    length[length == 0] = 1.0
    return normals / length[:, None]


def medial_radius(verts, normals, r_init=0.35, iters=24, eps=1e-6):
    """Shrinking-ball half-thickness of the solid under every vertex.

    A ball is placed tangent to the surface on the inside and shrunk until no
    other sample point falls inside it. The converged radius is tiny on claws,
    spines and webbing and large in a bulky hull - the signal that tells the
    Worms' bone parts from their chitin. Nothing needs to be watertight, which
    matters: these meshes are hundreds of loose shells.
    """
    tree = cKDTree(verts)
    radius = np.full(len(verts), float(r_init))
    for _ in range(iters):
        centre = verts - normals * radius[:, None]
        _, near = tree.query(centre, k=2, workers=-1)
        itself = near[:, 0] == np.arange(len(verts))
        other = np.where(itself[:, None], near[:, 1:2], near[:, 0:1]).ravel()
        delta = verts - verts[other]
        denom = 2.0 * np.einsum('ij,ij->i', delta, normals)
        shrunk = np.where(denom > eps,
                          np.einsum('ij,ij->i', delta, delta) / np.maximum(denom, eps),
                          radius)
        shrunk = np.minimum(shrunk, radius)
        if np.allclose(shrunk, radius, atol=1e-5):
            return shrunk
        radius = shrunk
    return radius


def _voxel_grid(verts, faces, res, pad):
    lo, hi = verts.min(0), verts.max(0)
    span = max((hi - lo).max(), 1e-6)
    h = span / (res - 2 * pad)
    origin = lo - pad * h
    dims = np.ceil((hi - origin) / h).astype(int) + pad + 1
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    longest = max(np.linalg.norm(b - a, axis=1).max(),
                  np.linalg.norm(c - a, axis=1).max(),
                  np.linalg.norm(c - b, axis=1).max())
    steps = min(int(np.ceil(longest / (h * 0.6))) + 1, 20)
    us, vs = np.meshgrid(np.linspace(0, 1, steps), np.linspace(0, 1, steps))
    inside = (us + vs) <= 1.0
    us, vs = us[inside], vs[inside]
    pts = (a[:, None, :] + (b - a)[:, None, :] * us[None, :, None]
           + (c - a)[:, None, :] * vs[None, :, None]).reshape(-1, 3)
    gi = np.floor((pts - origin) / h).astype(int)
    np.clip(gi, 0, dims - 1, out=gi)
    occ = np.zeros(dims, np.float32)
    occ[gi[:, 0], gi[:, 1], gi[:, 2]] = 1.0
    return occ, origin, h, dims


def occupancy_ao(verts, faces, normals, res=112, sigma=0.055, probe=2.5):
    """How buried each vertex is, roughly 0 (exposed) to 1 (walled in).

    A blurred voxel occupancy field sampled just above the surface. Stands in
    for a ray-traced AO bake and, unlike ray tracing, does not mind that the
    meshes are full of holes.
    """
    occ, origin, h, dims = _voxel_grid(verts, faces, res, pad=6)
    blur = ndimage.gaussian_filter(occ, sigma=sigma / h, mode='constant')
    probe_pt = verts + normals * (probe * h)
    pi = np.floor((probe_pt - origin) / h).astype(int)
    np.clip(pi, 0, dims - 1, out=pi)
    return blur[pi[:, 0], pi[:, 1], pi[:, 2]]


def component_labels(verts, faces):
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])),
                       shape=(len(verts), len(verts)))
    _, labels = connected_components(graph, directed=False)
    return labels


def eye_orbs(verts, normals, radius, labels, ao):
    """Flag the glossy orbs: a ball of surface budding off a much larger body.

    Around an orb every normal points away from one centre, so ``v + r*n`` (the
    inward ball centre used by the medial pass) collapses to a single point.
    Free-floating debris - the dirt clumps around the hive dwelling - is
    rejected by insisting the orb belongs to a component many times its size.
    """
    small = (radius > 0.006) & (radius < 0.055)
    if not small.any():
        return np.zeros(len(verts), bool)
    centres = verts - normals * radius[:, None]
    tree = cKDTree(centres)
    # an orb's tangent-ball centres all land within a fraction of its radius
    counts = np.array(tree.query_ball_point(centres, radius * 0.45,
                                            workers=-1, return_length=True))
    # how much of the local surface agrees on that centre
    surf = cKDTree(verts)
    local = np.array(surf.query_ball_point(verts, radius * 2.2,
                                           workers=-1, return_length=True))
    agreement = counts / np.maximum(local, 1)
    orb_like = small & (agreement > 0.55) & (counts >= 6)

    # An orb is nearly a whole sphere, so the directions from its centre to the
    # surface cancel out. The rounded cap of the factory chimney also agrees on
    # a centre, but only covers one hemisphere and fails this.
    cand = np.where(orb_like)[0]
    if len(cand):
        rings = surf.query_ball_point(centres[cand], radius[cand] * 1.25,
                                      workers=-1)
        for k, i in enumerate(cand):
            ring = np.asarray(rings[k], dtype=int)
            if len(ring) < 6:
                orb_like[i] = False
                continue
            d = verts[ring] - centres[i]
            n = np.linalg.norm(d, axis=1)
            d = d[n > 1e-9] / n[n > 1e-9, None]
            if np.linalg.norm(d.mean(0)) > 0.35:
                orb_like[i] = False

    # A loose pebble is orb-like end to end; a real orb is a bud on a much
    # larger shell, so only a small share of its component qualifies. This is
    # the only separation available - an eye and a dirt clump are the same
    # shape, and the debris fields around the hive dwelling do keep a few
    # stray specks, which reads fine against the reference.
    sizes = np.bincount(labels, minlength=labels.max() + 1)
    orb_share = (np.bincount(labels, weights=orb_like.astype(float),
                             minlength=len(sizes)) / np.maximum(sizes, 1))
    return orb_like & (orb_share[labels] < 0.75) & (ao < 0.30)


def short_protrusions(verts, faces, thin, max_span=0.20):
    """Keep only the thin geometry that is also *short*.

    Thinness alone calls the factory's tall chimney a claw. Claws, spines and
    tusks are stubby: the connected patch of thin surface they form spans a
    fraction of the model, while a chimney or a tentacle runs across it.
    """
    if not thin.any():
        return thin
    keep_faces = faces[thin[faces].all(1)]
    if not len(keep_faces):
        return np.zeros_like(thin)
    edges = np.vstack([keep_faces[:, [0, 1]], keep_faces[:, [1, 2]],
                       keep_faces[:, [2, 0]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])),
                       shape=(len(verts), len(verts)))
    _, patch = connected_components(graph, directed=False)
    patch = np.where(thin, patch, -1)
    out = np.zeros_like(thin)
    for pid in np.unique(patch[patch >= 0]):
        sel = patch == pid
        if (verts[sel].max(0) - verts[sel].min(0)).max() <= max_span:
            out[sel] = True
    return out


def shield_core(verts, radius, ao):
    """The caged bulb inside the two orbital shields.

    Both shields are one welded shell, so the core cannot be split off as a
    component: it is picked out as the thick mass sitting on the model's axis,
    above the tentacle base and shadowed by the cage arms.
    """
    axis = np.hypot(verts[:, 0], verts[:, 2])
    thick = np.percentile(radius, 70)
    return (axis < 0.24) & (verts[:, 1] > -0.12) & (radius > thick) & (ao > 0.12)


# ------------------------------------------------------------- classification

def classify(name, verts, faces, normals, kit):
    """Zone id per welded vertex."""
    lowered = name.lower()
    zones = np.full(len(verts), CHITIN, np.int8)

    # Ship-kit loose parts name themselves; trust the artist over the geometry.
    if 'eye_orb' in lowered:
        zones[:] = EYE
        return zones
    if 'stix' in lowered:
        zones[:] = BONE
        return zones

    radius = medial_radius(verts, normals)
    ao = occupancy_ao(verts, faces, normals)
    labels = component_labels(verts, faces)

    # Thin geometry is bone: claws, spines, tusks, the sharp rim teeth. The
    # references keep bone to the tips, so this stays a narrow slice.
    cutoff = min(np.percentile(radius, 12), 0.012)
    zones[short_protrusions(verts, faces, radius < cutoff)] = BONE

    tuning = TUNING[kit]

    # Broad, exposed, thick tops catch the light in the references.
    lit = ((ao < np.percentile(ao, tuning['light_pct']))
           & (radius > np.percentile(radius, 45)))
    zones[lit & (zones == CHITIN)] = CHITIN_LIGHT

    # Crevices, mouth interiors and the shaded underside go near-black.
    buried = ao > np.percentile(ao, tuning['dark_pct'])
    zones[buried] = CHITIN_DARK

    zones[eye_orbs(verts, normals, radius, labels, ao)] = EYE

    if 'shield' in lowered:
        zones[shield_core(verts, radius, ao)] = GLOW
    elif 'vida_loca' in lowered:
        # the canyon floor between the plates glows violet in the reference
        zones[ao > np.percentile(ao, 96)] = GLOW

    return zones


def face_zones(zones, faces):
    """One zone per triangle: whatever two of its three corners agree on.

    Majority rather than "strongest accent wins" - the exports are flat shaded,
    so a single stray corner would otherwise smear bone across a third of the
    hull. Ties fall to the rarer, more characterful zone.
    """
    priority = np.array([0, 1, 2, 3, 4, 5])  # CHITIN .. GLOW
    corner = zones[faces]
    same01 = corner[:, 0] == corner[:, 1]
    same12 = corner[:, 1] == corner[:, 2]
    same02 = corner[:, 0] == corner[:, 2]
    out = np.where(same01 | same02, corner[:, 0], corner[:, 1])
    out = np.where(same12 & ~same01 & ~same02, corner[:, 1], out)
    tie = ~(same01 | same12 | same02)
    if tie.any():
        best = priority[corner[tie]].argmax(1)
        out[tie] = corner[tie][np.arange(tie.sum()), best]
    return out


# ------------------------------------------------------------------ rewriting

def repaint(src, dst, kit, report=False):
    glb = Glb(src)
    gltf = glb.json
    palette = PALETTES[kit]

    name_of_mesh = {}
    for node in gltf['nodes']:
        if 'mesh' in node:
            name_of_mesh.setdefault(node['mesh'], node.get('name', ''))

    blob = bytearray(glb.bin)
    views = gltf['bufferViews']
    accessors = gltf['accessors']
    tally = np.zeros(6, np.int64)

    for mesh_index, mesh in enumerate(gltf['meshes']):
        name = name_of_mesh.get(mesh_index, mesh.get('name', ''))
        new_prims = []
        for prim in mesh['primitives']:
            if 'indices' not in prim or 'POSITION' not in prim['attributes']:
                new_prims.append(prim)
                continue
            pos = glb.accessor(prim['attributes']['POSITION']).astype(np.float64)
            idx = glb.accessor(prim['indices']).astype(np.int64)
            verts, faces, inv, keep = weld(pos, idx)
            normals = vertex_normals(verts, faces)
            zones = classify(name, verts, faces, normals, kit)

            tris = idx.reshape(-1, 3)
            per_face = np.full(len(tris), CHITIN, np.int8)
            per_face[keep] = face_zones(zones, faces)
            tally += np.bincount(per_face, minlength=6)

            dtype = np.uint32 if len(pos) > 65535 else np.uint16
            comp = 5125 if dtype is np.uint32 else 5123
            for zone in range(6):
                sel = tris[per_face == zone]
                if not len(sel):
                    continue
                flat = sel.astype(dtype).ravel()
                offset = len(blob)
                blob.extend(flat.tobytes())
                blob.extend(b'\x00' * ((4 - len(blob) % 4) % 4))
                views.append({'buffer': 0, 'byteOffset': offset,
                              'byteLength': int(flat.nbytes),
                              'target': 34963})
                accessors.append({'bufferView': len(views) - 1,
                                  'componentType': comp,
                                  'count': int(flat.size),
                                  'type': 'SCALAR'})
                new_prims.append({'attributes': dict(prim['attributes']),
                                  'indices': len(accessors) - 1,
                                  'material': zone,
                                  'mode': prim.get('mode', 4)})
        mesh['primitives'] = new_prims

    gltf['materials'] = palette
    gltf['buffers'] = [{'byteLength': len(blob)}]
    write_glb(dst, gltf, bytes(blob))

    if report:
        total = tally.sum()
        print(f'{src.split("/")[-1]} -> {dst.split("/")[-1]}')
        for zone in range(6):
            share = 100.0 * tally[zone] / max(total, 1)
            print(f'  {ZONE_NAMES[zone]:14s} {tally[zone]:8d} tris  {share:5.1f}%')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--kit', choices=sorted(PALETTES), required=True)
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args(argv)
    repaint(args.src, args.dst, args.kit, args.report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
