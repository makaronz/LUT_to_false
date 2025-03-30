# -*- coding: utf-8 -*-
"""
Moduł odpowiedzialny za interpolację wartości przy użyciu LUT 1D i 3D.
"""

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from typing import List

def interpolate_1d_lut(lut_1d: np.ndarray, input_values: np.ndarray, domain_min: float = 0.0, domain_max: float = 1.0) -> np.ndarray:
    """
    Interpolates values using a 1D LUT.

    Args:
        lut_1d (np.ndarray): The 1D LUT data (Nx3 RGB).
        input_values (np.ndarray): Input values to interpolate (grayscale, 1D array).
        domain_min (float): Minimum value of the LUT's input domain.
        domain_max (float): Maximum value of the LUT's input domain.

    Returns:
        np.ndarray: Interpolated RGB values (Mx3, where M is len(input_values)).
    """
    if not isinstance(lut_1d, np.ndarray) or lut_1d.ndim != 2 or lut_1d.shape[1] != 3:
        raise ValueError("lut_1d must be an Nx3 NumPy array.")
    if not isinstance(input_values, np.ndarray) or input_values.ndim != 1:
         raise ValueError("input_values must be a 1D NumPy array.")

    lut_size = len(lut_1d)
    if lut_size < 2:
        raise ValueError("1D LUT must have at least 2 entries.")

    # Create the input points corresponding to the LUT entries
    lut_input_points = np.linspace(domain_min, domain_max, lut_size)

    output_values = np.empty((len(input_values), 3), dtype=np.float32)
    for i in range(3):  # Interpolate each color channel separately
        # Use np.clip to handle inputs outside the domain before interpolation
        clipped_input = np.clip(input_values, lut_input_points[0], lut_input_points[-1])
        output_values[:, i] = np.interp(clipped_input, lut_input_points, lut_1d[:, i])

    return output_values

def interpolate_3d_lut(lut_3d_data: np.ndarray, lut_size: int, input_rgb: np.ndarray, domain_min: List[float] = [0.0, 0.0, 0.0], domain_max: List[float] = [1.0, 1.0, 1.0]) -> np.ndarray:
    """
    Interpolates values using a 3D LUT using linear interpolation.

    Args:
        lut_3d_data (np.ndarray): Flattened 3D LUT data (N*N*N x 3).
        lut_size (int): Size of the 3D LUT (N).
        input_rgb (np.ndarray): Input RGB values (Mx3 array).
        domain_min (list): Min input domain values [R, G, B].
        domain_max (list): Max input domain values [R, G, B].

    Returns:
        np.ndarray: Interpolated RGB values (Mx3 array).
    """
    if not isinstance(lut_3d_data, np.ndarray) or lut_3d_data.ndim != 2 or lut_3d_data.shape[1] != 3:
        raise ValueError("lut_3d_data must be an (N*N*N)x3 NumPy array.")
    if not isinstance(input_rgb, np.ndarray):
         input_rgb = np.array(input_rgb) # Try converting list of lists etc.
    if input_rgb.ndim == 1 and input_rgb.shape[0] == 3: # Handle single RGB triplet
         input_rgb = input_rgb.reshape(1, 3)
    elif input_rgb.ndim != 2 or input_rgb.shape[1] != 3:
         raise ValueError("input_rgb must be an Mx3 NumPy array or convertible.")

    if not isinstance(lut_size, int) or lut_size < 2:
        raise ValueError("LUT size must be an integer >= 2.")
    if len(lut_3d_data) != lut_size**3:
        raise ValueError(f"Inconsistent lut_3d_data size. Expected {lut_size**3} entries, got {len(lut_3d_data)}.")
    if len(domain_min) != 3 or len(domain_max) != 3:
        raise ValueError("domain_min and domain_max must be lists of 3 floats.")


    # Reshape LUT data into a 3D grid format (N x N x N x 3)
    try:
        # Assume standard order: Blue varies fastest, then Green, then Red.
        lut_grid = lut_3d_data.reshape((lut_size, lut_size, lut_size, 3))
    except ValueError:
         raise ValueError("Could not reshape lut_3d_data to (N, N, N, 3). Check data order and size.")


    # Create the grid points for each axis based on domain
    # Note: Order matters for RegularGridInterpolator: points correspond to dimensions 0, 1, 2
    # If lut_grid is (R, G, B, channels), points should be (R_points, G_points, B_points)
    grid_points = [np.linspace(domain_min[i], domain_max[i], lut_size) for i in range(3)]

    # Clip input values to the LUT's domain before interpolation
    clipped_input_rgb = np.clip(input_rgb, domain_min, domain_max)


    # Create the interpolator function
    # bounds_error=False and fill_value=None extrapolates using edge values,
    # but clipping input is generally safer.
    try:
        interpolator = RegularGridInterpolator(tuple(grid_points), lut_grid,
                                               method='linear', bounds_error=False, fill_value=None)
    except ValueError as e:
        raise ValueError(f"Failed to create interpolator. Check grid points and LUT grid shape. Error: {e}")

    # Interpolate the clipped input values
    try:
        output_rgb = interpolator(clipped_input_rgb)
    except ValueError as e:
         raise ValueError(f"Interpolation failed. Check input data shape and values. Error: {e}")

    return output_rgb
