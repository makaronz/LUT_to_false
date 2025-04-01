import numpy as np
from scipy.interpimport numpy as np
from scipy.interpolate import RegularGridInterpolator

def load_cube_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")

    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', or 'both'
    title = None

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    data_started = False  # Flag to indicate when LUT data starts
    for line_number, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if any(stripped_line.startswith(keyword) for keyword in keywords):
            parts = stripped_line.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid keyword format in line {line_number}: {line}")

            if 'TITLE' in stripped_line:
                title = stripped_line.split(' ', 1)[1].strip('"')
            elif 'LUT_1D_SIZE' in stripped_line:
                try:
                    lut_1d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_1D_SIZE value in line {line_number}: {line}")
                if lut_type == '3D':
                    lut_type = 'both'
                else:
                    lut_type = '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                try:
                    lut_3d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_3D_SIZE value in line {line_number}: {line}")
                if lut_type == '1D':
                    lut_type = 'both'
                else:
                    lut_type = '3D'
        elif not data_started:
            data_started = True # Assume data starts after header

        if data_started:
            # LUT data
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) != 3:
                    raise ValueError(f"Invalid data format in line {line_number}: {line}. Expected 3 values.")

                if lut_type == '1D' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type == 'both' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type in ('3D', 'both'):
                    lut_3d.append(values)
                else:
                    raise ValueError(f"Unexpected data in line {line_number}: {line}")

            except ValueError as e:
                raise ValueError(f"Error parsing data in line {line_number}: {e}")

    if lut_type == '1D' and len(lut_1d) != lut_1d_size:
        raise ValueError(f"Incorrect number of data entries for 1D LUT. Expected {lut_1d_size}, got {len(lut_1d)}")
    if lut_type == '3D' and len(lut_3d) != lut_3d_size**3:
        raise ValueError(f"Incorrect number of data entries for 3D LUT. Expected {lut_3d_size**3}, got {len(lut_3d)}")
    if lut_type == 'both' and (len(lut_1d) != lut_1d_size or len(lut_3d) != lut_3d_size**3):
        raise ValueError("Incorrect number of data entries for combined 1D and 3D LUT.")

    return {
        'title': title,
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d, dtype=np.float32),
        'lut_3d': np.array(lut_3d, dtype=np.float32)
    }


def slog3_curve(L):
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
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V


def rec709_curve(L):
    # Inverse of Rec.709 OETF
    V = np.where(
        L < 0.081,
        L / 4.5,
        np.power((L + 0.099) / 1.099, 1 / 0.45)
    )
    return V

