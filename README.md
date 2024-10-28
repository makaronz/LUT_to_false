# LUT Analysis Tool

## Description

The **LUT Analysis Tool** is a Python script that allows you to load a 3D LUT file in the `.cube` format and generate a comparative exposure value table. The table compares exposure values in:

- **S-Log3**
- **Rec.709**
- **Your loaded LUT**

This script is useful for filmmakers and colorists who want to analyze and compare the characteristics of different LUTs and their impact on exposure values.

## Features

- **Loading LUT Files**: Supports `.cube` files containing 1D LUTs, 3D LUTs, or both.
- **Value Interpolation**: Accurate mapping of exposure values through interpolation.
- **Generating Comparative Tables**: Creates a table with exposure values for S-Log3, Rec.709, and your loaded LUT.
- **Saving Results**: Ability to save the table to a CSV file.
- **User Interface**: Simple dialog window for selecting the LUT file.

## Requirements

- **Python 3.x**
- Python Libraries:
  - `numpy`
  - `pandas`
  - `tkinter` (standard with Python)
  - `scipy`

## Installation

1. **Install Python**

   Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install Required Libraries**

   Open a command prompt or terminal and type:

   ```bash
   pip install numpy pandas scipy
   ```

   **Note**: `tkinter` is typically included with Python. If you're using Linux and `tkinter` is not installed, you can install it using:

   ```bash
   sudo apt-get install python3-tk
   ```

## Usage

1. **Download the Script**

   Copy the `lut_analysis.py` script to a chosen folder on your computer.

2. **Run the Script**

   Open a command prompt or terminal in the folder containing the script and run:

   ```bash
   python lut_analysis.py
   ```

3. **Select a LUT File**

   After running the program, a dialog window will appear, allowing you to select a `.cube` file. Choose the LUT file you wish to analyze and click **"Open"**.

4. **Read the Results**

   - The script will generate a comparative table and display it in the console.
   - The table will also be saved to a file named `tabela_porownawcza.csv` in the same folder.

## Sample Table

| Exposure (%) | S-Log3 (%) | Rec.709 (%) | Your LUT (%) |
|--------------|------------|-------------|--------------|
| 1            | 6.54       | 4.50        | 2.20         |
| 5            | 8.70       | 18.60       | 9.80         |
| 10           | 15.23      | 29.05       | 17.60        |
| 15           | 20.26      | 36.92       | 24.00        |
| 20           | 24.34      | 43.33       | 29.50        |
| ...          | ...        | ...         | ...          |
| 95           | 55.19      | 91.88       | 71.80        |
| 99           | 56.33      | 93.86       | 73.00        |

## Additional Information

- **Handling 3D LUTs**: The script supports files containing 3D LUTs through three-dimensional interpolation.
- **Adding False Color Information**: If you have data on assigning colors to exposure values (e.g., for Sony Venice 1), you can add them to the table by modifying the `generate_table` function.

## Troubleshooting

- **Missing `tkinter` Module**:

  Ensure that `tkinter` is installed. On Linux systems, you can install it using:

  ```bash
  sudo apt-get install python3-tk
  ```

- **Errors When Running the Script**:

  - Verify that all required libraries are installed (`numpy`, `pandas`, `scipy`).
  - Ensure that the LUT file is correct and conforms to the specification.

- **Issues with the LUT File**:

  The script supports `.cube` files containing 1D LUTs, 3D LUTs, or both. Make sure your LUT file is valid.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

makaronz


# Narzędzie do Analizy LUT

## Opis

**Narzędzie do Analizy LUT** to skrypt napisany w Pythonie, który pozwala na wczytanie pliku 3D LUT w formacie `.cube` i wygenerowanie tabeli porównawczej wartości ekspozycji. Tabela zawiera porównanie wartości ekspozycji w:

- **S-Log3**
- **Rec.709**
- **Wczytanym przez użytkownika LUT**

Skrypt jest przydatny dla filmowców i kolorystów, którzy chcą analizować i porównywać charakterystykę różnych LUT-ów oraz ich wpływ na wartości ekspozycji.

## Funkcje

