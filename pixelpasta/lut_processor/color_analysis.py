import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

def slog3_curve(L):
    """
    Konwertuje wartości liniowe na S-Log3.
    
    Args:
        L (numpy.ndarray): Wartości liniowe (0-1)
        
    Returns:
        numpy.ndarray: Wartości S-Log3 (0-1)
    """
    a = 0.432699
    b = 0.009468
    c = 0.655
    d = 0.037584
    e = 0.01
    L_threshold = 0.01125000

    V = np.where(
        L >= L_threshold,
        a * np.log10(L + b) + c,
        d * L + e
    )
    return V

def inverse_slog3_curve(V):
    """
    Konwertuje wartości S-Log3 na liniowe.
    
    Args:
        V (numpy.ndarray): Wartości S-Log3 (0-1)
        
    Returns:
        numpy.ndarray: Wartości liniowe (0-1)
    """
    a = 0.432699
    b = 0.009468
    c = 0.655
    d = 0.037584
    e = 0.01
    V_threshold = slog3_curve(0.01125)

    L = np.where(
        V >= V_threshold,
        np.power(10, (V - c) / a) - b,
        (V - e) / d
    )
    return L

def rec709_oetf(L):
    """
    Konwertuje wartości liniowe na Rec.709 (z korekcją gamma).
    
    Args:
        L (numpy.ndarray): Wartości liniowe (0-1)
        
    Returns:
        numpy.ndarray: Wartości Rec.709 (0-1)
    """
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V

def interpolate_1d_lut(lut_1d, input_values):
    """
    Interpoluje wartości z 1D LUT.
    
    Args:
        lut_1d (numpy.ndarray): Dane 1D LUT
        input_values (numpy.ndarray): Wartości wejściowe do interpolacji
        
    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    lut_output = lut_1d[:, 0]  # Zakładając R=G=B
    output_values = np.interp(input_values, lut_input, lut_output)
    return output_values

def interpolate_3d_lut(lut_3d, lut_size, input_values):
    """
    Interpoluje wartości z 3D LUT.
    
    Args:
        lut_3d (numpy.ndarray): Dane 3D LUT
        lut_size (int): Rozmiar LUT
        input_values (numpy.ndarray): Wartości wejściowe do interpolacji
        
    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe
    """
    # Utworzenie siatki wejściowej dla R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Przekształcenie lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Przygotowanie punktów wejściowych, gdzie R=G=B
    input_points = np.array([[v, v, v] for v in input_values])

    # Interpolacja wartości
    output_values = interpolator(input_points)

    # Zakładając R=G=B, bierzemy pierwszy kanał
    return output_values[:, 0]

def s_gamut3_to_rec709(rgb_values):
    """
    Konwertuje wartości RGB z przestrzeni S-Gamut3 do Rec.709.
    
    Args:
        rgb_values (numpy.ndarray): Wartości RGB w przestrzeni S-Gamut3
        
    Returns:
        numpy.ndarray: Wartości RGB w przestrzeni Rec.709
    """
    # Macierz transformacji z S-Gamut3 do Rec.709
    matrix = np.array([
        [1.6410, -0.3245, -0.3165],
        [-0.6636, 1.6157, 0.0479],
        [0.0117, -0.0085, 0.9968]
    ])
    return np.dot(rgb_values, matrix.T)

def s_gamut3_cine_to_rec709(rgb_values):
    """
    Konwertuje wartości RGB z przestrzeni S-Gamut3.Cine do Rec.709.
    
    Args:
        rgb_values (numpy.ndarray): Wartości RGB w przestrzeni S-Gamut3.Cine
        
    Returns:
        numpy.ndarray: Wartości RGB w przestrzeni Rec.709
    """
    # Macierz transformacji z S-Gamut3.Cine do Rec.709
    matrix = np.array([
        [1.5529, -0.2555, -0.2974],
        [-0.5428, 1.5027, 0.0401],
        [-0.0026, -0.0186, 1.0212]
    ])
    return np.dot(rgb_values, matrix.T)

def generate_table(lut_filename, color_space):
    """
    Generuje tabelę porównawczą dla pliku LUT.
    
    Args:
        lut_filename (str): Ścieżka do pliku .CUBE
        color_space (str): Przestrzeń barwna ('S-Gamut3' lub 'S-Gamut3.Cine')
        
    Returns:
        pandas.DataFrame: Tabela porównawcza
    """
    from .cube_parser import load_cube_file
    
    # Wczytanie LUT
    lut_data = load_cube_file(lut_filename)

    # Zdefiniowanie wartości ekspozycji
    exposure_percentages = list(range(1, 100, 5))  # Od 1% do 99% z krokiem 5%
    L_values = np.array([p / 100.0 for p in exposure_percentages])

    # Obliczenie wartości S-Log3
    V_slog3 = slog3_curve(L_values)  # Wartości między 0 a 1

    # Konwersja S-Log3 na światło liniowe
    L_linear = inverse_slog3_curve(V_slog3)

    # Interpolacja wartości LUT
    if lut_data['lut_type'] == '1D' or lut_data['lut_type'] == 'both':
        lut_1d = lut_data['lut_1d']
        # Wejście do LUT to wartości S-Log3
        V_lut = interpolate_1d_lut(lut_1d, V_slog3)
    elif lut_data['lut_type'] == '3D':
        lut_3d = lut_data['lut_3d']
        lut_size = lut_data['lut_3d_size']
        V_lut = interpolate_3d_lut(lut_3d, lut_size, V_slog3)
    else:
        raise ValueError("Nie można określić typu LUT.")

    # Konwersja wyjścia LUT (w S-Log3) z powrotem na światło liniowe
    V_lut_linear = inverse_slog3_curve(V_lut)

    # Ponieważ pracujemy z wartościami w skali szarości, musimy utworzyć trójki RGB
    rgb_values = np.stack([V_lut_linear, V_lut_linear, V_lut_linear], axis=-1)

    if color_space == 'S-Gamut3':
        transformed_rgb = s_gamut3_to_rec709(rgb_values)
    elif color_space == 'S-Gamut3.Cine':
        transformed_rgb = s_gamut3_cine_to_rec709(rgb_values)
    else:
        # Brak transformacji
        transformed_rgb = rgb_values

    # Zastosowanie kodowania gamma (Rec.709 OETF)
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Obliczenie luminancji z przekształconych wartości RGB
    # Użycie współczynników luminancji Rec.709: Y = 0.2126 R + 0.7152 G + 0.0722 B
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    # Upewnienie się, że wartości luminancji są w zakresie [0,1]
    luminance = np.clip(luminance, 0, 1)

    # Konwersja wartości na procenty
    V_slog3_percent = V_slog3 * 100
    V_rec709_percent = rec709_oetf(L_linear) * 100
    V_lut_percent = luminance * 100

    # Utworzenie tabeli
    data = {
        'Exposure (%)': exposure_percentages,
        'S-Log3 (%)': V_slog3_percent,
        'Rec.709 (%)': V_rec709_percent,
        'Your LUT (%)': V_lut_percent,
        'Color Space': [color_space] * len(exposure_percentages)
    }
    df = pd.DataFrame(data)
    return df