def interpolate_1d_lut(lut_1d, input_values):
    """Interpolates values using a 1D LUT.

    Args:
        lut_1d (np.ndarray): The 1D LUT data. Assumed to be Nx3 (RGB).
        input_values (np.ndarray): The input values to interpolate (grayscale).

    Returns:
        np.ndarray: The interpolated RGB values (Nx3).
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    output_values = np.empty((len(input_values), 3), dtype=np.float32)
    for i in range(3):  # Interpolate each color channel separately
      output_values[:,i] = np.interp(input_values, lut_input, lut_1d[:,i])
    return output_values

def interpolate_3d_lut(lut_3d, lut_size, input_values):
    """
    Interpolates values using a 3D LUT.

    Args:
        lut_3d (np.ndarray):  3D LUT data.
        lut_size (int): Size of the 3D LUT.
        input_values (np.ndarray): Input RGB values (Nx3 array).

    Returns:
        np.ndarray: Interpolated RGB values (Nx3 array).
    """

    # Create input grid for R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Reshape lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Interpolate values
    output_values = interpolator(input_values)
    return output_values

# --- ARRI LogC4 Functions (from logc4.pdf) ---
# https://www.arri.com/resource/blob/35922/b87524555309a95e58555b49fe22b848/2022-08-arri-log-c4-data.pdf

# 4.1.1 Encoding Function
def arri_logc4_encode(e_scene):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_scene >= t,
                    (np.log2(a * e_scene + 64) - 6) / 14 * b + c,
                    (e_scene - t) / s)

# 4.1.2 Decoding Function
def arri_logc4_decode(e_prime):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_prime >= 0,
                    (2**(14 * (e_prime - c) / b + 6) - 64) / a,
                    e_prime * s + t)

# --- ARRI LogC3 Functions  ---
# https://www.arri.com/en/learn-help/learn-help-camera-system/tools/lut-generator
def arri_logc3_encode(e_scene):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928

    return np.where(e_scene >= t,
                    c * np.log10(a * e_scene + b) + d,
                    (e_scene/t) * (c * np.log10(a * t + b) + d))

def arri_logc3_decode(e_prime):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928
    
    return np.where(e_prime >= (c * np.log10(a * t + b) + d),
                    (np.power(10, ((e_prime - d) / c)) - b) / a,
                    (e_prime / (c * np.log10(a * t + b) + d)) * t)
                    

# 4.3.1 ARRI LogC4 to CIE XYZ Conversion
def arri_logc4_to_xyz(rgb_logc4):
    m_xyz = np.array([
        [0.704858320407232064, 0.129760295170463003, 0.115837311473976537],
        [0.254524176404027025, 0.781477732712002049, -0.036001909116029039],
        [0.000000000000000000, 0.000000000000000000, 1.089057750759878429]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_xyz, rgb_linear)

# 4.3.2 ARRI LogC4 to ACES Conversion
def arri_logc4_to_aces(rgb_logc4):
    m_aces = np.array([
        [0.750957362824734131, 0.144422786709757084, 0.104619850465508965],
        [0.000821837079380207, 1.007397584885003194, -0.008219421964383583],
        [-0.000499952143533471, -0.000854177231436971, 1.001354129374970370]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_aces, rgb_linear)


# --- Placeholder functions for S-Log3 (Approximation) ---

def slog3_encode(linear):
    """
    Approximates S-Log3 encoding.  This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog3_decode(log_value):
    """
    Approximates S-Log3 decoding. This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864

    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m

def slog2_encode(linear):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog2_decode(log_value):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m
        
# --- Placeholder functions for RED Log3G10 (Approximation) ---
def log3g10_encode(linear):
    """
    Approximates RED Log3G10 encoding. This is NOT the official formula.
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return np.clip(a * np.log10(b * linear + c) + d, 0, 1)

