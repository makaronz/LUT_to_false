"""Pure measurements for post-LUT exposure assistance."""

import hashlib
from pathlib import Path

import numpy as np

from curves import linear_to_slog3
from lut_analyzer_package.lut_interpolation import (
    interpolate_tetrahedral_3d_lut,
)
from lut_analyzer_package.lut_parsing import load_cube_file


MIDDLE_GRAY_LINEAR = 0.18
REC709_LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float64)
ANCHOR_EVS = (-1.25, -1.0, -0.75, 0.0, 0.5, 1.0, 2.0, 3.0)
NEUTRAL_AXIS_MIN_EV = -8.0
NEUTRAL_AXIS_MAX_EV = 8.0
NEUTRAL_AXIS_STEP_EV = 0.25
EXPECTED_LUT_SIZE = 33
EXPECTED_DOMAIN_MIN = [0.0, 0.0, 0.0]
EXPECTED_DOMAIN_MAX = [1.0, 1.0, 1.0]
LEGAL_WHITE_IRE = 100.0
STANDARD_CLIPPING_IRE = 99.0
ZERO_THRESHOLD = 0.0
SATURATION_THRESHOLD = 1.0
SERIALIZATION_PRECISION = 8

ZONE_DEFINITIONS = (
    ("deep_shadow", "DEEP SHADOW", "#312E81"),
    ("minus_one_ev", "-1 EV TARGET", "#22C55E"),
    ("mid_range", "MID RANGE", "#0891B2"),
    ("face_exposure", "FACE EXPOSURE", "#FA8072"),
    ("bright_safe", "BRIGHT SAFE", "#D4A017"),
    ("highlight_warn", "WARN", "#FACC15"),
    ("highlight_high", "HIGH", "#F97316"),
    ("white_clipping", "WHITE CLIPPING", "#DC2626"),
)

LIMITATIONS = (
    "Measurements describe display-referred Rec.709 luma after the LUT and do not replace a pre-LUT sensor clipping check.",
    "EV mapping follows the neutral RGB axis and does not identify skin or any other chromatic subject.",
    "LUT outputs are treated as display RGB and are not decoded through another display transfer function.",
    "Inputs outside the declared LUT domain are clipped by the existing tetrahedral interpolator.",
)


def analyze_exposure_assist(request):
    """Analyze one 3D LUT and return a JSON-serializable measurement contract."""
    lut_path = _validated_lut_path(request)
    parsed = load_cube_file(str(lut_path))
    _validate_3d_lut(parsed)

    anchors = _measure_ev_points(
        {
            "parsed": parsed,
            "ev_values": np.asarray(ANCHOR_EVS, dtype=np.float64),
        }
    )
    neutral_axis = _measure_neutral_axis({"parsed": parsed})
    grid_statistics = _measure_grid({"lut_data": parsed["lut_3d"]})
    signal_ceiling_ire = grid_statistics["luma_ire"]["maximum"]
    clipping_threshold_ire = _round_number(
        min(STANDARD_CLIPPING_IRE, signal_ceiling_ire)
    )

    return {
        "source": {
            "file_name": lut_path.name,
            "sha256": _sha256({"path": lut_path}),
            "lut_size": parsed["lut_3d_size"],
            "domain_min": [float(value) for value in parsed["domain_min"]],
            "domain_max": [float(value) for value in parsed["domain_max"]],
        },
        "anchor_points": anchors,
        "neutral_axis": neutral_axis,
        "grid_statistics": grid_statistics,
        "smallhd_zones": _build_smallhd_zones(
            {
                "anchors": anchors,
                "clipping_threshold_ire": clipping_threshold_ire,
            }
        ),
        "clipping": {
            "signal_ceiling_ire": signal_ceiling_ire,
            "threshold_ire": clipping_threshold_ire,
            "standard_threshold_ire": STANDARD_CLIPPING_IRE,
            "uses_measured_ceiling": signal_ceiling_ire < STANDARD_CLIPPING_IRE,
        },
        "limitations": list(LIMITATIONS),
        "confidence": _measure_confidence(
            {
                "parsed": parsed,
                "neutral_axis": neutral_axis,
            }
        ),
    }


def _validated_lut_path(request):
    if not isinstance(request, dict):
        raise TypeError("Exposure Assist request must be an object")

    lut_path_value = request.get("lut_path")
    if not isinstance(lut_path_value, str) or not lut_path_value.strip():
        raise ValueError("lut_path must be a non-empty string")

    lut_path = Path(lut_path_value).expanduser().resolve()
    if not lut_path.is_file():
        raise FileNotFoundError(f"LUT file not found: {lut_path}")
    return lut_path


def _validate_3d_lut(parsed):
    if parsed["lut_type"] != "3D" or parsed["lut_3d_size"] is None:
        raise ValueError("Exposure Assist requires a standalone 3D LUT")

    expected_entries = parsed["lut_3d_size"] ** 3
    if parsed["lut_3d"].shape != (expected_entries, 3):
        raise ValueError("3D LUT data does not match its declared size")

    domain_min = np.asarray(parsed["domain_min"], dtype=np.float64)
    domain_max = np.asarray(parsed["domain_max"], dtype=np.float64)
    if np.any(domain_max <= domain_min):
        raise ValueError("Every LUT domain maximum must exceed its minimum")


