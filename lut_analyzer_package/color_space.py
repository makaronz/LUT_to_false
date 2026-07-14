# -*- coding: utf-8 -*-
"""
Moduł zawierający funkcje do transformacji przestrzeni kolorów.
"""

import numpy as np
from typing import List, Union, Optional

# =========================================
# Precyzyjne transformacje przestrzeni kolorów
# =========================================

# Macierze konwersji gamutu (RGB -> RGB, oba w bieli D65).
#
# Wyprowadzone z oficjalnie publikowanych chromatyczności primaries każdej
# przestrzeni metodą normalized primary matrix (NPM):
#     M_src->709 = NPM(Rec.709, D65)^-1 @ NPM(src, D65)
# Poprawność zweryfikowana względem oficjalnie opublikowanej macierzy
# ARRI AWG3 -> Rec.709 (zgodność do ~1e-6). Każdy wiersz sumuje się do 1,
# co jest wymogiem dla konwersji D65 -> D65.
#
# Primaries (x, y):
#   S-Gamut3        R(0.730, 0.280)   G(0.140, 0.855)   B(0.100, -0.050)
#   S-Gamut3.Cine   R(0.766, 0.275)   G(0.225, 0.800)   B(0.089, -0.087)
#   ARRI AWG3       R(0.6840,0.3130)  G(0.2210,0.8480)  B(0.0861,-0.1020)
#   ARRI AWG4       R(0.7347,0.2653)  G(0.1424,0.8576)  B(0.0991,-0.0308)
#   RED Wide Gamut  R(0.780308,0.304253) G(0.121595,1.493994) B(0.095612,-0.084589)
#   Biała D65       (0.3127, 0.3290)
MATRIX_MAP = {
    # Sony S-Gamut3 -> Rec.709
    "sgamut3_to_rec709": np.array([
        [ 1.87791513, -0.79416876, -0.08374637],
        [-0.17680698,  1.35099962, -0.17419264],
        [-0.02620113, -0.14842226,  1.17462339]
    ], dtype=np.float64),

    # Sony S-Gamut3.Cine -> Rec.709
    "sgamut3_cine_to_rec709": np.array([
        [ 1.62694741, -0.54013854, -0.08680887],
        [-0.17851553,  1.41794093, -0.23942540],
        [-0.04443612, -0.19591997,  1.24035608]
    ], dtype=np.float64),

    # ARRI Wide Gamut 4 -> Rec.709
    "arri_wide_gamut4_to_rec709": np.array([
        [ 1.89312344, -0.78088150, -0.11224194],
        [-0.20570036,  1.34025749, -0.13455713],
        [-0.01270574, -0.15218488,  1.16489062]
    ], dtype=np.float64),

    # ARRI Wide Gamut 3 -> Rec.709
    "arri_wide_gamut3_to_rec709": np.array([
        [ 1.61752344, -0.53728662, -0.08023681],
        [-0.07057274,  1.33461306, -0.26404032],
        [-0.02110173, -0.22695388,  1.24805560]
    ], dtype=np.float64),

    # RED Wide Gamut RGB -> Rec.709
    "red_wide_gamut_rgb_to_rec709": np.array([
        [ 1.98197602, -0.90043184, -0.08154418],
        [-0.17814318,  1.50046836, -0.32232518],
        [-0.10179597, -0.53526346,  1.63705943]
    ], dtype=np.float64),
}

def precise_transform(rgb_values: np.ndarray, source_space: str, target_space: str) -> np.ndarray:
    """
    Precyzyjna transformacja między przestrzeniami kolorów z wykorzystaniem
    oficjalnych macierzy transformacji i podwójnej precyzji obliczeń.
    
    Args:
        rgb_values: Wartości RGB w przestrzeni źródłowej (Nx3)
        source_space: Przestrzeń źródłowa ("sgamut3", "sgamut3_cine", "arri_wide_gamut4", itd.)
        target_space: Przestrzeń docelowa ("rec709", "p3_d65", "rec2020", itd.)
        
    Returns:
        Wartości RGB w przestrzeni docelowej (Nx3)
    """
    # Konwersja do float64 dla maksymalnej precyzji
    rgb_in = np.asarray(rgb_values, dtype=np.float64)
    
    # Sprawdzenie wymiarowości
    if rgb_in.ndim == 1:
        if rgb_in.shape[0] == 3:  # Pojedyncza trójka RGB
            rgb_in = rgb_in.reshape(1, 3)
        else:
            raise ValueError("Dla jednowymiarowych danych wejściowych, długość musi wynosić 3 (RGB)")
    
    if rgb_in.ndim != 2 or rgb_in.shape[1] != 3:
        raise ValueError("Wejściowe dane muszą mieć kształt (N, 3) - N trójek RGB")
    
    # Klucz transformacji
    transform_key = f"{source_space}_to_{target_space}"
    
    # Sprawdzenie, czy istnieje bezpośrednia transformacja
    if transform_key in MATRIX_MAP:
        matrix = MATRIX_MAP[transform_key]
    elif f"{target_space}_to_{source_space}" in MATRIX_MAP:
        # Jeśli istnieje odwrotna transformacja, obliczymy jej odwrotność
        matrix = np.linalg.inv(MATRIX_MAP[f"{target_space}_to_{source_space}"])
    else:
        # Jeśli nie ma bezpośredniej transformacji, zgłaszamy błąd
        raise ValueError(f"Brak zdefiniowanej transformacji między {source_space} a {target_space}")
    
    # Transformacja z maksymalną precyzją
    rgb_out = np.dot(rgb_in, matrix.T)
    
    # Zabezpieczenie przed błędami numerycznymi - małe wartości ujemne
    eps = np.finfo(np.float64).eps * 100
    rgb_out = np.where(np.abs(rgb_out) < eps, 0.0, rgb_out)
    
    # Konwersja z powrotem do float32
    return rgb_out.astype(np.float32)

