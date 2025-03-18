# app.py - Główny plik aplikacji Flask

import os
import io
import tempfile
from flask import Flask, render_template, request, jsonify, send_file, session
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Ustawienie backendu bez GUI, dodany komentarz
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import numpy as np
from pixelpasta.lut_processor.cube_parser import load_cube_file
from pixelpasta.lut_processor.color_analysis import generate_table
import traceback
import sys

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit 16MB
app.secret_key = os.urandom(24) # Generowanie losowego klucza sesji

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/api/analyze', methods=['POST', 'GET'])
def analyze_lut():
    # Użycie sesji do przechowywania danych
    if request.method == 'GET':
        if 'last_analysis_results' in session:
            return jsonify(session['last_analysis_results'])
        else:
            return jsonify({'error': 'Brak danych analizy'}), 404

    if 'cube-file' not in request.files:
        return jsonify({'error': 'Nie przesłano pliku'}), 400
    
    file = request.files['cube-file']
    
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if not file.filename.lower().endswith('.cube'):
        return jsonify({'error': 'Nieprawidłowy format pliku. Wymagany plik .CUBE'}), 400

    # Dodatkowa walidacja zawartości pliku .cube
    content = file.read().decode('utf-8', errors='ignore')  # Dekodowanie z ignorowaniem błędów
    if not any(keyword in content for keyword in ['TITLE', 'LUT_1D_SIZE', 'LUT_3D_SIZE']):
        return jsonify({'error': 'Nieprawidłowy plik .CUBE - brak wymaganych słów kluczowych'}), 400
    file.seek(0)  # Powrót na początek pliku

    color_space = request.form.get('color-space')
    if not color_space:
        return jsonify({'error': 'Nie wybrano przestrzeni barwnej'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        comparison_table = generate_table(filepath, color_space)
        
        exposure_percentages = comparison_table['Exposure (%)'].tolist()
        slog3_percentages = comparison_table['S-Log3 (%)'].tolist()
        rec709_percentages = comparison_table['Rec.709 (%)'].tolist()
        lut_percentages = comparison_table['Your LUT (%)'].tolist()
        
        lut_data = load_cube_file(filepath)
        lut_info = {
            'filename': filename,
            'lut_type': lut_data['lut_type'],
            'lut_1d_size': lut_data['lut_1d_size'],
            'lut_3d_size': lut_data['lut_3d_size'],
            'color_space': color_space
        }
        
        session['last_analysis_results'] = {
            'exposure_percentages': exposure_percentages,
            'slog3_percentages': slog3_percentages,
            'rec709_percentages': rec709_percentages,
            'lut_percentages': lut_percentages,
            'lut_info': lut_info
        }
        session['last_comparison_table'] = comparison_table.to_dict(orient='records') # Zapis do sesji jako lista słowników
        
        return jsonify(session['last_analysis_results'])
    
    except ValueError as ve:
        return jsonify({'error': f'Błąd wartości: {str(ve)}'}), 400
    except KeyError as ke:
        return jsonify({'error': f'Brak klucza: {str(ke)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Nieoczekiwany błąd: {str(e)}'}), 500
    
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/api/download/csv', methods=['GET'])
def download_csv():
    if 'last_comparison_table' not in session:
        return jsonify({'error': 'Brak danych do pobrania'}), 400
    
    try:
        comparison_table = pd.DataFrame(session['last_comparison_table']) # Odczyt z sesji
        csv_data = io.StringIO()
        comparison_table.to_csv(csv_data, index=False)
        
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
    if 'last_analysis_results' not in session:
        return jsonify({'error': 'Brak danych do pobrania'}), 400
    
    try:
        plt.figure(figsize=(10, 6))
            
        exposure = session['last_analysis_results']['exposure_percentages']
        slog3 = session['last_analysis_results']['slog3_percentages']
        rec709 = session['last_analysis_results']['rec709_percentages']
        lut = session['last_analysis_results']['lut_percentages']
            
        plt.plot(exposure, slog3, label='S-Log3', color='blue')
        plt.plot(exposure, rec709, label='Rec.709', color='red')
        plt.plot(exposure, lut, label='Twój LUT', color='green')
        
        plt.title('Porównanie krzywych tonalnych')
        plt.xlabel('Ekspozycja (%)')
        plt.ylabel('Wartość wyjściowa (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', dpi=100, bbox_inches='tight')
        img_data.seek(0)
        plt.close()
        
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib.units import inch
        from PIL import Image
        
        table_data = [['Ekspozycja (%)', 'S-Log3 (%)', 'Rec.709 (%)', 'Twój LUT (%)']]
        for i in range(len(exposure)):
            table_data.append([
                str(exposure[i]),
                f"{slog3[i]:.2f}",
                f"{rec709[i]:.2f}",
                f"{lut[i]:.2f}"
            ])
        
        pdf_data = io.BytesIO()
        c = canvas.Canvas(pdf_data, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, height - inch, "Analiza LUT - Raport")
        
        c.setFont("Helvetica", 12)
        y_position = height - 1.5 * inch
        lut_info = session['last_analysis_results']['lut_info']
        
        c.drawString(inch, y_position, f"Nazwa pliku: {lut_info['filename']}")
        y_position -= 20
        c.drawString(inch, y_position, f"Typ LUT: {lut_info['lut_type']}")
        y_position -= 20
        c.drawString(inch, y_position, f"Przestrzeń barwna: {lut_info['color_space']}")
        y_position -= 40
        
        img = Image.open(img_data)
        img_width, img_height = img.size
        aspect = img_height / float(img_width)
        display_width = width - 2 * inch
        display_height = display_width * aspect
        
        c.drawImage(img_data, inch, y_position - display_height, width=display_width, height=display_height)
        y_position -= display_height + 40
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_position, "Tabela porównawcza:")
        y_position -= 30
        
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

        table.wrapOn(c, width, height)
        table.drawOn(c, inch, y_position - table._height)
        
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
    app.run(debug=False) # Wyłączenie trybu debugowania
