import numpy as np
import subprocess

def parse_lut_data(file_path):
    """
    Parses a .cube LUT file and returns the LUT size and data as a NumPy array.
    """
    try:
        # Get LUT size
        result = subprocess.run(['head', '-n', '1', file_path], capture_output=True, text=True, check=True)
        line = result.stdout.strip()
        parts = line.split()
        lut_size = int(parts[-1])

        # Extract data lines
        result = subprocess.run(['tail', '-n', '+2', file_path], capture_output=True, text=True, check=True)
        data_lines = result.stdout.strip().split('\n')

        # Parse data into a 3D NumPy array
        lut_data = np.zeros((lut_size, lut_size, lut_size, 3), dtype=np.float64)
        index = 0
        for z in range(lut_size):
            for y in range(lut_size):
                for x in range(lut_size):
                    r, g, b = map(float, data_lines[index].split())
                    lut_data[x, y, z] = [r, g, b]
                    index += 1

        return lut_size, lut_data
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error parsing LUT file: {e}")
        return None, None

def trilinear_interpolation(r, g, b, lut_data, lut_size):
    """
    Performs trilinear interpolation on the given LUT data.
    """
    # Normalize input values to the range 0-(lut_size-1)
    x = r * (lut_size - 1)
    y = g * (lut_size - 1)
    z = b * (lut_size - 1)

    # Get the integer and fractional parts of the coordinates
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    z0 = int(np.floor(z))
    x1 = int(np.ceil(x))
    y1 = int(np.ceil(y))
    z1 = int(np.ceil(z))

    xd = x - x0
    yd = y - y0
    zd = z - z0

    # Handle edge cases where input is exactly on a LUT boundary
    x1 = min(x1, lut_size - 1)
    y1 = min(y1, lut_size - 1)
    z1 = min(z1, lut_size - 1)
    
    # Perform trilinear interpolation
    c000 = lut_data[x0, y0, z0]
    c100 = lut_data[x1, y0, z0]
    c010 = lut_data[x0, y1, z0]
    c110 = lut_data[x1, y1, z0]
    c001 = lut_data[x0, y0, z1]
    c101 = lut_data[x1, y0, z1]
    c011 = lut_data[x0, y1, z1]
    c111 = lut_data[x1, y1, z1]

    c00 = c000 * (1 - xd) + c100 * xd
    c01 = c001 * (1 - xd) + c101 * xd
    c10 = c010 * (1 - xd) + c110 * xd
    c11 = c011 * (1 - xd) + c111 * xd

    c0 = c00 * (1 - yd) + c10 * yd
    c1 = c01 * (1 - yd) + c11 * yd

    c = c0 * (1 - zd) + c1 * zd

    return c

# --- LUT-based LogC4 conversion ---
def arri_logc4_to_linear_lut(log_value, lut_data, lut_size):
    """
    Converts an ARRI LogC4 encoded value to linear using the LUT and trilinear interpolation.
    """
    # Assume grayscale input and use it for all color channels
    r = g = b = log_value
    
    # Perform trilinear interpolation
    interpolated_rgb = trilinear_interpolation(r, g, b, lut_data, lut_size)
    
    # Return the average of the interpolated RGB values (simplification)
    return np.mean(interpolated_rgb)

def linear_to_arri_logc4_lut(linear_value, lut_data, lut_size):
    """
    Converts a linear value to ARRI LogC4 encoded value using a reverse lookup table (simplified).
    """
    # Create a reverse lookup table (LogC4 -> Linear)
    reverse_lookup = {}
    for log_value in np.linspace(0, 1, 1000):  # Sample 1000 LogC4 values
        linear = arri_logc4_to_linear_lut(log_value, lut_data, lut_size)
        reverse_lookup[linear] = log_value

    # Find the closest linear value in the lookup table
    closest_linear = min(reverse_lookup.keys(), key=lambda x: abs(x - linear_value))
    
    # Return the corresponding LogC4 value
    return reverse_lookup[closest_linear]

# --- ARRI LogC4 Functions (from logc4.pdf) ---

# 4.1.1 Encoding Function
def arri_logc4_encode(e_scene):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    if e_scene >= t:
        return (np.log2(a * e_scene + 64) - 6) / 14 * b + c
    else:
        return (e_scene - t) / s

