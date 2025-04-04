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
