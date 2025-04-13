import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
from pathlib import Path
import os

class ColorChecker:
    """
    Generate and transform a standard color checker for visual comparison
    """
    # Standard 24-patch ColorChecker Classic colors in sRGB
    COLORCHECKER_SRGB = np.array([
        [0.4, 0.4, 0.4],      # Gray 1
        [0.5, 0.5, 0.5],      # Gray 2
        [0.6, 0.6, 0.6],      # Gray 3
        [0.7, 0.7, 0.7],      # Gray 4
        [0.8, 0.8, 0.8],      # Gray 5
        [0.9, 0.9, 0.9],      # Gray 6
        [0.1, 0.1, 0.1],      # Black
        [0.2, 0.2, 0.2],      # Gray 7
        [0.3, 0.3, 0.3],      # Gray 8
        [0.243, 0.143, 0.127],  # Dark Skin
        [0.709, 0.281, 0.228],  # Light Skin
        [0.145, 0.293, 0.537],  # Blue Sky
        [0.138, 0.389, 0.149],  # Foliage
        [0.654, 0.545, 0.033],  # Yellow
        [0.494, 0.153, 0.371],  # Magenta
        [0.193, 0.535, 0.750],  # Cyan
        [0.929, 0.138, 0.063],  # Red
        [0.98, 0.505, 0.047],   # Orange
        [0.827, 0.196, 0.573],  # Purple
        [0.786, 0.633, 0.130],  # Yellow Green
        [0.847, 0.035, 0.463],  # Magenta Pink
        [0.086, 0.646, 0.591],  # Blue Green
        [0.017, 0.216, 0.503],  # Blue
        [0.970, 0.797, 0.018]   # Yellow
    ])
    
    def __init__(self, transform_function=None):
        """
        Initialize with an optional transform function
        """
        self.transform_function = transform_function
    
    def get_srgb_colorchecker(self):
        """Get the standard ColorChecker in sRGB space"""
        return self.COLORCHECKER_SRGB
    
    def transform_colorchecker(self, colorchecker, transform_function):
        """
        Apply a transform function to each color in the checker
        
        transform_function: A function that takes RGB values and returns transformed RGB values
        """
        transformed = np.zeros_like(colorchecker)
        for i in range(len(colorchecker)):
            rgb = colorchecker[i].reshape(1, 3)
            transformed[i] = transform_function(rgb).flatten()
        
        # Clip values to valid range
        transformed = np.clip(transformed, 0.0, 1.0)
        return transformed
    
    def plot_colorchecker_comparison(self, original, transformed, save_path=None, title=None):
        """
        Plot original and transformed color checkers side by side
        
        original: Original ColorChecker array
        transformed: Transformed ColorChecker array
        save_path: Optional file path to save the plot
        title: Optional plot title
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Set up the checker display grid
        rows, cols = 4, 6
        patch_size = 1.0
        
        # Display original
        for i in range(len(original)):
            row = i // cols
            col = i % cols
            
            # Create rectangle patch
            rect = plt.Rectangle(
                (col * patch_size, row * patch_size),
                patch_size, patch_size, 
                color=original[i],
                ec='k', lw=1
            )
            ax1.add_patch(rect)
        
        ax1.set_xlim(0, cols * patch_size)
        ax1.set_ylim(0, rows * patch_size)
        ax1.set_title('Original ColorChecker')
        ax1.set_aspect('equal')
        ax1.set_xticks([])
        ax1.set_yticks([])
        
        # Display transformed
        for i in range(len(transformed)):
            row = i // cols
            col = i % cols
            
            # Create rectangle patch
            rect = plt.Rectangle(
                (col * patch_size, row * patch_size),
                patch_size, patch_size, 
                color=transformed[i],
                ec='k', lw=1
            )
            ax2.add_patch(rect)
        
        ax2.set_xlim(0, cols * patch_size)
        ax2.set_ylim(0, rows * patch_size)
        ax2.set_title('Transformed ColorChecker')
        ax2.set_aspect('equal')
        ax2.set_xticks([])
        ax2.set_yticks([])
        
        if title:
            plt.suptitle(title)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()


class GradientVisualizer:
    """
    Generate and transform gradient ramps for visual comparison
    """
    def __init__(self, transform_function=None):
        """
        Initialize with an optional transform function
        """
        self.transform_function = transform_function
    
    def generate_gray_ramp(self, steps=100, log=False):
        """
        Generate a gray ramp (linear or logarithmic)
        
        steps: Number of steps in the ramp
        log: If True, use logarithmic spacing
        
        Returns array of shape (steps, 3) with RGB values
        """
        if log:
            # Logarithmic spacing (more detail in shadows)
            values = np.logspace(-3, 0, steps)
            # Normalize to 0-1 range
            values = (values - np.min(values)) / (np.max(values) - np.min(values))
        else:
            # Linear spacing
            values = np.linspace(0, 1, steps)
        
        # Create RGB array (identical values for R, G, B)
        gray_ramp = np.column_stack([values, values, values])
        return gray_ramp
    
    def generate_rgb_ramps(self, steps=100):
        """
        Generate RGB primary ramps
        
        Returns a list of three ramps (R, G, B) each of shape (steps, 3)
        """
        values = np.linspace(0, 1, steps)
        
        # Red ramp (R varies, G and B are 0)
        r_ramp = np.column_stack([values, np.zeros_like(values), np.zeros_like(values)])
        
        # Green ramp (G varies, R and B are 0)
        g_ramp = np.column_stack([np.zeros_like(values), values, np.zeros_like(values)])
        
        # Blue ramp (B varies, R and G are 0)
        b_ramp = np.column_stack([np.zeros_like(values), np.zeros_like(values), values])
        
        return [r_ramp, g_ramp, b_ramp]
    
    def transform_ramp(self, ramp, transform_function):
        """
        Apply a transform function to each color in the ramp
        
        transform_function: A function that takes RGB values and returns transformed RGB values
        """
        transformed = np.zeros_like(ramp)
        for i in range(len(ramp)):
            rgb = ramp[i].reshape(1, 3)
            transformed[i] = transform_function(rgb).flatten()
        
        # Clip values to valid range
        transformed = np.clip(transformed, 0.0, 1.0)
        return transformed
    
    def plot_gradient_comparison(self, original_ramps, transformed_ramps, save_path=None, title=None):
        """
        Plot original and transformed gradients side by side
        
        original_ramps: List of original ramp arrays
        transformed_ramps: List of transformed ramp arrays
        save_path: Optional file path to save the plot
        title: Optional plot title
        """
        fig = plt.figure(figsize=(12, 8))
        gs = GridSpec(4, 2)
        
        # Gray ramp comparison (top row)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        
        # RGB ramps (bottom three rows)
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])
        ax5 = fig.add_subplot(gs[2, 0])
        ax6 = fig.add_subplot(gs[2, 1])
        ax7 = fig.add_subplot(gs[3, 0])
        ax8 = fig.add_subplot(gs[3, 1])
        
        # Plot gray ramp
        for i in range(len(original_ramps[0])):
            color = original_ramps[0][i]
            ax1.add_patch(plt.Rectangle(
                (i / len(original_ramps[0]), 0), 
                1 / len(original_ramps[0]), 1, 
                color=color, ec=None
            ))
            
            color = transformed_ramps[0][i]
            ax2.add_patch(plt.Rectangle(
                (i / len(transformed_ramps[0]), 0), 
                1 / len(transformed_ramps[0]), 1, 
                color=color, ec=None
            ))
        
        ax1.set_title('Original Gray Ramp')
        ax2.set_title('Transformed Gray Ramp')
        
        # Plot R, G, B ramps
        for i, (ax_orig, ax_trans, label) in enumerate(zip(
            [ax3, ax5, ax7], [ax4, ax6, ax8], ['Red', 'Green', 'Blue']
        )):
            for j in range(len(original_ramps[i+1])):
                color = original_ramps[i+1][j]
                ax_orig.add_patch(plt.Rectangle(
                    (j / len(original_ramps[i+1]), 0), 
                    1 / len(original_ramps[i+1]), 1, 
                    color=color, ec=None
                ))
                
                color = transformed_ramps[i+1][j]
                ax_trans.add_patch(plt.Rectangle(
                    (j / len(transformed_ramps[i+1]), 0), 
                    1 / len(transformed_ramps[i+1]), 1, 
                    color=color, ec=None
                ))
            
            ax_orig.set_title(f'Original {label} Ramp')
            ax_trans.set_title(f'Transformed {label} Ramp')
        
        # Remove ticks
        for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]:
            ax.set_xticks([])
            ax.set_yticks([])
        
        if title:
            plt.suptitle(title)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()


class ReportVisualizer:
    """
    Comprehensive visualizer for LUT analysis reports
    """
    def __init__(self, lut_parser, transform_analyzer):
        """
        Initialize with a LUT parser and transformation analyzer
        """
        self.lut_parser = lut_parser
        self.analyzer = transform_analyzer
        self.colorchecker = ColorChecker()
        self.gradient = GradientVisualizer()
    
    def generate_report_visualizations(self, output_folder=None):
        """
        Generate a comprehensive set of visualizations for the LUT
        """
        if output_folder is None:
            output_folder = Path('analysis_results')
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(exist_ok=True)
        
        # Get filename without extension
        base_name = Path(self.lut_parser.cube_path).stem
        
        # Get transform function
        transform_function = lambda x: self.analyzer.simulate_transform(x, use_lut=True)
        
        # Generate and transform ColorChecker
        original_cc = self.colorchecker.get_srgb_colorchecker()
        transformed_cc = self.colorchecker.transform_colorchecker(original_cc, transform_function)
        
        cc_plot_path = output_folder / f"{base_name}_colorchecker.png"
        self.colorchecker.plot_colorchecker_comparison(
            original_cc, transformed_cc, 
            save_path=str(cc_plot_path),
            title=f"ColorChecker: {base_name} ({self.analyzer.source_space} → {self.analyzer.target_space})"
        )
        
        # Generate and transform gradients
        gray_ramp_lin = self.gradient.generate_gray_ramp(steps=200, log=False)
        gray_ramp_log = self.gradient.generate_gray_ramp(steps=200, log=True)
        rgb_ramps = self.gradient.generate_rgb_ramps(steps=200)
        
        # Transform ramps
        transformed_gray_lin = self.gradient.transform_ramp(gray_ramp_lin, transform_function)
        transformed_gray_log = self.gradient.transform_ramp(gray_ramp_log, transform_function)
        transformed_rgb = [
            self.gradient.transform_ramp(ramp, transform_function) for ramp in rgb_ramps
        ]
        
        # Plot linear ramps
        lin_ramps_path = output_folder / f"{base_name}_linear_ramps.png"
        self.gradient.plot_gradient_comparison(
            [gray_ramp_lin] + rgb_ramps, 
            [transformed_gray_lin] + transformed_rgb,
            save_path=str(lin_ramps_path),
            title=f"Linear Ramps: {base_name} ({self.analyzer.source_space} → {self.analyzer.target_space})"
        )
        
        # Plot log ramps
        log_ramps_path = output_folder / f"{base_name}_log_ramps.png"
        self.gradient.plot_gradient_comparison(
            [gray_ramp_log] + rgb_ramps, 
            [transformed_gray_log] + transformed_rgb,
            save_path=str(log_ramps_path),
            title=f"Log Ramps: {base_name} ({self.analyzer.source_space} → {self.analyzer.target_space})"
        )
        
        # Return paths to generated visualizations
        return {
            'colorchecker': str(cc_plot_path),
            'linear_ramps': str(lin_ramps_path),
            'log_ramps': str(log_ramps_path)
        } 