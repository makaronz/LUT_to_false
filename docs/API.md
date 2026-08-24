# API / application interfaces

> Earlier drafts of this file described a JWT REST API that **never existed in
> this codebase**. Below is what the apps actually expose.

## 1. Web app — `lutcomparetool_app.py` (local `:8080`)

HTML form app (no auth). Important routes:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Single-LUT upload (curve compare or Exposure Assist) |
| `POST` | `/analyze` | Analyze one `.cube` → HTML results or redirect to `/false-color` for EA (`?format=json` for JSON) |
| `GET` | `/batch` | Batch upload form |
| `POST` | `/analyze-batch` | Batch curve-compare **or** Exposure Assist |
| `GET` | `/false-color` | Exposure Assist / false-color scales from the latest run (alias: `/exposure-assist`) |
| `GET` | `/results` | Session-backed curve-compare results |
| `GET` | `/about` | About page |

### Form fields

- `lut_file` / `lut_files` — `.cube` upload(s)
- `analysis_mode` — `curve_compare` or `exposure_assist`
- `curve_select` — encoding key from `lut_analyzer_package.encoding_catalog` (valid transfer+gamut pairs only; default `slog3_cine`)

### Exposure Assist

- Engine: `analyze_exposure_assist({ lut_path, encoding })`
- Docs: [`exposure_assist/FALSE_COLOR_SCALE.md`](exposure_assist/FALSE_COLOR_SCALE.md)
- Per-LUT MAP scales; SENSOR SAFETY (pre-Look) vs LOOK EXPOSURE (post-Look)
- Highlight palette: yellow WARN, orange HIGH, red WHITE CLIPPING only

### Analyze example

```bash
curl -X POST -F "lut_file=@path/to/lut.cube" \
     -F "curve_select=slog3_cine" \
     -F "analysis_mode=exposure_assist" \
     "http://localhost:8080/analyze?format=json"
```

## 2. Experimental app — `pixelpasta/app.py` (port 5000)

Not the canonical Exposure Assist surface. Prefer `lutcomparetool_app.py`.

## 3. CLI — `cube_analyzer.py`

```bash
python cube_analyzer.py input.cube -s slog3 -t rec709 -o output_dir
```
