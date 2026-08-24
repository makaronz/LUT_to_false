"""Unit tests for Exposure Assist report helpers (pure logic + optional real LUT)."""

import csv
import importlib
import json
import os
from pathlib import Path

import pytest

from lut_analyzer_package.exposure_assist import analyze_exposure_assist
from lut_analyzer_package.encoding_catalog import DEFAULT_ENCODING


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


def _lut_dir():
    return os.environ.get("EXPOSURE_ASSIST_LUT_DIR") or os.environ.get(
        "SWINIEC_LUT_DIR"
    )


@pytest.fixture(scope="module")
def sample_lut_path():
    directory_value = _lut_dir()
    if not directory_value:
        pytest.skip(
            "EXPOSURE_ASSIST_LUT_DIR (or SWINIEC_LUT_DIR) must point to real .cube files"
        )
    paths = sorted(Path(directory_value).expanduser().resolve().glob("*.cube"))
    if not paths:
        pytest.skip("No .cube files found for reporting tests")
    return paths[0]


@pytest.fixture(scope="module")
def analysis(sample_lut_path):
    return analyze_exposure_assist(
        {"lut_path": str(sample_lut_path), "encoding": DEFAULT_ENCODING}
    )


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
            "basename": Path(analysis["source"]["file_name"]).stem,
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
    assert loaded["input_encoding"]["key"] == analysis["input_encoding"]["key"]
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
