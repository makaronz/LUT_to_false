# Swiniec Exposure Assist — False Color / SmallHD MAP Scale

Deterministic documentation generated from `lut_analyzer_package.exposure_assist.analyze_exposure_assist` on the four planowe LUTs (paths via `SWINIEC_LUT_DIR`; cubes are not copied into this repository).

| Field | Value |
|---|---|
| Input encoding | Sony S-Log3 / S-Gamut3.Cine (neutral RGB axis) |
| Middle gray | 0.18 scene-linear (= 0 EV) |
| Output metric | Display-referred Rec.709 luma **Y as IRE** after the LUT (no second display OETF decode) |
| Canonical viewing look | `Swiniec_LUT_0.cube` |
| Machine-readable artefacts | [`analysis.json`](analysis.json), [`false_color_preset.json`](false_color_preset.json) |

> **Important:** These IRE bands describe the **Look path after the viewing LUT**. They are not camera-log percentages and do not replace a pre-Look sensor safety check.

---

## SmallHD two-page workflow

### Page A — SENSOR SAFETY (measure **before** Look)

| Item | Guidance |
|---|---|
| Signal | Pre-Look path: S-Log3 (or the monitor’s camera/overlay false color on the sensor feed) |
| Goal | Protect the captured signal from sensor / log clipping |
| False color | Use the camera vendor overlay or a log-appropriate false-color profile — **not** the post-LUT Rec.709 MAP tables below |
| Why separate | Post-LUT IRE can look “safe” while the sensor is already clipped; conversely, a dark look can paint highlights orange/red while log headroom remains |

### Page B — LOOK EXPOSURE (measure **after** Look)

| Item | Guidance |
|---|---|
| Signal | Display path with the chosen Swiniec viewing LUT applied |
| Goal | Expose for the intended look (underrate / face band / highlight warnings in Rec.709 Y IRE) |
| False color | Load the **per-LUT** MAP table for that exact `.cube` (four independent scales — no shared percentage scale) |
| Semantic anchors | Green ≈ −1 EV · salmon = face exposure +0.5…+1 EV (not chromatic skin ID) · yellow = WARN (+2 EV) · orange = HIGH (+3 EV) · red = WHITE CLIPPING only |

On SmallHD-class monitors that support dual false-color pages or A/B signal routing: keep SENSOR SAFETY on the clean feed and LOOK EXPOSURE on the Look-processed feed.

---

## Source integrity (SHA-256)

| File | SHA-256 |
|---|---|
| `Swiniec_LUT_-1.cube` | `fcfc1e65dd09df257d0b2f43c1b379c3ac7f85b4d7015825687ba4eb9c1a33c2` |
| `Swiniec_LUT_0.cube` | `c1f029a1ef5c7bd865c6ce32c349a67d8ca44c9023362f0bbf54fecde6e0929f` |
| `Swiniec_LUT_1.cube` | `82ad34dfc03989c3f2201d40304a69b6566f567bbfb3a66340eced84301cdcb2` |
| `Swiniec_LUT_red.cube` | `d5da1bab519c3f498ee863c47f188fe148526d2f3dc361a14e491da174d36e64` |

All four are 33³ 3D LUTs, domain `[0,1]`, neutral-axis monotonic (confidence `high` / score `1.0`).

---

## Neutral-axis anchors (Rec.709 Y IRE after LUT)

Values from the engine at key EV points (18% = 0 EV). Full precision lives in `analysis.json`.

| EV | LUT_-1 | LUT_0 | LUT_1 | LUT_red |
|---:|---:|---:|---:|---:|
| −1.25 | 27.92 | 27.42 | 32.52 | 24.73 |
| −1.0 | 32.08 | **31.42** | 36.92 | 28.54 |
| −0.75 | 36.53 | 35.70 | 41.50 | 32.68 |
| 0.0 | 50.62 | **49.24** | 55.46 | 46.05 |
| +0.5 | 59.98 | 58.25 | 64.26 | 55.16 |
| +1.0 | 68.48 | **66.43** | 71.87 | 63.55 |
| +2.0 | 81.74 | 79.19 | 83.02 | 76.84 |
| +3.0 | 90.23 | 87.36 | 89.77 | 85.47 |

---