def log3g10_decode(log_value):
    """
    Approximates RED Log3G10 decoding. This is NOT the official formula
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return (10**((log_value - d) / a) - c) / b

def s_gamut3_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3 to Rec.709
    matrix = np.array([
        [1.6410, -0.3245, -0.3165],
        [-0.6636, 1.6157, 0.0479],
        [0.0117, -0.0085, 0.9968]
    ])
    return np.dot(rgb_values, matrix.T)


def s_gamut3_cine_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3.Cine to Rec.709
    matrix = np.array([
        [1.5529, -0.2555, -0.2974],
        [-0.5428, 1.5027, 0.0401],
        [-0.0026, -0.0186, 1.0212]
    ])
    return np.dot(rgb_values, matrix.T)


def generate_table(lut_filename, color_space, input_encoding='slog3'):
    """Generates a table comparing different color encodings and LUT conversions.

    Args:
        lut_filename (str): Path to the .cube LUT file.
        color_space (str): Target color space ('s-gamut3' or 's-gamut3.cine').
        input_encoding (str): Input color encoding ('slog3', 'arri_logc4', 'log3g10').
    Returns:
        np.ndarray: Table with comparison data.
    """

    lut_data = load_cube_file(lut_filename)

    exposure_percentages = np.arange(1, 100, 5)
    L_values = exposure_percentages / 100.0

    if input_encoding == 'slog3':
        input_values = slog3_curve(L_values)
        input_linear = inverse_slog3_curve(input_values)
    elif input_encoding == 'arri_logc4':
        input_values = arri_logc4_encode(L_values)
        input_linear = arri_logc4_decode(input_values)
    elif input_encoding == 'log3g10':
        input_values = log3g10_encode(L_values)
        input_linear = log3g10_decode(input_values)
    else:
        raise ValueError("Invalid input_encoding. Choose 'slog3', 'arri_logc4', or 'log3g10'.")

    # Create RGB triplets for input
    input_rgb = np.stack([input_values, input_values, input_values], axis=-1)

    if lut_data['lut_type'] == '1D':
        lut_output = interpolate_1d_lut(lut_data['lut_1d'], input_values)
    elif lut_data['lut_type'] == '3D':
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    elif lut_data['lut_type'] == 'both':  # Use 3D LUT if both are available
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    else:
        raise ValueError("Cannot determine LUT type.")

    if color_space.lower() == 's-gamut3':
        transformed_rgb = s_gamut3_to_rec709(lut_output)
    elif color_space.lower() == 's-gamut3.cine':
        transformed_rgb = s_gamut3_cine_to_rec709(lut_output)
    else:
        raise ValueError("Invalid color_space. Choose 's-gamut3' or 's-gamut3.cine'.")

    # Apply Rec.709 OETF
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Calculate luminance
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    luminance = np.clip(luminance, 0, 1)

    # Convert to percentages
    input_percent = input_values * 100
    rec709_percent = rec709_oetf(input_linear) * 100  # Using input_linear for Rec709
    lut_percent = luminance * 100

    table = np.column_stack([exposure_percentages, input_percent, rec709_percent, lut_percent])
    return table

import numpy as np
from scipy.interpolate import RegularGridInterpolator

def load_cube_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")

    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', or 'both'
    title = None

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    data_started = False  # Flag to indicate when LUT data starts
    for line_number, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if any(stripped_line.startswith(keyword) for keyword in keywords):
            parts = stripped_line.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid keyword format in line {line_number}: {line}")

            if 'TITLE' in stripped_line:
                title = stripped_line.split(' ', 1)[1].strip('"')
            elif 'LUT_1D_SIZE' in stripped_line:
                try:
                    lut_1d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_1D_SIZE value in line {line_number}: {line}")
                if lut_type == '3D':
                    lut_type = 'both'
                else:
                    lut_type = '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                try:
                    lut_3d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_3D_SIZE value in line {line_number}: {line}")
                if lut_type == '1D':
                    lut_type = 'both'
                else:
                    lut_type = '3D'
        elif not data_started:
            data_started = True # Assume data starts after header

        if data_started:
            # LUT data
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) != 3:
                    raise ValueError(f"Invalid data format in line {line_number}: {line}. Expected 3 values.")

                if lut_type == '1D' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type == 'both' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type in ('3D', 'both'):
                    lut_3d.append(values)
                else:
                    raise ValueError(f"Unexpected data in line {line_number}: {line}")

            except ValueError as e:
                raise ValueError(f"Error parsing data in line {line_number}: {e}")

    if lut_type == '1D' and len(lut_1d) != lut_1d_size:
        raise ValueError(f"Incorrect number of data entries for 1D LUT. Expected {lut_1d_size}, got {len(lut_1d)}")
    if lut_type == '3D' and len(lut_3d) != lut_3d_size**3:
        raise ValueError(f"Incorrect number of data entries for 3D LUT. Expected {lut_3d_size**3}, got {len(lut_3d)}")
    if lut_type == 'both' and (len(lut_1d) != lut_1d_size or len(lut_3d) != lut_3d_size**3):
        raise ValueError("Incorrect number of data entries for combined 1D and 3D LUT.")

    return {
        'title': title,
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d, dtype=np.float32),
        'lut_3d': np.array(lut_3d, dtype=np.float32)
    }


def slog3_curve(L):
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
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V


def rec709_curve(L):
    # Inverse of Rec.709 OETF
    V = np.where(
        L < 0.081,
        L / 4.5,
        np.power((L + 0.099) / 1.099, 1 / 0.45)
    )
    return V

def interpolate_1d_lut(lut_1d, input_values):
    """Interpolates values using a 1D LUT.

    Args:
        lut_1d (np.ndarray): The 1D LUT data. Assumed to be Nx3 (RGB).
        input_values (np.ndarray): The input values to interpolate (grayscale).

    Returns:
        np.ndarray: The interpolated RGB values (Nx3).
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    output_values = np.empty((len(input_values), 3), dtype=np.float32)
    for i in range(3):  # Interpolate each color channel separately
      output_values[:,i] = np.interp(input_values, lut_input, lut_1d[:,i])
    return output_values

