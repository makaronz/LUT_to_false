"""Exposure Assist tests: encoding-agnostic unit tests + optional real LUT integration."""

import hashlib
import importlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from lut_analyzer_package.encoding_catalog import (
    DEFAULT_ENCODING,
    ENCODING_INFO,
    resolve_encoding,
)
from lut_analyzer_package.exposure_assist import (
    ZONE_DEFINITIONS,
    _build_smallhd_zones,
)
from lut_analyzer_package.lut_interpolation import interpolate_tetrahedral_3d_lut
from lut_analyzer_package.lut_parsing import load_cube_file

FORBIDDEN_AUXILIARY_COLORS = {"#000000", "#FFFFFF"}
OPTIONAL_GOLDEN = {
    "Swiniec_LUT_-1.cube": {
        "sha256": "fcfc1e65dd09df257d0b2f43c1b379c3ac7f85b4d7015825687ba4eb9c1a33c2",
        "anchors": {-1.0: 32.07696, 0.0: 50.61539, 0.5: 59.97575, 1.0: 68.47641},
    },
    "Swiniec_LUT_0.cube": {
        "sha256": "c1f029a1ef5c7bd865c6ce32c349a67d8ca44c9023362f0bbf54fecde6e0929f",
        "anchors": {-1.0: 31.41912, 0.0: 49.24474, 0.5: 58.24788, 1.0: 66.42572},
    },
    "Swiniec_LUT_1.cube": {
        "sha256": "82ad34dfc03989c3f2201d40304a69b6566f567bbfb3a66340eced84301cdcb2",
        "anchors": {-1.0: 36.92338, 0.0: 55.46377, 0.5: 64.25910, 1.0: 71.86978},
    },
    "Swiniec_LUT_red.cube": {
        "sha256": "d5da1bab519c3f498ee863c47f188fe148526d2f3dc361a14e491da174d36e64",
        "anchors": {-1.0: 28.53685, 0.0: 46.05270, 0.5: 55.15759, 1.0: 63.54619},
    },
}
ANCHOR_TOLERANCE_IRE = 0.02


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as lut_file:
        for chunk in iter(lambda: lut_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lut_dir():
    return os.environ.get("EXPOSURE_ASSIST_LUT_DIR") or os.environ.get(
        "SWINIEC_LUT_DIR"
    )


@pytest.fixture(scope="session")
def real_lut_paths():
    directory_value = _lut_dir()
    if not directory_value:
        pytest.skip(
            "EXPOSURE_ASSIST_LUT_DIR (or SWINIEC_LUT_DIR) must point to real .cube files"
        )

    directory = Path(directory_value).expanduser().resolve()
    assert directory.is_dir(), f"LUT dir is not a directory: {directory}"
    paths = sorted(directory.glob("*.cube"))
    assert paths, f"No .cube files in {directory}"
    return paths


def _analyze(path, encoding=DEFAULT_ENCODING):
    module = importlib.import_module("lut_analyzer_package.exposure_assist")
    return module.analyze_exposure_assist(
        {"lut_path": str(path), "encoding": encoding}
    )


def test_resolve_encoding_rejects_unknown_keys():
    with pytest.raises(ValueError):
        resolve_encoding("not_a_real_encoding")


def test_encoding_catalog_covers_major_camera_pairs():
    required = {
        "slog3",
        "slog3_cine",
        "logc3",
        "logc4",
        "log3g10",
        "vlog",
        "canonlog2",
        "rec709",
        "acescct",
    }
    assert required.issubset(set(ENCODING_INFO))


def test_same_ev_yields_different_encoded_input_across_transfers():
    """No cube required — transfer curves must diverge at middle gray."""
    scene_linear = np.asarray([0.18], dtype=np.float64)
    encoded = {
        key: float(ENCODING_INFO[key]["curve_func"](scene_linear)[0])
        for key in ("slog3_cine", "logc3", "log3g10")
    }
    assert encoded["slog3_cine"] != pytest.approx(encoded["logc3"], abs=1e-4)
    assert encoded["slog3_cine"] != pytest.approx(encoded["log3g10"], abs=1e-4)
    assert encoded["logc3"] != pytest.approx(encoded["log3g10"], abs=1e-4)


def test_zone_palette_semantics_without_lut():
    fake_anchors = [
        {"ev": ev, "rec709_y_ire": value}
        for ev, value in (
            (-1.25, 20.0),
            (-0.75, 30.0),
            (0.5, 55.0),
            (1.0, 65.0),
            (2.0, 80.0),
            (3.0, 90.0),
        )
    ]
    zones = _build_smallhd_zones(
        {"anchors": fake_anchors, "clipping_threshold_ire": 99.0}
    )
    by_semantic = {zone["semantic"]: zone for zone in zones}
    assert by_semantic["minus_one_ev"]["color"] == "#22C55E"
    assert by_semantic["face_exposure"]["color"] == "#FA8072"
    assert by_semantic["highlight_warn"]["color"] == "#FACC15"
    assert by_semantic["highlight_high"]["color"] == "#F97316"
    red_zones = [zone for zone in zones if zone["color"] == "#DC2626"]
    assert len(red_zones) == 1
    assert red_zones[0]["semantic"] == "white_clipping"
    assert all(
        zone["color"].upper() not in FORBIDDEN_AUXILIARY_COLORS for zone in zones
    )
    assert [zone[0] for zone in ZONE_DEFINITIONS] == [
        zone["semantic"] for zone in zones
    ]


def test_engine_requires_encoding_and_returns_input_encoding(real_lut_paths):
    path = real_lut_paths[0]
    result = _analyze(path, encoding="logc3")
    assert json.loads(json.dumps(result)) == result
    assert result["input_encoding"]["key"] == "logc3"
    assert "encoded_input" in result["anchor_points"][0]
    assert "slog3_input" not in result["anchor_points"][0]
    assert "lut_size_33" not in result["confidence"]["checks"]
    assert set(result) >= {
        "source",
        "input_encoding",
        "anchor_points",
        "neutral_axis",
        "grid_statistics",
        "smallhd_zones",
        "clipping",
        "limitations",
        "confidence",
    }


def test_different_encodings_change_ire_anchors(real_lut_paths):
    path = real_lut_paths[0]
    slog = _anchor_ire(_analyze(path, encoding="slog3_cine"))
    logc = _anchor_ire(_analyze(path, encoding="logc3"))
    assert slog[0.0] != pytest.approx(logc[0.0], abs=0.05)


def test_real_luts_have_valid_3d_structure(real_lut_paths):
    for path in real_lut_paths:
        parsed = load_cube_file(str(path))
        assert parsed["lut_type"] == "3D"
        size = parsed["lut_3d_size"]
        assert size >= 2
        assert parsed["lut_3d"].shape == (size**3, 3)
        assert all(
            maximum > minimum
            for minimum, maximum in zip(parsed["domain_min"], parsed["domain_max"])
        )


def test_tetrahedral_interpolation_reproduces_neutral_grid_corners(real_lut_paths):
    path = real_lut_paths[0]
    parsed = load_cube_file(str(path))
    size = parsed["lut_3d_size"]
    grid_indices = np.array([0, size - 1], dtype=np.int64)
    neutral_inputs = np.repeat(
        (grid_indices / (size - 1))[:, None],
        3,
        axis=1,
    )
    output = interpolate_tetrahedral_3d_lut(
        parsed["lut_3d"],
        parsed["lut_3d_size"],
        neutral_inputs,
        parsed["domain_min"],
        parsed["domain_max"],
    )
    flat_neutral_indices = grid_indices * (size**2 + size + 1)
    assert np.allclose(output, parsed["lut_3d"][flat_neutral_indices], atol=1e-6)


def test_optional_golden_anchors_when_hashes_match(real_lut_paths):
    by_name = {path.name: path for path in real_lut_paths}
    matched = [
        name for name, meta in OPTIONAL_GOLDEN.items() if name in by_name
        and _sha256(by_name[name]) == meta["sha256"]
    ]
    if not matched:
        pytest.skip("No optional golden LUTs with matching SHA-256 in LUT dir")

    for name in matched:
        result = _analyze(by_name[name], encoding="slog3_cine")
        anchors = {point["ev"]: point["rec709_y_ire"] for point in result["anchor_points"]}
        for ev, expected_ire in OPTIONAL_GOLDEN[name]["anchors"].items():
            assert anchors[ev] == pytest.approx(expected_ire, abs=ANCHOR_TOLERANCE_IRE)


def _anchor_ire(result):
    return {point["ev"]: point["rec709_y_ire"] for point in result["anchor_points"]}
