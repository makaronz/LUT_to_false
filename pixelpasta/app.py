# app.py - Główny plik aplikacji Flask

import os
import io
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
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

@app.route('/api/analyze', methods=['POST'])
def analyze_lut():
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
        global last_analysis_results, last_comparison_table
        last_comparison_table = comparison_table
        
        # Przygotowanie danych do zwrócenia
        exposure_percentages = comparison_table['Exposure (%)'].tolist()
        slog3_percentages = comparison_table['S-Log3 (%)'].tolist()
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
            'slog3_percentages': slog3_percentages,
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

@app.route('/api/download/csv', methods=['GET'])
def download_csv():
    global last_comparison_table
    
    if last_comparison_table is None:
        return jsonify({'error': 'Brak danych do pobrania'}), 400
    
    try:
        # Utworzenie pliku CSV w pamięci
        csv_data = io.StringIO()
        last_comparison_table.to_csv(csv_data, index=False)
        
        # Przygotowanie odpowiedzi
        mem = io.BytesIO()
        mem.write(csv_data.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name='lut_analysis.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/pdf', methods=['GET'])
def download_pdf():
    global last_analysis_results
    
    if last_analysis_results is None:
        return jsonify({'error': 'Brak danych do pobrania'}), 400
    
    try:
        # Zapisz logi błędów do pliku
        import traceback
        import sys
        with open('pdf_error.log', 'w') as f:
            f.write('Rozpoczęcie generowania PDF\n')
            
        # Dodajmy więcej logów
        try:
            # Utworzenie wykresu
            with open('pdf_error.log', 'a') as f:
                f.write('Tworzenie wykresu...\n')
        # Utworzenie wykresu
        plt.figure(figsize=(10, 6))
        
        exposure = last_analysis_results['exposure_percentages']
        slog3 = last_analysis_results['slog3_percentages']
        rec709 = last_analysis_results['rec709_percentages']
        lut = last_analysis_results['lut_percentages']
        
        plt.plot(exposure, slog3, label='S-Log3', color='blue')
        plt.plot(exposure, rec709, label='Rec.709', color='red')
        plt.plot(exposure, lut, label='Twój LUT', color='green')
        
        plt.title('Porównanie krzywych tonalnych')
        plt.xlabel('Ekspozycja (%)')
        plt.ylabel('Wartość wyjściowa (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Zapisanie wykresu do pamięci
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', dpi=100, bbox_inches='tight')
        img_data.seek(0)
        plt.close()
        
        # Utworzenie PDF z wykresem i tabelą
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib.units import inch
        from PIL import Image
        
        # Przygotowanie danych do tabeli
        table_data = [['Ekspozycja (%)', 'S-Log3 (%)', 'Rec.709 (%)', 'Twój LUT (%)']]
        for i in range(len(exposure)):
            table_data.append([
                str(exposure[i]),
                f"{slog3[i]:.2f}",
                f"{rec709[i]:.2f}",
                f"{lut[i]:.2f}"
            ])
        
        # Utworzenie PDF w pamięci
        pdf_data = io.BytesIO()
        c = canvas.Canvas(pdf_data, pagesize=letter)
        width, height = letter
        
        # Dodanie tytułu
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, height - inch, "Analiza LUT - Raport")
        
        # Dodanie informacji o LUT
        c.setFont("Helvetica", 12)
        y_position = height - 1.5 * inch
        lut_info = last_analysis_results['lut_info']
        
        c.drawString(inch, y_position, f"Nazwa pliku: {lut_info['filename']}")
        y_position -= 20
        c.drawString(inch, y_position, f"Typ LUT: {lut_info['lut_type']}")
        y_position -= 20
        c.drawString(inch, y_position, f"Przestrzeń barwna: {lut_info['color_space']}")
        y_position -= 40
        
        # Dodanie wykresu
        img = Image.open(img_data)
        img_width, img_height = img.size
        aspect = img_height / float(img_width)
        display_width = width - 2 * inch
        display_height = display_width * aspect
        
        c.drawImage(img_data, inch, y_position - display_height, width=display_width, height=display_height)
        y_position -= display_height + 40
        
        # Dodanie tabeli
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_position, "Tabela porównawcza:")
        y_position -= 30
        
        # Utworzenie tabeli
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Rysowanie tabeli
        table.wrapOn(c, width, height)
        table.drawOn(c, inch, y_position - table._height)
        
        # Dodanie stopki
        c.setFont("Helvetica", 10)
        c.drawString(inch, inch, "Wygenerowano przez PixelPasta")
        c.drawRightString(width - inch, inch, "Strona 1 z 1")
        
        c.save()
        pdf_data.seek(0)
        
        return send_file(
            pdf_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='lut_analysis.pdf'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