def interpolate_3d_lut(lut_3d, lut_size, input_values):
    """
    Interpolates values using a 3D LUT.

    Args:
        lut_3d (np.ndarray):  3D LUT data.
        lut_size (int): Size of the 3D LUT.
        input_values (np.ndarray): Input RGB values (Nx3 array).

    Returns:
        np.ndarray: Interpolated RGB values (Nx3 array).
    """

    # Create input grid for R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Reshape lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Interpolate values
    output_values = interpolator(input_values)
    return output_values

# --- ARRI LogC4 Functions (from logc4.pdf) ---
# https://www.arri.com/resource/blob/35922/b87524555309a95e58555b49fe22b848/2022-08-arri-log-c4-data.pdf

# 4.1.1 Encoding Function
def arri_logc4_encode(e_scene):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_scene >= t,
                    (np.log2(a * e_scene + 64) - 6) / 14 * b + c,
                    (e_scene - t) / s)

# 4.1.2 Decoding Function
def arri_logc4_decode(e_prime):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_prime >= 0,
                    (2**(14 * (e_prime - c) / b + 6) - 64) / a,
                    e_prime * s + t)

# --- ARRI LogC3 Functions  ---
# https://www.arri.com/en/learn-help/learn-help-camera-system/tools/lut-generator
def arri_logc3_encode(e_scene):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928

    return np.where(e_scene >= t,
                    c * np.log10(a * e_scene + b) + d,
                    (e_scene/t) * (c * np.log10(a * t + b) + d))

def arri_logc3_decode(e_prime):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928
    
    return np.where(e_prime >= (c * np.log10(a * t + b) + d),
                    (np.power(10, ((e_prime - d) / c)) - b) / a,
                    (e_prime / (c * np.log10(a * t + b) + d)) * t)
                    

