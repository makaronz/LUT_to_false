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

## API

LUT Analyzer udostępnia kompletne API REST do integracji z innymi aplikacjami. Szczegółowa dokumentacja API jest dostępna w pliku [docs/API.md](docs/API.md).

Główne funkcje API:
- Analiza pojedynczych plików LUT
- Analiza wsadowa wielu plików
- Informacje o przestrzeniach kolorów
- Generowanie raportów i wizualizacji

Przykład użycia API w Python:
```python
import requests

# Inicjalizacja klienta API
api_url = "http://localhost:8080/api"
headers = {"Authorization": "Bearer your_token"}

# Analiza pliku LUT
with open("path/to/lut.cube", "rb") as f:
    response = requests.post(
        f"{api_url}/analyze",
        headers=headers,
        files={"file": f}
    )
    results = response.json()
```

Więcej przykładów i szczegółowa dokumentacja dostępne w [docs/API.md](docs/API.md).

## API Reference

The LUT Analyzer provides a RESTful API available at `http://localhost:8080/api`. This allows you to integrate LUT analysis capabilities into your own applications.

### API Endpoints

#### Analyze LUT
```http
POST /api/analyze
Content-Type: multipart/form-data

file: LUT file (.cube format)
```

Response:
```json
{
  "analysis": {
    "colorSpaceInfo": { ... },
    "transformationMetrics": { ... },
    "qualityMetrics": { ... }
  },
  "visualizations": {
    "rgbDistribution": "base64...",
    "colorCurves": "base64...",
    "gradientRamps": "base64..."
  }
}
```

#### Batch Analysis
```http
POST /api/analyze/batch
Content-Type: multipart/form-data

files: Multiple LUT files
```

Response:
```json
{
  "results": [
    {
      "filename": "lut1.cube",
      "analysis": { ... }
    },
    {
      "filename": "lut2.cube",
      "analysis": { ... }
    }
  ],
  "summary": {
    "totalFiles": 2,
    "averageMetrics": { ... }
  }
}
```

#### Get Color Space Info
```http
GET /api/colorspaces
```

Response:
```json
{
  "supported": [
    "S-Log3/S-Gamut3",
    "ARRI LogC/AWG",
    "RED Log3G10/REDWideGamut",
    "V-Log/V-Gamut",
    "Rec.709"
  ]
}
```

### API Usage Examples

Using curl:
```bash
# Analyze single LUT
curl -X POST -F "file=@path/to/lut.cube" http://localhost:8080/api/analyze

# Batch analysis
curl -X POST -F "files=@lut1.cube" -F "files=@lut2.cube" http://localhost:8080/api/analyze/batch

# Get supported color spaces
curl http://localhost:8080/api/colorspaces
```

Using Python requests:
```python
import requests

# Analyze single LUT
with open('path/to/lut.cube', 'rb') as f:
    response = requests.post('http://localhost:8080/api/analyze', files={'file': f})
    results = response.json()

# Batch analysis
files = [
    ('files', open('lut1.cube', 'rb')),
    ('files', open('lut2.cube', 'rb'))
]
response = requests.post('http://localhost:8080/api/analyze/batch', files=files)
batch_results = response.json()
```

### Running the API Server

Start the API server:
```bash
python api_server.py
```

The server will be available at `http://localhost:8080/api`.

For development, you can enable debug mode:
```bash
python api_server.py --debug
```
