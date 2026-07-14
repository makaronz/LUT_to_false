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
    # Oficjalna krzywa Sony S-Log3 (poprzednie stałe a=0.432699 należały do
    # starego S-Log1, dawały nieciągłość i 0.342 zamiast 0.4106 dla szarości 18%).
    L = np.asarray(L, dtype=np.float64)
    V = np.where(
        L >= 0.01125,
        (420.0 + 261.5 * np.log10((L + 0.01) / 0.19)) / 1023.0,
        (L * (171.2102946929 - 95.0) / 0.01125 + 95.0) / 1023.0,
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
    # Odwrotność oficjalnej krzywej Sony S-Log3.
    V = np.asarray(V, dtype=np.float64)
    cv = V * 1023.0
    L = np.where(
        cv >= 171.2102946929,
        np.power(10.0, (cv - 420.0) / 261.5) * 0.19 - 0.01,
        (cv - 95.0) * 0.01125 / (171.2102946929 - 95.0),
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
    L = np.clip(L, 0, 1)  # Upewnienie się, że wartości są nieujemne
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V

def _logc4_params():
    """Stałe oficjalnej krzywej ARRI LogC4 (whitepaper 2022-08)."""
    a = (2.0**18 - 16.0) / 117.45
    b = (1023.0 - 95.0) / 1023.0
    c = 95.0 / 1023.0
    s = (7.0 * np.log(2.0) * 2.0**(7.0 - 14.0 * c / b)) / (a * b)
    t = (2.0**(14.0 * (-c / b) + 6.0) - 64.0) / a
    return a, b, c, s, t

def logc4_curve(E_scene):
    """
    Konwertuje wartości liniowe na ARRI LogC4.

    Poprzednia parametryzacja (bit=12, s=1.0, ...) była wymyślona i dawała
    wartości >1 (np. ~1.58 dla szarości 18%). To jest oficjalna krzywa LogC4.
    """
    a, b, c, s, t = _logc4_params()
    E_scene = np.asarray(E_scene, dtype=np.float64)
    V = np.where(
        E_scene >= t,
        (np.log2(a * E_scene + 64.0) - 6.0) / 14.0 * b + c,
        (E_scene - t) / s,
    )
    return V

def inverse_logc4_curve(E):
    """
    Konwertuje wartości ARRI LogC4 na liniowe.
    """
    a, b, c, s, t = _logc4_params()
    E = np.asarray(E, dtype=np.float64)
    L = np.where(
        E >= 0.0,
        (np.power(2.0, 14.0 * (E - c) / b + 6.0) - 64.0) / a,
        E * s + t,
    )
    return L

def logc_curve(E_scene):
    """
    Konwertuje wartości liniowe na ARRI LogC3 (EI800).

    Poprzednia parametryzacja mieszała 10-bitowe code value z wejściem 0-1
    i dawała >1 (np. ~1.23 dla szarości 18%). To jest oficjalna krzywa LogC3.
    """
    cut, a, b, c, d, e, f = 0.010591, 5.555556, 0.052272, 0.247190, 0.385537, 5.367655, 0.092809
    E_scene = np.asarray(E_scene, dtype=np.float64)
    V = np.where(
        E_scene > cut,
        c * np.log10(a * E_scene + b) + d,
        e * E_scene + f,
    )
    return V

def inverse_logc_curve(E):
    """
    Konwertuje wartości ARRI LogC3 (EI800) na liniowe.
    """
    cut, a, b, c, d, e, f = 0.010591, 5.555556, 0.052272, 0.247190, 0.385537, 5.367655, 0.092809
    E = np.asarray(E, dtype=np.float64)
    log_cut = e * cut + f  # 0.149658
    L = np.where(
        E > log_cut,
        (np.power(10.0, (E - d) / c) - b) / a,
        (E - f) / e,
    )
    return L

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
    # Przekształcenie lut_3d. Spec Adobe .cube: czerwony zmienia się najszybciej,
    # więc po reshape oś 0 to niebieski — transponujemy do [red, green, blue].
    lut_3d = np.transpose(lut_3d.reshape((lut_size, lut_size, lut_size, 3)), (2, 1, 0, 3))
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
    # S-Gamut3 -> Rec.709 (D65), wyprowadzone z oficjalnych primaries Sony.
    # Poprzednia macierz była w rzeczywistości macierzą XYZ -> ACES AP1,
    # błędnie podpisaną jako konwersja Sony.
    matrix = np.array([
        [ 1.87791513, -0.79416876, -0.08374637],
        [-0.17680698,  1.35099962, -0.17419264],
        [-0.02620113, -0.14842226,  1.17462339]
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
    # S-Gamut3.Cine -> Rec.709 (D65), wyprowadzone z oficjalnych primaries Sony.
    matrix = np.array([
        [ 1.62694741, -0.54013854, -0.08680887],
        [-0.17851553,  1.41794093, -0.23942540],
        [-0.04443612, -0.19591997,  1.24035608]
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

    # Obliczenie wartości LogC4
    V_logc4 = logc4_curve(L_values)

    # Obliczenie wartości LogC
    V_logc = logc_curve(L_values)

    # Konwersja S-Log3 na światło liniowe
    L_linear_slog3 = inverse_slog3_curve(V_slog3)

    # Konwersja LogC4 na światło liniowe
    L_linear_logc4 = inverse_logc4_curve(V_logc4)

    # Konwersja LogC na światło liniowe
    L_linear_logc = inverse_logc_curve(V_logc)


    # Interpolacja wartości LUT
    if lut_data['lut_type'] == '1D' or lut_data['lut_type'] == 'both':
        lut_1d = lut_data['lut_1d']
        if color_space == 'LogC4':
            V_lut = interpolate_1d_lut(lut_1d, V_logc4)
        elif color_space == 'LogC':
            V_lut = interpolate_1d_lut(lut_1d, V_logc)
        else:
            V_lut = interpolate_1d_lut(lut_1d, V_slog3)
    elif lut_data['lut_type'] == '3D':
        lut_3d = lut_data['lut_3d']
        lut_size = lut_data['lut_3d_size']
        if color_space == 'LogC4':
             V_lut = interpolate_3d_lut(lut_3d, lut_size, V_logc4)
        elif color_space == 'LogC':
            V_lut = interpolate_3d_lut(lut_3d, lut_size, V_logc)
        else:
            V_lut = interpolate_3d_lut(lut_3d, lut_size, V_slog3)

    else:
        raise ValueError("Nie można określić typu LUT.")

    # Konwersja wyjścia LUT z powrotem na światło liniowe w zaleznosci od wybranej przestrzeni
    if color_space == 'LogC4':
        V_lut_linear = inverse_logc4_curve(V_lut)
    elif color_space == 'LogC':
        V_lut_linear = inverse_logc_curve(V_lut)
    else:
        V_lut_linear = inverse_slog3_curve(V_lut)


    # Ponieważ pracujemy z wartościami w skali szarości, musimy utworzyć trójki RGB
    rgb_values = np.stack([V_lut_linear, V_lut_linear, V_lut_linear], axis=-1)

    if color_space == 'S-Gamut3':
        transformed_rgb = s_gamut3_to_rec709(rgb_values)
    elif color_space == 'S-Gamut3.Cine':
        transformed_rgb = s_gamut3_cine_to_rec709(rgb_values)
    elif color_space == "LogC4" or color_space == "LogC":
        transformed_rgb = rgb_values #For LogC4 we do not apply matrix
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
    V_rec709_percent = rec709_oetf(L_linear_slog3) * 100
    V_lut_percent = luminance * 100
    V_logc4_percent = V_logc4 * 100
    V_logc_percent = V_logc * 100

    # Utworzenie tabeli
    data = {
        'Exposure (%)': exposure_percentages,
        'Rec.709 (%)': rec709_oetf(L_linear_slog3) * 100,
        'Your LUT (%)': V_lut_percent,
        'Color Space': [color_space] * len(exposure_percentages)
    }

    if color_space == "LogC4":
        data['LogC4 (%)'] = V_logc4_percent
    elif color_space == 'LogC':
        data['LogC (%)'] = V_logc_percent
    else:
        data['S-Log3 (%)'] = V_slog3_percent
    df = pd.DataFrame(data)

    # Reorder columns to ensure consistency
    if color_space == "LogC4":
        df = df[['Exposure (%)', 'LogC4 (%)', 'Rec.709 (%)', 'Your LUT (%)', 'Color Space']]
    elif color_space == 'LogC':
        df = df[['Exposure (%)', 'LogC (%)', 'Rec.709 (%)', 'Your LUT (%)', 'Color Space']]
    else:
        df = df[['Exposure (%)', 'S-Log3 (%)', 'Rec.709 (%)', 'Your LUT (%)', 'Color Space']]

    return df