# 4.3.1 ARRI LogC4 to CIE XYZ Conversion
def arri_logc4_to_xyz(rgb_logc4):
    m_xyz = np.array([
        [0.704858320407232064, 0.129760295170463003, 0.115837311473976537],
        [0.254524176404027025, 0.781477732712002049, -0.036001909116029039],
        [0.000000000000000000, 0.000000000000000000, 1.089057750759878429]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_xyz, rgb_linear)

# 4.3.2 ARRI LogC4 to ACES Conversion
def arri_logc4_to_aces(rgb_logc4):
    m_aces = np.array([
        [0.750957362824734131, 0.144422786709757084, 0.104619850465508965],
        [0.000821837079380207, 1.007397584885003194, -0.008219421964383583],
        [-0.000499952143533471, -0.000854177231436971, 1.001354129374970370]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_aces, rgb_linear)


# --- Placeholder functions for S-Log3 (Approximation) ---

def slog3_encode(linear):
    """
    Approximates S-Log3 encoding.  This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog3_decode(log_value):
    """
    Approximates S-Log3 decoding. This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864

    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m

def slog2_encode(linear):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog2_decode(log_value):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m
        
# --- Placeholder functions for RED Log3G10 (Approximation) ---
def log3g10_encode(linear):
    """
    Approximates RED Log3G10 encoding. This is NOT the official formula.
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return np.clip(a * np.log10(b * linear + c) + d, 0, 1)

def log3g10_decode(log_value):
    """
    Approximates RED Log3G10 decoding. This is NOT the official formula
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return (10**((log_value - d) / a) - c) / b

def s_gamut3_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3 to Rec.709
    matrix = np.array([
        [1.6410, -0.3245, -0.3165],
        [-0.6636, 1.6157, 0.0479],
        [0.0117, -0.0085, 0.9968]
    ])
    return np.dot(rgb_values, matrix.T)


def s_gamut3_cine_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3.Cine to Rec.709
    matrix = np.array([
        [1.5529, -0.2555, -0.2974],
        [-0.5428, 1.5027, 0.0401],
        [-0.0026, -0.0186, 1.0212]
    ])
    return np.dot(rgb_values, matrix.T)


def generate_table(lut_filename, color_space, input_encoding='slog3'):
    """Generates a table comparing different color encodings and LUT conversions.

    Args:
        lut_filename (str): Path to the .cube LUT file.
        color_space (str): Target color space ('s-gamut3' or 's-gamut3.cine').
        input_encoding (str): Input color encoding ('slog3', 'arri_logc4', 'log3g10').
    Returns:
        np.ndarray: Table with comparison data.
    """

    lut_data = load_cube_file(lut_filename)

    exposure_percentages = np.arange(1, 100, 5)
    L_values = exposure_percentages / 100.0

    if input_encoding == 'slog3':
        input_values = slog3_curve(L_values)
        input_linear = inverse_slog3_curve(input_values)
    elif input_encoding == 'arri_logc4':
        input_values = arri_logc4_encode(L_values)
        input_linear = arri_logc4_decode(input_values)
    elif input_encoding == 'log3g10':
        input_values = log3g10_encode(L_values)
        input_linear = log3g10_decode(input_values)
    else:
        raise ValueError("Invalid input_encoding. Choose 'slog3', 'arri_logc4', or 'log3g10'.")

    # Create RGB triplets for input
    input_rgb = np.stack([input_values, input_values, input_values], axis=-1)

    if lut_data['lut_type'] == '1D':
        lut_output = interpolate_1d_lut(lut_data['lut_1d'], input_values)
    elif lut_data['lut_type'] == '3D':
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    elif lut_data['lut_type'] == 'both':  # Use 3D LUT if both are available
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    else:
        raise ValueError("Cannot determine LUT type.")

    if color_space.lower() == 's-gamut3':
        transformed_rgb = s_gamut3_to_rec709(lut_output)
    elif color_space.lower() == 's-gamut3.cine':
        transformed_rgb = s_gamut3_cine_to_rec709(lut_output)
    else:
        raise ValueError("Invalid color_space. Choose 's-gamut3' or 's-gamut3.cine'.")

    # Apply Rec.709 OETF
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Calculate luminance
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    luminance = np.clip(luminance, 0, 1)

    # Convert to percentages
    input_percent = input_values * 100
    rec709_percent = rec709_oetf(input_linear) * 100  # Using input_linear for Rec709
    lut_percent = luminance * 100

    table = np.column_stack([exposure_percentages, input_percent, rec709_percent, lut_percent])
    return table

olate import RegularGridInterpolator

def load_cube_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")

    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', or 'both'
    title = None

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    data_started = False  # Flag to indicate when LUT data starts
    for line_number, line in enumerate(lines, 1):
        stripped_line = line.strip()

        if any(stripped_line.startswith(keyword) for keyword in keywords):
            parts = stripped_line.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid keyword format in line {line_number}: {line}")

            if 'TITLE' in stripped_line:
                title = stripped_line.split(' ', 1)[1].strip('"')
            elif 'LUT_1D_SIZE' in stripped_line:
                try:
                    lut_1d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_1D_SIZE value in line {line_number}: {line}")
                if lut_type == '3D':
                    lut_type = 'both'
                else:
                    lut_type = '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                try:
                    lut_3d_size = int(parts[-1])
                except ValueError:
                    raise ValueError(f"Invalid LUT_3D_SIZE value in line {line_number}: {line}")
                if lut_type == '1D':
                    lut_type = 'both'
                else:
                    lut_type = '3D'
        elif not data_started:
            data_started = True # Assume data starts after header

        if data_started:
            # LUT data
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) != 3:
                    raise ValueError(f"Invalid data format in line {line_number}: {line}. Expected 3 values.")

                if lut_type == '1D' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type == 'both' and len(lut_1d) < lut_1d_size:
                    lut_1d.append(values)
                elif lut_type in ('3D', 'both'):
                    lut_3d.append(values)
                else:
                    raise ValueError(f"Unexpected data in line {line_number}: {line}")

            except ValueError as e:
                raise ValueError(f"Error parsing data in line {line_number}: {e}")

    if lut_type == '1D' and len(lut_1d) != lut_1d_size:
        raise ValueError(f"Incorrect number of data entries for 1D LUT. Expected {lut_1d_size}, got {len(lut_1d)}")
    if lut_type == '3D' and len(lut_3d) != lut_3d_size**3:
        raise ValueError(f"Incorrect number of data entries for 3D LUT. Expected {lut_3d_size**3}, got {len(lut_3d)}")
    if lut_type == 'both' and (len(lut_1d) != lut_1d_size or len(lut_3d) != lut_3d_size**3):
        raise ValueError("Incorrect number of data entries for combined 1D and 3D LUT.")

    return {
        'title': title,
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d, dtype=np.float32),
        'lut_3d': np.array(lut_3d, dtype=np.float32)
    }


