# Element sheets for the planet status widgets

Unlike the rest of `refs/`, **these are not references - they are source
assets**, and they keep their full resolution and their alpha channel.

The planet status widgets do not show one picture per value. INDUSTRY has
no ceiling and a widget cell is around 230 x 100 px, so the picture is
composed at runtime from a small library of reusable sprites: see
`ascendancy-remake/docs/stat-art.md` and `view/statart`.

Each sheet here is one generation holding a whole library. They are made
as a single image on purpose - an image model holds a consistent
projection, scale and palette far better within one generation than across
several - and then cut apart by `tools/slice_stat_art.py`:

```bash
python3 docs/asset-bible/tools/slice_stat_art.py \
    docs/asset-bible/refs/ui/Ascendancy_Screen_Widgets/Industry/Industry_Stat_Details_Collection_4_no_background.png \
    --stat industry --out ~/.ascendancy/assets/common/stat-art
```

That writes `common/stat-art/<stat>/<id>.png` into the bundle, plus a
`<stat>-elements.json` of measured element boxes to paste into the game's
definition file.

`INDUSTRY_IDS` in the script is the sheet's reading order, and the sheet is
authoritative: a re-roll that puts a different element in a cell needs that
list edited to match, and the count check is what catches the mismatch.

## Which INDUSTRY sheet is the live one

Four were generated; **sheet 4, background removed, is the library the game
uses.** The others are kept because comparing them is how the choice was
made, and because the next stat's prompt should learn from them. Measured
against each sheet's own reference cube, the four factory halls came back:

| Sheet | Hall lengths, in tiles | Verdict |
| --- | --- | --- |
| 1 | 1.15 / 1.19 / 1.19 / 2.41 | Three identical, one long |
| 2 | 0.95 / 1.07 / 1.19 / 1.47 | Even ladder, no long hall |
| 3 | 0.99 / 1.00 / 1.22 / 1.36 | Two identical, no long hall |
| **4** | **1.26 / 1.40 / 1.59 / 2.10** | **Even ladder and a long hall** |

A hall ladder that visibly grows is the load-bearing requirement, since the
main hall is the one element that upgrades as INDUSTRY rises, and a swap
between two halls of the same length reads as nothing having happened.
Three sheets out of four got exactly that wrong while honouring projection,
palette, transparency and the reference cube without complaint. Ask for
relative proportions explicitly and expect to re-roll.

Two other things to check the moment a sheet arrives:

- **Judge it at the target size, not at full size.** In a widget cell the
  whole complex is around 100 px wide; contrast and silhouette decide
  everything and detail is invisible. Sheet 2's pastel-on-cream halls lost
  their windows completely at that scale and its plain capsule columns
  became indistinguishable from chimneys.
- **Check the alpha channel, not the checkerboard.** Sheet 4 first arrived
  as RGB with a light checkerboard *painted into the pixels*, which looks
  exactly like transparency in any viewer. The slicer prints the
  transparent fraction; 0% means the sheet needs re-exporting.


## Why these are not compressed like the other refs

The folder policy elsewhere in `refs/` is a squashed copy (<=1024px, JPEG
q85) with the original kept outside git. Neither half applies here:

- **JPEG would destroy the alpha channel**, and the alpha is the whole
  point. The sprites have to composite over the planet surface.
- **Downscaling would lose the scale key.** Every sheet carries a plain
  reference cube exactly one grid tile wide, which is what converts sprite
  pixels into the canvas units the definitions are written in. Resampling
  it costs precision on every element box derived from it.
- These are not reproducible. A rebuilt GLB is byte-different but visually
  identical, so it belongs outside git; a re-rolled generation is a
  different picture. The sheet is the master.

At a couple of megabytes each, and one sheet per stat, this stays far
away from the repository-size problem that the GLB bundle had.
