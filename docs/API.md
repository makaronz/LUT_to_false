# API / application interfaces

> Earlier drafts of this file described a JWT REST API that **never existed in
> this codebase**. Below is what the apps actually expose.

## 1. Web app — `lutcomparetool_app.py` (local `:8080`, production on Vercel)

HTML form app (no auth). Important routes:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Single-LUT upload form |
| `POST` | `/analyze` | Analyze one `.cube` → HTML results page (JSON if `?format=json`) |
| `GET` | `/batch` | Batch upload form |
| `POST` | `/analyze-batch` | Batch curve-compare **or** Exposure Assist |
| `GET` | `/false-color` | **Swiniec false-color / Exposure Assist scales** (alias: `/exposure-assist`) |
| `GET` | `/results` | Session-backed results (local disk); less reliable on serverless |
| `GET` | `/about` | About page |

### False color / Exposure Assist UI

Dedicated page: [`/false-color`](../templates/false_color.html) (also `/exposure-assist`).

Data sources shipped under `static/swiniec_false_color/` (mirrored from
`docs/swiniec_false_color/` so Vercel can serve them — `docs/` is ignored at deploy):

- `false_color_preset.json` — four SmallHD MAP tables + SENSOR SAFETY / LOOK EXPOSURE
- `analysis.json` — full engine contracts
- `false_color_strip.png` — reference strip graphic

Operator narrative (English): [`docs/swiniec_false_color/FALSE_COLOR_SCALE.md`](swiniec_false_color/FALSE_COLOR_SCALE.md).

Per-LUT chart packs (PNG/SVG/PDF/CSV) are generated via **Batch → Analysis mode:
Exposure Assist** (`generate_exposure_assist_report`).

### Analyze example

```bash
# HTML results (browser form)
curl -X POST -F "lut_file=@path/to/lut.cube" -F "curve_select=slog3_cine" \
     http://localhost:8080/analyze

# JSON payload
curl -X POST -F "lut_file=@path/to/lut.cube" -F "curve_select=slog3_cine" \
     "http://localhost:8080/analyze?format=json"
```

## 2. Experimental app — `pixelpasta/app.py` (port 5000)

- `POST /api/analyze` — fields `cube-file` + `color-space`.
  Returns percentage lists for exposure / log / Rec.709 / LUT curves.

## 3. CLI — `cube_analyzer.py`

```bash
python cube_analyzer.py input.cube -s slog3 -t rec709 -o output_dir
```

See the README CLI section for flags.
