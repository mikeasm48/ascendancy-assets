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
    docs/asset-bible/refs/ui/Ascendancy_Screen_Widgets/Industry/Industry_Stat_Details_Collection.png \
    --stat industry --out ~/.ascendancy/assets/common/stat-art
```

That writes `common/stat-art/<stat>/<id>.png` into the bundle, plus a
`<stat>-elements.json` of measured element boxes to paste into the game's
definition file.

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