## Four separate SmallHD MAP tables (LOOK EXPOSURE)

Zone construction (engine):

- **DEEP SHADOW** — indigo `#312E81` from 0 IRE to −1.25 EV
- **−1 EV TARGET** — green `#22C55E` from −1.25 EV to −0.75 EV
- **MID RANGE** — cyan `#0891B2` from −0.75 EV to +0.5 EV
- **FACE EXPOSURE** — salmon `#FA8072` from +0.5 EV to +1.0 EV
- **BRIGHT SAFE** — gold `#D4A017` from +1.0 EV to +2.0 EV
- **WARN** — yellow `#FACC15` from +2.0 EV to +3.0 EV
- **HIGH** — orange `#F97316` from +3.0 EV to clipping threshold
- **WHITE CLIPPING** — red `#DC2626` from clipping threshold to 100 IRE

Clipping threshold = `min(99.0 IRE, measured LUT grid luma ceiling)`.

### `Swiniec_LUT_-1` MAP

| Zone | Min IRE | Max IRE | Hex |
|---|---:|---:|---|
| DEEP SHADOW | 0.00 | 27.92 | `#312E81` |
| −1 EV TARGET | 27.92 | 36.53 | `#22C55E` |
| MID RANGE | 36.53 | 59.98 | `#0891B2` |
| FACE EXPOSURE | 59.98 | 68.48 | `#FA8072` |
| BRIGHT SAFE | 68.48 | 81.74 | `#D4A017` |
| WARN | 81.74 | 90.23 | `#FACC15` |
| HIGH | 90.23 | 99.00 | `#F97316` |
| WHITE CLIPPING | 99.00 | 100.00 | `#DC2626` |

Signal ceiling (grid max Y IRE): **99.77** → threshold uses standard **99.00**.

### `Swiniec_LUT_0` MAP (primary viewing look)

| Zone | Min IRE | Max IRE | Hex |
|---|---:|---:|---|
| DEEP SHADOW | 0.00 | 27.42 | `#312E81` |
| −1 EV TARGET | 27.42 | 35.70 | `#22C55E` |
| MID RANGE | 35.70 | 58.25 | `#0891B2` |
| FACE EXPOSURE | 58.25 | 66.43 | `#FA8072` |
| BRIGHT SAFE | 66.43 | 79.19 | `#D4A017` |
| WARN | 79.19 | 87.36 | `#FACC15` |
| HIGH | 87.36 | 97.58 | `#F97316` |
| WHITE CLIPPING | 97.58 | 100.00 | `#DC2626` |

Signal ceiling: **97.58** → WHITE CLIPPING starts at measured ceiling (below 99).

### `Swiniec_LUT_1` MAP

| Zone | Min IRE | Max IRE | Hex |
|---|---:|---:|---|
| DEEP SHADOW | 0.00 | 32.52 | `#312E81` |
| −1 EV TARGET | 32.52 | 41.50 | `#22C55E` |
| MID RANGE | 41.50 | 64.26 | `#0891B2` |
| FACE EXPOSURE | 64.26 | 71.87 | `#FA8072` |
| BRIGHT SAFE | 71.87 | 83.02 | `#D4A017` |
| WARN | 83.02 | 89.77 | `#FACC15` |
| HIGH | 89.77 | 98.02 | `#F97316` |
| WHITE CLIPPING | 98.02 | 100.00 | `#DC2626` |

Signal ceiling: **98.02** → WHITE CLIPPING starts at measured ceiling.

### `Swiniec_LUT_red` MAP

| Zone | Min IRE | Max IRE | Hex |
|---|---:|---:|---|
| DEEP SHADOW | 0.00 | 24.73 | `#312E81` |
| −1 EV TARGET | 24.73 | 32.68 | `#22C55E` |
| MID RANGE | 32.68 | 55.16 | `#0891B2` |
| FACE EXPOSURE | 55.16 | 63.55 | `#FA8072` |
| BRIGHT SAFE | 63.55 | 76.84 | `#D4A017` |
| WARN | 76.84 | 85.47 | `#FACC15` |
| HIGH | 85.47 | 96.37 | `#F97316` |
| WHITE CLIPPING | 96.37 | 100.00 | `#DC2626` |

