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
  - Integration with repomix for AI-friendly code analysis

- **Color Space Support**
  - S-Log3/S-Gamut3
  - ARRI LogC/AWG
  - RED Log3G10/REDWideGamut
  - V-Log/V-Gamut
  - Rec.709
  - Custom gamma curves

- **Development Tools**
  - repomix integration for code analysis
  - Automated documentation generation
  - Code quality checks
  - Performance profiling tools

## Installation

### Prerequisites
- Python 3.8+
- NumPy
- Matplotlib
- Node.js (for development tools)
- Additional dependencies in `requirements.txt`

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/makaronz/LUT_to_false.git
   cd LUT_to_false
   ```

2. Install dependencies:
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Development tools (optional)
   npm install -g repomix
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

### Development Tools

Generate AI-friendly code documentation:
```bash
repomix --style markdown --include "**/*.py,**/*.md"
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
- AI-friendly code documentation (via repomix)

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
- Integration with AI tools for code analysis

### Development Tools

The project includes several development tools:
- repomix for AI-friendly code documentation
- Automated testing suite
- Code quality checks
- Performance profiling tools

## License

This project is licensed under the MIT License.

## Author

makaronz

## Web application (lutcomparetool_app.py)

The web front-end is a Flask application that serves HTML pages and a small set
of form-based endpoints. It is **not** a REST/JSON API with authentication — the
routes below reflect what the code actually exposes.

Start the server:
```bash
python lutcomparetool_app.py
```
It listens on `http://localhost:8080/`.

### Actual routes

| Method & path        | Purpose                                                        |
|----------------------|----------------------------------------------------------------|
| `GET /`              | Upload page for a single LUT                                   |
| `GET /batch`         | Batch upload page                                              |
| `GET /compare`       | Two-LUT comparison page                                        |
| `POST /analyze`      | Analyze one LUT. Form fields: `lut_file` + `curve_select`. Returns JSON `{status, curve_data, table_data, lut_info}` |
| `POST /analyze-batch`| Analyze several LUTs (form fields `lut_files` + `curve_select`)|
| `POST /compare-luts` | Compare two LUTs and render `results.html`                     |
| `GET /results`       | Last single-analysis result (from session)                    |
| `GET /batch-results` | Last batch result (from session)                              |
| `GET /table-data`    | JSON of the current comparison table                          |
| `GET /reports/<file>`| Serve a generated PNG/PDF report                              |
| `GET /about`         | About page                                                    |

Example (single analysis):
```bash
curl -X POST -F "lut_file=@path/to/lut.cube" -F "curve_select=slog3" \
     http://localhost:8080/analyze
```

> Note: a separate experimental app, `pixelpasta/app.py`, exposes a
> `POST /api/analyze` route (form fields `cube-file` + `color-space`) on the
> default Flask port 5000. It is independent from the app above.
