# -*- coding: utf-8 -*-
"""
Moduł odpowiedzialny za generowanie raportów, wykresów i analiz porównawczych LUT.
"""

import numpy as np
import matplotlib
# Ustawienie backendu matplotlib na 'Agg' (non-interactive)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import reportlab.pdfgen.canvas as canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
from typing import Callable, Dict, Optional

# Importuj funkcje interpolacji z tego samego pakietu
from .lut_interpolation import interpolate_1d_lut, interpolate_3d_lut

# =========================================
# Funkcje Analizy i Porównania
# =========================================

def compare_lut_to_curve(lut_data: dict, curve_func: callable, num_points: int = 100, use_tetrahedral: bool = True) -> Dict[str, np.ndarray]:
    """
    Compares a LUT to a reference log/gamma curve.
    
    Args:
        lut_data (dict): LUT data from load_cube_file
        curve_func (callable): Reference curve function to compare with
        num_points (int): Number of test points to generate
        use_tetrahedral (bool): Use tetrahedral interpolation for 3D LUT (more accurate)
        
    Returns:
        dict: Dictionary with comparison data:
            'input_values': Linear input values
            'curve_values': Output values from the reference curve
            'lut_values': Output values from the LUT
    """
    # Generate test points in linear space (0-1 range)
    # Use logarithmic distribution to better sample the shadows
    # Używamy wartości float64 dla maksymalnej precyzji
    log_spaced = np.logspace(-8, 0, num_points, dtype=np.float64)
    # Normalizacja do zakresu 0-1
    input_values = log_spaced / log_spaced.max()
    
    # Zamiana na float32 po zakończeniu operacji - tylko na potrzeby kompatybilności
    input_values = input_values.astype(np.float32)
    
    # Compute reference curve values (what we're comparing LUT against)
    curve_values = curve_func(input_values)
    
    # LUT interpolation based on LUT type (1D/3D)
    if lut_data['lut_type'] == '1D':
        # 1D LUT interpolation
        from lut_analyzer_package.lut_interpolation import interpolate_1d_lut
        
        # Create RGB triplets for input to LUT - dla krzywych transferu wszystkie kanały są takie same
        input_rgb = np.column_stack([input_values] * 3)
        
        # Interpolate with 1D LUT
        lut_rgb = interpolate_1d_lut(
            lut_data['lut_1d'], 
            input_values,
            domain_min=lut_data['domain_min'][0],
            domain_max=lut_data['domain_max'][0]
        )
        
        # Average RGB channels for grayscale comparison
        # W ten sposób uwzględniamy potencjalne różnice między kanałami
        lut_values = np.mean(lut_rgb, axis=1)
        
    elif lut_data['lut_type'] in ('3D', 'both'):
        # 3D LUT interpolation - dla testingu używamy jednolitych wartości RGB
        from lut_analyzer_package.lut_interpolation import interpolate_3d_lut, interpolate_tetrahedral_3d_lut
        
        # Create RGB triplets for input to LUT
        input_rgb = np.column_stack([input_values] * 3)
        
        # Wybór precyzyjnej interpolacji tetrahedral dla większej dokładności
        if use_tetrahedral and lut_data['lut_type'] == '3D':
            # Użyj bardziej dokładnej interpolacji tetrahedral
            lut_rgb = interpolate_tetrahedral_3d_lut(
                lut_data['lut_3d'],
                lut_data['lut_3d_size'],
                input_rgb,
                domain_min=lut_data['domain_min'],
                domain_max=lut_data['domain_max']
            )
        else:
            # Fallback do standardowej interpolacji trójliniowej
            lut_rgb = interpolate_3d_lut(
                lut_data['lut_3d'],
                lut_data['lut_3d_size'],
                input_rgb,
                domain_min=lut_data['domain_min'],
                domain_max=lut_data['domain_max']
            )
            
        # Average RGB channels for grayscale comparison
        lut_values = np.mean(lut_rgb, axis=1)
    else:
        raise ValueError(f"Unsupported LUT type: {lut_data['lut_type']}")
    
    return {
        'input_values': input_values,
        'curve_values': curve_values,
        'lut_values': lut_values
    }

