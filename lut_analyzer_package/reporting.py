# -*- coding: utf-8 -*-
"""
Moduł odpowiedzialny za generowanie raportów, wykresów i analiz porównawczych LUT.
"""

import numpy as np
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
from typing import Callable, Dict, Optional

# Importuj funkcje interpolacji z tego samego pakietu
from .lut_interpolation import interpolate_1d_lut, interpolate_3d_lut

# =========================================
# Funkcje Analizy i Porównania
# =========================================

def compare_lut_to_curve(lut_data: dict, curve_func: Callable[[np.ndarray], np.ndarray], num_points: int = 100) -> Dict[str, np.ndarray]:
    """
    Compares LUT output to a reference curve.

    Args:
        lut_data (dict): Loaded LUT data from load_cube_file.
        curve_func (Callable): Function implementing the reference curve (e.g., linear_to_slog3).
        num_points (int): Number of points for comparison.

    Returns:
        dict: Dictionary containing 'input_linear', 'lut_output', 'curve_output'.
              Outputs are typically in the log/gamma domain of the curve_func.
    """
    print(f"Comparing LUT '{lut_data.get('title', 'N/A')}' to {curve_func.__name__}...")

    domain_min = lut_data['domain_min']
    domain_max = lut_data['domain_max']

    # Generate linear input values across the domain (use first channel's domain for simplicity)
    # Add small epsilon to avoid potential issues at exact domain boundaries if needed
    input_linear = np.linspace(domain_min[0], domain_max[0], num_points)
    input_linear_rgb = np.stack([input_linear] * 3, axis=-1) # Create RGB triplets

    # Apply reference curve to linear input
    try:
        curve_output = curve_func(input_linear)
    except Exception as e:
        print(f"Warning: Error applying reference curve {curve_func.__name__}: {e}")
        curve_output = np.full_like(input_linear, np.nan) # Return NaN on error


    # Apply LUT
    lut_output_rgb = None
    try:
        if lut_data['lut_type'] == '1D':
            if not lut_data.get('lut_1d_size') or lut_data['lut_1d'].size == 0:
                 raise ValueError("LUT type is 1D, but no 1D data found.")
            lut_output_rgb = interpolate_1d_lut(lut_data['lut_1d'], input_linear, domain_min[0], domain_max[0])
        elif lut_data['lut_type'] == '3D':
            if not lut_data.get('lut_3d_size') or lut_data['lut_3d'].size == 0:
                 raise ValueError("LUT type is 3D, but no 3D data found.")
            # Assuming LUT expects linear input for now. Needs refinement if LUT expects log.
            lut_output_rgb = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], input_linear_rgb, domain_min, domain_max)
        elif lut_data['lut_type'] == 'both':
            shaped_input_rgb = input_linear_rgb # Default if no 1D part
            if lut_data.get('lut_1d_size') and lut_data['lut_1d'].size > 0:
                shaped_input_rgb = interpolate_1d_lut(lut_data['lut_1d'], input_linear, domain_min[0], domain_max[0])

            if lut_data.get('lut_3d_size') and lut_data['lut_3d'].size > 0:
                # Assuming [0,1] domain for the 3D part after 1D shaper
                lut_output_rgb = interpolate_3d_lut(lut_data['lut_3d'], lut_data['lut_3d_size'], shaped_input_rgb, [0.0]*3, [1.0]*3)
            else:
                # If only 1D part exists in 'both' type, use its output
                lut_output_rgb = shaped_input_rgb
        else:
            raise ValueError(f"Unsupported lut_type: {lut_data['lut_type']}")

    except Exception as e:
        print(f"Warning: Error applying LUT: {e}")
        lut_output_rgb = np.full((num_points, 3), np.nan) # Return NaN array on error


    # For comparison, often want the luminance or average of the LUT output
    # Assuming LUT output is comparable to curve_output (e.g., both are log/gamma)
    # Taking the average of RGB channels as a simple representation
    if lut_output_rgb is not None:
        lut_output_mono = np.mean(lut_output_rgb, axis=1)
    else:
        lut_output_mono = np.full_like(input_linear, np.nan)


    return {
        'input_linear': input_linear,
        'lut_output': lut_output_mono, # Or lut_output_rgb if needed
        'curve_output': curve_output
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
        if not np.isnan(comparison_data['curve_output']).all():
            plt.plot(comparison_data['input_linear'], comparison_data['curve_output'], label='Reference Curve', linestyle='--')
        else:
            print("Warning: Reference curve data contains NaNs, skipping plot.")

        if not np.isnan(comparison_data['lut_output']).all():
            plt.plot(comparison_data['input_linear'], comparison_data['lut_output'], label='LUT Output (Avg RGB)')
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
