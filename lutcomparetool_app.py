# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import io
import time
from pathlib import Path

# Adding type hint for Pylance to help with import resolution
from flask import (Flask, request, render_template, redirect, url_for,  # type: ignore
                   send_from_directory, flash, session, send_file, jsonify)
from werkzeug.utils import secure_filename  # type: ignore
import traceback # For detailed error logging
try:
    import numpy as np  # type: ignore
except ImportError as e:
    print(f"Error importing numpy: {e}", file=sys.stderr)
    print("Please install numpy using: pip install numpy==1.26.0", file=sys.stderr)
    sys.exit(1)

# Ustawienie backendu matplotlib na 'Agg' (non-interactive)
# To pozwala na generowanie wykresów bez interfejsu graficznego
import matplotlib
matplotlib.use('Agg')

# Import functions from our package
try:
    from lut_analyzer_package.lut_parsing import load_cube_file
    from lut_analyzer_package.reporting import (compare_lut_to_curve,
                                                plot_lut_vs_curve,
                                                generate_pdf_report,
                                                compare_two_luts,
                                                plot_lut_vs_lut,
                                                generate_comparison_report)
    from lut_analyzer_package.transfer_functions import * # Import all transfer functions
    from lut_analyzer_package.color_space import (s_gamut3_to_rec709,
                                                 s_gamut3_cine_to_rec709,
                                                 arri_wide_gamut4_to_rec709,
                                                 arri_wide_gamut3_to_rec709,
                                                 red_wide_gamut_rgb_to_rec709)
except ImportError as e:
    print(f"Error importing lut_analyzer_package: {e}", file=sys.stderr)
    print("Ensure the package is in the Python path or installed.", file=sys.stderr)
    sys.exit(1)

# --- Application Configuration ---
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports' # Where generated reports (png, pdf) will be saved
BATCH_FOLDER = 'batch_reports' # For batch processing results
ALLOWED_EXTENSIONS = {'cube'}
MAX_BATCH_FILES = 20  # Maximum number of files for batch processing

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['BATCH_FOLDER'] = BATCH_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
# Required for flash messages (user notifications)
app.config['SECRET_KEY'] = os.urandom(24)

