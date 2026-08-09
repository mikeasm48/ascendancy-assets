#!/usr/bin/env python3
"""Export a Worms constructor .blend as one GLB, repairing it on the way out.

The Worms kits are not generated here - they arrive as .blend files whose one
collection holds the whole constructor, and the GLB that feeds
``paint_worms_constructors.py`` is an export of that collection. This script is
that export, plus the geometry repair the exports need:

* **merge by distance** - a few hundred vertices per kit sit exactly on top of
  one another, and two triangles meeting at a doubled vertex are not neighbours,
  so every one of them tears the shell open along a seam.
* **degenerate faces** - zero-area triangles left over from the doubles.
* **recalculate normals outside** - roughly 1.2% of the faces point into the
  solid. There is no NORMAL data in the source and none authored in the .blend,
  so the face orientation *is* the shading, in Blender and in the engine alike.

All three are left to Blender's own operators on purpose. Deciding "which way is
out" from the geometry alone was tried in the painter and abandoned: on shells
this open, enclosed volume is meaningless and an occupancy vote guessed wrong
more often than the exporter did (3.3k badly-facing triangles became 4.3k and
24k). ``recalc_face_normals`` ray-casts against the actual solid and gets it
right, and now that headless Blender is on PATH there is no reason to
reimplement it.

Flat shading survives all of this: it lives in the faces' ``use_smooth`` flag,
and the glTF exporter re-splits the vertices per corner on the way out. Welding
the *exported* buffer instead would destroy it - 99.6% of co-located exported
vertices carry different normals.

Usage:
    blender -b KIT.blend -P export_worms_kit.py -- --out OUT.glb [--no-repair]
"""

import argparse
import sys

import bmesh
import bpy


def parse_args(argv=None):
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, help='GLB to write')
    ap.add_argument('--merge-distance', type=float, default=1e-5)
    ap.add_argument('--no-repair', dest='repair', action='store_false',
                    help='export the collection exactly as it is')
    return ap.parse_args(argv)


def repair_mesh(mesh, merge_distance):
    """Weld, drop degenerates and face every triangle outward. Returns a tally."""
    bm = bmesh.new()
    bm.from_mesh(mesh)

    before_verts = len(bm.verts)
    before_faces = len(bm.faces)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=merge_distance)
    bmesh.ops.dissolve_degenerate(bm, dist=merge_distance, edges=bm.edges[:])

    bm.faces.ensure_lookup_table()
    was = [f.normal.copy() for f in bm.faces]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    reoriented = sum(1 for f, n in zip(bm.faces, was) if f.normal.dot(n) < 0)

    tally = {
        'merged_verts': before_verts - len(bm.verts),
        'removed_faces': before_faces - len(bm.faces),
        'reoriented_faces': reoriented,
    }
    bm.to_mesh(mesh)
    bm.free()
    return tally


def main():
    args = parse_args()
    meshes = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    if not meshes:
        raise SystemExit('no mesh objects in this .blend')

    total = {'merged_verts': 0, 'removed_faces': 0, 'reoriented_faces': 0}
    if args.repair:
        for ob in meshes:
            # One datablock can back several objects; repairing it twice is
            # harmless but the tally would double-count.
            if ob.data.get('_worms_repaired'):
                continue
            for key, value in repair_mesh(ob.data, args.merge_distance).items():
                total[key] += value
            ob.data['_worms_repaired'] = True
        for ob in meshes:
            ob.data.pop('_worms_repaired', None)

    bpy.ops.object.select_all(action='DESELECT')
    for ob in meshes:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]

    bpy.ops.export_scene.gltf(
        filepath=args.out,
        export_format='GLB',
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_apply=False,
    )

    print('__KIT_EXPORT__ {:s} meshes={:d} merged_verts={:d} '
          'removed_faces={:d} reoriented_faces={:d}'.format(
              args.out, len(meshes), total['merged_verts'],
              total['removed_faces'], total['reoriented_faces']))


if __name__ == '__main__':
    main()
