# FoodStock Loop Video

Data-driven 16:9 loop video (TV/in-store display) for **FoodStock** food court (471 พัฒนาการ 32).
JSON data → generated HTML composition → rendered to MP4 via HyperFrames. One restaurant scene per data row — reorder, re-theme, or swap photos without touching markup.

Sibling project to [`foodstock-reels`](https://github.com/nutttt-nut/foodstock-reels) (vertical social clips) — shares brand palette/typography, different structure (one long TV composition vs. one template rendered per clip).

## Stack

- **Generator:** `generate.py` (Python 3 stdlib only) — reads `data/*.json` → writes `index.html` (video source) + `editor.html` (basic editor)
- **Render:** [HyperFrames](https://www.npmjs.com/package/hyperframes) — renders `index.html` frame-by-frame → `ffmpeg` → MP4
- **Animation:** GSAP (ken-burns, crossfade, stagger text), loaded from CDN inside the generated HTML
- **VPS editor:** `editor-pro.html` + `server.py` (Flask) — drag-reorder scenes, upload photos/overlays, position overlays visually, then `Save` + `Regenerate`

## Quick start

```bash
python3 generate.py                                   # data/*.json -> index.html + editor.html
npx hyperframes render index.html --fps 30 --output foodstock-loop.mp4
```

Preview render (fast, low-res):

```bash
npx hyperframes render index.html --fps 15 --scale 0.5 --output preview.mp4
```

## Structure

```
generate.py          # main generator — data/*.json -> index.html + editor.html
server.py             # localhost-only Flask backend for the VPS editor
editor-pro.html        # VPS editor UI (drag reorder, upload, overlay positioning)
editor-blank.html      # blank starting template for editor-pro
direction-preview.html # visual direction / theme comparison sandbox
make_contact_sheet.py   # builds a contact sheet from data/photos for quick review
scrape/scrape.py        # scrapes restaurant/menu data from source listing
data/
  restaurants.json     # per-restaurant scene data + overlay positions
  brand-config.json    # intro/outro copy
  photos/               # restaurant photos (id-matched filenames)
  overlays/             # promo/badge overlay images
  brand/                 # logo assets
fonts/                  # Noto Sans Thai (bundled for consistent rendering)
```

`index.html` and `editor.html` are build artifacts (regenerate with `python3 generate.py`) and aren't committed.

## Editing content

**Via the VPS editor (recommended)** — reorder scenes, upload photos/overlays, drag-position overlays on a live 1920×1080 preview, `Save` writes `data/*.json`, `Regenerate` re-runs `generate.py` on the VPS.

**Directly** — edit `data/restaurants.json` (name / menu / photo) and `data/brand-config.json` (intro/outro copy), then `python3 generate.py`.

Pull VPS edits back to a local clone:

```bash
scripts/pull-editor-data.sh
```

Full step-by-step workflow, VPS deploy/service commands, and theme-switching: [`WORKFLOW.md`](WORKFLOW.md)
Brand palette, typography, motion rules: [`design.md`](design.md)
Open workflow pain points / ideas: [`WORKFLOW_NOTES.md`](WORKFLOW_NOTES.md)

## Output

1920×1080, 30fps MP4. Duration = intro (3.2s) + restaurants × `SCENE_HOLD` (5s each) + outro (~4s) — tune `SCENE_HOLD` in `generate.py` to change pacing globally.
