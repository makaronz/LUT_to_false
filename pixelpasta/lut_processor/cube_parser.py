import numpy as np


def load_cube_file(filename):
    """
    Wczytuje plik .CUBE i zwraca dane LUT.

    Args:
        filename (str): Ścieżka do pliku .CUBE

    Returns:
        dict: Słownik zawierający dane LUT

    Raises:
        ValueError: gdy plik jest pusty, ma nieprawidłowe wartości nagłówków,
            deklaruje rozmiar LUT po danych lub liczba wpisów danych nie zgadza
            się z zadeklarowanym rozmiarem.
    """
    with open(filename, 'r') as file:
        raw_lines = file.readlines()

    # Zachowujemy oryginalne numery linii (1-indeksowane) na potrzeby komunikatów.
    numbered = [
        (i, line.strip())
        for i, line in enumerate(raw_lines, start=1)
        if line.strip() != '' and not line.strip().startswith('#')
    ]

    if not numbered:
        raise ValueError("Plik jest pusty")

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', lub 'both'
    title = None
    domain_min = [0, 0, 0]
    domain_max = [1, 1, 1]
    data_started = False

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE', 'LUT_3D_SIZE']

    for lineno, stripped_line in numbered:
        if any(stripped_line.startswith(keyword) for keyword in keywords):
            if 'TITLE' in stripped_line:
                title = stripped_line.split('TITLE')[-1].strip()
            elif 'DOMAIN_MIN' in stripped_line:
                values = stripped_line.split('DOMAIN_MIN')[-1].strip().split()
                try:
                    domain_min = [float(v) for v in values]
                except ValueError:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowe wartości DOMAIN_MIN"
                    )
            elif 'DOMAIN_MAX' in stripped_line:
                values = stripped_line.split('DOMAIN_MAX')[-1].strip().split()
                try:
                    domain_max = [float(v) for v in values]
                except ValueError:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowe wartości DOMAIN_MAX"
                    )
            elif 'LUT_1D_SIZE' in stripped_line:
                if data_started:
                    raise ValueError(
                        f"Błąd w linii {lineno}: LUT_1D_SIZE zadeklarowane po danych LUT"
                    )
                try:
                    lut_1d_size = int(stripped_line.split()[-1])
                except ValueError:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowa wartość LUT_1D_SIZE"
                    )
                if lut_1d_size < 2:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowa wartość LUT_1D_SIZE"
                    )
                lut_type = 'both' if lut_type == '3D' else '1D'
            elif 'LUT_3D_SIZE' in stripped_line:
                if data_started:
                    raise ValueError(
                        f"Błąd w linii {lineno}: LUT_3D_SIZE zadeklarowane po danych LUT"
                    )
                try:
                    lut_3d_size = int(stripped_line.split()[-1])
                except ValueError:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowa wartość LUT_3D_SIZE"
                    )
                if lut_3d_size < 2:
                    raise ValueError(
                        f"Błąd w linii {lineno}: Nieprawidłowa wartość LUT_3D_SIZE"
                    )
                lut_type = 'both' if lut_type == '1D' else '3D'
            continue  # Pominięcie linii nagłówkowych
        else:
            # Dane LUT — nieparsowalne wartości są błędem, a nie po cichu pomijane.
            try:
                values = [float(v) for v in stripped_line.split()]
            except ValueError as exc:
                raise ValueError(f"Błąd w linii {lineno}: {exc}")
            if len(values) != 3:
                raise ValueError(
                    f"Błąd w linii {lineno}: oczekiwano 3 wartości RGB, otrzymano {len(values)}"
                )
            data_started = True
            if lut_type in ('1D', 'both') and lut_1d_size is not None and len(lut_1d) < lut_1d_size:
                lut_1d.append(values)
            else:
                lut_3d.append(values)

    # Walidacja liczby wpisów względem zadeklarowanych rozmiarów.
    if lut_3d_size is not None:
        expected_3d = lut_3d_size ** 3
        if len(lut_3d) != expected_3d:
            raise ValueError(
                f"Nieprawidłowy rozmiar LUT 3D. Oczekiwano {expected_3d} wpisów, "
                f"otrzymano {len(lut_3d)}"
            )
    if lut_1d_size is not None and lut_type in ('1D', 'both'):
        if len(lut_1d) != lut_1d_size:
            raise ValueError(
                f"Nieprawidłowy rozmiar LUT 1D. Oczekiwano {lut_1d_size} wpisów, "
                f"otrzymano {len(lut_1d)}"
            )

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
