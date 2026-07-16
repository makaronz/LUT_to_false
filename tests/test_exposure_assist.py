import hashlib
import importlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from lut_analyzer_package.lut_interpolation import interpolate_tetrahedral_3d_lut
from lut_analyzer_package.lut_parsing import load_cube_file


EXPECTED_LUTS = {
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
EXPECTED_DOMAIN_MIN = [0.0, 0.0, 0.0]
EXPECTED_DOMAIN_MAX = [1.0, 1.0, 1.0]
EXPECTED_LUT_SIZE = 33
FORBIDDEN_AUXILIARY_COLORS = {"#000000", "#FFFFFF"}


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as lut_file:
        for chunk in iter(lambda: lut_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@pytest.fixture(scope="session")
def real_lut_paths():
    directory_value = os.environ.get("SWINIEC_LUT_DIR")
    if not directory_value:
        pytest.skip("SWINIEC_LUT_DIR must point to the four approved production LUT files")

    directory = Path(directory_value).expanduser().resolve()
    assert directory.is_dir(), f"SWINIEC_LUT_DIR is not a directory: {directory}"

    paths = {path.name: path for path in directory.glob("*.cube")}
    assert set(paths) == set(EXPECTED_LUTS), (
        "SWINIEC_LUT_DIR must contain exactly the four approved production LUT files"
    )
    for name, path in paths.items():
        assert _sha256(path) == EXPECTED_LUTS[name]["sha256"], (
            f"SHA-256 mismatch for production LUT: {name}"
        )
    return paths


@pytest.fixture(params=sorted(EXPECTED_LUTS))
def real_lut(request, real_lut_paths):
    path = real_lut_paths[request.param]
    return {
        "name": request.param,
        "path": path,
        "parsed": load_cube_file(str(path)),
    }


def _analyze(path):
    module = importlib.import_module("lut_analyzer_package.exposure_assist")
    return module.analyze_exposure_assist({"lut_path": str(path)})


def _anchor_by_ev(result):
    return {point["ev"]: point for point in result["anchor_points"]}


def _zone_by_semantic(result):
    return {zone["semantic"]: zone for zone in result["smallhd_zones"]}


def test_real_lut_files_have_approved_structure_and_domain(real_lut):
    parsed = real_lut["parsed"]

    assert parsed["lut_type"] == "3D"
    assert parsed["lut_3d_size"] == EXPECTED_LUT_SIZE
    assert parsed["lut_3d"].shape == (EXPECTED_LUT_SIZE**3, 3)
    assert parsed["domain_min"] == EXPECTED_DOMAIN_MIN
    assert parsed["domain_max"] == EXPECTED_DOMAIN_MAX


def test_tetrahedral_interpolation_reproduces_real_neutral_grid_points(real_lut):
    parsed = real_lut["parsed"]
    grid_indices = np.array([0, 8, 16, 24, 32])
    neutral_inputs = np.repeat(
        (grid_indices / (EXPECTED_LUT_SIZE - 1))[:, None],
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
    flat_neutral_indices = grid_indices * (
        EXPECTED_LUT_SIZE**2 + EXPECTED_LUT_SIZE + 1
    )

    assert np.allclose(output, parsed["lut_3d"][flat_neutral_indices], atol=1e-6)


def test_engine_returns_serializable_per_lut_measurement_contract(real_lut):
    result = _analyze(real_lut["path"])

    assert json.loads(json.dumps(result)) == result
    assert result["source"]["file_name"] == real_lut["name"]
    assert result["source"]["sha256"] == EXPECTED_LUTS[real_lut["name"]]["sha256"]
    assert result["source"]["lut_size"] == EXPECTED_LUT_SIZE
    assert result["source"]["domain_min"] == EXPECTED_DOMAIN_MIN
    assert result["source"]["domain_max"] == EXPECTED_DOMAIN_MAX
    assert set(result) == {
        "source",
        "anchor_points",
        "neutral_axis",
        "grid_statistics",
        "smallhd_zones",
        "clipping",
        "limitations",
        "confidence",
    }


def test_engine_matches_measured_anchor_points(real_lut):
    result = _analyze(real_lut["path"])
    anchors = _anchor_by_ev(result)

    for ev, expected_ire in EXPECTED_LUTS[real_lut["name"]]["anchors"].items():
        assert anchors[ev]["rec709_y_ire"] == pytest.approx(
            expected_ire,
            abs=ANCHOR_TOLERANCE_IRE,
        )
        assert len(anchors[ev]["lut_rgb"]) == 3
        assert anchors[ev]["scene_linear"] == pytest.approx(0.18 * (2.0**ev))


def test_real_neutral_axis_is_monotonic_and_reports_grid_rates(real_lut):
    result = _analyze(real_lut["path"])
    neutral_axis = result["neutral_axis"]
    grid_statistics = result["grid_statistics"]

    assert neutral_axis["monotonic"] is True
    assert neutral_axis["violation_count"] == 0
    assert neutral_axis["minimum_step_ire"] >= 0.0
    assert len(neutral_axis["samples"]) > 4
    assert 0.0 <= grid_statistics["zero_rate"] <= 1.0
    assert 0.0 <= grid_statistics["saturation_rate"] <= 1.0
    assert grid_statistics["entry_count"] == EXPECTED_LUT_SIZE**3
    assert grid_statistics["luma_ire"]["maximum"] == pytest.approx(
        result["clipping"]["signal_ceiling_ire"]
    )


def test_smallhd_zone_boundaries_and_colors_follow_plan_semantics(real_lut):
    result = _analyze(real_lut["path"])
    zones = _zone_by_semantic(result)
    anchors = _anchor_by_ev(result)

    assert zones["minus_one_ev"]["color"] == "#22C55E"
    assert zones["minus_one_ev"]["minimum_ire"] == pytest.approx(
        anchors[-1.25]["rec709_y_ire"]
    )
    assert zones["minus_one_ev"]["maximum_ire"] == pytest.approx(
        anchors[-0.75]["rec709_y_ire"]
    )
    assert zones["face_exposure"]["color"] == "#FA8072"
    assert zones["face_exposure"]["minimum_ire"] == pytest.approx(
        anchors[0.5]["rec709_y_ire"]
    )
    assert zones["face_exposure"]["maximum_ire"] == pytest.approx(
        anchors[1.0]["rec709_y_ire"]
    )
    assert zones["highlight_warn"]["color"] == "#FACC15"
    assert zones["highlight_warn"]["minimum_ire"] == pytest.approx(
        anchors[2.0]["rec709_y_ire"]
    )
    assert zones["highlight_high"]["color"] == "#F97316"
    assert zones["highlight_high"]["minimum_ire"] == pytest.approx(
        anchors[3.0]["rec709_y_ire"]
    )

    red_zones = [zone for zone in result["smallhd_zones"] if zone["color"] == "#DC2626"]
    assert len(red_zones) == 1
    assert red_zones[0]["semantic"] == "white_clipping"
    assert red_zones[0]["minimum_ire"] == result["clipping"]["threshold_ire"]
    assert all(
        zone["color"].upper() not in FORBIDDEN_AUXILIARY_COLORS
        for zone in result["smallhd_zones"]
    )