def plot_lut_vs_curve(comparison_data: Dict[str, np.ndarray], title: str, output_png_path: Optional[str] = None):
    """
    Plots the LUT output against the reference curve using Matplotlib.

    Args:
        comparison_data (dict): Data from compare_lut_to_curve.
        title (str): Title for the plot.
        output_png_path (str, optional): Path to save the plot PNG. If None, shows plot.
    """
    print(f"Plotting: {title}")
    try:
        plt.figure(figsize=(10, 6))
        # Plot only if data is not NaN
        if not np.isnan(comparison_data['curve_values']).all():
            plt.plot(comparison_data['input_values'], comparison_data['curve_values'], label='Reference Curve', linestyle='--')
        else:
            print("Warning: Reference curve data contains NaNs, skipping plot.")

        if not np.isnan(comparison_data['lut_values']).all():
            plt.plot(comparison_data['input_values'], comparison_data['lut_values'], label='LUT Output (Avg RGB)')
        else:
             print("Warning: LUT output data contains NaNs, skipping plot.")

        plt.xlabel("Input Linear")
        plt.ylabel("Output (Log/Gamma)")
        plt.title(title)
        # Only show legend if there are labels to show
        handles, labels = plt.gca().get_legend_handles_labels()
        if labels:
            plt.legend()
        plt.grid(True, linestyle=':') # Add linestyle to grid

        if output_png_path:
            try:
                abs_path = os.path.abspath(output_png_path)
                dir_name = os.path.dirname(abs_path)
                # Ensure directory exists
                if dir_name: # Only create if path includes a directory
                    os.makedirs(dir_name, exist_ok=True)
                plt.savefig(abs_path)
                print(f"Plot saved to {abs_path}")
                plt.close() # Close plot window after saving
            except Exception as e:
                print(f"Error saving plot to {abs_path}: {e}")
                plt.show() # Show plot if saving failed
        else:
            plt.show()
    except Exception as plot_err:
        print(f"Error during plotting: {plot_err}")
        plt.close() # Ensure plot window is closed on error


def generate_pdf_report(lut_data: dict, plot_path: str, output_pdf_path: str):
    """
    Generates a simple PDF report using ReportLab.

    Args:
        lut_data (dict): Loaded LUT data.
        plot_path (str): Path to the generated plot image.
        output_pdf_path (str): Path to save the PDF report.
    """
    print(f"Generating PDF report: {output_pdf_path}")
    try:
        # Ensure directory exists
        abs_path = os.path.abspath(output_pdf_path)
        dir_name = os.path.dirname(abs_path)
        if dir_name:  # Only create if path includes a directory
            os.makedirs(dir_name, exist_ok=True)
            
        # Create the PDF with ReportLab
        c = canvas.Canvas(abs_path, pagesize=A4)
        width, height = A4  # A4 is defined as (595.27, 841.89) points
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 30, "LUT Analysis Report")
        
        # LUT Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 60, "LUT Information")
        
        c.setFont("Helvetica", 10)
        y_position = height - 80
        line_height = 15
        
        c.drawString(30, y_position, f"Title: {lut_data.get('title', 'N/A')}")
        y_position -= line_height
        
        c.drawString(30, y_position, f"Type: {lut_data.get('lut_type', 'N/A')}")
        y_position -= line_height
        
        if lut_data.get('lut_1d_size'):
            c.drawString(30, y_position, f"1D Size: {lut_data['lut_1d_size']}")
            y_position -= line_height
            
        if lut_data.get('lut_3d_size'):
            c.drawString(30, y_position, f"3D Size: {lut_data['lut_3d_size']}")
            y_position -= line_height
            
        c.drawString(30, y_position, f"Domain Min: {lut_data.get('domain_min', 'N/A')}")
        y_position -= line_height
        
        c.drawString(30, y_position, f"Domain Max: {lut_data.get('domain_max', 'N/A')}")
        y_position -= line_height * 2
        
        # Plot
        if os.path.exists(plot_path):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y_position, "LUT vs Reference Curve Plot")
            y_position -= line_height * 1.5
            
            try:
                # Add image, respecting page margins
                # ReportLab uses points (1/72 inch), so convert mm to points
                image_width = 190 * mm
                c.drawImage(plot_path, 30, y_position - 300, width=image_width, preserveAspectRatio=True)
                y_position -= 320  # Adjust based on image height
            except Exception as e:
                c.setFillColorRGB(1, 0, 0)  # Red color for error
                c.drawString(30, y_position, f"Error embedding plot: {e}")
                c.setFillColorRGB(0, 0, 0)  # Reset color
                y_position -= line_height
        else:
            c.drawString(30, y_position, f"Plot image not found at: {plot_path}")
            y_position -= line_height
        
        # TODO: Add False Color Table / Analysis here
        y_position -= line_height
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(30, y_position, "(False Color analysis not yet implemented)")
        
        # Save PDF
        c.save()
        print(f"PDF report saved to {abs_path}")
        
    except Exception as pdf_err:
        print(f"Error generating PDF report: {pdf_err}")

