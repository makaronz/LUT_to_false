# -*- coding: utf-8 -*-
import os
import sys
# Dodaję type hint dla Pylance aby pomóc w rozpoznaniu importu
from flask import (Flask, request, render_template, redirect, url_for,  # type: ignore
                   send_from_directory, flash, session)
from werkzeug.utils import secure_filename  # type: ignore
import traceback # For detailed error logging

# Importuj funkcje z naszego pakietu
try:
    from lut_analyzer_package.lut_parsing import load_cube_file
    from lut_analyzer_package.reporting import (compare_lut_to_curve,
                                                plot_lut_vs_curve,
                                                generate_pdf_report)
    from lut_analyzer_package.transfer_functions import * # Import all transfer functions
except ImportError as e:
    print(f"Error importing lut_analyzer_package: {e}", file=sys.stderr)
    print("Ensure the package is in the Python path or installed.", file=sys.stderr)
    sys.exit(1)

# --- Konfiguracja Aplikacji ---
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports' # Where generated reports (png, pdf) will be saved
ALLOWED_EXTENSIONS = {'cube'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
# Potrzebny do flash messages (informacje dla użytkownika)
app.config['SECRET_KEY'] = os.urandom(24)

# Utwórz foldery, jeśli nie istnieją
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# --- Funkcje Pomocnicze ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mapowanie nazw krzywych (jak w merged_lut_analyzer.py)
# Upewnij się, że wszystkie funkcje są zaimportowane z transfer_functions
CURVE_MAP = {name: func for name, func in locals().items() if name.startswith('linear_to_')}
# Dodajmy aliasy, jeśli chcemy
CURVE_MAP.update({
    "gamma22": linear_to_redgamma4,
    "gamma24": linear_to_redgamma3,
    "clog2": linear_to_canonlog2,
    "redipp2odt": linear_to_red_ipp2_odt_approx,
})
# Usuńmy funkcje, które nie są krzywymi (jeśli jakieś się załapały)
CURVE_MAP = {k: v for k, v in CURVE_MAP.items() if callable(v)}


# --- Trasy (Routes) ---
@app.route('/')
def index():
    """Wyświetla główną stronę z formularzem."""
    # Na razie zwraca prosty tekst, później będzie renderować szablon
    # return "Witaj w Pixel Pasta LUT Analyzer!"
    # Przekaż listę dostępnych krzywych do szablonu
    available_curves = sorted(CURVE_MAP.keys())
    return render_template('index.html', curves=available_curves)

@app.route('/analyze', methods=['POST'])
def analyze_lut_route():
    """Obsługuje przesyłanie pliku LUT i uruchamia analizę."""
    if 'lut_file' not in request.files:
        flash('Nie znaleziono części pliku w zapytaniu.', 'error')
        return redirect(request.url)
    file = request.files['lut_file']
    if file.filename == '':
        flash('Nie wybrano pliku.', 'error')
        return redirect(url_for('index')) # Wróć do strony głównej

    curve_name = request.form.get('curve_select', 'slog3') # Pobierz wybraną krzywą

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(upload_path)
            flash(f'Plik {filename} został pomyślnie przesłany.', 'success')

            # --- Uruchomienie Analizy ---
            report_basename = os.path.splitext(filename)[0]
            report_pdf_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".pdf")
            report_png_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".png")

            print(f"Rozpoczynanie analizy dla: {upload_path}, krzywa: {curve_name}")

            lut_data = load_cube_file(upload_path)
            curve_func = CURVE_MAP.get(curve_name)
            if not curve_func:
                 raise ValueError(f"Nieprawidłowa nazwa krzywej: {curve_name}")

            comparison_data = compare_lut_to_curve(lut_data, curve_func)
            plot_title = f"LUT '{lut_data.get('title', filename)}' vs {curve_name.upper()}"
            plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
            generate_pdf_report(lut_data, report_png_path, report_pdf_path)

            print(f"Analiza zakończona. Raporty w: {app.config['REPORTS_FOLDER']}")
            flash('Analiza zakończona pomyślnie!', 'success')

            # Zapisz ścieżki do raportów w sesji, aby wyświetlić je na stronie wyników
            session['report_pdf'] = os.path.basename(report_pdf_path)
            session['report_png'] = os.path.basename(report_png_path)
            session['lut_title'] = lut_data.get('title', filename)

            return redirect(url_for('show_results'))

        except (FileNotFoundError, ValueError, IOError) as e:
            flash(f'Błąd podczas analizy pliku {filename}: {e}', 'error')
            print(f"Błąd analizy: {e}\n{traceback.format_exc()}")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Wystąpił nieoczekiwany błąd: {e}', 'error')
            print(f"Nieoczekiwany błąd: {e}\n{traceback.format_exc()}")
            return redirect(url_for('index'))
        finally:
            # Opcjonalnie: usuń przesłany plik po analizie
            # if os.path.exists(upload_path):
            #     os.remove(upload_path)
            pass

    else:
        flash('Niedozwolony typ pliku. Akceptowane są tylko pliki .cube.', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def show_results():
    """Wyświetla stronę z wynikami analizy."""
    pdf_file = session.get('report_pdf')
    png_file = session.get('report_png')
    lut_title = session.get('lut_title', 'Analiza LUT')

    if not pdf_file or not png_file:
        flash('Brak wyników analizy do wyświetlenia.', 'warning')
        return redirect(url_for('index'))

    return render_template('results.html',
                           lut_title=lut_title,
                           pdf_file=pdf_file,
                           png_file=png_file)

@app.route('/reports/<filename>')
def serve_report(filename):
    """Serwuje wygenerowane pliki raportów (PDF, PNG)."""
    safe_filename = secure_filename(filename) # Dodatkowe zabezpieczenie
    try:
        return send_from_directory(app.config['REPORTS_FOLDER'], safe_filename)
    except FileNotFoundError:
        flash(f'Nie znaleziono pliku raportu: {safe_filename}', 'error')
        return redirect(url_for('index'))


# --- Uruchomienie Aplikacji ---
if __name__ == '__main__':
    # Uruchomienie w trybie debugowania dla łatwiejszego rozwoju
    # W środowisku produkcyjnym użyj serwera WSGI jak gunicorn lub waitress
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
