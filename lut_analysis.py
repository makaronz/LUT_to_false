import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def select_cube_file():
    root = tk.Tk()
    root.withdraw()  # Ukryj główne okno Tkinter
    root.update()  # Zaktualizuj okno, aby uniknąć błędów
    filetypes = [("Cube files", "*.cube"), ("All files", "*.*")]
    filename = filedialog.askopenfilename(title="Wybierz plik .cube", filetypes=filetypes)
    root.destroy()  # Zamknij okno Tkinter
    return filename


def load_cube_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Usuwamy komentarze i puste linie
    lines = [line.strip() for line in lines if line.strip() != '' and not line.strip().startswith('#')]

    lut_1d_size = None
    lut_3d_size = None
    lut_1d = []
    lut_3d = []
    lut_type = None  # '1D', '3D', or 'both'

    keywords = ['TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX']

    for line in lines:
        stripped_line = line.strip()
        if any(stripped_line.startswith(keyword) for keyword in keywords):
            continue  # Pomijamy linie z nagłówkami
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
        elif 'LUT_1D_INPUT_RANGE' in stripped_line or 'LUT_3D_INPUT_RANGE' in stripped_line:
            continue  # Pomijamy te linie
        else:
            # Dane LUT
            try:
                values = [float(v) for v in stripped_line.split()]
                if len(values) == 3:
                    lut_3d.append(values)
            except ValueError:
                # Jeśli nie można przekonwertować na float, pomijamy linię
                continue
    return {
        'lut_type': lut_type,
        'lut_1d_size': lut_1d_size,
        'lut_3d_size': lut_3d_size,
        'lut_1d': np.array(lut_1d),
        'lut_3d': np.array(lut_3d)
    }


def slog3_curve(L):
    a = 0.432699
    b = 0.01125000
    c = 0.00873
    d = 0.616596
    e = 3.538812
    f = 0.030001
    V = np.where(L >= b,
                 a * np.log10(L + c) + d,
                 e * L + f)
    return V


def rec709_curve(L):
    V = np.where(L <= 0.018,
                 4.5 * L,
                 1.099 * np.power(L, 0.45) - 0.099)
    return V


def interpolate_3d_lut(lut_3d, lut_size, input_values):
    from scipy.interpolate import RegularGridInterpolator

    # Tworzymy siatkę wartości wejściowych dla R, G i B
    grid = np.linspace(0, 1, lut_size)
    meshgrid = np.meshgrid(grid, grid, grid, indexing='ij')

    # Przygotowujemy punkty siatki
    points = np.stack(meshgrid, -1).reshape(-1, 3)

    # Wartości LUT
    values = lut_3d.reshape(-1, 3)

    # Tworzymy interpolator
    interpolator = RegularGridInterpolator((grid, grid, grid), values.reshape(lut_size, lut_size, lut_size, 3),
                                           bounds_error=False, fill_value=None)

    # Ponieważ interesują nas wartości dla ekspozycji szarości (gdzie R=G=B), przygotowujemy punkty wejściowe
    input_points = np.array([[v, v, v] for v in input_values])

    # Interpolujemy wartości
    output_values = interpolator(input_points)

    # Zakładamy, że R=G=B, więc bierzemy pierwszy kanał
    return output_values[:, 0]


def generate_table(lut_filename):
    # Wczytujemy LUT
    lut_data = load_cube_file(lut_filename)

    # Definiujemy wartości ekspozycji
    exposure_percentages = list(range(1, 100, 5))  # Od 1% do 99% co 5%
    L_values = np.array([p / 100.0 for p in exposure_percentages])

    # Obliczamy S-Log3
    V_slog3 = slog3_curve(L_values) * 100  # Konwertujemy na procenty

    # Obliczamy Rec.709
    V_rec709 = rec709_curve(L_values) * 100  # Konwertujemy na procenty

    if lut_data['lut_type'] == '1D' or lut_data['lut_type'] == 'both':
        lut_1d = lut_data['lut_1d']
        # Interpolujemy wartości z 1D LUT
        V_lut = interpolate_1d_lut(lut_1d, L_values) * 100  # Konwertujemy na procenty
    elif lut_data['lut_type'] == '3D':
        lut_3d = lut_data['lut_3d']
        lut_size = lut_data['lut_3d_size']
        # Interpolujemy wartości z 3D LUT
        V_lut = interpolate_3d_lut(lut_3d, lut_size, L_values) * 100  # Konwertujemy na procenty
    else:
        print("Nie można określić typu LUT.")
        return

    # Tworzymy tabelę
    data = {
        'Ekspozycja (%)': exposure_percentages,
        'S-Log3 (%)': V_slog3,
        'Rec.709 (%)': V_rec709,
        'Twój LUT (%)': V_lut,
        # 'Kolor False Color (Sony Venice 1)': [...]  # Jeśli dodasz te dane
    }
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # Wywołujemy funkcję do wyboru pliku
    lut_filename = select_cube_file()

    if lut_filename:
        tabela = generate_table(lut_filename)
        if tabela is not None:
            print(tabela)
            # Opcjonalnie zapisz tabelę do pliku CSV
            tabela.to_csv('tabela_porownawcza.csv', index=False)
    else:
        print("Nie wybrano pliku.")