# Ustawienie wysokiej precyzji dla obliczeń numerycznych
np.set_printoptions(precision=15)

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(BATCH_FOLDER, exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mapping of curve names to appropriate functions and color spaces
CURVE_INFO = {
    # Sony Curves
    "slog3": {
        "curve_func": linear_to_slog3,
        "inverse_func": slog3_to_linear,
        "color_space": "sgamut3",
        "color_transform": s_gamut3_to_rec709,
        "description": "Sony S-Log3 (S-Gamut3)"
    },
    "slog3_cine": {
        "curve_func": linear_to_slog3_cine,
        "inverse_func": slog3_cine_to_linear,
        "color_space": "sgamut3_cine",
        "color_transform": s_gamut3_cine_to_rec709,
        "description": "Sony S-Log3 (S-Gamut3.cine)"
    },
    "slog2": {
        "curve_func": linear_to_slog2,
        "inverse_func": slog2_to_linear,
        "color_space": "sgamut3",  # Simplified - often used with S-Gamut3
        "color_transform": s_gamut3_to_rec709,
        "description": "Sony S-Log2"
    },
    
    # ARRI Curves
    "logc4": {
        "curve_func": linear_to_logc4,
        "inverse_func": logc4_to_linear,
        "color_space": "arri_wide_gamut4",
        "color_transform": arri_wide_gamut4_to_rec709,
        "description": "ARRI LogC4 (Wide Gamut 4)"
    },
    "logc3": {
        "curve_func": linear_to_logc3,
        "inverse_func": logc3_to_linear,
        "color_space": "arri_wide_gamut3",
        "color_transform": arri_wide_gamut3_to_rec709,
        "description": "ARRI LogC3 (Wide Gamut 3)"
    },
    
    # RED Curves
    "log3g10": {
        "curve_func": linear_to_log3g10,
        "inverse_func": log3g10_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "description": "RED Log3G10"
    },
    "redgamma3": {
        "curve_func": linear_to_redgamma3,
        "inverse_func": redgamma3_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "description": "RED Gamma 3"
    },
    "redgamma4": {
        "curve_func": linear_to_redgamma4,
        "inverse_func": redgamma4_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "description": "RED Gamma 4"
    },
    "redlogfilm": {
        "curve_func": linear_to_redlogfilm,
        "inverse_func": redlogfilm_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "description": "RED Log Film"
    },
    "red_ipp2_odt_approx": {
        "curve_func": linear_to_red_ipp2_odt_approx,
        "inverse_func": red_ipp2_odt_approx_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "description": "RED IPP2 ODT Approximation"
    },
    
    # Other Curves
    "vlog": {
        "curve_func": linear_to_vlog,
        "inverse_func": vlog_to_linear,
        "color_space": "v_gamut",
        "description": "Panasonic V-Log"
    },
    "canonlog2": {
        "curve_func": linear_to_canonlog2,
        "inverse_func": canonlog2_to_linear,
        "color_space": "canon_cinema_gamut",
        "description": "Canon Log 2"
    },
    "rec709": {
        "curve_func": linear_to_rec709,
        "inverse_func": rec709_to_linear,
        "color_space": "rec709",
        "description": "Rec.709"
    }
}

# Aliasy dla zachowania kompatybilności
CURVE_ALIASES = {
    "gamma22": "redgamma4",
    "gamma24": "redgamma3",
    "clog2": "canonlog2",
    "redipp2odt": "red_ipp2_odt_approx"
}

# --- Routes ---
@app.route('/')
def index():
    """Displays the main page with the form."""
    # Pass the list of available curves to the template
    available_curves = sorted(list(CURVE_INFO.keys()) + list(CURVE_ALIASES.keys()))
    return render_template('index.html', curves=available_curves)

@app.route('/batch')
def batch_page():
    """Displays the batch analysis page."""
    available_curves = sorted(CURVE_INFO.keys())
    return render_template('batch.html', curves=available_curves)

@app.route('/compare')
def compare_page():
    """Displays the page for comparing two LUTs."""
    return render_template('compare.html')

@app.route('/analyze', methods=['POST'])
def analyze_lut_route():
    """Handles LUT file upload and initiates the analysis."""
    if 'lut_file' not in request.files:
        flash('No file part found in the request.', 'error')
        return redirect(request.url)
    file = request.files['lut_file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('index')) # Return to the main page

    curve_name = request.form.get('curve_select', 'slog3') # Get the selected curve
    
    # Sprawdzenie aliasów dla zachowania kompatybilności
    if curve_name in CURVE_ALIASES:
        curve_name = CURVE_ALIASES[curve_name]
    
    # Sprawdzenie, czy krzywa istnieje
    if curve_name not in CURVE_INFO:
        flash(f'Invalid curve name: {curve_name}', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(upload_path)
            flash(f'File {filename} was successfully uploaded.', 'success')

            # --- Running Analysis ---
            report_basename = os.path.splitext(filename)[0]
            report_pdf_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".pdf")
            report_png_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".png")

            print(f"Starting analysis for: {upload_path}, curve: {curve_name}")

            lut_data = load_cube_file(upload_path)
            curve_info = CURVE_INFO.get(curve_name)
            
            if not curve_info:
                raise ValueError(f"Invalid curve name: {curve_name}")
            
            # Użyj nowej, precyzyjnej funkcji porównującej
            comparison_data = compare_lut_to_curve(
                lut_data, 
                curve_info["curve_func"],
                use_tetrahedral=True  # Używaj dokładniejszej interpolacji tetrahedral
            )
            
            # Przygotuj dane do tabeli porównawczej
            table_data = []
            input_vals = comparison_data['input_values']
            curve_vals = comparison_data['curve_values']
            lut_vals = comparison_data['lut_values']
            for i in range(len(input_vals)):
                table_data.append({
                    'input': float(input_vals[i]),
                    'curve': float(curve_vals[i]),
                    'lut': float(lut_vals[i]),
                    'delta': float(lut_vals[i] - curve_vals[i])
                })
            session['table_data'] = table_data
            
            plot_title = f"LUT '{lut_data.get('title', filename)}' vs {curve_info['description']}"
            plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
            
            # Użyj pełnej informacji o krzywej w raporcie
            generate_pdf_report(lut_data, report_png_path, report_pdf_path)

            print(f"Analysis completed. Reports in: {app.config['REPORTS_FOLDER']}")
            flash('Analysis completed successfully!', 'success')

            # Save report paths in session to display them on the results page
            session['report_pdf'] = os.path.basename(report_pdf_path)
            session['report_png'] = os.path.basename(report_png_path)
            session['lut_title'] = lut_data.get('title', filename)
            session['curve_name'] = curve_info['description']

            # Serialize numpy arrays in comparison_data for JSON
            serialized_curve_data = {
                k: v.tolist() if hasattr(v, 'tolist') else v
                for k, v in comparison_data.items()
            }
            # Zamiast przekierowania, zwracamy dane JSON
            return jsonify({
                'status': 'success',
                'curve_data': serialized_curve_data,
                'table_data': table_data,
                'lut_info': {
                    'title': lut_data.get('title', filename),
                    'size': f"{lut_data.get('size')}",
                    'domain_min': float(lut_data.get('domain_min')[0] if isinstance(lut_data.get('domain_min'), list) and lut_data.get('domain_min') else lut_data.get('domain_min') or 0.0),
                    'domain_max': float(lut_data.get('domain_max')),
                    'curve_name': curve_info['description'],
                    'report_pdf': os.path.basename(report_pdf_path),
                    'report_png': os.path.basename(report_png_path)
                }
            })

        except (FileNotFoundError, ValueError, IOError) as e:
            flash(f'Error analyzing file {filename}: {e}', 'error')
            print(f"Analysis error: {e}\n{traceback.format_exc()}")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An unexpected error occurred: {e}', 'error')
            print(f"Unexpected error: {e}\n{traceback.format_exc()}")
            return redirect(url_for('index'))
        finally:
            # Optionally: delete the uploaded file after analysis
            # if os.path.exists(upload_path):
            #     os.remove(upload_path)
            pass

    else:
        flash('Invalid file type. Only .cube files are accepted.', 'error')
        return redirect(url_for('index'))

@app.route('/analyze-batch', methods=['POST'])
def analyze_batch_route():
    """Handles batch LUT file upload and initiates analysis."""
    if 'lut_files' not in request.files:
        flash('No files part found in the request.', 'error')
        return redirect(url_for('batch_page'))
        
    files = request.files.getlist('lut_files')
    if not files or files[0].filename == '':
        flash('No files selected.', 'error')
        return redirect(url_for('batch_page'))
        
    curve_name = request.form.get('curve_select', 'slog3')
    
    # Sprawdzenie aliasów dla zachowania kompatybilności
    if curve_name in CURVE_ALIASES:
        curve_name = CURVE_ALIASES[curve_name]
    
    # Sprawdzenie, czy krzywa istnieje
    if curve_name not in CURVE_INFO:
        flash(f'Invalid curve name: {curve_name}', 'error')
        return redirect(url_for('batch_page'))

    # Create a unique batch ID based on timestamp
    batch_id = f"batch_{int(time.time())}"
    batch_dir = os.path.join(app.config['BATCH_FOLDER'], batch_id)
    os.makedirs(batch_dir, exist_ok=True)
    
    # Limit number of files
    files = files[:MAX_BATCH_FILES]
    
    successful_files = []
    failed_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(upload_path)
                
                # Run analysis
                report_basename = os.path.splitext(filename)[0]
                report_pdf_path = os.path.join(batch_dir, report_basename + ".pdf")
                report_png_path = os.path.join(batch_dir, report_basename + ".png")
                
                lut_data = load_cube_file(upload_path)
                curve_info = CURVE_INFO.get(curve_name)
                
                if not curve_info:
                    raise ValueError(f"Invalid curve name: {curve_name}")
                
                # Użyj nowej, precyzyjnej funkcji porównującej
                comparison_data = compare_lut_to_curve(
                    lut_data, 
                    curve_info["curve_func"],
                    use_tetrahedral=True  # Używaj dokładniejszej interpolacji tetrahedral
                )
                
                # Przygotuj dane do tabeli porównawczej
                table_data = []
                input_vals = comparison_data['input_values']
                curve_vals = comparison_data['curve_values']
                lut_vals = comparison_data['lut_values']
                for i in range(len(input_vals)):
                    table_data.append({
                        'input': float(input_vals[i]),
                        'curve': float(curve_vals[i]),
                        'lut': float(lut_vals[i]),
                        'delta': float(lut_vals[i] - curve_vals[i])
                    })
                session['table_data'] = table_data
                
                plot_title = f"LUT '{lut_data.get('title', filename)}' vs {curve_info['description']}"
                plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
                
                # Użyj pełnej informacji o krzywej w raporcie
                generate_pdf_report(lut_data, report_png_path, report_pdf_path)
                
                successful_files.append({
                    'filename': filename,
                    'pdf': os.path.basename(report_pdf_path),
                    'png': os.path.basename(report_png_path),
                    'title': lut_data.get('title', filename)
                })
            except Exception as e:
                failed_files.append({'filename': filename, 'error': str(e)})
                print(f"Error processing {filename}: {e}\n{traceback.format_exc()}")
            finally:
                # Clean up upload
                if os.path.exists(upload_path):
                    os.remove(upload_path)
    
    # Create ZIP file with all reports
    if successful_files:
        zip_filename = f"{batch_id}.zip"
        zip_path = os.path.join(batch_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(batch_dir):
                for file in files:
                    if file.endswith('.pdf') or file.endswith('.png'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
        
        session['batch_id'] = batch_id
        session['successful_files'] = successful_files
        session['failed_files'] = failed_files
        session['zip_filename'] = zip_filename
        session['curve_name'] = curve_info['description']
        
        flash(f'Processed {len(successful_files)} files successfully. {len(failed_files)} files failed.', 'success')
        return redirect(url_for('show_batch_results'))
    else:
        flash('No files were processed successfully.', 'error')
        return redirect(url_for('batch_page'))

@app.route('/compare-luts', methods=['POST'])
def compare_luts_route():
    """Handles comparison of two LUT files."""
    if 'lut_file1' not in request.files or 'lut_file2' not in request.files:
        flash('Both LUT files are required.', 'error')
        return redirect(url_for('compare_page'))
        
    file1 = request.files['lut_file1']
    file2 = request.files['lut_file2']
    
    if file1.filename == '' or file2.filename == '':
        flash('Both LUT files must be selected.', 'error')
        return redirect(url_for('compare_page'))
        
    if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
        flash('Invalid file type. Only .cube files are accepted.', 'error')
        return redirect(url_for('compare_page'))
        
    # Save uploaded files
    filename1 = secure_filename(file1.filename)
    filename2 = secure_filename(file2.filename)
    
    upload_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
    upload_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
    
    try:
        file1.save(upload_path1)
        file2.save(upload_path2)
        
        # Generate unique report names
        timestamp = int(time.time())
        report_basename = f"compare_{timestamp}"
        report_pdf_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".pdf")
        report_png_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".png")
        
        # Load LUT data
        lut_data1 = load_cube_file(upload_path1)
        lut_data2 = load_cube_file(upload_path2)
        
        # Compare LUTs using tetrahedral interpolation for maximum accuracy
        comparison_data = compare_two_luts(lut_data1, lut_data2, use_tetrahedral=True)
        
        # Get LUT names from title or filename
        lut1_name = lut_data1.get('title', filename1)
        lut2_name = lut_data2.get('title', filename2)
        
        plot_title = f"Comparison: '{lut1_name}' vs '{lut2_name}'"
        plot_lut_vs_lut(comparison_data, plot_title, report_png_path)
        
        # Generate report
        generate_comparison_report(lut_data1, lut_data2, report_png_path, report_pdf_path)
        
        # Store results in session
        session['report_pdf'] = os.path.basename(report_pdf_path)
        session['report_png'] = os.path.basename(report_png_path)
        session['lut1_name'] = lut1_name
        session['lut2_name'] = lut2_name
        session['is_comparison'] = True
        
        return redirect(url_for('show_results'))
        
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
        print(f"Error comparing LUTs: {e}\n{traceback.format_exc()}")
        return redirect(url_for('compare_page'))
    finally:
        # Clean up uploaded files
        for path in [upload_path1, upload_path2]:
            if os.path.exists(path):
                os.remove(path)

@app.route('/results')
def show_results():
    """Displays the analysis results page."""
    pdf_file = session.get('report_pdf')
    png_file = session.get('report_png')
    lut_title = session.get('lut_title', 'LUT Analysis')
    curve_name = session.get('curve_name', '')
    is_comparison = session.get('is_comparison', False)
    
    if not pdf_file or not png_file:
        flash('No analysis results to display.', 'warning')
        return redirect(url_for('index'))
    
    context = {
        'lut_title': lut_title,
        'pdf_file': pdf_file,
        'png_file': png_file,
        'curve_name': curve_name,
        'is_comparison': is_comparison
    }
    
    if is_comparison:
        context['lut1_name'] = session.get('lut1_name', '')
        context['lut2_name'] = session.get('lut2_name', '')
    
    return render_template('results.html', **context)

@app.route('/batch-results')
def show_batch_results():
    """Displays the batch analysis results page."""
    batch_id = session.get('batch_id')
    successful_files = session.get('successful_files', [])
    failed_files = session.get('failed_files', [])
    zip_filename = session.get('zip_filename')
    curve_name = session.get('curve_name', '')
    
    if not batch_id or not successful_files:
        flash('No batch results to display.', 'warning')
        return redirect(url_for('batch_page'))
    
    return render_template('batch_results.html', 
                          batch_id=batch_id,
                          successful_files=successful_files,
                          failed_files=failed_files,
                          zip_filename=zip_filename,
                          curve_name=curve_name)

@app.route('/batch/<batch_id>/<filename>')
def serve_batch_file(batch_id, filename):
    """Serves files from batch directories."""
    # Security check - make sure filename is just a filename
    filename = os.path.basename(filename)
    batch_dir = os.path.join(app.config['BATCH_FOLDER'], batch_id)
    
    try:
        return send_from_directory(batch_dir, filename)
    except FileNotFoundError:
        flash(f'File not found: {filename}', 'error')
        return redirect(url_for('index'))

@app.route('/download-batch-zip/<batch_id>/<zip_filename>')
def download_batch_zip(batch_id, zip_filename):
    """Downloads all batch results as a ZIP archive."""
    batch_dir = os.path.join(app.config['BATCH_FOLDER'], batch_id)
    zip_path = os.path.join(batch_dir, zip_filename)
    
    try:
        return send_file(zip_path, as_attachment=True)
    except FileNotFoundError:
        flash('ZIP archive not found.', 'error')
        return redirect(url_for('batch_page'))

@app.route('/reports/<filename>')
def serve_report(filename):
    """Serves generated report files (PDF, PNG)."""
    safe_filename = secure_filename(filename) # Additional security
    try:
        return send_from_directory(app.config['REPORTS_FOLDER'], safe_filename)
    except FileNotFoundError:
        flash(f'Report file not found: {safe_filename}', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about_page():
    """Displays information about the application."""
    return render_template('about.html')

@app.route('/table-data')
def table_data():
    """Zwraca dane do tabeli porównawczej w formacie JSON."""
    table = session.get('table_data', [])
    return jsonify(table)

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, 
                          error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500,
                          error_message="Internal server error"), 500

# --- Application Launch ---
if __name__ == '__main__':
    # Upewnij się, że katalogi istnieją
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    # Uruchom aplikację na porcie 8080
    app.run(host='127.0.0.1', port=8080, debug=False)
