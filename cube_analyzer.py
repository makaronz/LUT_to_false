#!/usr/bin/env python3
"""
CUBE LUT Analyzer
-----------------
A comprehensive tool for analyzing CUBE LUT files, transformations, and generating reports.
"""

import os
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from lut_tools import LUTParser, LUTAnalyzer, LUTTransformationAnalyzer, ReportVisualizer

# Custom JSON encoder for NumPy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def analyze_lut(cube_path, output_folder='lut_reports', source_space=None, target_space=None):
    """
    Perform comprehensive analysis of a LUT file and generate a report
    """
    # Parse the LUT file
    parser = LUTParser(cube_path)
    metadata = parser.get_metadata()
    
    # Infer color spaces if not specified
    if source_space is None or target_space is None:
        inferred_spaces = parser.infer_color_spaces()
        if source_space is None:
            source_space = inferred_spaces['source_space']
        if target_space is None:
            target_space = inferred_spaces['target_space']
    
    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    # Base LUT analysis
    analyzer = LUTAnalyzer(parser)
    lut_report = analyzer.generate_summary_report(output_folder)
    
    # Transformation analysis
    transform_analyzer = LUTTransformationAnalyzer(
        parser, source_space=source_space, target_space=target_space
    )
    transform_report = transform_analyzer.generate_transformation_report(output_folder)
    
    # Generate visualizations
    visualizer = ReportVisualizer(parser, transform_analyzer)
    vis_report = visualizer.generate_report_visualizations(output_folder)
    
    # Combine reports
    report = {
        'metadata': metadata,
        'source_space': source_space,
        'target_space': target_space,
        'lut_analysis': lut_report,
        'transform_analysis': transform_report,
        'visualizations': vis_report
    }
    
    # Save report as JSON
    report_path = output_path / f"{Path(cube_path).stem}_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, cls=NumpyEncoder)
    
    print(f"Analysis complete. Report saved to: {report_path}")
    return report

