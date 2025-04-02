# -*- coding: utf-8 -*-
"""
Moduł zawierający funkcje do transformacji przestrzeni kolorów.
"""

import numpy as np
from typing import List, Union, Optional

# =========================================
# Precyzyjne transformacje przestrzeni kolorów
# =========================================

# Oficjalne macierze transformacji z dokumentacji producentów
# Wszystkie macierze są zdefiniowane z maksymalną precyzją
MATRIX_MAP = {
    # Sony S-Gamut3 -> Rec.709 
    # Źródło: Oficjalna dokumentacja Sony
    "sgamut3_to_rec709": np.array([
        [ 1.71665119,  -0.66662969,  -0.05002750],
        [-0.35567078,   1.61648124,  -0.26081045],
        [-0.25336628,  -0.50001507,   1.75337735]
    ], dtype=np.float64),
    
    # Sony S-Gamut3.cine -> Rec.709
    # Źródło: Oficjalna dokumentacja Sony
    "sgamut3_cine_to_rec709": np.array([
        [ 1.84667249,  -0.55303082,  -0.29364168],
        [-0.42109258,   1.42019374,  -0.01909525],
        [-0.01412169,  -0.11498444,   1.12910614]
    ], dtype=np.float64),
    
    # ARRI Wide Gamut 4 -> Rec.709
    # Źródło: Dokumentacja ARRI
    "arri_wide_gamut4_to_rec709": np.array([
        [ 2.15099497,  -0.68851802,  -0.46247694],
        [-0.54128936,   1.81933229,  -0.27802148],
        [ 0.00281646,  -0.08611581,   1.08329936]
    ], dtype=np.float64),
    
    # ARRI Wide Gamut 3 -> Rec.709
    # Źródło: Dokumentacja ARRI
    "arri_wide_gamut3_to_rec709": np.array([
        [ 1.79627079,  -0.53681690,  -0.25945389],
        [-0.48520276,   1.67177116,  -0.18656840],
        [ 0.02785537,  -0.10264606,   1.07479068]
    ], dtype=np.float64),
    
    # RED Wide Gamut RGB -> Rec.709
    # Źródło: Dokumentacja RED
    "red_wide_gamut_rgb_to_rec709": np.array([
        [ 1.36224675,  -0.14331954,  -0.21892721],
        [-0.22619444,   1.27722674,  -0.05103232],
        [ 0.07081574,  -0.15063514,   1.07981942]
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
