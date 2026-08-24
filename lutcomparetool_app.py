# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import io
import time
import json
import base64
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
                                                generate_comparison_report,
                                                generate_exposure_assist_report,
                                                generate_smallhd_workflow_diagram)
    from lut_analyzer_package.exposure_assist import analyze_exposure_assist
    from lut_analyzer_package.encoding_catalog import (
        DEFAULT_ENCODING,
        ENCODING_ALIASES,
        ENCODING_INFO,
        encoding_options_for_ui,
        resolve_encoding,
    )
    from lut_analyzer_package.transfer_functions import * # Import all transfer functions
    from lut_analyzer_package.color_space import (s_gamut3_to_rec709,
                                                 s_gamut3_cine_to_rec709,
                                                 arri_wide_gamut4_to_rec709,
                                                 arri_wide_gamut3_to_rec709,
                                                 red_wide_gamut_rgb_to_rec709,
                                                 v_gamut_to_rec709,
                                                 canon_cinema_gamut_to_rec709,
                                                 aces_ap1_to_rec709)
except ImportError as e:
    print(f"Error importing lut_analyzer_package: {e}", file=sys.stderr)
    print("Ensure the package is in the Python path or installed.", file=sys.stderr)
    sys.exit(1)

# --- Application Configuration ---
# Vercel Python functions have a read-only filesystem except /tmp.
_DATA_ROOT = '/tmp/lut_to_false' if os.environ.get('VERCEL') else '.'
UPLOAD_FOLDER = os.path.join(_DATA_ROOT, 'uploads')
REPORTS_FOLDER = os.path.join(_DATA_ROOT, 'reports')
BATCH_FOLDER = os.path.join(_DATA_ROOT, 'batch_reports')
ALLOWED_EXTENSIONS = {'cube'}
MAX_BATCH_FILES = 20  # Maximum number of files for batch processing


def _domain_scalar(value, default):
    """Zwraca pojedynczą liczbę z domeny LUT, która może być listą [R, G, B]."""
    if isinstance(value, (list, tuple)):
        return float(value[0]) if value else float(default)
    if value is None:
        return float(default)
    return float(value)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['BATCH_FOLDER'] = BATCH_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
# Stable SECRET_KEY required on multi-instance hosts (Vercel/gunicorn).
# Never use os.urandom here — it invalidates sessions across cold starts.
app.config['SECRET_KEY'] = (
    os.environ.get('SECRET_KEY')
    or 'lut-to-false-dev-secret-set-SECRET_KEY-in-production'
)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
if os.environ.get('VERCEL'):
    app.config['SESSION_COOKIE_SECURE'] = True

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


def _file_data_uri(path, mime_type):
    """Encode a local file as a data URI for same-request HTML responses."""
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'rb') as handle:
        encoded = base64.b64encode(handle.read()).decode('ascii')
    return f'data:{mime_type};base64,{encoded}'


def _write_table_json(report_basename, table_data):
    """Persist comparison table beside reports (avoids oversized session cookies)."""
    table_path = os.path.join(
        app.config['REPORTS_FOLDER'], f'{report_basename}_table.json'
    )
    with open(table_path, 'w', encoding='utf-8') as handle:
        json.dump(table_data, handle)
    return os.path.basename(table_path)


def _load_table_json(table_filename):
    if not table_filename:
        return []
    safe_name = secure_filename(table_filename)
    table_path = os.path.join(app.config['REPORTS_FOLDER'], safe_name)
    if not os.path.isfile(table_path):
        return []
    with open(table_path, encoding='utf-8') as handle:
        return json.load(handle)


def _render_analysis_results(
    *,
    lut_title,
    curve_name,
    report_pdf_path,
    report_png_path,
    table_data,
    is_comparison=False,
    lut1_name='',
    lut2_name='',
):
    """Render results HTML. On Vercel, embed assets inline (no redirect /tmp hop)."""
    pdf_file = os.path.basename(report_pdf_path) if report_pdf_path else None
    png_file = os.path.basename(report_png_path) if report_png_path else None
    context = {
        'lut_title': lut_title,
        'curve_name': curve_name,
        'pdf_file': pdf_file,
        'png_file': png_file,
        'png_data_uri': _file_data_uri(report_png_path, 'image/png'),
        'pdf_data_uri': _file_data_uri(report_pdf_path, 'application/pdf'),
        'table_data': table_data,
        'is_comparison': is_comparison,
        'lut1_name': lut1_name,
        'lut2_name': lut2_name,
    }
    return render_template('results.html', **context)

