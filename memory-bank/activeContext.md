# PixelPasta – Active Context

## Current focus
- **Universal Exposure Assist**: EV → selected camera log → any 3D `.cube` → Rec.709 Y IRE, with per-LUT SmallHD MAP tables and SENSOR SAFETY (pre-Look) vs LOOK EXPOSURE (post-Look).
- Canonical app: `lutcomparetool_app.py` on port 8080. Encoding selected at import via `encoding_catalog`. Optional real cubes via `EXPOSURE_ASSIST_LUT_DIR` (not copied into the repo).

## Recent changes
- Shared encoding catalog (`lut_analyzer_package/encoding_catalog.py`) with Sony/ARRI/RED/Panasonic/Canon/Rec.709/ACEScct pairs.
- Engine parameterized on `encoding`; contract includes `input_encoding` and `encoded_input`.
- UI: encoding always visible for batch + single; `/false-color` shows last-run scales (no vendor branding).
- Docs moved to `docs/exposure_assist/`.

## Active decisions
- Output metric is display-referred Rec.709 Y IRE **after** the viewing LUT.
- Highlight semantics: yellow = WARN, orange = HIGH, red = WHITE CLIPPING only; shadows use indigo (not pure black).
- Salmon = face exposure EV band (+0.5…+1), not chromatic skin detection.
- Encoding is never inferred from LUT filename.

## Next steps
- Keep verifying multi-encoding EA on `:8080` with real cubes when available.
- Do not commit or push without an explicit user request.
