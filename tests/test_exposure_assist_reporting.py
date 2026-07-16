"""Unit tests for Exposure Assist report helpers (pure logic, no mocks)."""

import csv
import importlib
import json
import os
from pathlib import Path

import pytest

from lut_analyzer_package.exposure_assist import analyze_exposure_assist


EXPECTED_LUT_0 = "Swiniec_LUT_0.cube"
EXPECTED_ARTIFACT_KEYS = {
    "json",
    "csv",
    "pdf",
    "ev_ire_png",
    "ev_ire_svg",
    "rgb_neutral_png",
    "rgb_neutral_svg",
    "clipping_png",
    "clipping_svg",
    "false_color_bar_png",
    "false_color_bar_svg",
    "dashboard_png",
    "dashboard_svg",
    "workflow_png",
    "workflow_svg",
}


@pytest.fixture(scope="module")
def lut_0_path():
    directory_value = os.environ.get("SWINIEC_LUT_DIR")
    if not directory_value:
        pytest.skip("SWINIEC_LUT_DIR must point to approved production LUT files")

    lut_path = Path(directory_value).expanduser().resolve() / EXPECTED_LUT_0
    if not lut_path.is_file():
        pytest.skip(f"Missing production LUT: {lut_path}")
    return lut_path


@pytest.fixture(scope="module")
def analysis(lut_0_path):
    return analyze_exposure_assist({"lut_path": str(lut_0_path)})


def _reporting():
    return importlib.import_module("lut_analyzer_package.reporting")


def test_csv_rows_cover_zones_and_anchors(analysis):
    reporting = _reporting()
    rows = reporting.exposure_assist_csv_rows({"analysis": analysis})

    assert rows[0] == [
        "section",
        "key",
        "ev",
        "minimum_ire",
        "maximum_ire",
        "rec709_y_ire",
        "color",
        "label",
    ]
    sections = {row[0] for row in rows[1:]}
    assert "anchor" in sections
    assert "zone" in sections
    assert "clipping" in sections
    assert any(row[0] == "zone" and row[1] == "white_clipping" for row in rows[1:])


def test_false_color_bar_segments_preserve_zone_order_and_colors(analysis):
    reporting = _reporting()
    segments = reporting.false_color_bar_segments(
        {"zones": analysis["smallhd_zones"]}
    )

    assert len(segments) == len(analysis["smallhd_zones"])
    for segment, zone in zip(segments, analysis["smallhd_zones"]):
        assert segment["semantic"] == zone["semantic"]
        assert segment["color"] == zone["color"]
        assert segment["label"] == zone["label"]
        assert segment["minimum_ire"] == zone["minimum_ire"]
        assert segment["maximum_ire"] == zone["maximum_ire"]


def test_generate_exposure_assist_report_writes_expected_artifacts(
    analysis, tmp_path
):
    reporting = _reporting()
    result = reporting.generate_exposure_assist_report(
        {
            "analysis": analysis,
            "output_dir": str(tmp_path),
            "basename": "Swiniec_LUT_0",
        }
    )

    artifacts = result["artifacts"]
    assert set(artifacts) == EXPECTED_ARTIFACT_KEYS
    for key, path_value in artifacts.items():
        path = Path(path_value)
        assert path.is_file(), f"Missing artifact: {key} -> {path}"
        assert path.stat().st_size > 0

    with Path(artifacts["json"]).open(encoding="utf-8") as handle:
        loaded = json.load(handle)
    assert loaded["source"]["file_name"] == analysis["source"]["file_name"]
    assert len(loaded["smallhd_zones"]) == len(analysis["smallhd_zones"])

    with Path(artifacts["csv"]).open(newline="", encoding="utf-8") as handle:
        reader = list(csv.reader(handle))
    assert reader[0][0] == "section"
    assert len(reader) > 10


def test_generate_smallhd_workflow_diagram_writes_png_and_svg(tmp_path):
    reporting = _reporting()
    result = reporting.generate_smallhd_workflow_diagram(
        {"output_dir": str(tmp_path), "basename": "smallhd_workflow"}
    )

    for key in ("workflow_png", "workflow_svg"):
        path = Path(result["artifacts"][key])
        assert path.is_file()
        assert path.stat().st_size > 0
