# Exposure Assist — False Color / SmallHD MAP

Universal per-LUT exposure assist for any 3D `.cube` viewing LUT.

| Field | Value |
|---|---|
| Input encoding | **User-selected** at import (Sony / ARRI / RED / Panasonic / Canon / Rec.709 / ACEScct pairs) |
| Middle gray | 0.18 scene-linear (= 0 EV) |
| Output metric | Display-referred Rec.709 luma **Y as IRE** after the LUT (no second display OETF decode) |
| Scale model | **One independent SmallHD MAP per uploaded LUT** — never a shared percentage scale |
| Engine | `lut_analyzer_package.exposure_assist.analyze_exposure_assist` |
| Encoding catalog | `lut_analyzer_package.encoding_catalog` |

> **Important:** These IRE bands describe the **Look path after the viewing LUT**. They are not camera-log percentages and do not replace a pre-Look sensor safety check.

---

## Import-time encoding selector

Choose a **valid transfer + gamut pair** when uploading (single or batch). Illegal combinations (e.g. LogC4 + S-Gamut3) are not offered.

Neutral-axis EV (R=G=B) depends on the **transfer curve**. Gamut is stored on the analysis contract for reporting; it does not change grayscale Y.

Default selection: Sony S-Log3 / S-Gamut3.Cine.

Optional real-LUT integration tests read cubes from `EXPOSURE_ASSIST_LUT_DIR` (deprecated alias: `SWINIEC_LUT_DIR`). Cubes are never copied into this repository without separate approval.

---

## SmallHD two-page workflow

### Page A — SENSOR SAFETY (measure **before** Look)

| Item | Guidance |
|---|---|
| Signal | Pre-Look path: camera log / sensor overlay or waveform |
| Goal | Protect the captured signal from sensor / log clipping |
| False color | Camera vendor overlay or a log-appropriate profile — **not** the post-LUT Rec.709 MAP |

### Page B — LOOK EXPOSURE (measure **after** Look)

| Item | Guidance |
|---|---|
| Signal | Display path with the chosen viewing LUT applied |
| Goal | Expose for the intended look (underexposure / face band / highlight warnings in Rec.709 Y IRE) |
| False color | Load the **per-LUT** MAP for that exact `.cube` |
| Semantic anchors | Green ≈ −1 EV · salmon = face exposure +0.5…+1 EV (not chromatic skin ID) · yellow = WARN (+2 EV) · orange = HIGH (+3 EV) · red = WHITE CLIPPING only |

---

## Highlight palette

| Role | Color | Rule |
|---|---|---|
| WARN | Yellow `#FACC15` | From +2 EV anchor |
| HIGH | Orange `#F97316` | From +3 EV anchor |
| WHITE CLIPPING | Red `#DC2626` | Only for 99 IRE / measured signal ceiling to 100 IRE |
| Shadows | Indigo / navy | Never pure black `#000000` as an assist band |

---

## Method

1. Scene EV → scene-linear (`0.18 × 2^EV`)
2. Encode with the **selected** camera log curve
3. Sample the 3D LUT on the neutral RGB axis (tetrahedral)
4. Rec.709 luma weights → IRE (×100)
5. Build SmallHD zones from EV anchors (−1.25 / −0.75 / +0.5 / +1 / +2 / +3) and clipping ceiling

Display look RGB is **not** re-decoded as camera log.

---

## Second-model audit (summary)

| Claim | Verdict |
|---|---|
| Post-LUT MAP is a standalone sensor exposure meter | **Rejected** — it is look exposure assist only |
| Encoding can be inferred from LUT filename | **Rejected** — encoding is user-selected at import |
| Shared percentage scale across different looks | **Rejected** — each LUT needs its own MAP |

---

## App entry

- Canonical app: `lutcomparetool_app.py` (`/` and `/batch`, mode **Exposure Assist**)
- Scales UI: `/false-color` (alias `/exposure-assist`) — shows scales from the latest analysis run
- API notes: [`../API.md`](../API.md)

Legacy vendor-specific notes (if present) under `docs/swiniec_false_color/` are historical and are superseded by this document.
