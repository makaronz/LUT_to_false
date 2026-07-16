# PixelPasta – Progress

## What works
- Flask LUT upload / analyze / compare against reference curves (Sony, ARRI, RED, Canon).
- Charts, PDF reports, comparison table data via `/table-data`.
- **Exposure Assist engine** (`lut_analyzer_package/exposure_assist.py`): real per-LUT anchors, zones, clipping ceilings for the four Swiniec planowe cubes when `SWINIEC_LUT_DIR` is set.
- **Exposure Assist tests** (`tests/test_exposure_assist.py`) — real LUTs only, hash-gated.
- **Exposure Assist documentation** (English, engine-sourced numbers):
  - `docs/swiniec_false_color/FALSE_COLOR_SCALE.md`
  - `docs/swiniec_false_color/analysis.json`
  - `docs/swiniec_false_color/false_color_preset.json`

## In progress
- Reporting pack: EV→IRE charts, RGB neutral-axis, clipping charts, false-color bars, multi-page PDF/ZIP per LUT.
- Flask batch mode `exposure_assist` on the 8080 app + results cards / CSS.

## Still to do
- End-to-end verification (upload four cubes, open all exports, regression on single/batch/compare).
- Broader WCAG polish, CI automation, creative prototypes (morphing / VR / temporal) — lower priority relative to Exposure Assist ship.

## Known limits
- Post-LUT MAP is look assist only; SENSOR SAFETY must measure pre-Look.
- Several LUTs peak below 99 IRE; WHITE CLIPPING starts at the measured ceiling where applicable.
- PixelPasta “Your LUT %” path that re-decodes display looks through OETF can saturate early — Exposure Assist measures LUT RGB directly as display code values.
