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
    data_started = False  # Flaga wskazująca, czy rozpoczęto wczytywanie danych LUT

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if any(stripped_line.startswith(keyword) for keyword in keywords):
            if 'TITLE' in stripped_line:
                title = stripped_line.split('TITLE')[-1].strip()
            elif 'DOMAIN_MIN' in stripped_line:
                values = stripped_line.split('DOMAIN_MIN')[-1].strip().split()
                try:
                    domain_min = [float(v) for v in values]
                except ValueError:
                    raise ValueError(f"Błąd w linii {line_num}: Nieprawidłowe wartości DOMAIN_MIN")
            elif 'DOMAIN_MAX' in stripped_line:
                values = stripped_line.split('DOMAIN_MAX')[-1].strip().split()
                try:
                    domain_max = [float(v) for v in values]
                except ValueError:
                    raise ValueError(f"Błąd w linii {line_num}: Nieprawidłowe wartości DOMAIN_MAX")
            elif 'LUT_1D_SIZE' in stripped_line:
                if data_started:
                    raise ValueError(f"Błąd w linii {line_num}: LUT_1D_SIZE zadeklarowane po danych LUT")
                try:
                    lut_1d_size = int(stripped_line.split()[-1])
                    if lut_1d_size <= 0:
                        raise ValueError("Rozmiar LUT_1D_SIZE musi być większy od zera")
                except ValueError:
                    raise ValueError(f"Błąd w linii {line_num}: Nieprawidłowa wartość LUT_1D_SIZE")
                if lut_type == '3D':
                    lut_type = 'both'
                else:
                    lut_type = '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                if data_started:
                     raise ValueError(f"Błąd w linii {line_num}: LUT_3D_SIZE zadeklarowane po danych LUT")
                try:
                    lut_3d_size = int(stripped_line.split()[-1])
                    if lut_3d_size <= 0:
                        raise ValueError("Rozmiar LUT_3D_SIZE musi być większy od zera")
                except ValueError:
                    raise ValueError(f"Błąd w linii {line_num}: Nieprawidłowa wartość LUT_3D_SIZE")

                if lut_type == '1D':
                    lut_type = 'both'
                else:
                    lut_type = '3D'
            continue  # Pominięcie linii nagłówkowych
        else:
            # Dane LUT
            data_started = True
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) == 3:
                    if lut_type == '1D' and len(lut_1d) < lut_1d_size:
                        lut_1d.append(values)
                    elif lut_type == 'both' and len(lut_1d) < lut_1d_size:
                        lut_1d.append(values)
                    elif lut_type == '3D' or (lut_type == 'both' and len(lut_1d) == lut_1d_size):
                        lut_3d.append(values)
                    else:
                        raise ValueError("Nieoczekiwane dane LUT")

                else:
                    raise ValueError(f"Błąd w linii {line_num}: Nieprawidłowa liczba wartości")
            except ValueError as e:
                raise ValueError(f"Błąd w linii {line_num}: {e}")

    # Sprawdzenie rozmiaru LUT 3D
    if lut_type in ('3D', 'both'):
        expected_3d_size = lut_3d_size ** 3
        if len(lut_3d) != expected_3d_size:
            raise ValueError(f"Nieprawidłowy rozmiar LUT 3D. Oczekiwano {expected_3d_size} wpisów, otrzymano {len(lut_3d)}")

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