def slog3_curve(L):
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
    V = np.where(
        L < 0.018,
        4.5 * L,
        1.099 * np.power(L, 0.45) - 0.099
    )
    return V


def rec709_curve(L):
    # Inverse of Rec.709 OETF
    V = np.where(
        L < 0.081,
        L / 4.5,
        np.power((L + 0.099) / 1.099, 1 / 0.45)
    )
    return V

def interpolate_1d_lut(lut_1d, input_values):
    """Interpolates values using a 1D LUT.

    Args:
        lut_1d (np.ndarray): The 1D LUT data. Assumed to be Nx3 (RGB).
        input_values (np.ndarray): The input values to interpolate (grayscale).

    Returns:
        np.ndarray: The interpolated RGB values (Nx3).
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    output_values = np.empty((len(input_values), 3), dtype=np.float32)
    for i in range(3):  # Interpolate each color channel separately
      output_values[:,i] = np.interp(input_values, lut_input, lut_1d[:,i])
    return output_values

def interpolate_3d_lut(lut_3d, lut_size, input_values):
    """
    Interpolates values using a 3D LUT.

    Args:
        lut_3d (np.ndarray):  3D LUT data.
        lut_size (int): Size of the 3D LUT.
        input_values (np.ndarray): Input RGB values (Nx3 array).

    Returns:
        np.ndarray: Interpolated RGB values (Nx3 array).
    """

    # Create input grid for R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Reshape lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Interpolate values
    output_values = interpolator(input_values)
    return output_values

# --- ARRI LogC4 Functions (from logc4.pdf) ---
# https://www.arri.com/resource/blob/35922/b87524555309a95e58555b49fe22b848/2022-08-arri-log-c4-data.pdf

# 4.1.1 Encoding Function
def arri_logc4_encode(e_scene):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_scene >= t,
                    (np.log2(a * e_scene + 64) - 6) / 14 * b + c,
                    (e_scene - t) / s)

# 4.1.2 Decoding Function
def arri_logc4_decode(e_prime):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    return np.where(e_prime >= 0,
                    (2**(14 * (e_prime - c) / b + 6) - 64) / a,
                    e_prime * s + t)

# --- ARRI LogC3 Functions  ---
# https://www.arri.com/en/learn-help/learn-help-camera-system/tools/lut-generator
def arri_logc3_encode(e_scene):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928

    return np.where(e_scene >= t,
                    c * np.log10(a * e_scene + b) + d,
                    (e_scene/t) * (c * np.log10(a * t + b) + d))

def arri_logc3_decode(e_prime):
    a = 5.555556
    b = 0.052272
    c = 0.247190
    d = 0.385537
    t = 0.00928
    
    return np.where(e_prime >= (c * np.log10(a * t + b) + d),
                    (np.power(10, ((e_prime - d) / c)) - b) / a,
                    (e_prime / (c * np.log10(a * t + b) + d)) * t)
                    

# 4.3.1 ARRI LogC4 to CIE XYZ Conversion
def arri_logc4_to_xyz(rgb_logc4):
    m_xyz = np.array([
        [0.704858320407232064, 0.129760295170463003, 0.115837311473976537],
        [0.254524176404027025, 0.781477732712002049, -0.036001909116029039],
        [0.000000000000000000, 0.000000000000000000, 1.089057750759878429]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_xyz, rgb_linear)

# 4.3.2 ARRI LogC4 to ACES Conversion
def arri_logc4_to_aces(rgb_logc4):
    m_aces = np.array([
        [0.750957362824734131, 0.144422786709757084, 0.104619850465508965],
        [0.000821837079380207, 1.007397584885003194, -0.008219421964383583],
        [-0.000499952143533471, -0.000854177231436971, 1.001354129374970370]
    ])
    rgb_linear = np.array([arri_logc4_decode(val) for val in rgb_logc4])
    return np.dot(m_aces, rgb_linear)


# --- Placeholder functions for S-Log3 (Approximation) ---

def slog3_encode(linear):
    """
    Approximates S-Log3 encoding.  This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog3_decode(log_value):
    """
    Approximates S-Log3 decoding. This is NOT the official formula.
    """
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.01
    m = 17.9177
    n = 0.092864

    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m

