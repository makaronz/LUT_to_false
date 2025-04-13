import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

class LUTAnalyzer:
    def __init__(self, cube_path):
        self.cube_path = cube_path
        self.title = ""
        self.size = 0
        self.data = None
        self._parse_cube_file()
    
    def _parse_cube_file(self):
        with open(self.cube_path, 'r') as f:
            lines = f.readlines()
            
        # Parse header
        for line in lines:
            if line.startswith('TITLE'):
                self.title = line.split('"')[1]
            elif line.startswith('LUT_3D_SIZE'):
                self.size = int(line.split()[-1])
                break
        
        # Parse data
        data_lines = [line.strip() for line in lines if line.strip() and not line.startswith(('#', 'TITLE', 'LUT_3D_SIZE'))]
        self.data = np.array([list(map(float, line.split())) for line in data_lines])
    
    def analyze_color_range(self):
        """Analyze the color range and distribution of the LUT"""
        min_values = np.min(self.data, axis=0)
        max_values = np.max(self.data, axis=0)
        mean_values = np.mean(self.data, axis=0)
        std_values = np.std(self.data, axis=0)
        
        return {
            'min': min_values,
            'max': max_values,
            'mean': mean_values,
            'std': std_values
        }
    
    def plot_color_distribution(self, save_path=None):
        """Plot the distribution of RGB values"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        channels = ['Red', 'Green', 'Blue']
        
        for i, (ax, channel) in enumerate(zip(axes, channels)):
            ax.hist(self.data[:, i], bins=50, alpha=0.7)
            ax.set_title(f'{channel} Channel Distribution')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
        
        plt.suptitle(f'Color Distribution - {os.path.basename(self.cube_path)}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

def analyze_all_luts(cube_folder):
    """Analyze all CUBE files in the specified folder"""
    results = {}
    output_folder = Path('analysis_results')
    output_folder.mkdir(exist_ok=True)
    
    for cube_file in Path(cube_folder).glob('*.cube'):
        analyzer = LUTAnalyzer(str(cube_file))
        
        # Analyze color range
        color_stats = analyzer.analyze_color_range()
        
        # Generate and save plot
        plot_path = output_folder / f'{cube_file.stem}_distribution.png'
        analyzer.plot_color_distribution(str(plot_path))
        
        results[cube_file.name] = {
            'title': analyzer.title,
            'size': analyzer.size,
            'color_stats': color_stats,
            'plot_path': str(plot_path)
        }
    
    return results

if __name__ == '__main__':
    cube_folder = '/Users/arkadiuszfudali/LUT_to_false/CUBE'
    results = analyze_all_luts(cube_folder)
    
    # Print summary
    print("\nLUT Analysis Summary:")
    print("=" * 50)
    for lut_name, stats in results.items():
        print(f"\nAnalyzing: {lut_name}")
        print(f"Title: {stats['title']}")
        print(f"LUT Size: {stats['size']}x{stats['size']}x{stats['size']}")
        print("\nColor Statistics:")
        print(f"Min RGB: {stats['color_stats']['min']}")
        print(f"Max RGB: {stats['color_stats']['max']}")
        print(f"Mean RGB: {stats['color_stats']['mean']}")
        print(f"Std RGB: {stats['color_stats']['std']}")
        print("\nPlot saved to:", stats['plot_path'])
        print("-" * 50) 