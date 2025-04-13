# LUT Analyzer

## Project Overview

LUT Analyzer is a comprehensive command-line tool for analyzing Look-Up Tables (LUTs) in the `.cube` format. It provides detailed technical analysis, visualization, and reporting capabilities for colorists, filmmakers, and technical directors working with color transformations.

## Features

- **Comprehensive LUT Analysis**
  - Color space transformation analysis
  - Dynamic range evaluation
  - Color bias detection
  - Tonal smoothness assessment
  - Banding detection

- **Advanced Visualization**
  - RGB distribution plots
  - Color curves analysis
  - ColorChecker comparisons
  - Linear and logarithmic gradient ramps
  - Transformation accuracy plots

- **Technical Reporting**
  - Detailed JSON reports for each LUT
  - Comprehensive technical documentation in Markdown
  - Summary reports for batch analysis
  - Visual quality assessment

- **Color Space Support**
  - S-Log3/S-Gamut3
  - ARRI LogC/AWG
  - RED Log3G10/REDWideGamut
  - V-Log/V-Gamut
  - Rec.709
  - Custom gamma curves

## Installation

### Prerequisites
- Python 3.8+
- NumPy
- Matplotlib
- Additional dependencies in `requirements.txt`

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/makaronz/LUT_to_false.git
   cd LUT_to_false
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Analyze a single LUT file:
```bash
python cube_analyzer.py path/to/your/lut.cube
```

Analyze all LUTs in a directory:
```bash
python cube_analyzer.py path/to/lut/directory
```

### Advanced Options

Specify source and target color spaces:
```bash
python cube_analyzer.py path/to/lut.cube --source "S-Log3/S-Gamut3" --target "Rec.709"
```

Custom output directory:
```bash
python cube_analyzer.py path/to/lut.cube --output custom_output_dir
```

### Output

The analyzer generates:
- Individual JSON reports for each LUT
- Visualization plots (PNG format)
  - RGB distribution
  - Color curves
  - ColorChecker comparison
  - Gradient ramps
  - Transformation accuracy
- A comprehensive technical document (Markdown)
- Summary report for batch analysis

## Technical Details

### Analysis Components

1. **LUT Parser (`lut_tools/lut_parser.py`)**
   - Parses .cube file format
   - Extracts metadata and 3D LUT data
   - Infers color spaces based on file characteristics

2. **Transfer Functions (`lut_tools/transfer_functions.py`)**
   - Implements standard camera and display transfer functions
   - Supports major log curves and gamma transformations
   - Provides color space conversion utilities

3. **Analyzers (`lut_tools/analyzers.py`)**
   - LUTAnalyzer: Basic LUT characteristics
   - LUTTransformationAnalyzer: Color space transformation analysis
   - Comprehensive metrics calculation

4. **Visualizers (`lut_tools/visualizers.py`)**
   - ColorChecker visualization
   - Gradient ramp generation
   - Technical plot creation
   - Report visualization tools

## Development

The project is structured for easy extension:
- Modular design for adding new analysis features
- Extensible visualization system
- Support for additional LUT formats (planned)
- API for integration with other tools (planned)

## License

This project is licensed under the MIT License.

## Author

makaronz