def analyze_all_luts(folder_path, output_folder='lut_reports'):
    """
    Analyze all .cube files in the specified folder
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")
    
    cube_files = list(folder.glob('*.cube'))
    if not cube_files:
        print(f"No .cube files found in {folder_path}")
        return
    
    print(f"Found {len(cube_files)} .cube files to analyze")
    
    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    # Technical report summary
    summary = {
        'luts': []
    }
    
    # Analyze each LUT
    for cube_file in cube_files:
        print(f"Analyzing: {cube_file.name}...")
        try:
            report = analyze_lut(cube_file, output_folder)
            summary['luts'].append({
                'filename': cube_file.name,
                'source_space': report['source_space'],
                'target_space': report['target_space'],
                'report_path': f"{cube_file.stem}_report.json"
            })
        except Exception as e:
            print(f"Error analyzing {cube_file.name}: {e}")
    
    # Save summary report
    summary_path = output_path / "lut_analysis_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, cls=NumpyEncoder)
    
    print(f"Analysis complete. Summary saved to: {summary_path}")
    return summary

def generate_technical_document(summary, output_folder='lut_reports'):
    """
    Generate a comprehensive technical document from analysis results
    """
    output_path = Path(output_folder)
    
    # Load all individual reports
    reports = []
    for lut in summary['luts']:
        report_path = output_path / lut['report_path']
        if report_path.exists():
            with open(report_path, 'r') as f:
                reports.append(json.load(f))
    
    # Create markdown document
    doc_path = output_path / "LUT_Technical_Analysis.md"
    
    with open(doc_path, 'w') as f:
        f.write("# Technical Analysis of LUT Files\n\n")
        f.write("## Overview\n\n")
        f.write(f"This document provides a comprehensive analysis of {len(reports)} LUT files.\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Summary](#summary)\n")
        f.write("2. [LUT Specifications](#lut-specifications)\n")
        f.write("3. [Color Space Transformations](#color-space-transformations)\n")
        for i, report in enumerate(reports):
            lut_name = Path(report['metadata']['filename']).stem
            f.write(f"{i+4}. [{lut_name}](#lut-{i+1})\n")
        f.write("\n")
        
        # Summary section
        f.write("## Summary\n\n")
        f.write("| LUT | Source Space | Target Space | Accuracy Score | Dynamic Range |\n")
        f.write("|-----|--------------|--------------|----------------|---------------|\n")
        
        for report in reports:
            lut_name = Path(report['metadata']['filename']).stem
            source = report['source_space']
            target = report['target_space']
            
            # Get accuracy score if available
            accuracy = report.get('transform_analysis', {}).get('transformation_accuracy', {}).get('accuracy_score', 'N/A')
            if isinstance(accuracy, float):
                accuracy = f"{accuracy:.2%}"
            
            # Get dynamic range
            dynamic_range = report.get('lut_analysis', {}).get('dynamic_range', {}).get('dynamic_range_ratio', 'N/A')
            if isinstance(dynamic_range, float):
                dynamic_range = f"{dynamic_range:.2f}"
            
            f.write(f"| {lut_name} | {source} | {target} | {accuracy} | {dynamic_range} |\n")
        
        f.write("\n")
        
        # LUT Specifications
        f.write("## LUT Specifications\n\n")
        f.write("| LUT | Size | Min RGB | Max RGB | Dominant Channel |\n")
        f.write("|-----|------|---------|---------|------------------|\n")
        
        for report in reports:
            lut_name = Path(report['metadata']['filename']).stem
            size = report['metadata'].get('size', 'N/A')
            
            min_rgb = 'N/A'
            max_rgb = 'N/A'
            dominant = 'N/A'
            
            color_stats = report.get('lut_analysis', {}).get('color_stats', {})
            if color_stats:
                min_vals = color_stats.get('min', [0, 0, 0])
                max_vals = color_stats.get('max', [1, 1, 1])
                min_rgb = f"[{min_vals[0]:.3f}, {min_vals[1]:.3f}, {min_vals[2]:.3f}]"
                max_rgb = f"[{max_vals[0]:.3f}, {max_vals[1]:.3f}, {max_vals[2]:.3f}]"
            
            color_bias = report.get('lut_analysis', {}).get('color_bias', {}).get('overall_bias', {})
            if color_bias:
                dominant = color_bias.get('dominant_channel', 'N/A')
            
            f.write(f"| {lut_name} | {size}x{size}x{size} | {min_rgb} | {max_rgb} | {dominant} |\n")
        
        f.write("\n")
        
        # Color Space Transformations
        f.write("## Color Space Transformations\n\n")
        f.write("| LUT | Source → Target | Mean Error | Max Error | RMSE | Correlation |\n")
        f.write("|-----|-----------------|------------|-----------|------|-------------|\n")
        
        for report in reports:
            lut_name = Path(report['metadata']['filename']).stem
            source = report['source_space']
            target = report['target_space']
            transform = f"{source} → {target}"
            
            accuracy = report.get('transform_analysis', {}).get('transformation_accuracy', {})
            mean_error = 'N/A'
            max_error = 'N/A'
            rmse = 'N/A'
            correlation = 'N/A'
            
            if accuracy:
                mean_error = f"{accuracy.get('mean_absolute_error', 0):.4f}"
                max_error = f"{accuracy.get('max_absolute_error', 0):.4f}"
                rmse = f"{accuracy.get('rmse', 0):.4f}"
                corr = accuracy.get('correlation', 0)
                correlation = f"{corr:.4f}"
            
            f.write(f"| {lut_name} | {transform} | {mean_error} | {max_error} | {rmse} | {correlation} |\n")
        
        f.write("\n")
        
        # Individual LUT analyses
        for i, report in enumerate(reports):
            lut_name = Path(report['metadata']['filename']).stem
            f.write(f"## LUT {i+1}: {lut_name}\n\n")
            
            # Get metadata
            metadata = report['metadata']
            title = metadata.get('title', 'Not specified')
            source = report['source_space']
            target = report['target_space']
            
            f.write(f"**Filename:** {metadata['filename']}  \n")
            f.write(f"**Title:** {title}  \n")
            f.write(f"**Source Color Space:** {source}  \n")
            f.write(f"**Target Color Space:** {target}  \n")
            f.write(f"**LUT Size:** {metadata.get('size', 'N/A')}x{metadata.get('size', 'N/A')}x{metadata.get('size', 'N/A')}  \n\n")
            
            # Color Analysis
            f.write("### Color Analysis\n\n")
            
            color_stats = report.get('lut_analysis', {}).get('color_stats', {})
            if color_stats:
                min_vals = color_stats.get('min', [0, 0, 0])
                max_vals = color_stats.get('max', [1, 1, 1])
                mean_vals = color_stats.get('mean', [0.5, 0.5, 0.5])
                std_vals = color_stats.get('std', [0, 0, 0])
                
                f.write("**RGB Range:**  \n")
                f.write(f"- Min: [{min_vals[0]:.4f}, {min_vals[1]:.4f}, {min_vals[2]:.4f}]  \n")
                f.write(f"- Max: [{max_vals[0]:.4f}, {max_vals[1]:.4f}, {max_vals[2]:.4f}]  \n")
                f.write(f"- Mean: [{mean_vals[0]:.4f}, {mean_vals[1]:.4f}, {mean_vals[2]:.4f}]  \n")
                f.write(f"- Std: [{std_vals[0]:.4f}, {std_vals[1]:.4f}, {std_vals[2]:.4f}]  \n\n")
            
            # Dynamic Range
            dynamic_range = report.get('lut_analysis', {}).get('dynamic_range', {})
            if dynamic_range:
                shadow_clip = dynamic_range.get('shadow_clip', {})
                highlight_clip = dynamic_range.get('highlight_clip', {})
                dr_ratio = dynamic_range.get('dynamic_range_ratio', 0)
                
                f.write("**Dynamic Range:**  \n")
                f.write(f"- Shadow Clipping: R={shadow_clip.get('r', 0):.4f}, G={shadow_clip.get('g', 0):.4f}, B={shadow_clip.get('b', 0):.4f}  \n")
                f.write(f"- Highlight Clipping: R={highlight_clip.get('r', 1):.4f}, G={highlight_clip.get('g', 1):.4f}, B={highlight_clip.get('b', 1):.4f}  \n")
                f.write(f"- Dynamic Range Ratio: {dr_ratio:.2f}  \n\n")
            
            # Color Bias
            color_bias = report.get('lut_analysis', {}).get('color_bias', {})
            if color_bias:
                overall = color_bias.get('overall_bias', {})
                f.write("**Color Bias:**  \n")
                f.write(f"- Red Ratio: {overall.get('r_ratio', 1):.4f}  \n")
                f.write(f"- Green Ratio: {overall.get('g_ratio', 1):.4f}  \n")
                f.write(f"- Blue Ratio: {overall.get('b_ratio', 1):.4f}  \n")
                f.write(f"- Dominant Channel: {overall.get('dominant_channel', 'None')}  \n\n")
            
            # Tonal Smoothness
            smoothness = report.get('lut_analysis', {}).get('tonal_smoothness', {})
            if smoothness:
                scores = smoothness.get('smoothness_scores', {})
                banding = smoothness.get('banding_regions', {})
                
                f.write("**Tonal Smoothness:**  \n")
                f.write(f"- Red Smoothness: {scores.get('r', 0):.4f}  \n")
                f.write(f"- Green Smoothness: {scores.get('g', 0):.4f}  \n")
                f.write(f"- Blue Smoothness: {scores.get('b', 0):.4f}  \n")
                f.write(f"- Overall Smoothness: {scores.get('overall', 0):.4f}  \n")
                f.write(f"- Banding Regions: R={banding.get('r', 0):.2%}, G={banding.get('g', 0):.2%}, B={banding.get('b', 0):.2%}  \n\n")
            
            # Transformation Accuracy
            f.write("### Transformation Accuracy\n\n")
            
            accuracy = report.get('transform_analysis', {}).get('transformation_accuracy', {})
            if accuracy:
                f.write(f"**Overall Accuracy Score: {accuracy.get('accuracy_score', 0):.2%}**  \n\n")
                f.write(f"- Mean Absolute Error: {accuracy.get('mean_absolute_error', 0):.4f}  \n")
                f.write(f"- Maximum Error: {accuracy.get('max_absolute_error', 0):.4f}  \n")
                f.write(f"- RMSE: {accuracy.get('rmse', 0):.4f}  \n")
                f.write(f"- Correlation: {accuracy.get('correlation', 0):.4f}  \n\n")
                
                channel_errors = accuracy.get('channel_errors', {})
                f.write("**Channel Errors:**  \n")
                f.write(f"- Red: {channel_errors.get('r', 0):.4f}  \n")
                f.write(f"- Green: {channel_errors.get('g', 0):.4f}  \n")
                f.write(f"- Blue: {channel_errors.get('b', 0):.4f}  \n\n")
            
            # Visualizations
            f.write("### Visualizations\n\n")
            
            vis = report.get('visualizations', {})
            plots = report.get('lut_analysis', {}).get('plot_paths', {})
            transform_plot = report.get('transform_analysis', {}).get('plot_path', '')
            
            if plots:
                dist_plot = plots.get('distribution', '')
                curves_plot = plots.get('curves', '')
                
                if dist_plot:
                    rel_path = os.path.basename(dist_plot)
                    f.write(f"![RGB Distribution]({rel_path})  \n")
                    f.write("*RGB Distribution*  \n\n")
                
                if curves_plot:
                    rel_path = os.path.basename(curves_plot)
                    f.write(f"![Color Curves]({rel_path})  \n")
                    f.write("*Color Curves*  \n\n")
            
            if transform_plot:
                rel_path = os.path.basename(transform_plot)
                f.write(f"![Transformation Comparison]({rel_path})  \n")
                f.write("*Transformation Comparison*  \n\n")
            
            if vis:
                cc_plot = vis.get('colorchecker', '')
                lin_ramps = vis.get('linear_ramps', '')
                log_ramps = vis.get('log_ramps', '')
                
                if cc_plot:
                    rel_path = os.path.basename(cc_plot)
                    f.write(f"![ColorChecker]({rel_path})  \n")
                    f.write("*ColorChecker Before/After*  \n\n")
                
                if lin_ramps:
                    rel_path = os.path.basename(lin_ramps)
                    f.write(f"![Linear Ramps]({rel_path})  \n")
                    f.write("*Linear Gradient Ramps*  \n\n")
                
                if log_ramps:
                    rel_path = os.path.basename(log_ramps)
                    f.write(f"![Log Ramps]({rel_path})  \n")
                    f.write("*Logarithmic Gradient Ramps*  \n\n")
            
            # Summary and Technical Assessment
            f.write("### Technical Assessment\n\n")
            
            # Compute overall quality score based on various metrics
            accuracy_score = accuracy.get('accuracy_score', 0) if accuracy else 0
            smoothness_score = smoothness.get('smoothness_scores', {}).get('overall', 0) if smoothness else 0
            banding_penalty = sum(banding.values()) / 3 if banding else 0
            
            quality_score = (accuracy_score * 0.5) + (smoothness_score * 0.3) - (banding_penalty * 0.2)
            quality_score = max(0, min(1, quality_score))  # Clamp to 0-1
            
            quality_rating = "Excellent" if quality_score > 0.9 else \
                            "Very Good" if quality_score > 0.8 else \
                            "Good" if quality_score > 0.7 else \
                            "Satisfactory" if quality_score > 0.6 else \
                            "Fair" if quality_score > 0.5 else \
                            "Poor" if quality_score > 0.3 else "Very Poor"
            
            f.write(f"**Overall Quality Rating: {quality_rating} ({quality_score:.2%})**\n\n")
            
            # Generate automatic technical assessment
            f.write("**Strengths:**  \n")
            
            if accuracy and accuracy.get('accuracy_score', 0) > 0.8:
                f.write("- High accuracy in color space transformation  \n")
            
            if smoothness and smoothness.get('smoothness_scores', {}).get('overall', 0) > 0.8:
                f.write("- Excellent tonal smoothness with minimal banding  \n")
            
            if dynamic_range and dynamic_range.get('dynamic_range_ratio', 0) > 5:
                f.write("- Good dynamic range preservation  \n")
            
            if color_bias and abs(1 - color_bias.get('overall_bias', {}).get('r_ratio', 1)) < 0.1 and \
               abs(1 - color_bias.get('overall_bias', {}).get('g_ratio', 1)) < 0.1 and \
               abs(1 - color_bias.get('overall_bias', {}).get('b_ratio', 1)) < 0.1:
                f.write("- Well-balanced color rendition  \n")
            
            f.write("\n**Weaknesses:**  \n")
            
            if accuracy and accuracy.get('accuracy_score', 0) < 0.6:
                f.write("- Lower accuracy in color transformation  \n")
            
            if smoothness and smoothness.get('smoothness_scores', {}).get('overall', 0) < 0.6:
                f.write("- Potential banding issues in smooth gradients  \n")
            
            if banding and any(v > 0.1 for v in banding.values()):
                f.write("- Noticeable banding in certain tonal regions  \n")
            
            if dynamic_range and dynamic_range.get('dynamic_range_ratio', 0) < 4:
                f.write("- Limited dynamic range  \n")
            
            if color_bias and \
               (abs(1 - color_bias.get('overall_bias', {}).get('r_ratio', 1)) > 0.2 or \
                abs(1 - color_bias.get('overall_bias', {}).get('g_ratio', 1)) > 0.2 or \
                abs(1 - color_bias.get('overall_bias', {}).get('b_ratio', 1)) > 0.2):
                dominant = color_bias.get('overall_bias', {}).get('dominant_channel', '')
                f.write(f"- Color bias toward {dominant} channel  \n")
            
            f.write("\n**Recommended Applications:**  \n")
            
            if source == 'S-Log3/S-Gamut3' and target == 'Rec.709':
                f.write("- Sony camera footage grading  \n")
            elif source == 'ARRI LogC/AWG' and target == 'Rec.709':
                f.write("- ARRI camera footage grading  \n")
            elif source == 'RED Log3G10/REDWideGamut' and target == 'Rec.709':
                f.write("- RED camera footage grading  \n")
            
            if 'stylized' in target.lower() or 'creative' in target.lower():
                f.write("- Creative color grading  \n")
            elif quality_score > 0.8:
                f.write("- Professional production work  \n")
            elif quality_score > 0.6:
                f.write("- Semi-professional and enthusiast work  \n")
            else:
                f.write("- Experimental or specific creative effects  \n")
            
            f.write("\n---\n\n")
    
    print(f"Technical document generated: {doc_path}")
    return doc_path

def main():
    parser = argparse.ArgumentParser(description="Analyze CUBE LUT files and generate technical reports")
    parser.add_argument('input', help="Path to a CUBE file or directory containing CUBE files")
    parser.add_argument('--output', '-o', default='lut_reports', help="Output directory for reports")
    parser.add_argument('--source', '-s', help="Override source color space")
    parser.add_argument('--target', '-t', help="Override target color space")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file() and input_path.suffix.lower() == '.cube':
        # Single file analysis
        analyze_lut(str(input_path), args.output, args.source, args.target)
    elif input_path.is_dir():
        # Directory analysis
        summary = analyze_all_luts(str(input_path), args.output)
        generate_technical_document(summary, args.output)
    else:
        print(f"Error: Input must be a .cube file or a directory containing .cube files")
        return 1
    
    return 0

if __name__ == '__main__':
    main() 