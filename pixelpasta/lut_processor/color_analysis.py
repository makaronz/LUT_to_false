import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from .cube_parser import load_cube_file

def slog3_curve(L):
    """
    Konwertuje wartości liniowe na S-Log3.

    Args:
        L (numpy.ndarray): Wartości liniowe (0-1)

    Returns:
        numpy.ndarray: Wartości S-Log3 (0-1)
    """
    L = np.clip(L, 0, 1)  # Upewnienie się, że wartości są w zakresie [0, 1]
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
    V = np.clip(V, 0, 1)  # Upewnienie się, że wartości są w zakresie [0, 1]
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
    L = np.clip(L, 0, 1)  # Upewnienie się, że wartości są w zakresie [0, 1]
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V

def interpolate_1d_lut(lut_1d, input_values_r, input_values_g, input_values_b):
    """
    Interpoluje wartości z 1D LUT.

    Args:
        lut_1d (numpy.ndarray): Dane 1D LUT
        input_values_r (numpy.ndarray): Wartości wejściowe dla kanału R
        input_values_g (numpy.ndarray): Wartości wejściowe dla kanału G
        input_values_b (numpy.ndarray): Wartości wejściowe dla kanału B

    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe (R, G, B)
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    lut_output_r = lut_1d[:, 0]
    lut_output_g = lut_1d[:, 1]
    lut_output_b = lut_1d[:, 2]

    output_values_r = np.interp(input_values_r, lut_input, lut_output_r)
    output_values_g = np.interp(input_values_g, lut_input, lut_output_g)
    output_values_b = np.interp(input_values_b, lut_input, lut_output_b)

    return np.stack([output_values_r, output_values_g, output_values_b], axis=-1)

def interpolate_3d_lut(lut_3d, lut_size, input_values_r, input_values_g, input_values_b):
    """
    Interpoluje wartości z 3D LUT.

    Args:
        lut_3d (numpy.ndarray): Dane 3D LUT
        lut_size (int): Rozmiar LUT
        input_values_r (numpy.ndarray): Wartości wejściowe dla kanału R
        input_values_g (numpy.ndarray): Wartości wejściowe dla kanału G
        input_values_b (numpy.ndarray): Wartości wejściowe dla kanału B
    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe (R, G, B)
    """
    grid = np.linspace(0, 1, lut_size)
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=0)

    input_points = np.stack([input_values_r, input_values_g, input_values_b], axis=-1)
    output_values = interpolator(input_points)

    return output_values

def srgb_to_rec709(rgb_values, color_space='S-Gamut3'):
    """
    Konwertuje wartości RGB z przestrzeni S-Gamut3 lub S-Gamut3.Cine do Rec.709.

    Args:
        rgb_values (numpy.ndarray): Wartości RGB
        color_space (str): Przestrzeń barwna ('S-Gamut3' lub 'S-Gamut3.Cine')

    Returns:
        numpy.ndarray: Wartości RGB w przestrzeni Rec.709
    """
    if color_space == 'S-Gamut3':
        matrix = np.array([
            [1.6410, -0.3245, -0.3165],
            [-0.6636, 1.6157, 0.0479],
            [0.0117, -0.0085, 0.9968]
        ])
    elif color_space == 'S-Gamut3.Cine':
        matrix = np.array([
            [1.5529, -0.2555, -0.2974],
            [-0.5428, 1.5027, 0.0401],
            [-0.0026, -0.0186, 1.0212]
        ])
    else:
        raise ValueError("Nieobsługiwana przestrzeń barwna. Wybierz 'S-Gamut3' lub 'S-Gamut3.Cine'")

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

    # Wczytanie LUT
    lut_data = load_cube_file(lut_filename)

    # Zdefiniowanie wartości ekspozycji
    exposure_percentages = list(range(1, 100, 5))  # Od 1% do 99% z krokiem 5%
    L_values = np.array([p / 100.0 for p in exposure_percentages])

    # Obliczenie wartości S-Log3
    V_slog3 = slog3_curve(L_values)  # Wartości między 0 a 1

    # Konwersja S-Log3 na światło liniowe
    L_linear = inverse_slog3_curve(V_slog3)

    # Interpolacja wartości LUT - teraz dla R, G, B
    if lut_data['lut_type'] == '1D' or lut_data['lut_type'] == 'both':
        lut_1d = lut_data['lut_1d']
        V_lut_rgb = interpolate_1d_lut(lut_1d, V_slog3, V_slog3, V_slog3) # Wejście to wartości S-Log3
    elif lut_data['lut_type'] == '3D':
        lut_3d = lut_data['lut_3d']
        lut_size = lut_data['lut_3d_size']
        V_lut_rgb = interpolate_3d_lut(lut_3d, lut_size, V_slog3, V_slog3, V_slog3)
    else:
        raise ValueError("Nie można określić typu LUT.")

    # Konwersja wyjścia LUT z powrotem na światło liniowe
    V_lut_linear_r = inverse_slog3_curve(V_lut_rgb[:, 0])
    V_lut_linear_g = inverse_slog3_curve(V_lut_rgb[:, 1])
    V_lut_linear_b = inverse_slog3_curve(V_lut_rgb[:, 2])

    rgb_values = np.stack([V_lut_linear_r, V_lut_linear_g, V_lut_linear_b], axis=-1)

    transformed_rgb = srgb_to_rec709(rgb_values, color_space)

    # Zastosowanie kodowania gamma (Rec.709 OETF)
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Obliczenie luminancji z przekształconych wartości RGB
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    luminance = np.clip(luminance, 0, 1)

    V_slog3_percent = V_slog3 * 100
    V_rec709_percent = rec709_oetf(L_linear) * 100
    V_lut_percent = luminance * 100

    data = {
        'Exposure (%)': exposure_percentages,
        'S-Log3 (%)': V_slog3_percent,
        'Rec.709 (%)': V_rec709_percent,
        'Your LUT (%)': V_lut_percent,
        'Color Space': [color_space] * len(exposure_percentages)
    }
    df = pd.DataFrame(data)
    return df
