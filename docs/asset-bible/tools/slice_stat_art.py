#!/usr/bin/env python3
"""Slice a generated stat-art element sheet into one transparent PNG per element.

The sheets are produced one image at a time (an image model holds a
consistent projection and scale far better within a single generation than
across several), so they arrive as a grid of separate objects on a
transparent background. This cuts them apart by connected component
rather than by an assumed grid, which survives the model spacing the
objects unevenly or slipping an extra variant into a row.

One cell of every sheet is a plain reference cube exactly one grid tile
wide. That is the scale key: it converts sprite pixels into the canvas
units the game's stat-art definitions are written in, so the element
boxes in the JSON are measured from the artwork instead of guessed.

Usage:
    python3 slice_stat_art.py SHEET.png --stat industry \\
        --out ~/.ascendancy/assets/common/stat-art

Writes <out>/<stat>/<id>.png plus <out>/<stat>-elements.json, a starting
point for the "elements" section of the game's definition file
(see ascendancy-remake docs/stat-art.md).
"""

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

# Element ids in sheet reading order, left to right and top to bottom.
# REFERENCE_CUBE is the scale key and is not written out as a sprite.
REFERENCE_CUBE = "_reference_cube"

# These follow the sheet, not the other way round: a re-rolled sheet with a
# different element in a cell needs this list edited to match, and the count
# check below is what catches the mismatch. The current list is for
# Industry_Stat_Details_Collection_4_no_background.png, whose four halls form
# a real length ladder (1.26 / 1.40 / 1.59 / 2.10 tiles) so the main hall can
# actually upgrade - the earlier sheets gave three halls of one length.
INDUSTRY_IDS = [
    "hall_2w", "hall_3w", "hall_4w", "hall_6w", REFERENCE_CUBE,
    "chimney_short", "chimney_tall", "column_teal", "column_red", "column_yellow",
    "silo_grey", "silo_pair", "sphere_teal", "sphere_pink", "vat_open",
    "gantry_truss", "pipe_bridge", "cooling_tower", "power_plant", "tower_slab",
]

SHEETS = {"industry": INDUSTRY_IDS}

# Alpha at or below this counts as background. Generated sheets come out
# cleanly keyed, so this only has to discard the antialiased fringe.
ALPHA_FLOOR = 40
# Components smaller than this are specks, not elements.
MIN_AREA = 400
# Closing radius that keeps a ribbed body from splitting into rings.
CLOSE_RADIUS = 5
# Two elements belong to the same row when their vertical centres are closer
# together than this fraction of the taller one's height.
ROW_TOLERANCE = 0.75

# Canvas units per grid tile in the game's definitions. The reference cube
# is one tile wide, so its pixel width maps to this many units.
TILE_UNITS = 56.0

# Bounds on the guessed footing height, as a fraction of the sprite box.
# A thin chimney sits almost on its bottom edge; nothing sits above the
# middle of its own artwork.
ANCHOR_Y_MIN = 0.04
ANCHOR_Y_MAX = 0.45


def find_elements(alpha):
    """Locate every element on the sheet, in reading order.

    Rows are grouped by how close the elements' vertical centres are, not
    by banding their top edges. Banding tops looks equivalent and is not:
    a short chimney standing beside tall distillation towers has its top
    edge most of its own height lower than theirs, lands in the next band,
    and sorts after the whole row - which silently shifts every id in that
    row by one and hands each element its neighbour's sprite.
    """
    mask = ndimage.binary_closing(
        alpha > ALPHA_FLOOR, structure=np.ones((CLOSE_RADIUS, CLOSE_RADIUS))
    )
    labels, _ = ndimage.label(mask)
    boxes = []
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        rows, columns = slices
        if (labels[slices] == index).sum() < MIN_AREA:
            continue
        boxes.append((columns.start, rows.start,
                      columns.stop - columns.start, rows.stop - rows.start))
    if not boxes:
        return []

    def centre(box):
        return box[1] + box[3] / 2.0

    boxes.sort(key=centre)
    rows_of = [[boxes[0]]]
    for box in boxes[1:]:
        previous = rows_of[-1][-1]
        limit = max(box[3], previous[3]) * ROW_TOLERANCE
        if abs(centre(box) - centre(previous)) > limit:
            rows_of.append([box])
        else:
            rows_of[-1].append(box)

    ordered = []
    for row in rows_of:
        row.sort(key=lambda box: box[0])
        ordered.extend(row)
    return ordered


def guess_anchor_y(width, height):
    """A starting guess at where the element's footing sits in its box.

    An isometric element rests on a diamond, and the point that lands on
    a grid tile is that diamond's centre, not the sprite's lowest pixel.
    For a box-shaped building the diamond is as wide as the silhouette and
    half as tall, which puts the centre a quarter of the width above the
    bottom.

    This is a guess and not a measurement, deliberately. Inferring the
    contact point from the pixels does not generalise: a sphere on three
    slim legs and an open lattice gantry have no visible base diamond at
    all, and trying to find one from the opaque-width profile gave three
    near-identical factory halls three different answers. So the formula
    is applied uniformly, and the numbers are tuned by eye against
    StatArtSheetTool's contact sheet, which is what it exists for.
    """
    return round(min(ANCHOR_Y_MAX, max(ANCHOR_Y_MIN, (width / 4.0) / height)), 2)


def slice_sheet(sheet, ids, out_dir, stat):
    image = Image.open(sheet).convert("RGBA")
    alpha = np.array(image)[:, :, 3]
    boxes = find_elements(alpha)
    if len(boxes) != len(ids):
        raise SystemExit(
            f"{sheet}: found {len(boxes)} elements but '{stat}' expects "
            f"{len(ids)}. Boxes: {boxes}"
        )

    cube_width = None
    for (x, y, w, h), name in zip(boxes, ids):
        if name == REFERENCE_CUBE:
            cube_width = w
    if not cube_width:
        raise SystemExit(f"{sheet}: no {REFERENCE_CUBE} in the id list.")
    units_per_pixel = TILE_UNITS / cube_width

    sprite_dir = out_dir / stat
    sprite_dir.mkdir(parents=True, exist_ok=True)
    elements = []
    for (x, y, w, h), name in zip(boxes, ids):
        if name == REFERENCE_CUBE:
            continue
        image.crop((x, y, x + w, y + h)).save(sprite_dir / f"{name}.png")
        elements.append({
            "id": name,
            "sprite": f"{stat}/{name}.png",
            "width": round(w * units_per_pixel, 1),
            "height": round(h * units_per_pixel, 1),
            "anchorX": 0.5,
            "anchorY": guess_anchor_y(w, h),
        })

    manifest = out_dir / f"{stat}-elements.json"
    manifest.write_text(json.dumps(elements, indent=2) + "\n")
    print(f"Wrote {len(elements)} sprites to {sprite_dir}")
    print(f"Reference cube {cube_width}px = {TILE_UNITS} canvas units "
          f"({units_per_pixel:.4f} units/px)")
    print(f"Element boxes for the definition: {manifest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", help="the generated element sheet")
    parser.add_argument("--stat", required=True, choices=sorted(SHEETS),
                        help="which stat's id list the sheet follows")
    parser.add_argument("--out", required=True,
                        help="directory to write <stat>/<id>.png into")
    args = parser.parse_args()
    slice_sheet(pathlib.Path(args.sheet).expanduser(), SHEETS[args.stat],
                pathlib.Path(args.out).expanduser(), args.stat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