# Shared encoding catalog (valid transfer + gamut pairs)
CURVE_INFO = ENCODING_INFO
CURVE_ALIASES = ENCODING_ALIASES

# --- Routes ---
@app.route('/')
def index():
    """Displays the main page with the form."""
    return render_template(
        'index.html',
        encoding_groups=encoding_options_for_ui(),
        default_encoding=DEFAULT_ENCODING,
        analysis_modes=(
            {
                "value": "curve_compare",
                "label": "Curve compare (LUT vs reference transfer)",
            },
            {
                "value": "exposure_assist",
                "label": "Exposure Assist (per-LUT Rec.709 Y / IRE after look)",
            },
        ),
        default_mode="curve_compare",
    )

@app.route('/batch')
def batch_page():
    """Displays the batch analysis page."""
    return render_template(
        'batch.html',
        encoding_groups=encoding_options_for_ui(),
        default_encoding=DEFAULT_ENCODING,
        analysis_modes=(
            {
                "value": "curve_compare",
                "label": "Curve compare (LUT vs reference transfer)",
            },
            {
                "value": "exposure_assist",
                "label": "Exposure Assist (per-LUT Rec.709 Y / IRE after look)",
            },
        ),
        default_mode="curve_compare",
    )


FALSE_COLOR_SHORT_LABELS = {
    'deep_shadow': 'DEEP',
    'minus_one_ev': '−1 EV',
    'mid_range': 'MID',
    'face_exposure': 'FACE',
    'bright_safe': 'SAFE',
    'highlight_warn': 'WARN',
    'highlight_high': 'HIGH',
    'white_clipping': 'CLIP',
}


def _analysis_to_false_color_entry(analysis):
    """Build one false-color card from an Exposure Assist contract."""
    zones = []
    for zone in analysis.get('smallhd_zones') or []:
        z = dict(zone)
        span = max(0.0, float(z['maximum_ire']) - float(z['minimum_ire']))
        z['width_pct'] = max(span, 0.01)
        z['short_label'] = FALSE_COLOR_SHORT_LABELS.get(
            z.get('semantic'), (z.get('label') or '')[:6]
        )
        zones.append(z)

    anchors = {
        str(point['ev']): float(point['rec709_y_ire'])
        for point in analysis.get('anchor_points') or []
    }
    return {
        'file_name': analysis['source']['file_name'],
        'confidence': analysis.get('confidence') or {},
        'clipping': analysis.get('clipping') or {},
        'smallhd_map_zones': zones,
        'anchor_ire_by_ev_sorted': sorted(
            anchors.items(),
            key=lambda item: float(item[0]),
        ),
        'input_encoding': analysis.get('input_encoding') or {},
    }


def _store_exposure_assist_session(analyses):
    """Persist last Exposure Assist runs for the /false-color page."""
    entries = []
    for analysis in analyses:
        key = Path(analysis['source']['file_name']).stem
        entries.append((key, _analysis_to_false_color_entry(analysis)))
    session['exposure_assist_scales'] = entries
    if analyses:
        session['exposure_assist_encoding'] = analyses[0].get('input_encoding')