- **Wczytywanie plików LUT**: Obsługa plików `.cube` zawierających 1D LUT, 3D LUT lub oba typy.
- **Interpolacja wartości**: Dokładne mapowanie wartości ekspozycji poprzez interpolację.
- **Generowanie tabeli porównawczej**: Tworzenie tabeli z wartościami ekspozycji dla S-Log3, Rec.709 i wczytanego LUT.
- **Zapisywanie wyników**: Możliwość zapisu tabeli do pliku CSV.
- **Interfejs użytkownika**: Proste okno dialogowe do wyboru pliku LUT.

## Wymagania

- **Python 3.x**
- Biblioteki Python:
  - `numpy`
  - `pandas`
  - `tkinter` (standardowo dostępny w Pythonie)
  - `scipy`

## Instalacja

1. **Zainstaluj Pythona**

   Pobierz i zainstaluj Pythona ze strony [python.org](https://www.python.org/downloads/).

2. **Zainstaluj wymagane biblioteki**

   Otwórz wiersz poleceń lub terminal i wpisz:

   ```bash
   pip install numpy pandas scipy
   ```

   **Uwaga**: `tkinter` jest standardowo dostępny w Pythonie. Jeśli jednak korzystasz z systemu Linux i `tkinter` nie jest zainstalowany, możesz go zainstalować poleceniem:

   ```bash
   sudo apt-get install python3-tk
   ```

## Użycie

1. **Pobierz skrypt**

   Skopiuj skrypt `lut_analysis.py` do wybranego folderu na swoim komputerze.

2. **Uruchom skrypt**

   Otwórz wiersz poleceń lub terminal w folderze, w którym znajduje się skrypt, i uruchom:

   ```bash
   python lut_analysis.py
   ```

3. **Wybierz plik LUT**

   Po uruchomieniu programu pojawi się okno dialogowe pozwalające wybrać plik `.cube`. Wskaż plik LUT, który chcesz przeanalizować, i kliknij **"Otwórz"**.

4. **Odczytaj wyniki**

   - Skrypt wygeneruje tabelę porównawczą i wyświetli ją w konsoli.
   - Tabela zostanie również zapisana do pliku `tabela_porownawcza.csv` w tym samym folderze.

## Przykład tabeli

| Ekspozycja (%) | S-Log3 (%) | Rec.709 (%) | Twój LUT (%) |
|----------------|------------|-------------|--------------|
| 1              | 6.54       | 4.50        | 2.20         |
| 5              | 8.70       | 18.60       | 9.80         |
| 10             | 15.23      | 29.05       | 17.60        |
| 15             | 20.26      | 36.92       | 24.00        |
| 20             | 24.34      | 43.33       | 29.50        |
| ...            | ...        | ...         | ...          |
| 95             | 55.19      | 91.88       | 71.80        |
| 99             | 56.33      | 93.86       | 73.00        |

## Dodatkowe informacje

- **Obsługa 3D LUT**: Skrypt obsługuje pliki zawierające 3D LUT poprzez interpolację trójwymiarową.
- **Dodawanie kolorów False Color**: Jeśli posiadasz dane dotyczące przypisania kolorów do wartości ekspozycji (np. dla Sony Venice 1), możesz je dodać do tabeli, modyfikując funkcję `generate_table`.

## Problemy i ich rozwiązania

- **Brak modułu `tkinter`**:

  Upewnij się, że `tkinter` jest zainstalowany. W systemie Linux możesz go zainstalować poleceniem:

  ```bash
  sudo apt-get install python3-tk
  ```

- **Błędy podczas uruchamiania skryptu**:

  - Sprawdź, czy wszystkie wymagane biblioteki są zainstalowane (`numpy`, `pandas`, `scipy`).
  - Upewnij się, że plik LUT jest poprawny i zgodny ze specyfikacją.

- **Problemy z plikiem LUT**:

  Skrypt obsługuje pliki `.cube` zawierające 1D LUT, 3D LUT lub oba typy. Upewnij się, że Twój plik LUT jest poprawny.

## Licencja

Ten projekt jest udostępniany na licencji MIT. Szczegóły licencji znajdują się w pliku `LICENSE`.

## Autor

makaronz
