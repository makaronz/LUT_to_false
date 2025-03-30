import numpy as np
import pytest
from lut_analysis import (
    load_cube_file,
    slog3_curve,
    inverse_slog3_curve,
    rec709_oetf,
    rec709_curve,
    interpolate_1d_lut,
    interpolate_3d_lut,
    arri_logc4_encode,
    arri_logc4_decode,
    arri_logc4_to_xyz,
    arri_logc4_to_aces,
    slog3_encode,
    slog3_decode,
    log3g10_encode,
    log3g10_decode,
    s_gamut3_to_rec709,
    s_gamut3_cine_to_rec709,
    generate_table
)

# Mock LUT data for testing
LUT_1D_SIZE = 17
LUT_1D_DATA = np.linspace(0, 1, LUT_1D_SIZE * 3, dtype=np.float32).reshape(LUT_1D_SIZE, 3)

LUT_3D_SIZE = 5
LUT_3D_DATA = np.linspace(0, 1, LUT_3D_SIZE**3 * 3, dtype=np.float32).reshape(LUT_3D_SIZE**3, 3)


@pytest.fixture
def mock_1d_lut(tmp_path):
    lut_file = tmp_path / "test_1d.cube"
    with open(lut_file, "w") as f:
        f.write("TITLE \"Test 1D LUT\"\n")
        f.write(f"LUT_1D_SIZE {LUT_1D_SIZE}\n")
        for i in range(LUT_1D_SIZE):
            f.write(f"{LUT_1D_DATA[i, 0]:.6f} {LUT_1D_DATA[i, 1]:.6f} {LUT_1D_DATA[i, 2]:.6f}\n")
    return str(lut_file)

@pytest.fixture
def mock_3d_lut(tmp_path):
    lut_file = tmp_path / "test_3d.cube"
    with open(lut_file, "w") as f:
        f.write("TITLE \"Test 3D LUT\"\n")
        f.write(f"LUT_3D_SIZE {LUT_3D_SIZE}\n")
        for i in range(LUT_3D_SIZE**3):
            f.write(f"{LUT_3D_DATA[i, 0]:.6f} {LUT_3D_DATA[i, 1]:.6f} {LUT_3D_DATA[i, 2]:.6f}\n")
    return str(lut_file)

def test_load_cube_file_1d(mock_1d_lut):
    lut_data = load_cube_file(mock_1d_lut)
    assert lut_data['lut_type'] == '1D'
    assert lut_data['lut_1d_size'] == LUT_1D_SIZE
    assert np.allclose(lut_data['lut_1d'], LUT_1D_DATA, atol=1e-6)

def test_load_cube_file_3d(mock_3d_lut):
    lut_data = load_cube_file(mock_3d_lut)
    assert lut_data['lut_type'] == '3D'
    assert lut_data['lut_3d_size'] == LUT_3D_SIZE
    assert np.allclose(lut_data['lut_3d'], LUT_3D_DATA, atol=1e-6)

def test_load_cube_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_cube_file("nonexistent_file.cube")

def test_load_cube_file_invalid_format(tmp_path):
    invalid_file = tmp_path / "invalid.cube"
    with open(invalid_file, "w") as f:
        f.write("INVALID_KEYWORD 123\n")
    with pytest.raises(ValueError):
        load_cube_file(str(invalid_file))

def test_slog3_curve():
    assert np.isclose(slog3_curve(0.18), 0.4109, atol=1e-4)

def test_inverse_slog3_curve():
    assert np.isclose(inverse_slog3_curve(0.4109), 0.18, atol=1e-2)

def test_rec709_oetf():
    assert np.isclose(rec709_oetf(0.18), 0.409, atol=1e-3)

def test_rec709_curve():
    assert np.isclose(rec709_curve(0.409), 0.18, atol=1e-2)

def test_interpolate_1d_lut(mock_1d_lut):
    lut_data = load_cube_file(mock_1d_lut)
    input_values = np.array([0.0, 0.5, 1.0], dtype=np.float32)
    interpolated_values = interpolate_1d_lut(lut_data['lut_1d'], input_values)
    expected_values = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]], dtype=np.float32)
    assert np.allclose(interpolated_values, expected_values)

def test_interpolate_3d_lut(mock_3d_lut):
    lut_data = load_cube_file(mock_3d_lut)
    input_values = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]], dtype=np.float32)
    interpolated_values = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_values)
    
    assert interpolated_values.shape == (3, 3)


def test_arri_logc4_encode():
    assert np.isclose(arri_logc4_encode(0.18), 0.391, atol=1e-3)

def test_arri_logc4_decode():
    assert np.isclose(arri_logc4_decode(0.391), 0.18, atol=1e-2)

def test_arri_logc4_to_xyz():
    # Example values taken from ARRI LogC4 documentation
    logc4_values = np.array([0.391, 0.411, 0.352])
    xyz = arri_logc4_to_xyz(logc4_values)
    assert xyz.shape == (3,)

def test_arri_logc4_to_aces():
    logc4_values = np.array([0.391, 0.411, 0.352])
    aces = arri_logc4_to_aces(logc4_values)
    assert aces.shape == (3,)

def test_slog3_encode():
    assert np.isclose(slog3_encode(0.18), 0.4109, atol=1e-4)

def test_slog3_decode():
    assert np.isclose(slog3_decode(0.4109), 0.18, atol=1e-2)

def test_log3g10_encode():
    assert np.isclose(log3g10_encode(0.18), 0.461, atol=1e-3)

def test_log3g10_decode():
    assert np.isclose(log3g10_decode(0.461), 0.18, atol=1e-2)

def test_s_gamut3_to_rec709():
    rgb_values = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    rec709_values = s_gamut3_to_rec709(rgb_values)
    assert rec709_values.shape == (2, 3)

def test_s_gamut3_cine_to_rec709():
    rgb_values = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    rec709_values = s_gamut3_cine_to_rec709(rgb_values)
    assert rec709_values.shape == (2, 3)

def test_generate_table(mock_3d_lut):
    table = generate_table(mock_3d_lut, 's-gamut3')
    assert table.shape == (19, 4)
    assert np.all(table[:, 0] == np.arange(1, 100, 5))
