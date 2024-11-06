import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def select_cube_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    filetypes = [("Cube files", "*.cube"), ("All files", "*.*")]
    filename = filedialog.askopenfilename(title="Select .cube file", filetypes=filetypes)
    root.destroy()
    return filename


def select_color_space():
    print("Select the color space you are using:")
    print("1: S-Gamut3/S-Log3")
    print("2: S-Gamut3.Cine/S-Log3")
    choice = input("Enter 1 or 2: ")
    if choice == '1':
        return 'S-Gamut3'
    elif choice == '2':
        return 'S-Gamut3.Cine'
    else:
        print("Invalid selection. Defaulting to S-Gamut3.")
        return 'S-Gamut3'


def load_cube_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', or 'both'

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    for line in lines:
        stripped_line = line.strip()
        if any(stripped_line.startswith(keyword) for keyword in keywords):
            if 'LUT_1D_SIZE' in stripped_line:
                lut_1d_size = int(stripped_line.split()[-1])
                if lut_type == '3D':
                    lut_type = 'both'
                else:
                    lut_type = '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                lut_3d_size = int(stripped_line.split()[-1])
                if lut_type == '1D':
                    lut_type = 'both'
                else:
                    lut_type = '3D'
            continue  # Skip header lines
        else:
            # LUT data
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) == 3:
                    if lut_type == '1D' and len(lut_1d) < lut_1d_size:
                        lut_1d.append(values)
                    elif lut_type == 'both' and len(lut_1d) < lut_1d_size:
                        lut_1d.append(values)
                    else:
                        lut_3d.append(values)
            except ValueError:
                continue  # Skip lines that cannot be converted to float
    return {
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d),
        'lut_3d': np.array(lut_3d)
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
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    lut_output = lut_1d[:, 0]  # Assuming R=G=B
    output_values = np.interp(input_values, lut_input, lut_output)
    return output_values


def interpolate_3d_lut(lut_3d, lut_size, input_values):
    from scipy.interpolate import RegularGridInterpolator

    # Create input grid for R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Reshape lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Prepare input points where R=G=B
    input_points = np.array([[v, v, v] for v in input_values])

    # Interpolate values
    output_values = interpolator(input_points)

    # Assuming R=G=B, take the first channel
    return output_values[:, 0]


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


def generate_table(lut_filename, color_space):
    # Load LUT
    lut_data = load_cube_file(lut_filename)

    # Define exposure values
    exposure_percentages = list(range(1, 100, 5))  # From 1% to 99% in steps of 5%
    L_values = np.array([p / 100.0 for p in exposure_percentages])

    # Calculate S-Log3 values
    V_slog3 = slog3_curve(L_values)  # Values between 0 and 1

    # Convert S-Log3 to linear light
    L_linear = inverse_slog3_curve(V_slog3)

    # Interpolate LUT values
    if lut_data['lut_type'] == '1D' or lut_data['lut_type'] == 'both':
        lut_1d = lut_data['lut_1d']
        # Input to LUT is S-Log3 values
        V_lut = interpolate_1d_lut(lut_1d, V_slog3)
    elif lut_data['lut_type'] == '3D':
        lut_3d = lut_data['lut_3d']
        lut_size = lut_data['lut_3d_size']
        V_lut = interpolate_3d_lut(lut_3d, lut_size, V_slog3)
    else:
        print("Cannot determine LUT type.")
        return

    # Convert LUT output (in S-Log3) back to linear light
    V_lut_linear = inverse_slog3_curve(V_lut)

    # Since we're working with grayscale values, we need to create RGB triplets
    rgb_values = np.stack([V_lut_linear, V_lut_linear, V_lut_linear], axis=-1)

    if color_space == 'S-Gamut3':
        transformed_rgb = s_gamut3_to_rec709(rgb_values)
    elif color_space == 'S-Gamut3.Cine':
        transformed_rgb = s_gamut3_cine_to_rec709(rgb_values)
    else:
        print("Unknown color space. No transformation applied.")
        transformed_rgb = rgb_values  # No transformation

    # Apply gamma encoding (Rec.709 OETF)
    transformed_rgb_gamma = rec709_oetf(transformed_rgb)

    # Calculate luminance from transformed RGB values
    # Use Rec.709 luminance coefficients: Y = 0.2126 R + 0.7152 G + 0.0722 B
    luminance = (0.2126 * transformed_rgb_gamma[:, 0] +
                 0.7152 * transformed_rgb_gamma[:, 1] +
                 0.0722 * transformed_rgb_gamma[:, 2])

    # Ensure luminance values are within [0,1]
    luminance = np.clip(luminance, 0, 1)

    # Convert values to percentages
    V_slog3_percent = V_slog3 * 100
    V_rec709_percent = rec709_oetf(L_linear) * 100
    V_lut_percent = luminance * 100

    # Create the table
    data = {
        'Exposure (%)': exposure_percentages,
        'S-Log3 (%)': V_slog3_percent,
        'Rec.709 (%)': V_rec709_percent,
        'Your LUT (%)': V_lut_percent,
        'Color Space': [color_space] * len(exposure_percentages)
    }
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # Select color space
    color_space = select_color_space()

    # Select LUT file
    lut_filename = select_cube_file()

    if lut_filename:
        tabela = generate_table(lut_filename, color_space)
        if tabela is not None:
            print(tabela)
            # Optionally save the table to a CSV file
            tabela.to_csv('comparison_table.csv', index=False)
    else:
        print("No file selected.")
