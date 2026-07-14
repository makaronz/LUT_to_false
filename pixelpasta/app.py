# app.py - Główny plik aplikacji Flask

import os
import io
import tempfile
from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Ustawienie backendu bez GUI
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import numpy as np
from pixelpasta.lut_processor.cube_parser import load_cube_file
from pixelpasta.lut_processor.color_analysis import generate_table

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit 16MB

# Globalne zmienne do przechowywania ostatnich wyników
last_analysis_results = None
last_comparison_table = None

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/api/analyze', methods=['POST', 'GET'])
def analyze_lut():
    global last_analysis_results, last_comparison_table
    # Jeśli to żądanie GET, zwróć ostatnie wyniki analizy
    if request.method == 'GET':
        if last_analysis_results is not None:
            return jsonify(last_analysis_results)
        else:
            return jsonify({'error': 'Brak danych analizy'}), 404
    # Sprawdzenie czy plik został przesłany
    if 'cube-file' not in request.files:
        return jsonify({'error': 'Nie przesłano pliku'}), 400

    file = request.files['cube-file']

    # Sprawdzenie czy plik ma nazwę
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400

    # Sprawdzenie rozszerzenia pliku
    if not file.filename.lower().endswith('.cube'):
        return jsonify({'error': 'Nieprawidłowy format pliku. Wymagany plik .CUBE'}), 400

    # Sprawdzenie czy wybrano przestrzeń barwną
    color_space = request.form.get('color-space')
    if not color_space:
        return jsonify({'error': 'Nie wybrano przestrzeni barwnej'}), 400

    # Zapisanie pliku tymczasowo
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Generowanie tabeli porównawczej
        comparison_table = generate_table(filepath, color_space)

        # Zapisanie wyników do zmiennych globalnych

        last_comparison_table = comparison_table

       # Przygotowanie danych do zwrócenia
        exposure_percentages = comparison_table['Exposure (%)'].tolist()

        #Zmienne do przechowywania danych w zaleznosci od wybranej opcji
        log_percentages = None
        log_label = None

       # Przygotowanie danych do zwrócenia
        exposure_percentages = comparison_table['Exposure (%)'].tolist()

        #Zmienne do przechowywania danych w zaleznosci od wybranej opcji
        log_percentages = None
        log_label = None

        if color_space == "LogC4":
            log_percentages = comparison_table['LogC4 (%)'].tolist()
            log_label = 'LogC4 (%)'
        elif color_space == "LogC":
            log_percentages = comparison_table['LogC (%)'].tolist()
            log_label = 'LogC (%)'
        else:
            log_percentages = comparison_table['S-Log3 (%)'].tolist()
            log_label = 'S-Log3 (%)'

        rec709_percentages = comparison_table['Rec.709 (%)'].tolist()
        lut_percentages = comparison_table['Your LUT (%)'].tolist()

        # Informacje o LUT
        lut_data = load_cube_file(filepath)
        lut_info = {
            'filename': filename,
            'lut_type': lut_data['lut_type'],
            'lut_1d_size': lut_data['lut_1d_size'],
            'lut_3d_size': lut_data['lut_3d_size'],
            'color_space': color_space
        }

        # Przygotowanie odpowiedzi
        last_analysis_results = {
            'exposure_percentages': exposure_percentages,
            'log_percentages': log_percentages,
            'log_label': log_label,
            'rec709_percentages': rec709_percentages,
            'lut_percentages': lut_percentages,
            'lut_info': lut_info
        }
        return jsonify(last_analysis_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Usunięcie pliku tymczasowego
        if os.path.exists(filepath):
            os.remove(filepath)


# Trasa testowa do demonstracji
@app.route('/test')
def test():
    global last_analysis_results, last_comparison_table
    # Użyj przykładowego pliku LUT
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'example.cube')

    if not os.path.exists(filepath):
        return jsonify({'error': 'Przykładowy plik LUT nie istnieje'}), 404

    try:
        # Generowanie tabeli porównawczej
        color_space = 'S-Gamut3'
        comparison_table = generate_table(filepath, color_space)

        # Zapisanie wyników do zmiennych globalnych
        last_comparison_table = comparison_table

       # Przygotowanie danych do zwrócenia
        exposure_percentages = comparison_table['Exposure (%)'].tolist()
        log_percentages = None
        log_label = None

       # Przygotowanie danych do zwrócenia
        exposure_percentages = comparison_table['Exposure (%)'].tolist()
        log_percentages = None
        log_label = None

        if color_space == "LogC4":
            log_percentages = comparison_table['LogC4 (%)'].tolist()
            log_label = 'LogC4 (%)'
        elif color_space == 'LogC':
            log_percentages = comparison_table['LogC (%)'].tolist()
            log_label = 'LogC (%)'
        else:
            log_percentages = comparison_table['S-Log3 (%)'].tolist()
            log_label = 'S-Log3 (%)'

        rec709_percentages = comparison_table['Rec.709 (%)'].tolist()
        lut_percentages = comparison_table['Your LUT (%)'].tolist()

        # Informacje o LUT
        lut_data = load_cube_file(filepath)
        lut_info = {
            'filename': 'example.cube',
            'lut_type': lut_data['lut_type'],
            'lut_1d_size': lut_data['lut_1d_size'],
            'lut_3d_size': lut_data['lut_3d_size'],
            'color_space': color_space
        }

        # Przygotowanie odpowiedzi
        last_analysis_results = {
            'exposure_percentages': exposure_percentages,
            'log_percentages': log_percentages,
            'log_label': log_label,
            'rec709_percentages': rec709_percentages,
            'lut_percentages': lut_percentages,
            'lut_info': lut_info
        }

        # Przekierowanie do strony głównej
        return render_template('upload.html')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Debug wyłączony domyślnie; włącz świadomie przez FLASK_DEBUG=1.
    # debug=True udostępnia debugger Werkzeuga (zdalne wykonanie kodu).
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(debug=debug)