def slog2_encode(linear):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    
    if linear >= t:
        return np.clip(a * np.log(b * linear + c) + d, 0, 1)
    else:
        return np.clip(m * linear + n, 0, 1)

def slog2_decode(log_value):
    #a = 0.1596;
    #b = 10.1572;
    #c = 0.0393;
    #d = 0.6306;
    a = 0.432699
    b = 7.3
    c = 0.037584
    d = 0.616596
    t = 0.014
    m = 15.1927
    n = 0.096636
    if log_value >= (m*t + n) :
        return (np.exp((log_value - d) / a) - c) / b
    else:
        return (log_value - n) / m
        
# --- Placeholder functions for RED Log3G10 (Approximation) ---
def log3g10_encode(linear):
    """
    Approximates RED Log3G10 encoding. This is NOT the official formula.
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return np.clip(a * np.log10(b * linear + c) + d, 0, 1)

def log3g10_decode(log_value):
    """
    Approximates RED Log3G10 decoding. This is NOT the official formula
    """
    a = 0.555556
    b = 10.0
    c = 0.001
    d = 0.0722
    
    return (10**((log_value - d) / a) - c) / b

def s_gamut3_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3 to Rec.709
    matrix = np.array([
        [1.6410, -0.3245, -0.3165],
        [-0.6636, 1.6157, 0.0479],
        [0.0117, -0.0085, 0.9968]
    ])
    return np.dot(rgb_values, matrix.T)


def s_gamut3_cine_to_rec709(rgb_values):
    # Transformation matrix from S-Gamut3.Cine to Rec.709
    matrix = np.array([
        [1.5529, -0.2555, -0.2974],
        [-0.5428, 1.5027, 0.0401],
        [-0.0026, -0.0186, 1.0212]
    ])
    return np.dot(rgb_values, matrix.T)


def generate_table(lut_filename, color_space, input_encoding='slog3'):
    """Generates a table comparing different color encodings and LUT conversions.

    Args:
        lut_filename (str): Path to the .cube LUT file.
        color_space (str): Target color space ('s-gamut3' or 's-gamut3.cine').
        input_encoding (str): Input color encoding ('slog3', 'arri_logc4', 'log3g10').
    Returns:
        np.ndarray: Table with comparison data.
    """

    lut_data = load_cube_file(lut_filename)

    exposure_percentages = np.arange(1, 100, 5)
    L_values = exposure_percentages / 100.0

    if input_encoding == 'slog3':
        input_values = slog3_curve(L_values)
        input_linear = inverse_slog3_curve(input_values)
    elif input_encoding == 'arri_logc4':
        input_values = arri_logc4_encode(L_values)
        input_linear = arri_logc4_decode(input_values)
    elif input_encoding == 'log3g10':
        input_values = log3g10_encode(L_values)
        input_linear = log3g10_decode(input_values)
    else:
        raise ValueError("Invalid input_encoding. Choose 'slog3', 'arri_logc4', or 'log3g10'.")

    # Create RGB triplets for input
    input_rgb = np.stack([input_values, input_values, input_values], axis=-1)

    if lut_data['lut_type'] == '1D':
        lut_output = interpolate_1d_lut(lut_data['lut_1d'], input_values)
    elif lut_data['lut_type'] == '3D':
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    elif lut_data['lut_type'] == 'both':  # Use 3D LUT if both are available
        lut_output = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_rgb)
    else:
        raise ValueError("Cannot determine LUT type.")

    if color_space.lower() == 's-gamut3':
        transformed_rgb = s_gamut3_to_rec709(lut_output)
    elif color_space.lower() == 's-gamut3.cine':
        transformed_rgb = s_gamut3_cine_to_rec709(lut_output)
    else:
        raise ValueError("Invalid color_space. Choose 's-gamut3' or 's-gamut3.cine'.")

    # Apply Rec.709 OETF
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Calculate luminance
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    luminance = np.clip(luminance, 0, 1)

    # Convert to percentages
    input_percent = input_values * 100
    rec709_percent = rec709_oetf(input_linear) * 100  # Using input_linear for Rec709
    lut_percent = luminance * 100

    table = np.column_stack([exposure_percentages, input_percent, rec709_percent, lut_percent])
    return table
