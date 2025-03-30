# -*- coding: utf-8 -*-
import os
import sys
# Adding type hint for Pylance to help with import resolution
from flask import (Flask, request, render_template, redirect, url_for,  # type: ignore
                   send_from_directory, flash, session)
from werkzeug.utils import secure_filename  # type: ignore
import traceback # For detailed error logging

# Import functions from our package
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

# --- Application Configuration ---
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports' # Where generated reports (png, pdf) will be saved
ALLOWED_EXTENSIONS = {'cube'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
# Required for flash messages (user notifications)
app.config['SECRET_KEY'] = os.urandom(24)

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mapping curve names (as in merged_lut_analyzer.py)
# Make sure all functions are imported from transfer_functions
CURVE_MAP = {name: func for name, func in locals().items() if name.startswith('linear_to_')}
# Add aliases if needed
CURVE_MAP.update({
    "gamma22": linear_to_redgamma4,
    "gamma24": linear_to_redgamma3,
    "clog2": linear_to_canonlog2,
    "redipp2odt": linear_to_red_ipp2_odt_approx,
})
# Remove functions that are not curves (if any were included)
CURVE_MAP = {k: v for k, v in CURVE_MAP.items() if callable(v)}


# --- Routes ---
@app.route('/')
def index():
    """Displays the main page with the form."""
    # For now returns a simple text, later will render a template
    # return "Welcome to LUTcompareTool!"
    # Pass the list of available curves to the template
    available_curves = sorted(CURVE_MAP.keys())
    return render_template('index.html', curves=available_curves)

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
            curve_func = CURVE_MAP.get(curve_name)
            if not curve_func:
                 raise ValueError(f"Invalid curve name: {curve_name}")

            comparison_data = compare_lut_to_curve(lut_data, curve_func)
            plot_title = f"LUT '{lut_data.get('title', filename)}' vs {curve_name.upper()}"
            plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
            generate_pdf_report(lut_data, report_png_path, report_pdf_path)

            print(f"Analysis completed. Reports in: {app.config['REPORTS_FOLDER']}")
            flash('Analysis completed successfully!', 'success')

            # Save report paths in session to display them on the results page
            session['report_pdf'] = os.path.basename(report_pdf_path)
            session['report_png'] = os.path.basename(report_png_path)
            session['lut_title'] = lut_data.get('title', filename)

            return redirect(url_for('show_results'))

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

@app.route('/results')
def show_results():
    """Displays the analysis results page."""
    pdf_file = session.get('report_pdf')
    png_file = session.get('report_png')
    lut_title = session.get('lut_title', 'LUT Analysis')

    if not pdf_file or not png_file:
        flash('No analysis results to display.', 'warning')
        return redirect(url_for('index'))

    return render_template('results.html',
                           lut_title=lut_title,
                           pdf_file=pdf_file,
                           png_file=png_file)

@app.route('/reports/<filename>')
def serve_report(filename):
    """Serves generated report files (PDF, PNG)."""
    safe_filename = secure_filename(filename) # Additional security
    try:
        return send_from_directory(app.config['REPORTS_FOLDER'], safe_filename)
    except FileNotFoundError:
        flash(f'Report file not found: {safe_filename}', 'error')
        return redirect(url_for('index'))


# --- Application Launch ---
if __name__ == '__main__':
    # Run in debug mode for easier development
    # In production environment, use a WSGI server like gunicorn or waitress
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