# 4.1.2 Decoding Function
def arri_logc4_decode(e_prime):
    a = (2**18 - 16) / 117.45
    b = (1023 - 95) / 1023
    c = 95 / 1023
    s = (7 * np.log(2) * 2**(7 - 14 * c/b)) / (a * b)
    t = (2**(14 * (-c/b) + 6) - 64) / a

    if e_prime >= 0:
        return (2**(14 * (e_prime - c) / b + 6) - 64) / a
    else:
        return e_prime * s + t

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

# --- Validation Tests ---
if __name__ == "__main__":
    # Load the LUT data
    lut_file = "ARRI_LogC4_v1_LUT_Package/LUTs/ARRI_LogC4-to-Gamma24_Rec709-D65_v1-65.cube"
    lut_size, lut_data = parse_lut_data(lut_file)

    if lut_data is not None:
        # Define test values (linear light values)
        test_values = np.array([0.01, 0.1, 0.5, 1.0, 10.0])

        # Test LogC4 to Linear
        print("Testing LogC4 to Linear:")
        for linear_value in test_values:
            log_value = linear_to_arri_logc4_lut(linear_value, lut_data, lut_size)
            recovered_linear = arri_logc4_to_linear_lut(log_value, lut_data, lut_size)
            print(f"  Linear: {linear_value:.4f}, LogC4: {log_value:.6f}, Recovered: {recovered_linear:.6f}")

        # Test Linear to LogC4
        print("\nTesting Linear to LogC4:")
        for log_value in np.linspace(0, 1, 5):  # Test a few LogC4 values
            linear_value = arri_logc4_to_linear_lut(log_value, lut_data, lut_size)
            recovered_log = linear_to_arri_logc4_lut(linear_value, lut_data, lut_size)
            print(f"  LogC4: {log_value:.4f}, Linear: {linear_value:.6f}, Recovered: {recovered_log:.6f}")
    else:
        print("LUT data could not be loaded. Validation tests skipped.")

    # --- S-Log3 Validation (Approximation) ---
    print("\nTesting S-Log3 Approximation:")
    lut_file_slog3 = "ARRI_LogC4_v1_LUT_Package/LUTs/ARRI_LogC4-to-Gamma24_Rec709-D65_v1-65.cube"
    lut_size_slog3, lut_data_slog3 = parse_lut_data(lut_file_slog3)

    if lut_data_slog3 is not None:
        test_values_linear = np.linspace(0, 1, 10)
        for linear_value in test_values_linear:
            # Encode to S-Log3
            slog3_value = slog3_encode(linear_value)

            # Convert to Rec.709 using the LUT
            rec709_lut = trilinear_interpolation(slog3_value, slog3_value, slog3_value, lut_data_slog3, lut_size_slog3)

            # Convert to Rec.709 directly (gamma 2.4)
            rec709_direct = linear_value**(1/2.4)

            print(f"  Linear: {linear_value:.4f}, S-Log3: {slog3_value:.6f}, Rec.709 (LUT): {rec709_lut[0]:.6f}, Rec.709 (Direct): {rec709_direct:.6f}")
    else:
        print("S-Log3 LUT data could not be loaded. Validation tests skipped.")

    # --- RED Log3G10 Validation (Approximation) ---
    print("\nTesting RED Log3G10 Approximation:")
    lut_file_log3g10 = "ARRI_LogC4_v1_LUT_Package/LUTs/ARRI_LogC4-to-Gamma24_Rec709-D65_v1-65.cube"  # Using LogC4 LUT as a placeholder
    lut_size_log3g10, lut_data_log3g10 = parse_lut_data(lut_file_log3g10)

    if lut_data_log3g10 is not None:
        test_values_linear = np.linspace(0, 1, 10)
        for linear_value in test_values_linear:
            # Encode to Log3G10
            log3g10_value = log3g10_encode(linear_value)

            # Convert to Rec.709 using the LUT (LogC4 LUT used as placeholder)
            rec709_lut = trilinear_interpolation(log3g10_value, log3g10_value, log3g10_value, lut_data_log3g10, lut_size_log3g10)

            # Convert to Rec.709 directly (gamma 2.4)
            rec709_direct = linear_value**(1/2.4)

            print(f"  Linear: {linear_value:.4f}, Log3G10: {log3g10_value:.6f}, Rec.709 (LUT): {rec709_lut[0]:.6f}, Rec.709 (Direct): {rec709_direct:.6f}")
    else:
        print("Log3G10 LUT data could not be loaded. Validation tests skipped.")