@app.route('/false-color')
@app.route('/exposure-assist')
def false_color_page():
    """Exposure Assist / false-color scales from the latest analysis run."""
    lut_entries = session.get('exposure_assist_scales') or []
    encoding = session.get('exposure_assist_encoding') or {
        'description': 'Select an encoding when you analyze a LUT',
        'transfer': '—',
        'gamut': '—',
    }
    preset = {
        'signal': 'display_referred_rec709_y_ire_after_lut',
        'input_assumed': encoding.get('description', 'user-selected encoding'),
        'measurement_pages': {
            'SENSOR_SAFETY': {
                'measure': 'before Look',
                'purpose': (
                    'Protect sensor/log signal from clipping; not derived from '
                    'post-LUT Rec.709 Y of the viewing LUT.'
                ),
                'note': (
                    'Use camera/monitor false color or waveform on the pre-Look path.'
                ),
            },
            'LOOK_EXPOSURE': {
                'measure': 'after Look',
                'purpose': 'Look exposure assist for the applied viewing LUT',
                'maps': 'per_lut_smallhd_zones',
            },
        },
        'highlight_policy': {
            'WARN': {'color': '#FACC15', 'role': 'yellow'},
            'HIGH': {'color': '#F97316', 'role': 'orange'},
            'WHITE_CLIPPING': {
                'color': '#DC2626',
                'role': 'red_only_for_clipping',
            },
        },
    }
    return render_template(
        'false_color.html',
        preset=preset,
        lut_entries=lut_entries,
        has_scales=bool(lut_entries),
        strip_url=None,
    )

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

    analysis_mode = request.form.get('analysis_mode', 'curve_compare')
    if analysis_mode not in ('curve_compare', 'exposure_assist'):
        flash(f'Invalid analysis mode: {analysis_mode}', 'error')
        return redirect(url_for('index'))

    encoding_raw = request.form.get('curve_select', DEFAULT_ENCODING)
    try:
        encoding_key, curve_info = resolve_encoding(encoding_raw)
    except ValueError:
        flash(f'Invalid encoding: {encoding_raw}', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(upload_path)
            flash(f'File {filename} was successfully uploaded.', 'success')

            report_basename = os.path.splitext(filename)[0]

            if analysis_mode == 'exposure_assist':
                analysis = analyze_exposure_assist(
                    {
                        "lut_path": upload_path,
                        "encoding": encoding_key,
                    }
                )
                report = generate_exposure_assist_report(
                    {
                        "analysis": analysis,
                        "output_dir": app.config['REPORTS_FOLDER'],
                        "basename": report_basename,
                    }
                )
                _store_exposure_assist_session([analysis])
                session['exposure_assist_artifacts'] = {
                    key: os.path.basename(path)
                    for key, path in report['artifacts'].items()
                }
                flash('Exposure Assist completed successfully!', 'success')
                if request.args.get('format') == 'json':
                    return jsonify({'status': 'success', 'analysis': analysis})
                return redirect(url_for('false_color_page'))

            # --- Curve compare ---
            report_pdf_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".pdf")
            report_png_path = os.path.join(app.config['REPORTS_FOLDER'], report_basename + ".png")

            print(f"Starting analysis for: {upload_path}, encoding: {encoding_key}")

            lut_data = load_cube_file(upload_path)
            comparison_data = compare_lut_to_curve(
                lut_data,
                curve_info["curve_func"],
                use_tetrahedral=True,
            )

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

            plot_title = f"LUT '{lut_data.get('title', filename)}' vs {curve_info['description']}"
            plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
            
            # Użyj pełnej informacji o krzywej w raporcie
            generate_pdf_report(lut_data, report_png_path, report_pdf_path)

            print(f"Analysis completed. Reports in: {app.config['REPORTS_FOLDER']}")
            flash('Analysis completed successfully!', 'success')

            # Persist table beside reports — never put large arrays in cookie sessions
            table_filename = _write_table_json(report_basename, table_data)
            session['report_pdf'] = os.path.basename(report_pdf_path)
            session['report_png'] = os.path.basename(report_png_path)
            session['table_file'] = table_filename
            session['lut_title'] = lut_data.get('title', filename)
            session['curve_name'] = curve_info['description']
            session.pop('table_data', None)

            if request.args.get('format') == 'json':
                serialized_curve_data = {
                    k: v.tolist() if hasattr(v, 'tolist') else v
                    for k, v in comparison_data.items()
                }
                return jsonify({
                    'status': 'success',
                    'curve_data': serialized_curve_data,
                    'table_data': table_data,
                    'lut_info': {
                        'title': lut_data.get('title', filename),
                        'size': f"{lut_data.get('lut_3d_size') or lut_data.get('lut_1d_size')}",
                        'domain_min': _domain_scalar(lut_data.get('domain_min'), 0.0),
                        'domain_max': _domain_scalar(lut_data.get('domain_max'), 1.0),
                        'curve_name': curve_info['description'],
                        'report_pdf': os.path.basename(report_pdf_path),
                        'report_png': os.path.basename(report_png_path)
                    }
                })

            # Same-request HTML: required on Vercel (ephemeral /tmp + multi-instance)
            return _render_analysis_results(
                lut_title=lut_data.get('title', filename),
                curve_name=curve_info['description'],
                report_pdf_path=report_pdf_path,
                report_png_path=report_png_path,
                table_data=table_data,
            )

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

    analysis_mode = request.form.get('analysis_mode', 'curve_compare')
    if analysis_mode not in ('curve_compare', 'exposure_assist'):
        flash(f'Invalid analysis mode: {analysis_mode}', 'error')
        return redirect(url_for('batch_page'))

    encoding_raw = request.form.get('curve_select', DEFAULT_ENCODING)
    try:
        encoding_key, curve_info = resolve_encoding(encoding_raw)
    except ValueError:
        flash(f'Invalid encoding: {encoding_raw}', 'error')
        return redirect(url_for('batch_page'))

    batch_id = f"batch_{int(time.time())}"
    batch_dir = os.path.join(app.config['BATCH_FOLDER'], batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    files = files[:MAX_BATCH_FILES]
    successful_files = []
    failed_files = []
    exposure_analyses = []

    if analysis_mode == 'exposure_assist':
        generate_smallhd_workflow_diagram(
            {
                "output_dir": batch_dir,
                "basename": "smallhd_workflow_shared",
            }
        )

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(upload_path)
                report_basename = os.path.splitext(filename)[0]

                if analysis_mode == 'exposure_assist':
                    analysis = analyze_exposure_assist(
                        {
                            "lut_path": upload_path,
                            "encoding": encoding_key,
                        }
                    )
                    exposure_analyses.append(analysis)
                    report = generate_exposure_assist_report(
                        {
                            "analysis": analysis,
                            "output_dir": batch_dir,
                            "basename": report_basename,
                        }
                    )
                    artifacts = report["artifacts"]
                    anchor_map = {
                        point["ev"]: point["rec709_y_ire"]
                        for point in analysis["anchor_points"]
                    }
                    successful_files.append(
                        {
                            "filename": filename,
                            "title": analysis["source"]["file_name"],
                            "mode": "exposure_assist",
                            "pdf": os.path.basename(artifacts["pdf"]),
                            "png": os.path.basename(artifacts["dashboard_png"]),
                            "json": os.path.basename(artifacts["json"]),
                            "csv": os.path.basename(artifacts["csv"]),
                            "false_color_bar": os.path.basename(
                                artifacts["false_color_bar_png"]
                            ),
                            "ev_ire": os.path.basename(artifacts["ev_ire_png"]),
                            "workflow": os.path.basename(artifacts["workflow_png"]),
                            "anchors": {
                                "minus_one_ev": anchor_map.get(-1.0),
                                "zero_ev": anchor_map.get(0.0),
                                "plus_half_ev": anchor_map.get(0.5),
                                "plus_one_ev": anchor_map.get(1.0),
                                "warn_ev": anchor_map.get(2.0),
                                "high_ev": anchor_map.get(3.0),
                            },
                            "zones": analysis["smallhd_zones"],
                            "clipping": analysis["clipping"],
                            "confidence": analysis["confidence"],
                            "limitations": analysis["limitations"],
                            "encoding": analysis["input_encoding"]["description"],
                        }
                    )
                else:
                    report_pdf_path = os.path.join(
                        batch_dir, report_basename + ".pdf"
                    )
                    report_png_path = os.path.join(
                        batch_dir, report_basename + ".png"
                    )

                    lut_data = load_cube_file(upload_path)
                    comparison_data = compare_lut_to_curve(
                        lut_data,
                        curve_info["curve_func"],
                        use_tetrahedral=True,
                    )

                    table_data = []
                    input_vals = comparison_data['input_values']
                    curve_vals = comparison_data['curve_values']
                    lut_vals = comparison_data['lut_values']
                    for i in range(len(input_vals)):
                        table_data.append(
                            {
                                'input': float(input_vals[i]),
                                'curve': float(curve_vals[i]),
                                'lut': float(lut_vals[i]),
                                'delta': float(lut_vals[i] - curve_vals[i]),
                            }
                        )
                    session['table_data'] = table_data

                    plot_title = (
                        f"LUT '{lut_data.get('title', filename)}' "
                        f"vs {curve_info['description']}"
                    )
                    plot_lut_vs_curve(comparison_data, plot_title, report_png_path)
                    generate_pdf_report(
                        lut_data, report_png_path, report_pdf_path
                    )

                    successful_files.append(
                        {
                            'filename': filename,
                            'pdf': os.path.basename(report_pdf_path),
                            'png': os.path.basename(report_png_path),
                            'title': lut_data.get('title', filename),
                            'mode': 'curve_compare',
                        }
                    )
            except Exception as e:
                failed_files.append({'filename': filename, 'error': str(e)})
                print(f"Error processing {filename}: {e}\n{traceback.format_exc()}")
            finally:
                if os.path.exists(upload_path):
                    os.remove(upload_path)

    if successful_files:
        zip_filename = f"{batch_id}.zip"
        zip_path = os.path.join(batch_dir, zip_filename)
        archive_extensions = (
            '.pdf',
            '.png',
            '.svg',
            '.json',
            '.csv',
        )

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, walk_files in os.walk(batch_dir):
                for walk_file in walk_files:
                    if walk_file.endswith(archive_extensions):
                        file_path = os.path.join(root, walk_file)
                        zipf.write(file_path, os.path.basename(file_path))

        session['batch_id'] = batch_id
        session['successful_files'] = successful_files
        session['failed_files'] = failed_files
        session['zip_filename'] = zip_filename
        session['analysis_mode'] = analysis_mode
        if analysis_mode == 'exposure_assist':
            _store_exposure_assist_session(exposure_analyses)
            session['curve_name'] = (
                f"{curve_info['description']} → Rec.709 Y (Exposure Assist)"
            )
        else:
            session['curve_name'] = curve_info['description']

        flash(
            f'Processed {len(successful_files)} files successfully. '
            f'{len(failed_files)} files failed.',
            'success',
        )
        return redirect(url_for('show_batch_results'))

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

    report_pdf_path = os.path.join(app.config['REPORTS_FOLDER'], secure_filename(pdf_file))
    report_png_path = os.path.join(app.config['REPORTS_FOLDER'], secure_filename(png_file))
    return _render_analysis_results(
        lut_title=lut_title,
        curve_name=curve_name,
        report_pdf_path=report_pdf_path if os.path.isfile(report_pdf_path) else None,
        report_png_path=report_png_path if os.path.isfile(report_png_path) else None,
        table_data=_load_table_json(session.get('table_file')),
        is_comparison=is_comparison,
        lut1_name=session.get('lut1_name', ''),
        lut2_name=session.get('lut2_name', ''),
    )

@app.route('/batch-results')
def show_batch_results():
    """Displays the batch analysis results page."""
    batch_id = session.get('batch_id')
    successful_files = session.get('successful_files', [])
    failed_files = session.get('failed_files', [])
    zip_filename = session.get('zip_filename')
    curve_name = session.get('curve_name', '')
    analysis_mode = session.get('analysis_mode', 'curve_compare')

    if not batch_id or not successful_files:
        flash('No batch results to display.', 'warning')
        return redirect(url_for('batch_page'))

    return render_template(
        'batch_results.html',
        batch_id=batch_id,
        successful_files=successful_files,
        failed_files=failed_files,
        zip_filename=zip_filename,
        curve_name=curve_name,
        analysis_mode=analysis_mode,
    )

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
    """Return comparison table JSON from on-disk file (not cookie session)."""
    table = _load_table_json(session.get('table_file'))
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