def s_gamut3_to_rec709(rgb_sgamut3: np.ndarray) -> np.ndarray:
    """
    Converts S-Gamut3 primaries to Rec.709 primaries (assuming D65 whitepoint).
    
    Uses precise matrix transformation with double precision for accuracy.
    
    Args:
        rgb_sgamut3: RGB values in S-Gamut3 color space (Nx3)
        
    Returns:
        RGB values in Rec.709 color space (Nx3)
    """
    return precise_transform(rgb_sgamut3, "sgamut3", "rec709")

def s_gamut3_cine_to_rec709(rgb_sgamut3_cine: np.ndarray) -> np.ndarray:
    """
    Converts S-Gamut3.Cine primaries to Rec.709 primaries (assuming D65 whitepoint).
    
    Uses precise matrix transformation with double precision for accuracy.
    
    Args:
        rgb_sgamut3_cine: RGB values in S-Gamut3.Cine color space (Nx3)
        
    Returns:
        RGB values in Rec.709 color space (Nx3)
    """
    return precise_transform(rgb_sgamut3_cine, "sgamut3_cine", "rec709")

def arri_wide_gamut4_to_rec709(rgb_awg4: np.ndarray) -> np.ndarray:
    """
    Converts ARRI Wide Gamut 4 primaries to Rec.709 primaries.
    
    ARRI Wide Gamut 4 is the color space associated with LogC4.
    
    Args:
        rgb_awg4: RGB values in ARRI Wide Gamut 4 color space (Nx3)
        
    Returns:
        RGB values in Rec.709 color space (Nx3)
    """
    return precise_transform(rgb_awg4, "arri_wide_gamut4", "rec709")

def arri_wide_gamut3_to_rec709(rgb_awg3: np.ndarray) -> np.ndarray:
    """
    Converts ARRI Wide Gamut 3 primaries to Rec.709 primaries.
    
    ARRI Wide Gamut 3 is the color space associated with LogC3.
    
    Args:
        rgb_awg3: RGB values in ARRI Wide Gamut 3 color space (Nx3)
        
    Returns:
        RGB values in Rec.709 color space (Nx3)
    """
    return precise_transform(rgb_awg3, "arri_wide_gamut3", "rec709")

def red_wide_gamut_rgb_to_rec709(rgb_rwg: np.ndarray) -> np.ndarray:
    """
    Converts RED Wide Gamut RGB primaries to Rec.709 primaries.
    
    RED Wide Gamut RGB is the color space associated with RED cameras.
    
    Args:
        rgb_rwg: RGB values in RED Wide Gamut RGB color space (Nx3)
        
    Returns:
        RGB values in Rec.709 color space (Nx3)
    """
    return precise_transform(rgb_rwg, "red_wide_gamut_rgb", "rec709")

def transform_with_curve(rgb_values: np.ndarray, 
                        source_space: str, 
                        source_curve: callable, 
                        target_space: str,
                        target_curve_inverse: callable) -> np.ndarray:
    """
    Pełna transformacja między przestrzeniami kolorów z uwzględnieniem 
    krzywej transferu i macierzy transformacji przestrzeni.
    
    Ta funkcja wykonuje następujące kroki:
    1. Dekoduje wartości z krzywej źródłowej do liniowej przestrzeni
    2. Transformuje z liniowej przestrzeni źródłowej do liniowej przestrzeni docelowej
    3. Enkoduje z liniowej przestrzeni do krzywej docelowej
    
    Args:
        rgb_values: Wartości w przestrzeni źródłowej z krzywą (np. S-Gamut3/S-Log3)
        source_space: Przestrzeń kolorów źródłowa (np. "sgamut3")
        source_curve: Funkcja dekodująca z krzywej źródłowej do liniowej
        target_space: Przestrzeń kolorów docelowa (np. "rec709")
        target_curve_inverse: Funkcja kodująca z liniowej do krzywej docelowej
        
    Returns:
        Wartości w przestrzeni docelowej z krzywą docelową
    """
    # 1. Dekodowanie do liniowej przestrzeni
    linear_source = source_curve(rgb_values)
    
    # 2. Transformacja przestrzeni kolorów (w domenach liniowych)
    linear_target = precise_transform(linear_source, source_space, target_space)
    
    # 3. Enkodowanie do krzywej docelowej
    return target_curve_inverse(linear_target)

# TODO: Add other transformations if needed (e.g., Rec709 to XYZ, ACES to XYZ)
# Consider using the 'colour-science' library for comprehensive transformations.
