# LUTcompareTool - LUT Analyzer

## Project Overview

LUTcompareTool is a comprehensive toolkit for filmmakers, colorists, and developers working with Look-Up Tables (LUTs). This application allows you to analyze `.cube` LUT files, compare them against various color spaces (like S-Log3, LogC, RED Log), and visualize the results through detailed reports.

The application provides a web interface for uploading LUT files, selecting reference curves, and generating analysis reports in both PNG and PDF formats.

## Features

- **LUT File Analysis**: Upload and analyze `.cube` LUT files
- **Multiple Curve Comparison**: Compare LUTs against various transfer functions (S-Log3, LogC, RED Log, etc.)
- **Visual Reports**: Generate detailed PNG graphs showing the comparison between your LUT and selected curve
- **PDF Reports**: Create comprehensive PDF reports with LUT metadata and analysis results
- **Web Interface**: Easy-to-use web interface for uploading and analyzing LUT files

## Core Components

1. **Web Application (`lutcomparetool_app.py`)**: Flask-based web server providing the user interface and handling LUT analysis
2. **LUT Analysis Package (`lut_analyzer_package`)**: Core modules for LUT parsing, analysis, and report generation
   - `lut_parsing.py`: Handles loading and parsing .cube files
   - `reporting.py`: Generates comparison data, plots, and PDF reports
   - `transfer_functions.py`: Implements various camera log and gamma curves

## Installation & Usage

### Prerequisites
- Python 3.11+
- Libraries listed in `requirements.txt`

### Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/makaronz/LUT_to_false.git
   cd LUT_to_false
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python lutcomparetool_app.py
   ```
   The web interface will be available at `http://localhost:8080`

### Using the Application

1. Access the web interface at `http://localhost:8080`
2. Select a reference curve (S-Log3, LogC, etc.) from the dropdown
3. Upload your `.cube` LUT file
4. View the analysis results, including comparison graphs and a detailed PDF report

## Development

- The application is developed in Python using Flask for the web server
- The core LUT analysis is handled by custom modules in the `lut_analyzer_package`
- The web interface uses HTML templates with Bootstrap for styling

## Future Development

- Support for additional LUT formats
- More detailed analysis metrics
- Batch processing of multiple LUTs
- API endpoints for integration with other applications

## License

This project is licensed under the MIT License.

## Author

makaronz
