# PixelPasta – Active Context

## Current focus
- **Swiniec Exposure Assist**: deterministic EV→S-Log3→LUT→Rec.709 Y IRE analysis for four planowe LUTs (`-1`, `0`, `1`, `red`), with separate SmallHD MAP tables and SENSOR SAFETY (pre-Look) vs LOOK EXPOSURE (post-Look) workflow.
- Canonical app entry remains `lutcomparetool_app.py` on port 8080; LUTs are read from `SWINIEC_LUT_DIR` and are **not** copied into the repo.

## Recent changes
- Pure engine: `lut_analyzer_package/exposure_assist.py` (anchors, neutral axis, grid stats, per-LUT SmallHD zones, clipping ceiling).
- Tests: `tests/test_exposure_assist.py` against real cubes + SHA-256 gates.
- Docs refreshed from engine output (English): `docs/swiniec_false_color/FALSE_COLOR_SCALE.md`, `analysis.json`, `false_color_preset.json` — including second-model audit (rejected RED-camera speculation for `_red`).
- Parallel work in progress (other agents): reporting/visuals + Flask batch `exposure_assist` mode — do not fight those file ownership boundaries unless reassigned.

## Active decisions
- Output metric is display-referred Rec.709 Y IRE **after** the viewing LUT.
- Primary viewing look for examples: `Swiniec_LUT_0`.
- Highlight semantics: yellow = WARN, orange = HIGH, red = WHITE CLIPPING only; shadows use indigo (not pure black).
- Salmon = face exposure EV band (+0.5…+1), not chromatic skin detection.
- `Swiniec_LUT_red` = S-Log3/S-Gamut3.Cine look variant, **not** RED input.

## Next steps
- Complete visuals/PDF/exports per LUT (`reporting.py`) and Flask batch Integration UI.
- End-to-end verify on `127.0.0.1:8080` with the four real cubes; run full test + lint pass.
- Do not commit or push without an explicit user request.
