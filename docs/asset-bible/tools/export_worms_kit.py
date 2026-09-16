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

Two optional passes trim the result down:

* ``--exclude-shared-with SHIPS.glb`` drops every object whose name is also a
  node of that GLB. The buildings .blend accumulated 26 parts belonging to the
  ship kit - an abandoned experiment - and they were a third of the shipped
  file, each one a full copy rather than an instance.
* ``--strip-normals`` deletes the NORMAL accessors from the finished GLB, which
  is about 46% of its bytes. gdx-gltf recomputes them on load
  (``MeshLoader`` -> ``MeshTangentSpaceGenerator.computeNormals``) by summing
  face normals into each vertex, so a corner that belongs to exactly one face -
  which is what flat shading already forces - gets that face's normal back
  unchanged, and a shared corner in a smooth-shaded patch gets the average it
  wanted anyway. Note the order: this has to happen *after* the export, because
  Blender's own ``export_normals=False`` would weld the corners first and the
  recomputed normals would then come out smooth, flattening the facets.

Usage:
    blender -b KIT.blend -P export_worms_kit.py -- --out OUT.glb [--no-repair]
        [--exclude-shared-with OTHER.glb] [--exclude NAME ...] [--strip-normals]
"""

import argparse
import json
import os
import struct
import sys

import bmesh
import bpy

_COMPONENT_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
_TYPE_COUNT = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


def parse_args(argv=None):
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, help='GLB to write')
    ap.add_argument('--merge-distance', type=float, default=1e-5)
    ap.add_argument('--no-repair', dest='repair', action='store_false',
                    help='export the collection exactly as it is')
    ap.add_argument('--exclude', nargs='*', default=[], metavar='NAME',
                    help='object names to leave out of the export')
    ap.add_argument('--exclude-shared-with', metavar='GLB',
                    help='also leave out every object that is a node of this GLB')
    ap.add_argument('--strip-normals', action='store_true',
                    help='drop the NORMAL accessors from the exported GLB')
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


def read_glb(path):
    """Split a GLB into its JSON and binary chunks."""
    data = open(path, 'rb').read()
    gltf, blob, offset = None, b'', 12
    while offset < len(data):
        length, kind = struct.unpack('<II', data[offset:offset + 8])
        chunk = data[offset + 8:offset + 8 + length]
        if kind == _JSON_CHUNK:
            gltf = json.loads(chunk.decode('utf-8'))
        elif kind == _BIN_CHUNK:
            blob = chunk
        offset += 8 + length
    return gltf, blob


def write_glb(path, gltf, blob):
    """Write a GLB, padding both chunks to the 4-byte alignment the spec wants."""
    js = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    blob += b'\x00' * ((4 - len(blob) % 4) % 4)
    with open(path, 'wb') as fh:
        fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        fh.write(struct.pack('<II', len(js), _JSON_CHUNK))
        fh.write(js)
        fh.write(struct.pack('<II', len(blob), _BIN_CHUNK))
        fh.write(blob)


def accessor_bytes(gltf, blob, index):
    """One accessor's data, tightly packed, whatever stride its view uses."""
    acc = gltf['accessors'][index]
    view = gltf['bufferViews'][acc['bufferView']]
    elem = _TYPE_COUNT[acc['type']] * _COMPONENT_SIZE[acc['componentType']]
    base = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    stride = view.get('byteStride', elem)
    if stride == elem:
        return blob[base:base + elem * acc['count']]
    return b''.join(blob[base + i * stride:base + i * stride + elem]
                    for i in range(acc['count']))


def node_names(path):
    """Names of the mesh-bearing nodes of a GLB."""
    gltf, _ = read_glb(path)
    return {n['name'] for n in gltf.get('nodes', ()) if 'mesh' in n and 'name' in n}


def strip_normals(path):
    """Drop the NORMAL accessors and repack the buffer around what is left.

    Rebuilds every buffer view from scratch rather than editing in place, so the
    bytes the normals used to occupy actually leave the file instead of becoming
    an unreferenced hole.
    """
    gltf, blob = read_glb(path)
    if any('targets' in prim for mesh in gltf['meshes'] for prim in mesh['primitives']) \
            or gltf.get('skins'):
        raise SystemExit('morph targets or skins present - accessor rewrite would lose them')

    out = bytearray()
    views, accessors, remap = [], [], {}

    def keep(index, target):
        if index not in remap:
            data = accessor_bytes(gltf, blob, index)
            while len(out) % 4:
                out.append(0)
            views.append({'buffer': 0, 'byteOffset': len(out),
                          'byteLength': len(data), 'target': target})
            out.extend(data)
            acc = gltf['accessors'][index]
            new = {'bufferView': len(views) - 1,
                   'componentType': acc['componentType'],
                   'count': acc['count'], 'type': acc['type']}
            for key in ('min', 'max', 'normalized'):
                if key in acc:
                    new[key] = acc[key]
            accessors.append(new)
            remap[index] = len(accessors) - 1
        return remap[index]

    dropped = 0
    for mesh in gltf['meshes']:
        for prim in mesh['primitives']:
            if prim['attributes'].pop('NORMAL', None) is not None:
                dropped += 1
            prim['attributes'] = {name: keep(acc, 34962)
                                  for name, acc in prim['attributes'].items()}
            if 'indices' in prim:
                prim['indices'] = keep(prim['indices'], 34963)

    gltf['bufferViews'] = views
    gltf['accessors'] = accessors
    gltf['buffers'] = [{'byteLength': len(out)}]
    write_glb(path, gltf, bytes(out))
    return dropped


def main():
    args = parse_args()

    excluded = set(args.exclude)
    if args.exclude_shared_with:
        excluded |= node_names(args.exclude_shared_with)
    dropped_objects = [ob.name for ob in bpy.data.objects
                       if ob.type == 'MESH' and ob.name in excluded]
    for name in dropped_objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    # Orphaned meshes and materials would otherwise ride along in the export;
    # the ship parts bring a whole second palette with them.
    for mesh in [m for m in bpy.data.meshes if m.users == 0]:
        bpy.data.meshes.remove(mesh)
    for material in [m for m in bpy.data.materials if m.users == 0]:
        bpy.data.materials.remove(material)

    meshes = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    if not meshes:
        raise SystemExit('no mesh objects left to export')

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

    size_before = os.path.getsize(args.out)
    stripped = strip_normals(args.out) if args.strip_normals else 0

    print('__KIT_EXPORT__ {:s} meshes={:d} excluded={:d} merged_verts={:d} '
          'removed_faces={:d} reoriented_faces={:d} stripped_normals={:d} '
          'MB={:.1f}{:s}'.format(
              args.out, len(meshes), len(dropped_objects), total['merged_verts'],
              total['removed_faces'], total['reoriented_faces'], stripped,
              os.path.getsize(args.out) / 1048576,
              ' (was {:.1f})'.format(size_before / 1048576) if stripped else ''))


if __name__ == '__main__':
    main()
