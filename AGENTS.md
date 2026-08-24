---
ijfw_version: 1.3.2
ijfw_schema: 1
type: software
primary_type: software
secondary_types: []
confidence: 0.907
detected_at: 2026-07-15T06:05:31.581Z
signals:
  - kind: manifest
    weight: 0.9
    manifests: [package.json, setup.py]
  - kind: file_extension_ratio
    weight: 0.7
    domain: software
    ratio: 1
    count: 35
  - kind: filename_pattern
    weight: 0.2
    domain: content
    name: post-edit.md
  - kind: filename_pattern
    weight: 0.2
    domain: content
    name: post-task.md
---
# AGENTS.md

This file follows the open AGENTS.md spec (https://agents.md/) and is the
canonical agent-instructions surface for this project. Platform-specific
files (CLAUDE.md, GEMINI.md, WAYLAND.md, codex/AGENTS.md, .cursorrules,
.windsurfrules, copilot-instructions.md) are thin adapters that point here.

Five IJFW-managed regions live in this file. Content outside the markers is
yours -- IJFW will never touch it.

| Region | Purpose |
|---|---|
| MEMORY | Project memory recalled from `.ijfw/memory/` |
| ROUTING | Platform skill-routing rules |
| AGENTS | Registered agent roster |
| BLACKBOARD | Multi-CLI orchestration scratchpad (Pillar B) |
| DISCIPLINE | Per-domain discipline rules (code \| narrative \| business \| design \| research) |

<!-- IJFW-MEMORY-START -->
Project memory at .ijfw/memory/. Call `ijfw_memory_prelude` for full context.
<!-- IJFW-MEMORY-END -->

<!-- IJFW-ROUTING-START -->
<!-- IJFW-ROUTING-END -->

<!-- IJFW-AGENTS-START -->
No project agents yet. Run `ijfw team` to set them up.
<!-- IJFW-AGENTS-END -->

<!-- IJFW-BLACKBOARD-START -->
<!-- Reserved for Pillar B multi-CLI orchestration. Empty in alpha. -->
<!-- IJFW-BLACKBOARD-END -->

<!-- IJFW-DISCIPLINE-START -->
<!-- IJFW-DISCIPLINE-END -->

## Learned User Preferences
- Respond in Polish in chat; keep code, comments, commits, and documentation in English
- Prefer real production `.cube` LUT files only; never invent mock, demo, or artificial LUT data for analysis or tests
- Do not copy vendor `.cube` files into the repository; point optional integration tests at external paths via `EXPOSURE_ASSIST_LUT_DIR` (deprecated alias: `SWINIEC_LUT_DIR`)
- For highlight false-color bands: yellow = warn, orange = high, red = white clipping
- When implementing an attached plan, do not edit the plan file; complete existing todos without recreating them

## Learned Workspace Facts
- Canonical Flask app is `lutcomparetool_app.py` on port 8080 (not experimental `pixelpasta/app.py` for Exposure Assist)
- Exposure Assist is encoding-agnostic: user selects a valid transfer+gamut pair at import; docs live in `docs/exposure_assist/`
- False-color and exposure-assist thresholds are display-referred Rec.709 Y% after the viewing LUT, not camera-log percentages
- One independent SmallHD MAP scale per uploaded LUT; SENSOR SAFETY is pre-Look, LOOK EXPOSURE is post-Look
