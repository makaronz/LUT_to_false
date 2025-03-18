import numpy as np

def load_cube_file(filename):
    """
    Wczytuje plik .CUBE i zwraca dane LUT.
    
    Args:
        filename (str): Ścieżka do pliku .CUBE
        
    Returns:
        dict: Słownik zawierający dane LUT
    """
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Usunięcie komentarzy i pustych linii
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', lub 'both'
    title = None
    domain_min = [0, 0, 0]
    domain_max = [1, 1, 1]

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    for line in lines:
        stripped_line = line.strip()
        if any(stripped_line.startswith(keyword) for keyword in keywords):
            if 'TITLE' in stripped_line:
                title = stripped_line.split('TITLE')[-1].strip()
            elif 'DOMAIN_MIN' in stripped_line:
                values = stripped_line.split('DOMAIN_MIN')[-1].strip().split()
                domain_min = [float(v) for v in values]
            elif 'DOMAIN_MAX' in stripped_line:
                values = stripped_line.split('DOMAIN_MAX')[-1].strip().split()
                domain_max = [float(v) for v in values]
            elif 'LUT_1D_SIZE' in stripped_line:
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
            continue  # Pominięcie linii nagłówkowych
        else:
            # Dane LUT
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
                continue  # Pominięcie linii, które nie mogą być przekształcone na float
    
    return {
        'title': title,
        'domain_min': domain_min,
        'domain_max': domain_max,
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d) if lut_1d else None,
        'lut_3d': np.array(lut_3d) if lut_3d else None
    }