Signal ceiling: **96.37** → WHITE CLIPPING starts at measured ceiling.  
`_red` is a **S-Log3 / S-Gamut3.Cine viewing look** with a cooler/redder grade — **not** a RED-camera input transform.

---

## Clipping limitations

1. **Post-LUT ≠ sensor clip.** Red on LOOK EXPOSURE means the Look already paints that output near legal white; the sensor may have clipped earlier (or may still have headroom). Always run SENSOR SAFETY on the clean path.
2. **Ceiling may be below 99 IRE.** For LUT_0 / LUT_1 / LUT_red the measured grid luma peak is below 99; WHITE CLIPPING therefore begins at that ceiling, not at a fictional 99/100 plateau.
3. **Neutral-axis model.** EV→IRE follows achromatic RGB. Salmon is the **+0.5…+1 EV exposure band**, not “detected skin.” Chromatic subjects can fall in different zones.
4. **No second OETF decode.** LUT RGB is treated as display RGB; converting again through Rec.709 OETF would mis-report IRE.
5. **Domain clip.** Inputs outside the declared LUT domain are clipped by tetrahedral interpolation before measurement.

Engine limitation strings are also stored under each LUT entry in `analysis.json`.

---

## Sony / SmallHD references

| Topic | Source |
|---|---|
| S-Log3 / S-Gamut3.Cine encoding and middle-gray behaviour | Sony Imaging technical summaries for S-Log3 (e.g. “S-Log3 Technical Summary” / camera white papers; 18% gray maps to ~41% S-Log3 code value) |
| Legal / full vs IRE monitoring conventions | ITU-R BT.709 luma weights (`0.2126 / 0.7152 / 0.0722`); production monitors treat 100 IRE as legal white for Rec.709 display |
| SmallHD false color / exposure assist tooling | SmallHD monitor documentation for False Color and custom false-color maps (PAGE / SIGNAL routing so Look and clean feeds can use different overlays) |
| Implementation curve in this repo | `curves.linear_to_slog3` (official S-Log3 formula) feeding `exposure_assist` |

Cursor docs and monitor firmware versions change; pin the monitor firmware in production SOPs when loading custom MAP values from `false_color_preset.json`.

---

## Second-model audit (cross-check summary)

Brief independent review against an earlier second-LLM pass on the same LUT set:

| Finding | Status |
|---|---|
| Neutral-axis EV → S-Log3 → tetrahedral LUT → Rec.709 Y IRE is the correct measurement path for display looks | **Agreed** |
| Four LUTs need four MAP tables; shared percentage scale is wrong | **Agreed** |
| Green around −1 EV and salmon for face exposure EV span match the exposure-assist intent | **Agreed** |
| Yellow / orange / red highlight policy (warn / high / white clipping only) | **Agreed** |
| Speculation that `Swiniec_LUT_red` encodes a **RED camera** input space | **REJECTED** — user-confirmed input remains **Sony S-Log3 / S-Gamut3.Cine**; `_red` is a look variant |
| Post-LUT MAP as a standalone sensor / stop meter | **REJECTED as a use case** |

**Verdict:** The post-LUT SmallHD MAP is a **look exposure assist** for the applied Swiniec viewing LUT. It must sit beside a separate **SENSOR SAFETY** page on the pre-Look signal. It is not a substitute for a sensor clipping meter.

---

## On-set checklist (LOOK EXPOSURE, after Look)

1. Load the MAP for the **exact** LUT on the Look feed (0 vs −1 vs 1 vs red change mid IRE by several points).
2. Target face key into **FACE EXPOSURE** (salmon); −1 EV underrate into **green**.
3. Treat yellow as WARN and orange as HIGH; **red = WHITE CLIPPING** only.
4. Keep SENSOR SAFETY active on the clean / pre-Look page before trusting Look colours.
5. Prefer numbers in `analysis.json` / `false_color_preset.json` over hand-copied ranges when programming monitors.

---

## Regeneration

```bash
export SWINIEC_LUT_DIR="/path/to/LUTy_planowe"
# From repo root — re-run analyze_exposure_assist for each cube and rewrite
# docs/swiniec_false_color/{analysis.json,false_color_preset.json}
# then refresh the MAP tables in this markdown from those files.
```