def compare_two_luts(lut_data1: dict, lut_data2: dict, num_points: int = 100, use_tetrahedral: bool = True) -> Dict[str, np.ndarray]:
    """
    Compares two LUTs with each other.
    
    Args:
        lut_data1 (dict): First LUT data from load_cube_file
        lut_data2 (dict): Second LUT data from load_cube_file
        num_points (int): Number of test points to generate
        use_tetrahedral (bool): Use tetrahedral interpolation for 3D LUT (more accurate)
        
    Returns:
        dict: Dictionary with comparison data:
            'input_values': Linear input values
            'lut1_values': Output values from first LUT
            'lut2_values': Output values from second LUT
    """
    # Generate test points in linear space (0-1 range)
    # Use logarithmic distribution to better sample the shadows
    # Używamy wartości float64 dla maksymalnej precyzji
    log_spaced = np.logspace(-8, 0, num_points, dtype=np.float64)
    # Normalizacja do zakresu 0-1
    input_values = log_spaced / log_spaced.max()
    
    # Zamiana na float32 po zakończeniu operacji - tylko na potrzeby kompatybilności
    input_values = input_values.astype(np.float32)
    
    # Create RGB triplets for input to LUT
    input_rgb = np.column_stack([input_values] * 3)
    
    # Interpolate values for LUT1
    if lut_data1['lut_type'] == '1D':
        from lut_analyzer_package.lut_interpolation import interpolate_1d_lut
        lut1_rgb = interpolate_1d_lut(
            lut_data1['lut_1d'], 
            input_values,
            domain_min=lut_data1['domain_min'][0],
            domain_max=lut_data1['domain_max'][0]
        )
    elif lut_data1['lut_type'] in ('3D', 'both'):
        from lut_analyzer_package.lut_interpolation import interpolate_3d_lut, interpolate_tetrahedral_3d_lut
        if use_tetrahedral and lut_data1['lut_type'] == '3D':
            lut1_rgb = interpolate_tetrahedral_3d_lut(
                lut_data1['lut_3d'],
                lut_data1['lut_3d_size'],
                input_rgb,
                domain_min=lut_data1['domain_min'],
                domain_max=lut_data1['domain_max']
            )
        else:
            lut1_rgb = interpolate_3d_lut(
                lut_data1['lut_3d'],
                lut_data1['lut_3d_size'],
                input_rgb,
                domain_min=lut_data1['domain_min'],
                domain_max=lut_data1['domain_max']
            )
    else:
        raise ValueError(f"Unsupported LUT type for LUT1: {lut_data1['lut_type']}")
    
    # Interpolate values for LUT2
    if lut_data2['lut_type'] == '1D':
        from lut_analyzer_package.lut_interpolation import interpolate_1d_lut
        lut2_rgb = interpolate_1d_lut(
            lut_data2['lut_1d'], 
            input_values,
            domain_min=lut_data2['domain_min'][0],
            domain_max=lut_data2['domain_max'][0]
        )
    elif lut_data2['lut_type'] in ('3D', 'both'):
        from lut_analyzer_package.lut_interpolation import interpolate_3d_lut, interpolate_tetrahedral_3d_lut
        if use_tetrahedral and lut_data2['lut_type'] == '3D':
            lut2_rgb = interpolate_tetrahedral_3d_lut(
                lut_data2['lut_3d'],
                lut_data2['lut_3d_size'],
                input_rgb,
                domain_min=lut_data2['domain_min'],
                domain_max=lut_data2['domain_max']
            )
        else:
            lut2_rgb = interpolate_3d_lut(
                lut_data2['lut_3d'],
                lut_data2['lut_3d_size'],
                input_rgb,
                domain_min=lut_data2['domain_min'],
                domain_max=lut_data2['domain_max']
            )
    else:
        raise ValueError(f"Unsupported LUT type for LUT2: {lut_data2['lut_type']}")
    
    # Average RGB channels for grayscale comparison
    lut1_values = np.mean(lut1_rgb, axis=1)
    lut2_values = np.mean(lut2_rgb, axis=1)
    
    return {
        'input_values': input_values,
        'lut1_values': lut1_values,
        'lut2_values': lut2_values
    }

def plot_lut_vs_lut(comparison_data: Dict[str, np.ndarray], title: str, output_png_path: Optional[str] = None):
    """
    Plots comparison between two LUTs.
    
    Args:
        comparison_data (dict): Dictionary from compare_two_luts
        title (str): Title for the plot
        output_png_path (str): Path to save the PNG image
    """
    plt.figure(figsize=(10, 6))
    
    # Plot LUT1 and LUT2 curves if data is valid
    if not np.isnan(comparison_data['lut1_values']).all():
        plt.plot(comparison_data['input_values'], comparison_data['lut1_values'], label='LUT 1', linestyle='-', color='blue')
    else:
        print("Warning: LUT1 data contains NaNs, skipping plot.")
        
    if not np.isnan(comparison_data['lut2_values']).all():
        plt.plot(comparison_data['input_values'], comparison_data['lut2_values'], label='LUT 2', linestyle='-', color='red')
    else:
        print("Warning: LUT2 data contains NaNs, skipping plot.")
    
    # Plot difference curve
    difference = comparison_data['lut2_values'] - comparison_data['lut1_values']
    plt.plot(comparison_data['input_values'], difference, label='Difference (LUT2 - LUT1)', linestyle='--', color='green')
    
    # Add horizontal line at 0 for reference
    plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    
    # Plot settings
    plt.title(title)
    plt.xlabel('Input Linear Value')
    plt.ylabel('Output Value')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Use logarithmic scale for x-axis to better show shadow detail
    plt.xscale('log')
    
    # Improve visual formatting
    plt.tight_layout()
    
    # Save plot if path is provided
    if output_png_path:
        plt.savefig(output_png_path, dpi=300)
        print(f"Saved comparison plot to {output_png_path}")
    
    plt.close()  # Close figure to free memory

