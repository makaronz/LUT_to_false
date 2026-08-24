# PixelPasta – Progress

## What works
- Flask LUT upload / analyze / compare against reference encodings (Sony, ARRI, RED, Canon, Panasonic, Rec.709, ACEScct).
- Charts, PDF reports, comparison table data via `/table-data`.
- **Universal Exposure Assist** (`lut_analyzer_package/exposure_assist.py` + `encoding_catalog.py`): per-LUT anchors, zones, clipping; encoding selected at import.
- Batch + single Exposure Assist UI on `lutcomparetool_app.py`; `/false-color` shows last-run scales.
- Docs: `docs/exposure_assist/FALSE_COLOR_SCALE.md`, `docs/API.md`.

## Still to do
- Broader WCAG polish, CI automation — lower priority relative to Exposure Assist.

## Known limits
- Post-LUT MAP is look assist only; SENSOR SAFETY must measure pre-Look.
- Neutral-axis EV depends on transfer curve; gamut is metadata for grayscale Y.
- Several LUTs peak below 99 IRE; WHITE CLIPPING starts at the measured ceiling where applicable.
