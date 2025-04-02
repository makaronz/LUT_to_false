# -*- coding: utf-8 -*-
"""
Moduł zawierający implementacje różnych funkcji transferu
(logarytmicznych, gamma, OETF, EOTF) używanych w przetwarzaniu obrazu.
"""

import numpy as np

# =========================================
# Funkcje Log/Gamma/OETF/EOTF
# =========================================

# --- ARRI LogC4 ---
# Source: https://www.arri.com/resource/blob/35922/b87524555309a95e58555b49fe22b848/2022-08-arri-log-c4-data.pdf
def linear_to_logc4(linear_exposure: np.ndarray) -> np.ndarray:
    """ARRI LogC4 Encoding Function (Linear Scene Exposure to LogC4).
    
    This is the LogC4 implementation, which is different from LogC3.
    LogC4 uses different mathematical constants and has a different response curve
    compared to LogC3. This version is the newer standard used in recent ARRI cameras
    and provides improved dynamic range and color reproduction.
    
    Uses double precision internally for calculations to maximize accuracy.
    
    Args:
        linear_exposure: Linear scene exposure values, typically in range [0, ∞)
        
    Returns:
        LogC4 encoded values in range [0, 1]
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    e_scene = np.asarray(linear_exposure, dtype=np.float64)
    
    # Constants from the official ARRI LogC4 Technical Paper (section 4.1.1)
    # Precise values with full precision
    a = (2.0**18 - 16.0) / 117.45
    b = (1023.0 - 95.0) / 1023.0
    c = 95.0 / 1023.0
    s = (7.0 * np.log(2.0) * 2.0**(7.0 - 14.0 * c/b)) / (a * b)
    t = (2.0**(14.0 * (-c/b) + 6.0) - 64.0) / a
    
    # Wysokoprecyzyjne obliczenia
    log_segment = (np.log2(a * e_scene + 64.0) - 6.0) / 14.0 * b + c
    lin_segment = (e_scene - t) / s
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    log_c4_val = np.where(e_scene >= t, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.clip(log_c4_val, 0.0, 1.0).astype(np.float32)

def logc4_to_linear(logc4_value: np.ndarray) -> np.ndarray:
    """ARRI LogC4 Decoding Function (LogC4 to Linear Scene Exposure).
    
    This is the LogC4 implementation, which is different from LogC3.
    LogC4 uses different mathematical constants and has a different response curve
    compared to LogC3. This version is the newer standard used in recent ARRI cameras
    and provides improved dynamic range and color reproduction.
    
    Uses double precision internally for calculations to maximize accuracy.
    
    Args:
        logc4_value: LogC4 encoded values in range [0, 1]
        
    Returns:
        Linear scene exposure values, typically in range [0, ∞)
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    e_prime = np.asarray(logc4_value, dtype=np.float64)
    
    # Constants from the official ARRI LogC4 Technical Paper (section 4.1.2)
    a = (2.0**18 - 16.0) / 117.45
    b = (1023.0 - 95.0) / 1023.0
    c = 95.0 / 1023.0
    s = (7.0 * np.log(2.0) * 2.0**(7.0 - 14.0 * c/b)) / (a * b)
    t = (2.0**(14.0 * (-c/b) + 6.0) - 64.0) / a
    
    # Threshold is at e_prime = 0 based on the specification
    threshold = 0.0
    
    # Wysokoprecyzyjne obliczenia
    log_segment = (np.power(2.0, (14.0 * (e_prime - c) / b + 6.0)) - 64.0) / a
    lin_segment = e_prime * s + t
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    linear_exp = np.where(e_prime >= threshold, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.maximum(linear_exp, 0.0).astype(np.float32)

# --- ARRI LogC3 ---
# Source: ARRI LUT Generator / Whitepapers
# https://www.arri.com/en/learn-help/learn-help-camera-system/tools/lut-generator
# https://www.arri.com/resource/blob/37366/4802a6c87817392e361b84d99b285845/logc3-specification-data.pdf
def linear_to_logc3(linear_exposure: np.ndarray) -> np.ndarray:
    """ARRI LogC3 Encoding Function (Linear Scene Exposure to LogC3).
    
    This is the LogC3 implementation, which is different from LogC4.
    LogC3 uses different mathematical constants and has a different response curve
    compared to LogC4. This version is commonly used in older ARRI cameras and
    post-production workflows.
    
    Uses double precision internally for calculations to maximize accuracy.
    
    Args:
        linear_exposure: Linear scene exposure values, typically in range [0, ∞)
        
    Returns:
        LogC3 encoded values in range [0, 1]
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    e_scene = np.asarray(linear_exposure, dtype=np.float64)
    
    # Dokładne wartości z oficjalnej specyfikacji ARRI dla LogC v3
    # Wartości dla "EI800 (native)" z dokumentacji ARRI
    a = 5.555556  # Dokładna wartość z dokumentacji
    b = 0.052272  # Dokładna wartość z dokumentacji
    c = 0.247190  # Dokładna wartość z dokumentacji
    d = 0.385537  # Dokładna wartość z dokumentacji
    cut = 0.011361  # Precyzyjny punkt odcięcia

    # Wysokoprecyzyjne obliczenia
    log_segment = c * np.log10(a * e_scene + b) + d
    lin_segment = e_scene * (c * np.log10(a * cut + b) + d) / cut
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    log_c3_val = np.where(e_scene > cut, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.clip(log_c3_val, 0.0, 1.0).astype(np.float32)

def logc3_to_linear(logc3_value: np.ndarray) -> np.ndarray:
    """ARRI LogC3 Decoding Function (LogC3 to Linear Scene Exposure).
    
    This is the LogC3 implementation, which is different from LogC4.
    LogC3 uses different mathematical constants and has a different response curve
    compared to LogC4. This version is commonly used in older ARRI cameras and
    post-production workflows.
    
    Uses double precision internally for calculations to maximize accuracy.
    
    Args:
        logc3_value: LogC3 encoded values in range [0, 1]
        
    Returns:
        Linear scene exposure values, typically in range [0, ∞)
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    e_prime = np.asarray(logc3_value, dtype=np.float64)
    
    # Dokładne wartości z oficjalnej specyfikacji ARRI dla LogC v3
    # Wartości dla "EI800 (native)" z dokumentacji ARRI
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    cut = 0.011361
    log_cut = c * np.log10(a * cut + b) + d  # Wartość LogC w punkcie odcięcia

    # Wysokoprecyzyjne obliczenia
    log_segment = (np.power(10.0, (e_prime - d) / c) - b) / a
    lin_segment = e_prime * cut / log_cut
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    linear_exp = np.where(e_prime > log_cut, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.maximum(linear_exp, 0.0).astype(np.float32)


# --- Sony S-Log3 (Standard) ---
# Source: https://pro.sony/ue_US/technologies/s-log3
# Standard S-Log3 implementation for S-Gamut3
def linear_to_slog3(linear_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log3 Encoding Function (Linear Reflection 0-1 to S-Log3 0-1).
    
    Standard S-Log3 implementation for S-Gamut3 color space.
    This is the standard implementation used in most Sony cameras.
    
    Uses double precision internally for calculations to maximize accuracy.
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    lin = np.asarray(linear_signal, dtype=np.float64)
    # Ensure input is non-negative
    lin = np.maximum(lin, 0.0)
    
    # Oficjalne parametry Sony z dokumentacji technicznej
    a = 0.01
    b = 0.18
    c = 261.5  # Dokładna wartość z Sony
    d = 420.0  # Dokładna wartość z Sony
    
    # Progi odcięcia z oficjalnej dokumentacji
    cut1 = 0.01125  # (7bit_equivalent) cutoff for linear segment
    
    # Obliczenia S-Log3 z maksymalną precyzją
    log_segment = (d + np.log10((lin + a) / (b + a)) * c) / 1023.0
    lin_segment = (lin * (171.2102946929 - 95.0) / cut1 + 95.0) / 1023.0
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    slog3_val = np.where(lin >= cut1, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.clip(slog3_val, 0.0, 1.0).astype(np.float32)

def slog3_to_linear(slog3_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log3 Decoding Function (S-Log3 0-1 to Linear Reflection 0-1).
    
    Standard S-Log3 implementation for S-Gamut3 color space.
    This is the standard implementation used in most Sony cameras.
    
    Uses double precision internally for calculations to maximize accuracy.
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    slog3 = np.asarray(slog3_signal, dtype=np.float64)
    
    # Oficjalne parametry Sony
    a = 0.01
    b = 0.18
    c = 261.5
    d = 420.0
    
    # Progi odcięcia
    cut2 = 171.2102946929 / 1023.0  # Wartość w zakresie 0-1
    
    # Scale to 0-1023 range used in formula derivation
    slog3_scaled = slog3 * 1023.0
    
    # Wysokoprecyzyjne obliczenia
    log_segment = (np.power(10.0, (slog3_scaled - d) / c) * (b + a)) - a
    lin_segment = (slog3_scaled - 95.0) * 0.01125 / (171.2102946929 - 95.0)
    
    linear_val = np.where(slog3_scaled >= cut2, log_segment, lin_segment)
    
    # Ensure non-negative output i konwersja do float32
    return np.maximum(linear_val, 0.0).astype(np.float32)


# --- Sony S-Log3 (S-Gamut3.cine variant) ---
# Source: Sony S-Gamut3.cine Technical Specification
def linear_to_slog3_cine(linear_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log3 Encoding Function for S-Gamut3.cine (Linear Reflection 0-1 to S-Log3 0-1).
    
    Special implementation for S-Gamut3.cine color space.
    This variant uses the same S-Log3 curve but is associated with S-Gamut3.cine color space,
    which has a different gamut than standard S-Gamut3. This distinction is critical for
    correct color reproduction.
    
    Uses double precision internally for calculations to maximize accuracy.
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych - krzywa jest ta sama co dla S-Gamut3
    # Różnice dotyczą głównie przestrzeni kolorów, nie krzywej transferu
    lin = np.asarray(linear_signal, dtype=np.float64)
    lin = np.maximum(lin, 0.0)
    
    # Oficjalne parametry Sony z dokumentacji technicznej
    a = 0.01
    b = 0.18
    c = 261.5
    d = 420.0
    
    # Progi odcięcia z oficjalnej dokumentacji
    cut1 = 0.01125
    
    # Obliczenia S-Log3 z maksymalną precyzją
    log_segment = (d + np.log10((lin + a) / (b + a)) * c) / 1023.0
    lin_segment = (lin * (171.2102946929 - 95.0) / cut1 + 95.0) / 1023.0
    
    # Zastosowanie wektoryzacji numpy dla lepszej wydajności
    slog3_val = np.where(lin >= cut1, log_segment, lin_segment)
    
    # Konwersja z powrotem do float32 po zakończeniu precyzyjnych obliczeń
    return np.clip(slog3_val, 0.0, 1.0).astype(np.float32)

def slog3_cine_to_linear(slog3_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log3 Decoding Function for S-Gamut3.cine (S-Log3 0-1 to Linear Reflection 0-1).
    
    Special implementation for S-Gamut3.cine color space.
    This variant uses the same S-Log3 curve but is associated with S-Gamut3.cine color space,
    which has a different gamut than standard S-Gamut3. This distinction is critical for
    correct color reproduction.
    
    Uses double precision internally for calculations to maximize accuracy.
    """
    # Użycie float64 dla wszystkich obliczeń wewnętrznych
    slog3 = np.asarray(slog3_signal, dtype=np.float64)
    
    # Oficjalne parametry Sony
    a = 0.01
    b = 0.18
    c = 261.5
    d = 420.0
    
    # Progi odcięcia
    cut2 = 171.2102946929 / 1023.0
    
    # Scale to 0-1023 range used in formula derivation
    slog3_scaled = slog3 * 1023.0
    
    # Wysokoprecyzyjne obliczenia
    log_segment = (np.power(10.0, (slog3_scaled - d) / c) * (b + a)) - a
    lin_segment = (slog3_scaled - 95.0) * 0.01125 / (171.2102946929 - 95.0)
    
    linear_val = np.where(slog3_scaled >= cut2, log_segment, lin_segment)
    
    # Ensure non-negative output i konwersja do float32
    return np.maximum(linear_val, 0.0).astype(np.float32)


# --- Rec.709 OETF/EOTF (Gamma ~2.4) ---
# Source: ITU-R BT.709-6 Standard
def linear_to_rec709(linear_signal: np.ndarray) -> np.ndarray:
    """Rec.709 OETF (Opto-Electronic Transfer Function) - Linear to Non-linear Video."""
    lin = np.asarray(linear_signal)
    # Clip input to avoid issues with negative numbers in power function
    lin = np.maximum(lin, 0.0)
    rec709_val = np.where(lin < 0.018,
                          4.5 * lin,
                          1.099 * np.power(lin, 0.45) - 0.099)
    return rec709_val

def rec709_to_linear(rec709_signal: np.ndarray) -> np.ndarray:
    """Rec.709 Inverse OETF / EOTF (Electro-Optical Transfer Function) - Non-linear Video to Linear."""
    vid = np.asarray(rec709_signal)
    # Clip input
    vid = np.maximum(vid, 0.0)
    linear_val = np.where(vid < (4.5 * 0.018), # Threshold is 0.081
                          vid / 4.5,
                          np.power((vid + 0.099) / 1.099, 1.0 / 0.45))
    return linear_val


# --- Sony S-Log2 ---
# Source: Derived from Sony documentation/common implementations. Note: Less standardized than S-Log3.
# Formula structure similar to Kod 2's linear_to_slog2
def linear_to_slog2(linear_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log2 Encoding Function (Approximate)."""
    lin = np.asarray(linear_signal)
    lin = np.maximum(lin, 0.0)
    # Constants derived to roughly match typical S-Log2 curves (10-bit CV)
    log_val = np.where(lin >= 0.03, # Approximate threshold
                       (155.0 * np.log10(lin * 0.9 + 0.03) + 352.0) / 1023.0,
                       (lin * (300.0 - 90.0) / 0.03 + 90.0) / 1023.0 # Linear segment approx
                      )
    return np.clip(log_val, 0.0, 1.0) # Clip output

def slog2_to_linear(slog2_signal: np.ndarray) -> np.ndarray:
    """Sony S-Log2 Decoding Function (Approximate)."""
    slog2 = np.asarray(slog2_signal)
    slog2_scaled = slog2 * 1023.0
    # Threshold value corresponding to lin=0.03 in encoding
    threshold_log = (0.03 * (300.0 - 90.0) / 0.03 + 90.0) # = 300.0
    linear_val = np.where(slog2_scaled >= threshold_log,
                          (np.power(10.0, (slog2_scaled - 352.0) / 155.0) - 0.03) / 0.9,
                          (slog2_scaled - 90.0) * 0.03 / (300.0 - 90.0)
                         )
    return np.maximum(linear_val, 0.0) # Ensure non-negative output


# --- RED Log3G10 ---
# Source: RED Cine-X Documentation / Community implementations. Formula from Kod 2 seems plausible.
# Note: Official RED formulas often involve gamma adjustments depending on ISO/settings. This is simplified.
def linear_to_log3g10(linear_signal: np.ndarray) -> np.ndarray:
    """RED Log3G10 Encoding Function (Simplified)."""
    # Using a common approximation structure based on Colour Science library form:
    # log = gain * log10(black_offset + linear * slope)
    # Constants adjusted to roughly match expected range 0-1
    gain = 0.171752
    slope = 155.975314
    black_offset = 1.0
    cut = 0.01 # Linear segment cut-off (approx)
    lin = np.asarray(linear_signal)
    lin = np.maximum(lin, 0.0)

    log_val = np.where(lin > cut,
                       gain * np.log10(black_offset + lin * slope),
                       lin * (gain * np.log10(black_offset + cut * slope)) / cut # Linear segment
                      )
    return log_val

def log3g10_to_linear(log3g10_signal: np.ndarray) -> np.ndarray:
    """RED Log3G10 Decoding Function (Simplified)."""
    gain = 0.171752
    slope = 155.975314
    black_offset = 1.0
    cut = 0.01
    log_cut = gain * np.log10(black_offset + cut * slope)
    log_val = np.asarray(log3g10_signal)

    linear_val = np.where(log_val > log_cut,
                          (np.power(10.0, log_val / gain) - black_offset) / slope,
                          log_val * cut / log_cut
                         )
    return np.maximum(linear_val, 0.0)

# --- REDgamma3 / REDgamma4 (Display-referred approximations) ---
# Source: Kod 2 - These are simple gamma curves, likely approximations.
def linear_to_redgamma3(linear_signal: np.ndarray) -> np.ndarray:
    """REDgamma3 Approximation (Gamma 2.4)."""
    lin = np.asarray(linear_signal)
    return np.power(np.maximum(lin, 0.0), 1.0/2.4)

def redgamma3_to_linear(gamma_signal: np.ndarray) -> np.ndarray:
    """Inverse REDgamma3 Approximation (Gamma 2.4)."""
    gamma = np.asarray(gamma_signal)
    return np.power(np.maximum(gamma, 0.0), 2.4)

def linear_to_redgamma4(linear_signal: np.ndarray) -> np.ndarray:
    """REDgamma4 Approximation (Gamma 2.2)."""
    lin = np.asarray(linear_signal)
    return np.power(np.maximum(lin, 0.0), 1.0/2.2)

def redgamma4_to_linear(gamma_signal: np.ndarray) -> np.ndarray:
    """Inverse REDgamma4 Approximation (Gamma 2.2)."""
    gamma = np.asarray(gamma_signal)
    return np.power(np.maximum(gamma, 0.0), 2.2)

# --- REDlogFilm (Legacy) ---
# Source: Kod 2 - Formula looks like a generic log curve.
def linear_to_redlogfilm(linear_signal: np.ndarray) -> np.ndarray:
    """REDlogFilm Encoding Function (Legacy, Approximate)."""
    lin = np.asarray(linear_signal)
    # Kod 2: (np.log10(x + 0.01) + 0.6) / 1.3
    return (np.log10(np.maximum(lin, 0.0) + 0.01) + 0.6) / 1.3

def redlogfilm_to_linear(log_signal: np.ndarray) -> np.ndarray:
    """REDlogFilm Decoding Function (Legacy, Approximate)."""
    log = np.asarray(log_signal)
    linear_val = np.power(10.0, log * 1.3 - 0.6) - 0.01
    return np.maximum(linear_val, 0.0)


# --- ACEScct ---
# Source: ACES Documentation S-2016-001
# https://github.com/ampas/aces-dev/blob/master/documents/LaTeX/S-2016-001/S-2016-001.tex
def linear_to_acescct(linear_signal: np.ndarray) -> np.ndarray:
    """ACEScct Encoding Function (Linear ACES 0-1 to ACEScct 0-1)."""
    lin = np.asarray(linear_signal)
    # Constants from spec
    T = 0.0078125
    alpha = 10.54023774
    beta = 0.07290553419
    # Formula scales output to approx 0-1 range
    acescct_val = np.where(lin > T,
                           (np.log2(lin + beta) + 9.72) / 17.52,
                           alpha * lin + beta)
    return acescct_val

def acescct_to_linear(acescct_signal: np.ndarray) -> np.ndarray:
    """ACEScct Decoding Function (ACEScct 0-1 to Linear ACES 0-1)."""
    cct = np.asarray(acescct_signal)
    # Constants from spec
    alpha = 10.54023774
    beta = 0.07290553419
    # Threshold value at T=0.0078125
    cct_T = alpha * 0.0078125 + beta # = 0.15549153419...

    linear_val = np.where(cct > cct_T,
                          np.power(2.0, cct * 17.52 - 9.72) - beta,
                          (cct - beta) / alpha)
    return linear_val

# --- ACEScc ---
# Source: ACES Documentation S-2013-001
def linear_to_acescc(linear_signal: np.ndarray) -> np.ndarray:
    """ACEScc Encoding Function (Linear ACES 0-1 to ACEScc 0-1)."""
    lin = np.asarray(linear_signal)
    # Constants from spec
    # Formula scales output to approx 0-1 range
    acescc_val = np.where(lin > -1.0/32768.0, # Handle slightly negative values
                          (np.log2(lin * 0.5 + 1.0/65536.0) + 9.72) / 17.52,
                          -np.inf) # Or handle as needed
    return acescc_val

def acescc_to_linear(acescc_signal: np.ndarray) -> np.ndarray:
    """ACEScc Decoding Function (ACEScc 0-1 to Linear ACES 0-1)."""
    cc = np.asarray(acescc_signal)
    linear_val = (np.power(2.0, cc * 17.52 - 9.72) - (1.0/65536.0)) * 2.0
    return linear_val

# --- ACESproxy ---
# Source: ACES Documentation S-2013-002 (10-bit) / S-2014-001 (12-bit)
def linear_to_acesproxy10(linear_signal: np.ndarray) -> np.ndarray:
    """ACESproxy 10-bit Encoding Function (Linear ACES 0-1 to ACESproxy10 0-1)."""
    lin = np.asarray(linear_signal)
    # Formula from spec (simplified, assumes input >= 0)
    # Maps ACES range [-0.002, 6.1] roughly to 10-bit CV [64, 940] then scales 0-1
    proxy10 = (np.log2(np.maximum(lin, 6.103515625e-05)) * 68.06754 + 659.34066) / 1023.0
    return np.clip(proxy10, 0.0, 1.0)

def acesproxy10_to_linear(proxy10_signal: np.ndarray) -> np.ndarray:
    """ACESproxy 10-bit Decoding Function (ACESproxy10 0-1 to Linear ACES 0-1)."""
    p10 = np.asarray(proxy10_signal) * 1023.0
    linear_val = np.power(2.0, (p10 - 659.34066) / 68.06754)
    return linear_val


# --- Panasonic V-Log ---
# Source: Panasonic Documentation / Common implementations
def linear_to_vlog(linear_signal: np.ndarray) -> np.ndarray:
    """Panasonic V-Log Encoding Function (Linear 0-1 to V-Log 0-1)."""
    lin = np.asarray(linear_signal)
    lin = np.maximum(lin, 0.0)
    # Constants
    c = 0.241514
    d = 0.598206
    b = 0.00873 # Offset
    cut = 0.01 # Linear segment threshold
    # Formula from Kod 2 seems plausible structure: c + d * log10(a * x + b_offset)
    # Let's use a verified form:
    vlog_val = np.where(lin >= cut,
                        c + d * np.log10(lin + b),
                        5.6 * lin + 0.125) # Linear segment
    return vlog_val

def vlog_to_linear(vlog_signal: np.ndarray) -> np.ndarray:
    """Panasonic V-Log Decoding Function (V-Log 0-1 to Linear 0-1)."""
    vlog = np.asarray(vlog_signal)
    # Constants
    c = 0.241514
    d = 0.598206
    b = 0.00873
    cut = 0.01
    vlog_cut = 5.6 * cut + 0.125 # Value at cut point = 0.181

    linear_val = np.where(vlog >= vlog_cut,
                          np.power(10.0, (vlog - c) / d) - b,
                          (vlog - 0.125) / 5.6)
    return np.maximum(linear_val, 0.0)


# --- Canon Log 2 ---
# Source: Canon Whitepapers / Common implementations
def linear_to_canonlog2(linear_signal: np.ndarray) -> np.ndarray:
    """Canon Log 2 Encoding Function (Linear 0-1 to CLog2 0-1)."""
    lin = np.asarray(linear_signal)
    lin = np.maximum(lin, 0.0)
    # Constants (approximate, may vary slightly by camera/setting)
    a = 5.5556
    b = 0.0646
    c = 0.224282
    d = 0.396286
    cut = 0.013 # Approximate cut point
    # Using a more standard form:
    clog2_val = np.where(lin >= cut,
                         c * np.log10(a * lin + b) + d,
                         lin * (c * np.log10(a * cut + b) + d) / cut) # Linear segment
    return clog2_val

def canonlog2_to_linear(clog2_signal: np.ndarray) -> np.ndarray:
    """Canon Log 2 Decoding Function (CLog2 0-1 to Linear 0-1)."""
    clog2 = np.asarray(clog2_signal)
    # Constants
    a = 5.5556
    b = 0.0646
    c = 0.224282
    d = 0.396286
    cut = 0.013
    clog2_cut = c * np.log10(a * cut + b) + d

    linear_val = np.where(clog2 >= clog2_cut,
                          (np.power(10.0, (clog2 - d) / c) - b) / a,
                          clog2 * cut / clog2_cut)
    return np.maximum(linear_val, 0.0)


# --- Rec.2020 PQ (ST 2084) ---
# Source: SMPTE ST 2084 standard
def linear_to_pq(linear_signal: np.ndarray, L_peak: float = 1000.0) -> np.ndarray:
    """Rec.2020 PQ (ST 2084) Encoding Function (Linear 0-1 to PQ 0-1)."""
    # Assumes linear_signal is normalized scene-linear light (0=black, 1=reference white)
    # L_peak is the peak luminance of the target display in cd/m^2
    L = np.asarray(linear_signal) * L_peak # Scale to absolute luminance
    L = np.maximum(L, 0.0) # Ensure non-negative

    # Constants from ST 2084
    m1 = 2610.0 / 16384.0 # 0.1593017578125
    m2 = (2523.0 / 4096.0) * 128.0 # 78.84375
    c1 = 3424.0 / 4096.0 # 0.8359375
    c2 = (2413.0 / 4096.0) * 32.0 # 18.8515625
    c3 = (2392.0 / 4096.0) * 32.0 # 18.6875

    # Normalize L to 0-10000 range first
    L_norm = L / 10000.0
    L_pow_m1 = np.power(L_norm, m1)
    pq_val = np.power((c1 + c2 * L_pow_m1) / (1.0 + c3 * L_pow_m1), m2)
    return pq_val

def pq_to_linear(pq_signal: np.ndarray, L_peak: float = 1000.0) -> np.ndarray:
    """Rec.2020 PQ (ST 2084) Decoding Function (PQ 0-1 to Linear 0-1)."""
    N = np.asarray(pq_signal)
    N = np.maximum(N, 0.0) # Ensure non-negative

    # Constants
    m1 = 2610.0 / 16384.0
    m2 = (2523.0 / 4096.0) * 128.0
    c1 = 3424.0 / 4096.0
    c2 = (2413.0 / 4096.0) * 32.0
    c3 = (2392.0 / 4096.0) * 32.0

    N_pow_1_m2 = np.power(N, 1.0 / m2)
    # Avoid division by zero if N_pow_1_m2 happens to be exactly c1
    numerator = np.maximum(N_pow_1_m2 - c1, 0.0)
    denominator = c2 - c3 * N_pow_1_m2
    # Handle potential division by zero or negative results if denominator is <= 0
    # Add small epsilon to denominator check
    L_norm = np.where(denominator > 1e-9,
                      np.power(numerator / denominator, 1.0 / m1),
                      0.0)

    L = L_norm * 10000.0 # Denormalize from 0-10000 range
    linear_signal = L / L_peak # Normalize back to 0-1 relative to peak
    return linear_signal


# --- Rec.2020 HLG (ARIB STD-B67) ---
# Source: ITU-R BT.2100 / ARIB STD-B67
def linear_to_hlg(linear_signal: np.ndarray, L_peak: float = 1000.0) -> np.ndarray:
    """Rec.2020 HLG Encoding Function (Linear 0-1 to HLG 0-1)."""
    # Assumes linear_signal is normalized scene-linear (0-1)
    # L_peak is nominal peak luminance (typically 1000 cd/m^2)
    # HLG is scene-referred, so L_peak is less critical than for PQ but affects scaling.
    E = np.asarray(linear_signal)
    E = np.maximum(E, 0.0)

    # Constants for nominal 1000 nit display
    a = 0.17883277
    b = 1.0 - 4.0 * a # 0.28466892
    c = 0.5 - a * np.log(4.0 * a) # 0.55991073

    hlg_val = np.where(E <= 1.0/12.0,
                       np.sqrt(3.0 * E),
                       a * np.log(12.0 * E - b) + c)
    return hlg_val

def hlg_to_linear(hlg_signal: np.ndarray, L_peak: float = 1000.0) -> np.ndarray:
    """Rec.2020 HLG Decoding Function (HLG 0-1 to Linear 0-1)."""
    E_prime = np.asarray(hlg_signal)
    E_prime = np.maximum(E_prime, 0.0)

    # Constants
    a = 0.17883277
    b = 1.0 - 4.0 * a
    c = 0.5 - a * np.log(4.0 * a)

    linear_val = np.where(E_prime <= 0.5, # Threshold is sqrt(3 * 1/12) = sqrt(1/4) = 0.5
                          np.power(E_prime, 2.0) / 3.0,
                          (np.exp((E_prime - c) / a) + b) / 12.0)
    return linear_val


# --- RED IPP2 Output Tone Map (Simulation) ---
# Source: Kod 2 - Simple curve, likely a rough approximation of IPP2's effect.
def linear_to_red_ipp2_odt_approx(linear_signal: np.ndarray) -> np.ndarray:
    """Approximation of RED IPP2 Output Tone Map."""
    lin = np.asarray(linear_signal)
    # Kod 2: np.clip((x ** 0.55) * 1.05 - 0.025, 0.0, 1.0)
    return np.clip(np.power(np.maximum(lin, 0.0), 0.55) * 1.05 - 0.025, 0.0, 1.0)

def red_ipp2_odt_approx_to_linear(odt_signal: np.ndarray) -> np.ndarray:
    """Inverse of approximated RED IPP2 ODT."""
    odt = np.asarray(odt_signal)
    # Inverse operation:
    linear_val = np.power(np.maximum((odt + 0.025) / 1.05, 0.0), 1.0 / 0.55)
    return linear_val
