# app.py - Główny plik aplikacji Flask

import os
import io
import tempfile
import json
from flask import Flask, render_template, request, jsonify, Response
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Ustawienie backendu bez GUI
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import numpy as np
from pixelpasta.lut_processor.cube_parser import load_cube_file
from pixelpasta.lut_processor.color_analysis import generate_table

# Load environment variables and configure Gemini API
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Streams Gemini model responses about the analyzed LUT data."""
    data = request.get_json() or {}
    message = data.get('message', '')
    history = data.get('history', [])

    global last_analysis_results
    context_text = ""
    if last_analysis_results is not None:
        lut_info = last_analysis_results['lut_info']
        exposure = last_analysis_results['exposure_percentages']
        log = last_analysis_results['log_percentages']
        log_label = last_analysis_results['log_label']
        rec709 = last_analysis_results['rec709_percentages']
        lut = last_analysis_results['lut_percentages']
        
        context_text = f"Analyzed LUT File: {lut_info['filename']} ({lut_info['lut_type']}, camera space: {lut_info['color_space']}).\n"
        context_text += f"Measurement values (Exposure % -> {log_label} -> Rec709 % -> Output LUT %):\n"
        for i in range(len(exposure)):
            context_text += f"- {exposure[i]}% exp -> {log[i]:.2f}% -> Rec709 {rec709[i]:.2f}% -> LUT {lut[i]:.2f}%\n"

    # Configure Gemini API Key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        def error_gen():
            yield "data: " + json.dumps({
                "type": "FINAL_RESPONSE",
                "content": "⚠️ Błąd: Brak klucza API Gemini w konfiguracji środowiska serwera. Skonfiguruj klucz `GOOGLE_API_KEY` lub `GEMINI_API_KEY` w pliku `.env` projektu."
            }) + "\n\n"
            yield "data: [DONE]\n\n"
        return Response(error_gen(), mimetype='text/event-stream')

    try:
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are a professional LUT and color space analysis assistant for colorists and filmmakers. "
            "Your name is PixelPasta. Answer questions about the analyzed LUT based on the provided technical measurements (exposure and output percentage values).\n"
            "Analyze and explain curves, contrast, highlight clipping, deep shadows, and color behavior based on this data. "
            "If no LUT was analyzed yet, invite the user to upload a LUT.\n"
            "Be precise, professional, and highly technical.\n"
            "Respond in Polish (as requested by the user), but keep technical terms (clipping, EV, Rec.709, S-Log3, etc.) correct."
        )
        if context_text:
            system_instruction += f"\n\nHere is the detailed technical measurement data for the currently analyzed LUT:\n{context_text}\n"

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction
        )

        # Convert history format
        contents = []
        for msg in history:
            role = 'user' if msg.get('role') == 'user' else 'model'
            contents.append({'role': role, 'parts': [msg.get('content', '')]})

        contents.append({'role': 'user', 'parts': [message]})

        def sse_generator():
            yield "data: " + json.dumps({"type": "THOUGHT", "content": "Analizuję pytanie..."}) + "\n\n"
            yield "data: " + json.dumps({"type": "THOUGHT", "content": "Przetwarzam pomiary pliku LUT..."}) + "\n\n"
            
            try:
                response_stream = model.generate_content(contents, stream=True)
                yield "data: " + json.dumps({"type": "THOUGHT", "content": "Generuję odpowiedź..."}) + "\n\n"
                
                for chunk in response_stream:
                    if chunk.text:
                        yield "data: " + json.dumps({"type": "FINAL_RESPONSE", "content": chunk.text}) + "\n\n"
            except Exception as inner_e:
                yield "data: " + json.dumps({"type": "FINAL_RESPONSE", "content": f"\n\n⚠️ Błąd generowania Gemini: {str(inner_e)}"}) + "\n\n"

            # Dynamic suggestions based on context
            suggestions = [
                "Czy ten LUT przycina pasma świateł?",
                "Jaki jest kontrast tego LUT-a w cieniach?",
                "Jak ten LUT różni się od referencyjnego Rec.709?"
            ]
            for s in suggestions:
                yield "data: " + json.dumps({"type": "SUGGESTION", "content": s}) + "\n\n"

            yield "data: [DONE]\n\n"

        return Response(sse_generator(), mimetype='text/event-stream')
    except Exception as e:
        def error_gen():
            yield "data: " + json.dumps({"type": "FINAL_RESPONSE", "content": f"⚠️ Błąd inicjalizacji Gemini: {str(e)}"}) + "\n\n"
            yield "data: [DONE]\n\n"
        return Response(error_gen(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Debug wyłączony domyślnie; włącz świadomie przez FLASK_DEBUG=1.
    # debug=True udostępnia debugger Werkzeuga (zdalne wykonanie kodu).
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(debug=debug)