def _measure_ev_points(request):
    parsed = request["parsed"]
    ev_values = np.asarray(request["ev_values"], dtype=np.float64)
    scene_linear = MIDDLE_GRAY_LINEAR * np.power(2.0, ev_values)
    slog3_values = np.asarray(linear_to_slog3(scene_linear), dtype=np.float64)
    neutral_inputs = np.repeat(slog3_values[:, None], 3, axis=1)
    lut_rgb = interpolate_tetrahedral_3d_lut(
        parsed["lut_3d"],
        parsed["lut_3d_size"],
        neutral_inputs,
        parsed["domain_min"],
        parsed["domain_max"],
    ).astype(np.float64)
    luma_ire = lut_rgb @ REC709_LUMA_WEIGHTS * LEGAL_WHITE_IRE

    return [
        {
            "ev": float(ev),
            "scene_linear": _round_number(linear),
            "slog3_input": _round_number(slog3),
            "lut_rgb": [_round_number(channel) for channel in rgb],
            "rec709_y_ire": _round_number(ire),
        }
        for ev, linear, slog3, rgb, ire in zip(
            ev_values,
            scene_linear,
            slog3_values,
            lut_rgb,
            luma_ire,
        )
    ]


def _measure_neutral_axis(request):
    ev_values = np.arange(
        NEUTRAL_AXIS_MIN_EV,
        NEUTRAL_AXIS_MAX_EV + NEUTRAL_AXIS_STEP_EV / 2.0,
        NEUTRAL_AXIS_STEP_EV,
        dtype=np.float64,
    )
    samples = _measure_ev_points(
        {
            "parsed": request["parsed"],
            "ev_values": ev_values,
        }
    )
    luma_values = np.asarray(
        [sample["rec709_y_ire"] for sample in samples],
        dtype=np.float64,
    )
    differences = np.diff(luma_values)
    violation_count = int(np.count_nonzero(differences < 0.0))

    return {
        "monotonic": violation_count == 0,
        "violation_count": violation_count,
        "minimum_step_ire": _round_number(float(np.min(differences))),
        "samples": samples,
    }


def _measure_grid(request):
    lut_data = np.asarray(request["lut_data"], dtype=np.float64)
    luma_ire = lut_data @ REC709_LUMA_WEIGHTS * LEGAL_WHITE_IRE

    return {
        "entry_count": int(lut_data.shape[0]),
        "channel_minimum": [
            _round_number(value) for value in np.min(lut_data, axis=0)
        ],
        "channel_maximum": [
            _round_number(value) for value in np.max(lut_data, axis=0)
        ],
        "luma_ire": {
            "minimum": _round_number(float(np.min(luma_ire))),
            "maximum": _round_number(float(np.max(luma_ire))),
            "mean": _round_number(float(np.mean(luma_ire))),
            "standard_deviation": _round_number(float(np.std(luma_ire))),
        },
        "zero_rate": _round_number(float(np.mean(lut_data <= ZERO_THRESHOLD))),
        "saturation_rate": _round_number(
            float(np.mean(lut_data >= SATURATION_THRESHOLD))
        ),
    }


def _build_smallhd_zones(request):
    anchors = {
        anchor["ev"]: anchor["rec709_y_ire"] for anchor in request["anchors"]
    }
    boundaries = (
        0.0,
        anchors[-1.25],
        anchors[-0.75],
        anchors[0.5],
        anchors[1.0],
        anchors[2.0],
        anchors[3.0],
        request["clipping_threshold_ire"],
        LEGAL_WHITE_IRE,
    )

    return [
        {
            "semantic": semantic,
            "label": label,
            "minimum_ire": _round_number(minimum),
            "maximum_ire": _round_number(maximum),
            "color": color,
        }
        for (semantic, label, color), minimum, maximum in zip(
            ZONE_DEFINITIONS,
            boundaries[:-1],
            boundaries[1:],
        )
    ]


def _measure_confidence(request):
    parsed = request["parsed"]
    checks = {
        "lut_size_33": parsed["lut_3d_size"] == EXPECTED_LUT_SIZE,
        "domain_zero_to_one": (
            parsed["domain_min"] == EXPECTED_DOMAIN_MIN
            and parsed["domain_max"] == EXPECTED_DOMAIN_MAX
        ),
        "neutral_axis_monotonic": request["neutral_axis"]["monotonic"],
    }
    passed_checks = sum(checks.values())
    score = passed_checks / len(checks)

    return {
        "level": "high" if score == 1.0 else "limited",
        "score": _round_number(score),
        "checks": checks,
    }


def _sha256(request):
    digest = hashlib.sha256()
    with request["path"].open("rb") as lut_file:
        for chunk in iter(lambda: lut_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round_number(value):
    return round(float(value), SERIALIZATION_PRECISION)