def generate_comparison_report(lut_data1: dict, lut_data2: dict, plot_path: str, output_pdf_path: str):
    """
    Generates a PDF report comparing two LUT files.
    
    Args:
        lut_data1 (dict): First LUT data from load_cube_file
        lut_data2 (dict): Second LUT data from load_cube_file
        plot_path (str): Path to the comparison plot PNG
        output_pdf_path (str): Path to save the PDF report
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    # Create PDF document
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', 
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    normal_style = styles['Normal']
    
    # Build document content
    content = []
    
    # Title
    title = f"LUT Comparison Report"
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 0.2 * inch))
    
    # Add comparison plot image
    try:
        img = Image(plot_path)
        img.drawHeight = 4 * inch
        img.drawWidth = 6 * inch
        content.append(img)
    except Exception as e:
        content.append(Paragraph(f"Error loading plot image: {e}", normal_style))
    
    content.append(Spacer(1, 0.3 * inch))
    
    # LUT Information Table
    lut1_title = lut_data1.get('title', 'Untitled LUT 1')
    lut2_title = lut_data2.get('title', 'Untitled LUT 2')
    
    content.append(Paragraph("LUT Information", subtitle_style))
    
    lut_info_data = [
        ["Property", "LUT 1", "LUT 2"],
        ["Title", lut1_title, lut2_title],
        ["Type", lut_data1['lut_type'], lut_data2['lut_type']],
        ["1D Size", str(lut_data1.get('lut_1d_size', 'N/A')), str(lut_data2.get('lut_1d_size', 'N/A'))],
        ["3D Size", str(lut_data1.get('lut_3d_size', 'N/A')), str(lut_data2.get('lut_3d_size', 'N/A'))],
        ["Domain Min", str(lut_data1['domain_min']), str(lut_data2['domain_min'])],
        ["Domain Max", str(lut_data1['domain_max']), str(lut_data2['domain_max'])]
    ]
    
    lut_info_table = Table(lut_info_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    lut_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    content.append(lut_info_table)
    content.append(Spacer(1, 0.3 * inch))
    
    # Differences Analysis
    content.append(Paragraph("Analysis", subtitle_style))
    
    # Calculate differences based on LUT types
    if lut_data1['lut_type'] == '1D' and lut_data2['lut_type'] == '1D':
        # For 1D LUTs, compare directly if same size
        if lut_data1['lut_1d_size'] == lut_data2['lut_1d_size']:
            mean_diff = np.mean(np.abs(lut_data1['lut_1d'] - lut_data2['lut_1d']))
            max_diff = np.max(np.abs(lut_data1['lut_1d'] - lut_data2['lut_1d']))
            
            content.append(Paragraph(f"Mean Absolute Difference: {mean_diff:.6f}", normal_style))
            content.append(Paragraph(f"Maximum Absolute Difference: {max_diff:.6f}", normal_style))
        else:
            content.append(Paragraph("1D LUTs have different sizes, detailed difference analysis not available.", normal_style))
    else:
        content.append(Paragraph("Detailed numerical analysis not available for 3D LUTs or mixed types.", normal_style))
        content.append(Paragraph("Please refer to the plot for visual comparison.", normal_style))
    
    # Add notes and conclusion
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph("Notes:", subtitle_style))
    content.append(Paragraph("- This comparison shows the average RGB response of each LUT to the same linear input values.", normal_style))
    content.append(Paragraph("- The difference curve shows LUT2 values minus LUT1 values.", normal_style))
    content.append(Paragraph("- Logarithmic scale is used on the x-axis for better shadow detail visualization.", normal_style))
    
    # Build the PDF
    doc.build(content)
    
    print(f"Generated comparison report at {output_pdf_path}")


# =========================================
# Exposure Assist reporting (post-LUT look aid)
# =========================================

import csv
import json
from pathlib import Path

EXPOSURE_ASSIST_CHART_DPI = 150
EXPOSURE_ASSIST_FIGURE_BG = "#FFFFFF"
EXPOSURE_ASSIST_TEXT_COLOR = "#111827"
SMALLHD_WORKFLOW_PAGES = (
    {
        "title": "SENSOR SAFETY (pre-Look)",
        "subtitle": "Measure the camera signal before the viewing LUT.",
        "bullets": (
            "Apply SmallHD false color to the clean feed / sensor path.",
            "Protect highlight headroom before any look compresses the signal.",
            "Treat this page as the clipping authority for the capture.",
        ),
    },
    {
        "title": "LOOK EXPOSURE (post-Look)",
        "subtitle": "Measure Rec.709 Y / IRE after the Swiniec display look.",
        "bullets": (
            "Use the per-LUT MAP zones from this report — never a shared scale.",
            "Green = -1 EV target; salmon = face exposure (+0.5 to +1 EV).",
            "Yellow = WARN, orange = HIGH, red = WHITE CLIPPING only.",
        ),
    },
)


def exposure_assist_csv_rows(request):
    """Build CSV rows from an Exposure Assist analysis contract."""
    analysis = _validated_exposure_analysis(request)
    rows = [
        [
            "section",
            "key",
            "ev",
            "minimum_ire",
            "maximum_ire",
            "rec709_y_ire",
            "color",
            "label",
        ]
    ]

    for point in analysis["anchor_points"]:
        rows.append(
            [
                "anchor",
                f"ev_{point['ev']}",
                point["ev"],
                "",
                "",
                point["rec709_y_ire"],
                "",
                "",
            ]
        )

    for zone in analysis["smallhd_zones"]:
        rows.append(
            [
                "zone",
                zone["semantic"],
                "",
                zone["minimum_ire"],
                zone["maximum_ire"],
                "",
                zone["color"],
                zone["label"],
            ]
        )

    clipping = analysis["clipping"]
    rows.append(
        [
            "clipping",
            "signal_ceiling_ire",
            "",
            "",
            "",
            clipping["signal_ceiling_ire"],
            "",
            "Signal ceiling",
        ]
    )
    rows.append(
        [
            "clipping",
            "threshold_ire",
            "",
            "",
            "",
            clipping["threshold_ire"],
            "#DC2626",
            "WHITE CLIPPING threshold",
        ]
    )
    return rows


def false_color_bar_segments(request):
    """Return ordered false-color bar segments for charts and SVG."""
    if not isinstance(request, dict):
        raise TypeError("false_color_bar_segments request must be an object")
    zones = request.get("zones")
    if not isinstance(zones, list) or not zones:
        raise ValueError("zones must be a non-empty list")

    return [
        {
            "semantic": zone["semantic"],
            "label": zone["label"],
            "color": zone["color"],
            "minimum_ire": zone["minimum_ire"],
            "maximum_ire": zone["maximum_ire"],
        }
        for zone in zones
    ]


def generate_exposure_assist_report(request):
    """
    Write per-LUT Exposure Assist charts, JSON, CSV, and multi-page PDF.

    request:
        analysis: contract from analyze_exposure_assist
        output_dir: directory path
        basename: optional file stem (default: source file stem)
    """
    analysis = _validated_exposure_analysis(request)
    output_dir = Path(request["output_dir"]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    source_name = analysis["source"]["file_name"]
    basename = request.get("basename") or Path(source_name).stem
    basename = str(basename).strip() or "exposure_assist"

    artifacts = {}
    artifacts["json"] = str(_write_exposure_json(analysis, output_dir / f"{basename}.json"))
    artifacts["csv"] = str(_write_exposure_csv(analysis, output_dir / f"{basename}.csv"))

    chart_specs = (
        ("ev_ire", _plot_exposure_ev_ire),
        ("rgb_neutral", _plot_exposure_rgb_neutral),
        ("clipping", _plot_exposure_clipping),
        ("false_color_bar", _plot_exposure_false_color_bar),
        ("dashboard", _plot_exposure_dashboard),
    )
    for key, plot_fn in chart_specs:
        png_path = output_dir / f"{basename}_{key}.png"
        svg_path = output_dir / f"{basename}_{key}.svg"
        plot_fn({"analysis": analysis, "png_path": png_path, "svg_path": svg_path})
        artifacts[f"{key}_png"] = str(png_path)
        artifacts[f"{key}_svg"] = str(svg_path)

    workflow = generate_smallhd_workflow_diagram(
        {
            "output_dir": str(output_dir),
            "basename": f"{basename}_smallhd_workflow",
        }
    )
    artifacts["workflow_png"] = workflow["artifacts"]["workflow_png"]
    artifacts["workflow_svg"] = workflow["artifacts"]["workflow_svg"]

    pdf_path = output_dir / f"{basename}_exposure_assist.pdf"
    _write_exposure_assist_pdf(
        {
            "analysis": analysis,
            "artifacts": artifacts,
            "output_pdf_path": pdf_path,
        }
    )
    artifacts["pdf"] = str(pdf_path)

    return {
        "output_dir": str(output_dir),
        "basename": basename,
        "artifacts": artifacts,
    }


def generate_smallhd_workflow_diagram(request):
    """Write the shared two-page SmallHD SENSOR SAFETY / LOOK EXPOSURE diagram."""
    if not isinstance(request, dict):
        raise TypeError("Workflow diagram request must be an object")
    output_dir = Path(request["output_dir"]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    basename = str(request.get("basename") or "smallhd_workflow").strip()

    png_path = output_dir / f"{basename}.png"
    svg_path = output_dir / f"{basename}.svg"
    _plot_smallhd_workflow({"png_path": png_path, "svg_path": svg_path})
    return {
        "output_dir": str(output_dir),
        "artifacts": {
            "workflow_png": str(png_path),
            "workflow_svg": str(svg_path),
        },
    }


def _validated_exposure_analysis(request):
    if not isinstance(request, dict):
        raise TypeError("Exposure Assist report request must be an object")
    analysis = request.get("analysis")
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be an Exposure Assist contract object")
    required = (
        "source",
        "anchor_points",
        "neutral_axis",
        "smallhd_zones",
        "clipping",
        "limitations",
        "confidence",
    )
    for key in required:
        if key not in analysis:
            raise ValueError(f"analysis is missing required key: {key}")
    return analysis


def _write_exposure_json(analysis, path):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(analysis, handle, indent=2, sort_keys=True)
    return path


def _write_exposure_csv(analysis, path):
    rows = exposure_assist_csv_rows({"analysis": analysis})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _save_figure_png_svg(fig, png_path, svg_path):
    png_path = Path(png_path)
    svg_path = Path(svg_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        png_path,
        dpi=EXPOSURE_ASSIST_CHART_DPI,
        bbox_inches="tight",
        facecolor=EXPOSURE_ASSIST_FIGURE_BG,
    )
    fig.savefig(
        svg_path,
        format="svg",
        bbox_inches="tight",
        facecolor=EXPOSURE_ASSIST_FIGURE_BG,
    )
    plt.close(fig)


def _anchor_lookup(analysis):
    return {point["ev"]: point for point in analysis["anchor_points"]}


def _plot_exposure_ev_ire(request):
    analysis = request["analysis"]
    samples = analysis["neutral_axis"]["samples"]
    evs = [sample["ev"] for sample in samples]
    ires = [sample["rec709_y_ire"] for sample in samples]
    anchors = _anchor_lookup(analysis)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)
    ax.plot(evs, ires, color="#0F766E", linewidth=2.0, label="Neutral axis Rec.709 Y")
    for ev, point in anchors.items():
        ax.scatter([ev], [point["rec709_y_ire"]], color="#111827", zorder=5)
        ax.annotate(
            f"{ev:+g} EV\n{point['rec709_y_ire']:.1f} IRE",
            (ev, point["rec709_y_ire"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=7,
            color=EXPOSURE_ASSIST_TEXT_COLOR,
        )
    ax.axhline(
        analysis["clipping"]["threshold_ire"],
        color="#DC2626",
        linestyle="--",
        linewidth=1.2,
        label="WHITE CLIPPING threshold",
    )
    ax.set_title(
        f"EV → Rec.709 Y / IRE — {analysis['source']['file_name']}",
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )
    ax.set_xlabel("Scene EV relative to 18% gray")
    ax.set_ylabel("Display-referred Rec.709 Y (IRE)")
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="lower right")
    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _plot_exposure_rgb_neutral(request):
    analysis = request["analysis"]
    samples = analysis["neutral_axis"]["samples"]
    evs = [sample["ev"] for sample in samples]
    red = [sample["lut_rgb"][0] for sample in samples]
    green = [sample["lut_rgb"][1] for sample in samples]
    blue = [sample["lut_rgb"][2] for sample in samples]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)
    ax.plot(evs, red, color="#DC2626", label="R", linewidth=1.8)
    ax.plot(evs, green, color="#16A34A", label="G", linewidth=1.8)
    ax.plot(evs, blue, color="#2563EB", label="B", linewidth=1.8)
    ax.set_title(
        f"Neutral-axis RGB response — {analysis['source']['file_name']}",
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )
    ax.set_xlabel("Scene EV relative to 18% gray")
    ax.set_ylabel("LUT output (display RGB)")
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="lower right")
    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _plot_exposure_clipping(request):
    analysis = request["analysis"]
    ceiling = analysis["clipping"]["signal_ceiling_ire"]
    threshold = analysis["clipping"]["threshold_ire"]
    standard = analysis["clipping"]["standard_threshold_ire"]
    labels = ["Signal ceiling", "Clipping threshold", "99 IRE standard"]
    values = [ceiling, threshold, standard]
    colors = ["#7C3AED", "#DC2626", "#9CA3AF"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)
    bars = ax.barh(labels, values, color=colors)
    for bar, value in zip(bars, values):
        ax.text(
            value + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f} IRE",
            va="center",
            fontsize=9,
            color=EXPOSURE_ASSIST_TEXT_COLOR,
        )
    ax.set_xlim(0, 110)
    ax.set_xlabel("IRE")
    ax.set_title(
        f"Clipping / ceiling — {analysis['source']['file_name']}",
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )
    ax.grid(True, axis="x", linestyle=":", alpha=0.5)
    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _plot_exposure_false_color_bar(request):
    analysis = request["analysis"]
    segments = false_color_bar_segments({"zones": analysis["smallhd_zones"]})
    fig, ax = plt.subplots(figsize=(11, 3.2))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)

    for segment in segments:
        width = max(segment["maximum_ire"] - segment["minimum_ire"], 0.05)
        ax.barh(
            0,
            width,
            left=segment["minimum_ire"],
            height=0.65,
            color=segment["color"],
            edgecolor="#111827",
            linewidth=0.4,
        )
        mid = segment["minimum_ire"] + width / 2.0
        ax.text(
            mid,
            0.12,
            f"{segment['label']}\n{segment['minimum_ire']:.1f}–{segment['maximum_ire']:.1f}",
            ha="center",
            va="bottom",
            fontsize=6.5,
            color="#111827",
            rotation=0,
        )

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 1.1)
    ax.set_yticks([])
    ax.set_xlabel("Display-referred Rec.709 Y (IRE)")
    ax.set_title(
        f"False-color MAP — {analysis['source']['file_name']}",
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )
    ax.grid(True, axis="x", linestyle=":", alpha=0.4)
    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _plot_exposure_dashboard(request):
    analysis = request["analysis"]
    anchors = _anchor_lookup(analysis)
    zones = analysis["smallhd_zones"]
    confidence = analysis["confidence"]

    fig = plt.figure(figsize=(12, 7.5))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0], hspace=0.35, wspace=0.28)

    ax_curve = fig.add_subplot(gs[0, :])
    samples = analysis["neutral_axis"]["samples"]
    ax_curve.plot(
        [s["ev"] for s in samples],
        [s["rec709_y_ire"] for s in samples],
        color="#0F766E",
        linewidth=2.0,
    )
    for ev in (-1.0, 0.0, 0.5, 1.0, 2.0, 3.0):
        if ev in anchors:
            ax_curve.scatter(
                [ev],
                [anchors[ev]["rec709_y_ire"]],
                color="#111827",
                zorder=5,
            )
    ax_curve.axhline(
        analysis["clipping"]["threshold_ire"],
        color="#DC2626",
        linestyle="--",
        linewidth=1.0,
    )
    ax_curve.set_title("Exposure Assist dashboard", fontsize=14, fontweight="bold")
    ax_curve.set_xlabel("EV")
    ax_curve.set_ylabel("IRE")
    ax_curve.set_ylim(0, 105)
    ax_curve.grid(True, linestyle=":", alpha=0.45)

    ax_targets = fig.add_subplot(gs[1, 0])
    ax_targets.axis("off")
    target_lines = [
        f"Source: {analysis['source']['file_name']}",
        f"Confidence: {confidence['level']} ({confidence['score']})",
        "",
        "Key targets (Rec.709 Y IRE):",
        f"  -1 EV: {anchors[-1.0]['rec709_y_ire']:.2f}",
        f"  0 EV:  {anchors[0.0]['rec709_y_ire']:.2f}",
        f"  +0.5 EV (face low): {anchors[0.5]['rec709_y_ire']:.2f}",
        f"  +1 EV (face high):  {anchors[1.0]['rec709_y_ire']:.2f}",
        f"  WARN (+2 EV): {anchors[2.0]['rec709_y_ire']:.2f}",
        f"  HIGH (+3 EV): {anchors[3.0]['rec709_y_ire']:.2f}",
        f"  WHITE CLIPPING ≥ {analysis['clipping']['threshold_ire']:.2f}",
    ]
    ax_targets.text(
        0.02,
        0.98,
        "\n".join(target_lines),
        va="top",
        ha="left",
        family="monospace",
        fontsize=9,
        transform=ax_targets.transAxes,
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )

    ax_legend = fig.add_subplot(gs[1, 1])
    ax_legend.axis("off")
    legend_y = 0.95
    ax_legend.text(
        0.02,
        legend_y,
        "SmallHD MAP zones (this LUT only)",
        va="top",
        fontsize=10,
        fontweight="bold",
        transform=ax_legend.transAxes,
    )
    legend_y -= 0.08
    for zone in zones:
        ax_legend.add_patch(
            plt.Rectangle(
                (0.02, legend_y - 0.04),
                0.06,
                0.045,
                transform=ax_legend.transAxes,
                color=zone["color"],
                clip_on=False,
            )
        )
        ax_legend.text(
            0.11,
            legend_y - 0.015,
            (
                f"{zone['label']}: "
                f"{zone['minimum_ire']:.1f}–{zone['maximum_ire']:.1f} IRE"
            ),
            va="top",
            fontsize=8,
            transform=ax_legend.transAxes,
            color=EXPOSURE_ASSIST_TEXT_COLOR,
        )
        legend_y -= 0.095

    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _plot_smallhd_workflow(request):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.patch.set_facecolor(EXPOSURE_ASSIST_FIGURE_BG)
    page_colors = ("#1E3A5F", "#0F766E")

    for ax, page, color in zip(axes, SMALLHD_WORKFLOW_PAGES, page_colors):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(
            plt.Rectangle(
                (0.03, 0.08),
                0.94,
                0.84,
                fill=True,
                facecolor="#F8FAFC",
                edgecolor=color,
                linewidth=2.5,
            )
        )
        ax.text(
            0.5,
            0.82,
            page["title"],
            ha="center",
            va="top",
            fontsize=13,
            fontweight="bold",
            color=color,
        )
        ax.text(
            0.5,
            0.68,
            page["subtitle"],
            ha="center",
            va="top",
            fontsize=9,
            color=EXPOSURE_ASSIST_TEXT_COLOR,
            wrap=True,
        )
        bullet_y = 0.52
        for bullet in page["bullets"]:
            ax.text(
                0.1,
                bullet_y,
                f"• {bullet}",
                ha="left",
                va="top",
                fontsize=8.5,
                color=EXPOSURE_ASSIST_TEXT_COLOR,
            )
            bullet_y -= 0.14

    fig.suptitle(
        "SmallHD two-page workflow",
        fontsize=14,
        fontweight="bold",
        color=EXPOSURE_ASSIST_TEXT_COLOR,
    )
    _save_figure_png_svg(fig, request["png_path"], request["svg_path"])


def _write_exposure_assist_pdf(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    analysis = request["analysis"]
    artifacts = request["artifacts"]
    output_pdf_path = Path(request["output_pdf_path"])
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExposureTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "ExposureHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = styles["Normal"]

    doc = SimpleDocTemplate(str(output_pdf_path), pagesize=letter)
    story = []
    source = analysis["source"]
    anchors = _anchor_lookup(analysis)

    story.append(Paragraph("Exposure Assist Report", title_style))
    story.append(
        Paragraph(
            (
                f"LUT: {source['file_name']} &nbsp;|&nbsp; "
                f"Size: {source['lut_size']}³ &nbsp;|&nbsp; "
                f"SHA-256: {source['sha256'][:16]}…"
            ),
            body_style,
        )
    )
    story.append(
        Paragraph(
            (
                "Input assumed as Sony S-Log3 / S-Gamut3.Cine neutral axis. "
                "Outputs are display-referred Rec.709 Y / IRE after the look LUT."
            ),
            body_style,
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("1. Targets", heading_style))
    target_table = Table(
        [
            ["EV", "Rec.709 Y (IRE)", "Role"],
            ["-1.0", f"{anchors[-1.0]['rec709_y_ire']:.3f}", "-1 EV target (green zone)"],
            ["0.0", f"{anchors[0.0]['rec709_y_ire']:.3f}", "Middle gray"],
            ["+0.5", f"{anchors[0.5]['rec709_y_ire']:.3f}", "Face exposure low"],
            ["+1.0", f"{anchors[1.0]['rec709_y_ire']:.3f}", "Face exposure high"],
            ["+2.0", f"{anchors[2.0]['rec709_y_ire']:.3f}", "WARN"],
            ["+3.0", f"{anchors[3.0]['rec709_y_ire']:.3f}", "HIGH"],
        ],
        colWidths=[1.0 * inch, 1.6 * inch, 3.6 * inch],
    )
    target_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.92)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(target_table)
    story.append(PageBreak())

    story.append(Paragraph("2. SmallHD MAP", heading_style))
    zone_rows = [["Zone", "Min IRE", "Max IRE", "Color", "Semantic"]]
    for zone in analysis["smallhd_zones"]:
        zone_rows.append(
            [
                zone["label"],
                f"{zone['minimum_ire']:.3f}",
                f"{zone['maximum_ire']:.3f}",
                zone["color"],
                zone["semantic"],
            ]
        )
    zone_table = Table(
        zone_rows,
        colWidths=[1.7 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 1.8 * inch],
    )
    zone_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.92)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(zone_table)
    story.append(Spacer(1, 0.15 * inch))
    if Path(artifacts["false_color_bar_png"]).is_file():
        story.append(
            Image(artifacts["false_color_bar_png"], width=6.5 * inch, height=1.9 * inch)
        )
    if Path(artifacts["workflow_png"]).is_file():
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("SmallHD two-page workflow", heading_style))
        story.append(
            Image(artifacts["workflow_png"], width=6.5 * inch, height=3.0 * inch)
        )
    story.append(PageBreak())

    story.append(Paragraph("3. Curves", heading_style))
    if Path(artifacts["ev_ire_png"]).is_file():
        story.append(Image(artifacts["ev_ire_png"], width=6.5 * inch, height=3.5 * inch))
    if Path(artifacts["rgb_neutral_png"]).is_file():
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Image(artifacts["rgb_neutral_png"], width=6.5 * inch, height=3.5 * inch)
        )
    story.append(PageBreak())

    story.append(Paragraph("4. Limits", heading_style))
    clipping = analysis["clipping"]
    story.append(
        Paragraph(
            (
                f"Signal ceiling: {clipping['signal_ceiling_ire']:.3f} IRE. "
                f"WHITE CLIPPING threshold: {clipping['threshold_ire']:.3f} IRE. "
                f"Uses measured ceiling: {clipping['uses_measured_ceiling']}."
            ),
            body_style,
        )
    )
    if Path(artifacts["clipping_png"]).is_file():
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Image(artifacts["clipping_png"], width=6.0 * inch, height=3.2 * inch)
        )
    if Path(artifacts["dashboard_png"]).is_file():
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Image(artifacts["dashboard_png"], width=6.5 * inch, height=4.0 * inch)
        )
    story.append(PageBreak())

    story.append(Paragraph("5. Method / review notes", heading_style))
    story.append(
        Paragraph(
            (
                "Method: scene EV → linear (18% × 2^EV) → official S-Log3 → "
                "tetrahedral 3D LUT → Rec.709 luma weights → IRE (×100). "
                "Display look RGB is not re-decoded as camera log."
            ),
            body_style,
        )
    )
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Limitations:", heading_style))
    for limitation in analysis["limitations"]:
        story.append(Paragraph(f"• {limitation}", body_style))
    story.append(Spacer(1, 0.1 * inch))
    confidence = analysis["confidence"]
    story.append(
        Paragraph(
            (
                f"Confidence: {confidence['level']} "
                f"(score {confidence['score']}). "
                f"Checks: {confidence['checks']}."
            ),
            body_style,
        )
    )
    story.append(
        Paragraph(
            (
                "Independent review note: post-LUT MAP is a look exposure aid. "
                "Sensor clipping authority remains on the pre-Look page."
            ),
            body_style,
        )
    )

    doc.build(story)
