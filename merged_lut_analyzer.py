#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Główny skrypt analizatora LUT, wykorzystujący moduły z pakietu lut_analyzer_package.

Ten skrypt obsługuje interfejs linii komend (CLI) do analizy plików .cube,
porównywania ich z krzywymi referencyjnymi i generowania raportów.
"""

import argparse
import os
import sys
import numpy as np # Potrzebne do testów konwersji w bloku testowym

# Importuj funkcje z pakietu
from lut_analyzer_package.lut_parsing import load_cube_file
from lut_analyzer_package.reporting import compare_lut_to_curve, plot_lut_vs_curve, generate_pdf_report
# Importuj wszystkie funkcje transferu, aby zbudować CURVE_MAP
from lut_analyzer_package.transfer_functions import *
# Importuj funkcje przestrzeni kolorów (jeśli będą potrzebne w przyszłości w main)
# from lut_analyzer_package.color_space import *

# =========================================
# Główna logika / CLI
# =========================================

# Dictionary mapping curve names to functions (using imported functions)
# Note: This relies on the functions being imported from transfer_functions using '*'
# A more explicit approach might be preferred in larger projects.
CURVE_MAP = {
    "logc3": linear_to_logc3,
    "logc4": linear_to_logc4,
    "slog3": linear_to_slog3,
    "slog2": linear_to_slog2,
    "rec709": linear_to_rec709, # OETF
    "gamma22": linear_to_redgamma4, # Alias for Gamma 2.2 approx
    "gamma24": linear_to_redgamma3, # Alias for Gamma 2.4 approx
    "log3g10": linear_to_log3g10,
    "acescct": linear_to_acescct,
    "acescc": linear_to_acescc,
    "acesproxy10": linear_to_acesproxy10,
    "vlog": linear_to_vlog,
    "clog2": linear_to_canonlog2, # Canon Log 2
    "pq": linear_to_pq,
    "hlg": linear_to_hlg,
    "redlogfilm": linear_to_redlogfilm,
    "redipp2odt": linear_to_red_ipp2_odt_approx,
    # Add inverse functions if needed for specific analyses
}

def main():
    """Main function to handle CLI arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description="LUT Analyzer Tool: Analyzes .cube LUTs, compares them to reference curves, and generates reports.",
        formatter_class=argparse.RawTextHelpFormatter # Preserve formatting in help
    )
    parser.add_argument("lut_path", help="Path to the .cube LUT file")
    parser.add_argument("--curve", default="slog3", choices=sorted(CURVE_MAP.keys()),
                        help="Reference curve name for comparison.\nAvailable curves:\n" + "\n".join(f"- {k}" for k in sorted(CURVE_MAP.keys())))
    parser.add_argument("--output", default="lut_report.pdf",
                        help="Output PDF report path. Plot PNG will be saved with the same base name.")
    parser.add_argument("--num_points", type=int, default=100,
                        help="Number of points for curve comparison (default: 100).")
    # Add more arguments as needed (e.g., --false_color_standard)

    args = parser.parse_args()

    print(f"Analyzing LUT: {args.lut_path}")
    print(f"Reference curve: {args.curve}")
    print(f"Output report: {args.output}")
    print(f"Comparison points: {args.num_points}")

    try:
        # --- Load LUT ---
        lut_data = load_cube_file(args.lut_path)
        print(f"\nSuccessfully loaded LUT: {lut_data.get('title', 'No Title')}")
        print(f"Type: {lut_data['lut_type']}, 1D Size: {lut_data['lut_1d_size']}, 3D Size: {lut_data['lut_3d_size']}")
        print(f"Domain: {lut_data['domain_min']} -> {lut_data['domain_max']}")

        # --- Get Curve Function ---
        curve_func = CURVE_MAP.get(args.curve)
        if not curve_func:
            raise ValueError(f"Invalid curve name: {args.curve}") # Should be caught by argparse

        # --- Run Analysis Steps ---
        print("\nStarting analysis...")
        comparison_data = compare_lut_to_curve(lut_data, curve_func, num_points=args.num_points)

        # --- Generate Plot ---
        plot_png_path = os.path.splitext(args.output)[0] + ".png"
        plot_title = f"LUT '{lut_data.get('title', os.path.basename(args.lut_path))}' vs {args.curve.upper()}"
        plot_lut_vs_curve(comparison_data, plot_title, plot_png_path)

        # TODO: Add False Color analysis call here if implemented

        # --- Generate PDF Report ---
        generate_pdf_report(lut_data, plot_png_path, args.output)

        print("\nAnalysis complete.")

    except (FileNotFoundError, ValueError, IOError, argparse.ArgumentError) as e:
        print(f"\nError during analysis: {e}", file=sys.stderr)
        sys.exit(1) # Exit with error code
    except ImportError as e:
         print(f"\nImport Error: {e}. Please ensure all dependencies are installed.", file=sys.stderr)
         print("You might need to run: pip install -r requirements.txt", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        # Consider logging traceback for unexpected errors
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # --- Basic Test (only if no CLI args provided) ---
    if len(sys.argv) == 1: # No arguments provided, run basic test
        print("No CLI arguments provided. Running basic test with example.cube (if exists)...")
        example_cube_path = 'example.cube'
        output_dir = 'test_output' # Save test files in a subdirectory
        output_report_path = os.path.join(output_dir, 'test_report.pdf')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(example_cube_path):
             print(f"Creating dummy {example_cube_path} for testing...")
             dummy_content = """# Dummy 3D LUT
TITLE "Dummy Test LUT"
LUT_3D_SIZE 2
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0

# R G B   R G B
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""
             try:
                 with open(example_cube_path, 'w') as f:
                     f.write(dummy_content)
             except IOError as e:
                 print(f"Could not create dummy file: {e}")

        if os.path.exists(example_cube_path):
            # Simulate CLI arguments for the test
            test_args = ['merged_lut_analyzer.py', example_cube_path, '--curve', 'rec709', '--output', output_report_path]
            # Temporarily replace sys.argv for argparse
            original_argv = sys.argv
            sys.argv = test_args
            try:
                main()
            finally:
                sys.argv = original_argv # Restore original argv
        else:
            print(f"{example_cube_path} not found, skipping test.")

        # Test some conversions separately (using imported functions)
        linear_vals = np.array([0.0, 0.01, 0.18, 0.5, 1.0])
        print("\n--- Conversion Tests ---")
        print("LogC4 Encode:", linear_to_logc4(linear_vals))
        print("LogC4 Decode:", logc4_to_linear(linear_to_logc4(linear_vals)))
        print("\nLogC3 Encode:", linear_to_logc3(linear_vals))
        print("LogC3 Decode:", logc3_to_linear(linear_to_logc3(linear_vals)))
        print("\nSLog3 Encode:", linear_to_slog3(linear_vals))
        print("SLog3 Decode:", slog3_to_linear(linear_to_slog3(linear_vals)))
        print("\nRec709 Encode:", linear_to_rec709(linear_vals))
        print("Rec709 Decode:", rec709_to_linear(linear_to_rec709(linear_vals)))
        print("--- End Conversion Tests ---")
    else:
        # If CLI arguments were provided, just run main
        main()
