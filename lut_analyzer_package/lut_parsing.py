# -*- coding: utf-8 -*-
"""
Moduł odpowiedzialny za wczytywanie i parsowanie plików LUT, np. w formacie .cube.
"""

import numpy as np
from typing import Dict, List # For type hinting

def load_cube_file(filename: str) -> Dict:
    """
    Loads a .cube LUT file, parsing its header and data.

    Handles 1D, 3D, and combined LUTs.

    Args:
        filename (str): Path to the .cube file.

    Returns:
        dict: A dictionary containing LUT metadata and data:
              'title': str or None
              'lut_type': '1D', '3D', or 'both'
              'lut_1d_size': int or None
              'lut_3d_size': int or None
              'lut_1d': np.ndarray (Nx3) or empty array
              'lut_3d': np.ndarray (Mx3) or empty array
              'domain_min': list[float]
              'domain_max': list[float]

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid or inconsistent.
        IOError: If there's an error reading the file.
    """
    try:
        # Use 'iso-8859-1' as a fallback if utf-8 fails, common for some LUTs
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            print(f"Warning: UTF-8 decoding failed for {filename}, trying ISO-8859-1.")
            with open(filename, 'r', encoding='iso-8859-1') as file:
                lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except Exception as e:
        raise IOError(f"Error opening or reading file {filename}: {e}")

    # Remove comments and empty lines, handle potential BOM
    lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
    if lines and lines[0].startswith('\ufeff'): # Handle UTF-8 BOM
        lines[0] = lines[0][1:]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None
    title = None
    domain_min = [0.0, 0.0, 0.0] # Default domain
    domain_max = [1.0, 1.0, 1.0] # Default domain

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']
    data_lines = []
    in_data_section = False
    header_lines = 0

    for line_number, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if not stripped_line: continue # Skip truly empty lines after strip

        parts = stripped_line.split()
        if not parts: continue # Skip lines that become empty after split

        if not in_data_section:
            header_lines += 1
            if parts[0] in keywords:
                if len(parts) < 2:
                    raise ValueError(f"Invalid keyword format in line {line_number}: {line}")

                keyword = parts[0]
                value_str = " ".join(parts[1:])

                if keyword == 'TITLE':
                    title = value_str.strip('"')
                elif keyword == 'LUT_1D_SIZE':
                    try:
                        lut_1d_size = int(value_str)
                        if lut_1d_size < 2:
                             raise ValueError("LUT_1D_SIZE must be at least 2")
                    except ValueError:
                        raise ValueError(f"Invalid LUT_1D_SIZE value in line {line_number}: {line}")
                    if lut_type == '3D':
                        lut_type = 'both'
                    else:
                        lut_type = '1D'
                elif keyword == 'LUT_3D_SIZE':
                    try:
                        lut_3d_size = int(value_str)
                        if lut_3d_size < 2:
                             raise ValueError("LUT_3D_SIZE must be at least 2")
                    except ValueError:
                        raise ValueError(f"Invalid LUT_3D_SIZE value in line {line_number}: {line}")
                    if lut_type == '1D':
                        lut_type = 'both'
                    else:
                        lut_type = '3D'
                elif keyword == 'DOMAIN_MIN':
                    try:
                        domain_min = [float(v) for v in parts[1:]]
                        if len(domain_min) != 3: raise ValueError()
                    except (ValueError, IndexError):
                         raise ValueError(f"Invalid DOMAIN_MIN format in line {line_number}: {line}")
                elif keyword == 'DOMAIN_MAX':
                    try:
                        domain_max = [float(v) for v in parts[1:]]
                        if len(domain_max) != 3: raise ValueError()
                    except (ValueError, IndexError):
                         raise ValueError(f"Invalid DOMAIN_MAX format in line {line_number}: {line}")
            else:
                # First line that is not a keyword is assumed to be data
                try:
                    # Check if it looks like data (3 floats)
                    _ = [float(v) for v in parts]
                    if len(_) != 3:
                        raise ValueError("Expected 3 float values")
                    in_data_section = True
                    data_lines.append(stripped_line)
                    header_lines -= 1 # This line was actually data
                except ValueError:
                    # If it's not a keyword and not valid data, raise error
                    raise ValueError(f"Unexpected content or invalid data format in line {line_number}: {line}")
        else:
             # Already in data section, just append
             data_lines.append(stripped_line)

    # --- Process Data Lines ---
    if not lut_type:
        # If only data lines were found, try to infer type (less reliable)
        if len(data_lines) in [16, 32, 33, 64, 65, 128, 129]: # Common 1D sizes
             print(f"Warning: LUT type not specified in header. Assuming 1D LUT based on {len(data_lines)} data points.")
             lut_1d_size = len(data_lines)
             lut_type = '1D'
        elif len(data_lines) in [16**3, 17**3, 32**3, 33**3, 64**3, 65**3]: # Common 3D sizes
             size_guess = round(len(data_lines)**(1/3))
             if size_guess**3 == len(data_lines):
                 print(f"Warning: LUT type not specified in header. Assuming 3D LUT (size {size_guess}) based on {len(data_lines)} data points.")
                 lut_3d_size = size_guess
                 lut_type = '3D'
             else:
                 raise ValueError("LUT type (1D or 3D) could not be determined from the header or data count.")
        else:
             raise ValueError("LUT type (1D or 3D) could not be determined from the header or data count.")


    expected_1d_count = lut_1d_size if lut_1d_size else 0
    expected_3d_count = lut_3d_size**3 if lut_3d_size else 0
    total_expected = expected_1d_count + expected_3d_count

    if len(data_lines) != total_expected:
         # Allow for common case where 1D LUT is shaper and 3D follows immediately
         if lut_type == 'both' and len(data_lines) == expected_1d_count + expected_3d_count:
             pass # This is expected for 'both'
         else:
             raise ValueError(f"Incorrect number of data entries. Expected {total_expected} for type '{lut_type}', got {len(data_lines)}")

    line_offset = header_lines # For accurate error reporting line numbers

    for i, line in enumerate(data_lines):
        line_number = i + 1 + line_offset
        try:
            values = [float(v) for v in line.split()]
            if len(values) != 3:
                raise ValueError("Expected 3 float values")

            # Prioritize filling 1D LUT if 'both' or '1D'
            if lut_type in ('1D', 'both') and len(lut_1d) < expected_1d_count:
                lut_1d.append(values)
            # Then fill 3D LUT if 'both' or '3D'
            elif lut_type in ('3D', 'both') and len(lut_3d) < expected_3d_count:
                 lut_3d.append(values)
            else:
                 # This should ideally not be reached if counts match
                 raise ValueError("More data found than expected or inconsistent state.")

        except ValueError as e:
            raise ValueError(f"Error parsing data in line {line_number}: {e} ('{line}')")

    # Final check after parsing all data lines
    if lut_type in ('1D', 'both') and len(lut_1d) != expected_1d_count:
         raise ValueError(f"Final check failed: Expected {expected_1d_count} 1D entries, got {len(lut_1d)}")
    if lut_type in ('3D', 'both') and len(lut_3d) != expected_3d_count:
         raise ValueError(f"Final check failed: Expected {expected_3d_count} 3D entries, got {len(lut_3d)}")


    return {
        'title': title,
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d, dtype=np.float32),
        'lut_3d': np.array(lut_3d, dtype=np.float32),
        'domain_min': domain_min,
        'domain_max': domain_max,
    }
