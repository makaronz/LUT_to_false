# Change Log 2025

## 📌 Task List
- [x] ✅ Done: Integracja tabeli porównawczej na froncie (HTML, JS, CSS)
- [x] ✅ Done: Implementacja podstawowego trybu ciemnego (Dark Mode)
- [x] ✅ Done: Exposure Assist engine (`lut_analyzer_package/exposure_assist.py`) for four real Swiniec planowe LUTs
- [x] ✅ Done: Exposure Assist tests (`tests/test_exposure_assist.py`) — real cubes via `SWINIEC_LUT_DIR`, SHA-256 gates
- [x] ✅ Done: Regenerate English `docs/swiniec_false_color/` from engine (FALSE_COLOR_SCALE.md, analysis.json, false_color_preset.json); SENSOR SAFETY vs LOOK EXPOSURE; second-model audit
- [x] ✅ Done: Exposure Assist visuals / PDF / ZIP exports (`reporting.py`)
- [x] ✅ Done: Flask batch `exposure_assist` mode on port 8080 (`lutcomparetool_app.py` + templates/CSS)
- [x] ✅ Done: Universal Exposure Assist — encoding catalog, any LUT, import-time colorspace/gamut, debrand Swiniec product naming
- [ ] End-to-end verify app exports + regression on existing flows
- [ ] Rozbudowa dostępności (WCAG) dla kluczowych komponentów
- [ ] Prototypowanie jednej z koncepcji: LUT Morphing Gallery, Color Memory Palace lub Temporal LUT Analyzer

---

## 🔍 Analysis
Swiniec viewing LUTs are display looks (Rec.709-like output). False-color MAP values must be Rec.709 Y IRE **after** the LUT, computed on the neutral S-Log3 axis, with **independent** SmallHD tables per cube. A separate pre-Look SENSOR SAFETY page is required; post-LUT red is look clipping assist, not a sensor stop meter. Earlier Polish draft docs used rounded / single-LUT shared bands and must be replaced by engine output.

## 🛠️ Functions / Components
- `lut_analyzer_package/exposure_assist.py` — `analyze_exposure_assist({lut_path})` contract (anchors, zones, clipping, confidence, limitations).
- `docs/swiniec_false_color/FALSE_COLOR_SCALE.md` — operator documentation (English).
- `docs/swiniec_false_color/analysis.json` — full per-LUT contracts (samples summarized).
- `docs/swiniec_false_color/false_color_preset.json` — four MAP tables + measurement page semantics.
- LUT binaries remain external (`SWINIEC_LUT_DIR`); not committed.

## 🚀 Action Plan
1. Engine + tests (done).
2. Docs from engine + memory-bank sync (this entry).
3. Finish reporting visuals and Flask integration (owned by parallel workstreams).
4. Verify E2E on 8080; do not commit until user requests.

## ⚠️ Problems & Risks
- LUT_0 / LUT_1 / LUT_red grid luma ceilings sit below 99 IRE — custom MAP red bands differ from a naive 99–100 clip.
- Confusion risk if MONITOR false color is left on the Look feed while operators expect sensor protection.
- Parallel agents own `lutcomparetool_app.py` / `reporting.py` — docs must not invent export UI behaviour ahead of those merges.

## 💡 Recommendations
- Program SmallHD MAP values from `false_color_preset.json`, not from chat transcripts.
- Keep regenerating docs whenever SHA-256 of any planowe cube changes.
- Reject any treatment of `Swiniec_LUT_red` as RED-camera IRE tables; input stays S-Log3/S-Gamut3.Cine.
