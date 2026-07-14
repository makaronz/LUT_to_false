import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
from .lut_parser import LUTParser
from .transfer_functions import TransferFunctions

class LUTAnalyzer:
    """
    Advanced analyzer for LUT characteristics, color transformations, and quality
    """
    def __init__(self, lut_parser):
        """
        Initialize with a LUTParser instance
        """
        self.lut_parser = lut_parser
        self.tf = TransferFunctions()
        self.lut_data = lut_parser.get_data()
        self.metadata = lut_parser.get_metadata()
    
    def analyze_color_range(self):
        """
        Analyze the color range and distribution of the LUT
        """
        min_values = np.min(self.lut_data, axis=0)
        max_values = np.max(self.lut_data, axis=0)
        mean_values = np.mean(self.lut_data, axis=0)
        std_values = np.std(self.lut_data, axis=0)
        
        return {
            'min': min_values,
            'max': max_values,
            'mean': mean_values,
            'std': std_values
        }
    
    def analyze_dynamic_range(self):
        """
        Analyze dynamic range characteristics of the LUT
        """
        # Find where values start clipping in both shadows and highlights
        r_channel = self.lut_data[:, 0]
        g_channel = self.lut_data[:, 1]
        b_channel = self.lut_data[:, 2]
        
        # Calculate brightness (simple average - could use perceptual formula)
        brightness = (r_channel + g_channel + b_channel) / 3.0
        
        # Sort by brightness to find clipping points
        brightness_idx = np.argsort(brightness)
        sorted_rgb = self.lut_data[brightness_idx]
        
        # Find where values start clipping
        shadow_clip = {}
        highlight_clip = {}
        
        # Analyze shadow clipping (looking at bottom 10%)
        shadow_samples = sorted_rgb[:int(len(sorted_rgb) * 0.1)]
        shadow_clip['r'] = np.min(shadow_samples[:, 0])
        shadow_clip['g'] = np.min(shadow_samples[:, 1])
        shadow_clip['b'] = np.min(shadow_samples[:, 2])
        shadow_clip['avg'] = (shadow_clip['r'] + shadow_clip['g'] + shadow_clip['b']) / 3.0
        
        # Analyze highlight clipping (looking at top 10%)
        highlight_samples = sorted_rgb[int(len(sorted_rgb) * 0.9):]
        highlight_clip['r'] = np.max(highlight_samples[:, 0])
        highlight_clip['g'] = np.max(highlight_samples[:, 1])
        highlight_clip['b'] = np.max(highlight_samples[:, 2])
        highlight_clip['avg'] = (highlight_clip['r'] + highlight_clip['g'] + highlight_clip['b']) / 3.0
        
        return {
            'shadow_clip': shadow_clip,
            'highlight_clip': highlight_clip,
            'dynamic_range_ratio': highlight_clip['avg'] / (shadow_clip['avg'] + 1e-6)
        }
    
    def analyze_color_bias(self):
        """
        Analyze color balance and bias across the LUT
        """
        # Divide brightness range into 10 segments and analyze color bias in each
        r_channel = self.lut_data[:, 0]
        g_channel = self.lut_data[:, 1]
        b_channel = self.lut_data[:, 2]
        
        # Calculate brightness
        brightness = (r_channel + g_channel + b_channel) / 3.0
        
        # Sort by brightness
        brightness_idx = np.argsort(brightness)
        sorted_rgb = self.lut_data[brightness_idx]
        
        # Divide into segments and analyze
        num_segments = 10
        segment_size = len(sorted_rgb) // num_segments
        segments = []
        
        for i in range(num_segments):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < num_segments - 1 else len(sorted_rgb)
            segment_data = sorted_rgb[start_idx:end_idx]
            
            # Analyze color balance within segment
            segment_avg = np.mean(segment_data, axis=0)
            r_ratio = segment_avg[0] / (np.mean(segment_avg) + 1e-6)
            g_ratio = segment_avg[1] / (np.mean(segment_avg) + 1e-6)
            b_ratio = segment_avg[2] / (np.mean(segment_avg) + 1e-6)
            
            segment_brightness = np.mean(brightness[brightness_idx[start_idx:end_idx]])
            
            segments.append({
                'brightness': segment_brightness,
                'r_ratio': r_ratio,
                'g_ratio': g_ratio,
                'b_ratio': b_ratio,
                'color_deviation': np.std([r_ratio, g_ratio, b_ratio])
            })
        
        # Overall color bias
        overall_r = np.mean(r_channel) / (np.mean([np.mean(r_channel), np.mean(g_channel), np.mean(b_channel)]) + 1e-6)
        overall_g = np.mean(g_channel) / (np.mean([np.mean(r_channel), np.mean(g_channel), np.mean(b_channel)]) + 1e-6)
        overall_b = np.mean(b_channel) / (np.mean([np.mean(r_channel), np.mean(g_channel), np.mean(b_channel)]) + 1e-6)
        
        return {
            'segments': segments,
            'overall_bias': {
                'r_ratio': overall_r,
                'g_ratio': overall_g,
                'b_ratio': overall_b,
                'dominant_channel': 'R' if overall_r > overall_g and overall_r > overall_b else
                                  'G' if overall_g > overall_r and overall_g > overall_b else 'B'
            }
        }
    
    def analyze_tonal_smoothness(self):
        """
        Analyze the smoothness of tonal transitions
        """
        # For tonal smoothness, we look at the derivatives of the RGB curves
        # If there are sudden jumps, it indicates potential banding issues
        r_channel = self.lut_data[:, 0]
        g_channel = self.lut_data[:, 1]
        b_channel = self.lut_data[:, 2]
        
        # Calculate brightness and sort
        brightness = (r_channel + g_channel + b_channel) / 3.0
        brightness_idx = np.argsort(brightness)
        
        # Get sorted channels
        sorted_r = r_channel[brightness_idx]
        sorted_g = g_channel[brightness_idx]
        sorted_b = b_channel[brightness_idx]
        
        # Calculate first derivatives
        r_diff = np.diff(sorted_r)
        g_diff = np.diff(sorted_g)
        b_diff = np.diff(sorted_b)
        
        # Calculate second derivatives (acceleration)
        r_accel = np.diff(r_diff)
        g_accel = np.diff(g_diff)
        b_accel = np.diff(b_diff)
        
        # Analyze smoothness via acceleration statistics
        r_smoothness = np.std(r_accel) / (np.mean(np.abs(r_diff)) + 1e-6)
        g_smoothness = np.std(g_accel) / (np.mean(np.abs(g_diff)) + 1e-6)
        b_smoothness = np.std(b_accel) / (np.mean(np.abs(b_diff)) + 1e-6)
        
        # Find regions with potential banding
        banding_threshold = 5.0  # Threshold for identifying sudden jumps
        r_banding = np.where(np.abs(r_accel) > banding_threshold * np.std(r_accel))[0]
        g_banding = np.where(np.abs(g_accel) > banding_threshold * np.std(g_accel))[0]
        b_banding = np.where(np.abs(b_accel) > banding_threshold * np.std(b_accel))[0]
        
        return {
            'smoothness_scores': {
                'r': 1.0 / (1.0 + r_smoothness),  # Higher is smoother
                'g': 1.0 / (1.0 + g_smoothness),
                'b': 1.0 / (1.0 + b_smoothness),
                'overall': 1.0 / (1.0 + (r_smoothness + g_smoothness + b_smoothness) / 3.0)
            },
            'banding_regions': {
                'r': len(r_banding) / len(r_accel) if len(r_accel) > 0 else 0,
                'g': len(g_banding) / len(g_accel) if len(g_accel) > 0 else 0,
                'b': len(b_banding) / len(b_accel) if len(b_accel) > 0 else 0
            }
        }
    
    def plot_color_distribution(self, save_path=None):
        """
        Plot the distribution of RGB values
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        channels = ['Red', 'Green', 'Blue']
        
        for i, (ax, channel) in enumerate(zip(axes, channels)):
            ax.hist(self.lut_data[:, i], bins=50, alpha=0.7)
            ax.set_title(f'{channel} Channel Distribution')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
        
        plt.suptitle(f'Color Distribution - {os.path.basename(self.lut_parser.cube_path)}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def plot_color_curves(self, save_path=None):
        """
        Plot the RGB and luma curves of the LUT
        """
        # Generate input values (normalized from 0 to 1)
        inputs = np.linspace(0, 1, 100)
        
        # Create a figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Sample the LUT at these points
        r_curve = np.zeros(len(inputs))
        g_curve = np.zeros(len(inputs))
        b_curve = np.zeros(len(inputs))
        
        # Sample the LUT by picking closest values
        # This is simplified - in practice you would interpolate within the 3D LUT
        lut_size = self.metadata['size']
        step = 1.0 / (lut_size - 1)
        
        for i, value in enumerate(inputs):
            # Find the nearest LUT entry
            idx = min(int(value / step), lut_size - 1)
            r_curve[i] = self.lut_data[idx * lut_size * lut_size, 0]  # Simplified for gray ramp
            g_curve[i] = self.lut_data[idx * lut_size * lut_size + idx * lut_size + idx, 1]
            b_curve[i] = self.lut_data[idx * lut_size * lut_size + idx * lut_size + idx, 2]
        
        # Calculate luma
        luma_curve = 0.2126 * r_curve + 0.7152 * g_curve + 0.0722 * b_curve
        
        # Plot RGB curves
        ax1.plot(inputs, r_curve, 'r-', label='Red')
        ax1.plot(inputs, g_curve, 'g-', label='Green')
        ax1.plot(inputs, b_curve, 'b-', label='Blue')
        ax1.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Linear')
        ax1.set_title('RGB Curves')
        ax1.set_xlabel('Input Value')
        ax1.set_ylabel('Output Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot luma curve
        ax2.plot(inputs, luma_curve, 'k-', label='Luma')
        ax2.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Linear')
        ax2.set_title('Luma Curve')
        ax2.set_xlabel('Input Value')
        ax2.set_ylabel('Output Value')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(f'Color Curves - {os.path.basename(self.lut_parser.cube_path)}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def generate_summary_report(self, output_folder=None):
        """
        Generate a comprehensive summary report with all analyses
        """
        if output_folder is None:
            output_folder = Path('analysis_results')
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(exist_ok=True)
        
        # Get filename without extension
        base_name = Path(self.lut_parser.cube_path).stem
        
        # Perform all analyses
        color_stats = self.analyze_color_range()
        dynamic_range = self.analyze_dynamic_range()
        color_bias = self.analyze_color_bias()
        tonal_smoothness = self.analyze_tonal_smoothness()
        
        # Generate plots
        dist_plot_path = output_folder / f"{base_name}_distribution.png"
        self.plot_color_distribution(str(dist_plot_path))
        
        curves_plot_path = output_folder / f"{base_name}_curves.png"
        self.plot_color_curves(str(curves_plot_path))
        
        # Compile all results
        results = {
            'metadata': self.metadata,
            'color_stats': color_stats,
            'dynamic_range': dynamic_range,
            'color_bias': color_bias,
            'tonal_smoothness': tonal_smoothness,
            'plot_paths': {
                'distribution': str(dist_plot_path),
                'curves': str(curves_plot_path)
            }
        }
        
        return results


class LUTTransformationAnalyzer:
    """
    Analyzer for specific color space transformations performed by LUTs
    """
    def __init__(self, lut_parser, source_space=None, target_space=None):
        """
        Initialize with a LUTParser instance and optional color space info
        If not specified, will use inferred spaces from the LUT parser
        """
        self.lut_parser = lut_parser
        self.tf = TransferFunctions()
        self.lut_data = lut_parser.get_data()
        self.metadata = lut_parser.get_metadata()
        
        # Use specified or inferred color spaces
        if source_space is None:
            self.source_space = self.metadata.get('inferred_source_space', 'Unknown')
        else:
            self.source_space = source_space
            
        if target_space is None:
            self.target_space = self.metadata.get('inferred_target_space', 'Unknown')
        else:
            self.target_space = target_space
    
    def get_source_to_linear_function(self):
        """
        Get the appropriate function to convert from source space to linear
        """
        if 'S-Log3' in self.source_space:
            return self.tf.slog3_to_linear
        elif 'LogC' in self.source_space:
            return self.tf.logc_to_linear
        elif 'RED Log' in self.source_space:
            return self.tf.redlog3g10_to_linear
        elif 'V-Log' in self.source_space:
            return self.tf.vlog_to_linear
        elif 'Rec.709' in self.source_space:
            return self.tf.rec709_to_linear
        else:
            # Default to identity function if unknown
            return lambda x: x
    
    def get_linear_to_target_function(self):
        """
        Get the appropriate function to convert from linear to target space
        """
        if 'Rec.709' in self.target_space:
            return self.tf.linear_to_rec709
        elif '2.4' in self.target_space or '2.4' in self.metadata.get('inferred_gamma', ''):
            return lambda x: self.tf.linear_to_gamma(x, 2.4)
        elif '2.2' in self.target_space or '2.2' in self.metadata.get('inferred_gamma', ''):
            return lambda x: self.tf.linear_to_gamma(x, 2.2)
        else:
            # Default to Rec.709 if unknown
            return self.tf.linear_to_rec709
    
    def simulate_transform(self, input_values, use_lut=True):
        """
        Simulate the color transformation for a given set of input values
        Compare LUT-based vs. standard transform (source to target)
        
        input_values: numpy array of shape (N, 3) with RGB values in source space
        use_lut: If True, use the LUT for transformation, else use standard formulas
        
        Returns transformed RGB values in target space
        """
        output = np.zeros_like(input_values)
        
        if use_lut:
            # Apply LUT (simplified - assumes inputs in 0-1 range)
            lut_size = self.metadata['size']
            scale = lut_size - 1
            
            for i in range(len(input_values)):
                # Map input values to LUT indices
                r, g, b = input_values[i]
                r_idx = min(int(r * scale), scale)
                g_idx = min(int(g * scale), scale)
                b_idx = min(int(b * scale), scale)
                
                # Adobe .cube order: red varies fastest, so it has stride 1
                # and blue the largest stride (N*N).
                lut_idx = b_idx * lut_size * lut_size + g_idx * lut_size + r_idx
                if lut_idx < len(self.lut_data):
                    output[i] = self.lut_data[lut_idx]
                else:
                    # Fallback if index out of range
                    output[i] = input_values[i]
        else:
            # Use standard transform functions
            src_to_linear = self.get_source_to_linear_function()
            linear_to_tgt = self.get_linear_to_target_function()
            
            # Convert source to linear
            linear_rgb = np.zeros_like(input_values)
            for i in range(len(input_values)):
                linear_rgb[i, 0] = src_to_linear(input_values[i, 0])
                linear_rgb[i, 1] = src_to_linear(input_values[i, 1])
                linear_rgb[i, 2] = src_to_linear(input_values[i, 2])
            
            # Convert linear to target
            for i in range(len(linear_rgb)):
                output[i, 0] = linear_to_tgt(linear_rgb[i, 0])
                output[i, 1] = linear_to_tgt(linear_rgb[i, 1])
                output[i, 2] = linear_to_tgt(linear_rgb[i, 2])
        
        return output
    
    def analyze_transformation_accuracy(self, num_samples=100):
        """
        Analyze the accuracy of the LUT's transformation compared to the standard formula
        """
        # Generate test samples in source space
        # Using a combination of gray ramp and color primaries
        
        # Gray ramp (R=G=B)
        gray_ramp = np.linspace(0, 1, num_samples)
        gray_samples = np.column_stack([gray_ramp, gray_ramp, gray_ramp])
        
        # RGB primaries
        r_ramp = np.column_stack([gray_ramp, np.zeros_like(gray_ramp), np.zeros_like(gray_ramp)])
        g_ramp = np.column_stack([np.zeros_like(gray_ramp), gray_ramp, np.zeros_like(gray_ramp)])
        b_ramp = np.column_stack([np.zeros_like(gray_ramp), np.zeros_like(gray_ramp), gray_ramp])
        
        # Combine samples
        test_samples = np.vstack([gray_samples, r_ramp, g_ramp, b_ramp])
        
        # Apply both transformations
        lut_transform = self.simulate_transform(test_samples, use_lut=True)
        standard_transform = self.simulate_transform(test_samples, use_lut=False)
        
        # Calculate errors
        abs_errors = np.abs(lut_transform - standard_transform)
        mean_abs_error = np.mean(abs_errors)
        max_abs_error = np.max(abs_errors)
        channel_errors = np.mean(abs_errors, axis=0)  # Errors by channel
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean(np.square(lut_transform - standard_transform)))
        
        # Calculate correlation
        correlation = np.corrcoef(lut_transform.flatten(), standard_transform.flatten())[0, 1]
        
        return {
            'mean_absolute_error': mean_abs_error,
            'max_absolute_error': max_abs_error,
            'channel_errors': {
                'r': channel_errors[0],
                'g': channel_errors[1],
                'b': channel_errors[2]
            },
            'rmse': rmse,
            'correlation': correlation,
            'accuracy_score': 1.0 - min(1.0, mean_abs_error * 5.0)  # Scale so that 0.2 error = 0% accuracy
        }
    
    def plot_transformation_comparison(self, save_path=None):
        """
        Plot comparisons between LUT transformation and standard transformation
        """
        # Generate test values (gray ramp from 0 to 1)
        gray_ramp = np.linspace(0, 1, 100)
        gray_samples = np.column_stack([gray_ramp, gray_ramp, gray_ramp])
        
        # Apply both transformations
        lut_transform = self.simulate_transform(gray_samples, use_lut=True)
        standard_transform = self.simulate_transform(gray_samples, use_lut=False)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot RGB curves
        for i, channel, color in zip(range(3), ['R', 'G', 'B'], ['r', 'g', 'b']):
            axes[0, 0].plot(gray_ramp, lut_transform[:, i], f'{color}-', label=f'LUT {channel}')
            axes[0, 0].plot(gray_ramp, standard_transform[:, i], f'{color}--', label=f'Standard {channel}')
        
        axes[0, 0].set_title('RGB Curves Comparison')
        axes[0, 0].set_xlabel('Input Value (Gray)')
        axes[0, 0].set_ylabel('Output Value')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot Luma curve
        lut_luma = 0.2126 * lut_transform[:, 0] + 0.7152 * lut_transform[:, 1] + 0.0722 * lut_transform[:, 2]
        std_luma = 0.2126 * standard_transform[:, 0] + 0.7152 * standard_transform[:, 1] + 0.0722 * standard_transform[:, 2]
        
        axes[0, 1].plot(gray_ramp, lut_luma, 'k-', label='LUT Luma')
        axes[0, 1].plot(gray_ramp, std_luma, 'k--', label='Standard Luma')
        axes[0, 1].set_title('Luma Curve Comparison')
        axes[0, 1].set_xlabel('Input Value (Gray)')
        axes[0, 1].set_ylabel('Output Value')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot absolute errors
        abs_errors = np.abs(lut_transform - standard_transform)
        for i, channel, color in zip(range(3), ['R', 'G', 'B'], ['r', 'g', 'b']):
            axes[1, 0].plot(gray_ramp, abs_errors[:, i], f'{color}-', label=f'{channel} Error')
        
        axes[1, 0].set_title('Absolute Errors')
        axes[1, 0].set_xlabel('Input Value (Gray)')
        axes[1, 0].set_ylabel('Absolute Error')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot differences in a colormap
        im = axes[1, 1].imshow(abs_errors[:50].T, aspect='auto', cmap='viridis')
        axes[1, 1].set_title('Error Heatmap (RGB channels)')
        axes[1, 1].set_xlabel('Input Value Index')
        axes[1, 1].set_ylabel('Channel (R,G,B)')
        axes[1, 1].set_yticks([0, 1, 2])
        axes[1, 1].set_yticklabels(['R', 'G', 'B'])
        plt.colorbar(im, ax=axes[1, 1], label='Absolute Error')
        
        plt.suptitle(f'LUT vs Standard Transformation: {self.source_space} → {self.target_space}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def generate_transformation_report(self, output_folder=None):
        """
        Generate a comprehensive report of the LUT's transformation accuracy
        """
        if output_folder is None:
            output_folder = Path('analysis_results')
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(exist_ok=True)
        
        # Get filename without extension
        base_name = Path(self.lut_parser.cube_path).stem
        
        # Analyze transformation accuracy
        accuracy = self.analyze_transformation_accuracy()
        
        # Generate comparison plot
        plot_path = output_folder / f"{base_name}_transform_comparison.png"
        self.plot_transformation_comparison(str(plot_path))
        
        # Compile results
        results = {
            'metadata': {
                'filename': self.metadata.get('filename'),
                'title': self.metadata.get('title', ''),
                'source_space': self.source_space,
                'target_space': self.target_space
            },
            'transformation_accuracy': accuracy,
            'plot_path': str(plot_path)
        }
        
        return results 