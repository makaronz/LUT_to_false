# -*- coding: utf-8 -*-
"""
Moduł zawierający funkcje do transformacji przestrzeni kolorów.
"""

import numpy as np

# =========================================
# Transformacje Przestrzeni Kolorów
# =========================================

def s_gamut3_to_rec709(rgb_sgamut3: np.ndarray) -> np.ndarray:
    """Converts S-Gamut3 primaries to Rec.709 primaries (assuming D65 whitepoint)."""
    # Matrix from Colour Science library (using Bradford chromatic adaptation)
    matrix = np.array([
        [ 1.71665118835796, -0.66662369310349, -0.05002749525447],
        [-0.35567078377639,  1.61648123663494, -0.26081045285855],
        [-0.25336628137361, -0.50001106818996,  1.75337734956357]
    ])
    rgb_in = np.atleast_2d(rgb_sgamut3)
    if rgb_in.shape[1] != 3:
        raise ValueError("Input must be an Nx3 array")
    rgb_rec709 = np.dot(rgb_in, matrix.T)
    return rgb_rec709

def s_gamut3_cine_to_rec709(rgb_sgamut3_cine: np.ndarray) -> np.ndarray:
    """Converts S-Gamut3.Cine primaries to Rec.709 primaries (assuming D65 whitepoint)."""
    # Matrix from Colour Science library (using Bradford chromatic adaptation)
    matrix = np.array([
        [ 1.34594333, -0.2556075 , -0.09033583],
        [-0.5445988 ,  1.5081673 ,  0.0364315 ],
        [ 0.        ,  0.        ,  1.        ] # Simplified Z axis
    ])
    rgb_in = np.atleast_2d(rgb_sgamut3_cine)
    if rgb_in.shape[1] != 3:
        raise ValueError("Input must be an Nx3 array")
    rgb_rec709 = np.dot(rgb_in, matrix.T)
    return rgb_rec709

# TODO: Add other transformations if needed (e.g., Rec709 to XYZ, ACES to XYZ)
# Consider using the 'colour-science' library for comprehensive transformations.
