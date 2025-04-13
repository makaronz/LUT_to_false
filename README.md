# LUTcompareTool - LUT Analyzer

## Project Overview

LUTcompareTool is a comprehensive toolkit for filmmakers, colorists, and developers working with Look-Up Tables (LUTs). This application allows you to analyze `.cube` LUT files, compare them against various color spaces (like S-Log3, LogC, RED Log), and visualize the results through detailed reports.

The application provides a web interface for uploading LUT files, selecting reference curves, and generating analysis reports in both PNG and PDF formats.

## About

LUTcompareTool is a professional-grade tool designed to help filmmakers and colorists analyze and compare Look-Up Tables (LUTs) used in digital film production. It provides detailed insights into how LUTs transform color spaces and helps ensure accurate color reproduction across different camera systems and workflows.

Key capabilities include:
- Analysis of .cube LUT files against industry-standard color spaces
- Support for major camera log curves (S-Log3, LogC, RED Log, etc.)
- Detailed visualization of LUT transformations
- Comprehensive PDF reports with technical analysis
- Web-based interface for easy access and use

This tool is particularly useful for:
- Colorists verifying LUT accuracy
- DITs (Digital Imaging Technicians) validating on-set LUTs
- Post-production teams ensuring color consistency
- Camera manufacturers testing LUT implementations
- Educational purposes in film and media production

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

## Deployment Options

### Heroku

The application is already configured for deployment on Heroku:

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku CLI:
   ```bash
   heroku login
   ```
3. Create a new Heroku app:
   ```bash
   heroku create your-lutcomparetool-app
   ```
4. Push your code to Heroku:
   ```bash
   git push heroku merge:main
   ```

### Docker

You can also deploy using Docker:

1. Create a Dockerfile in the project root:
   ```
   FROM python:3.11-slim

   WORKDIR /app

   COPY . .
   RUN pip install --no-cache-dir -r requirements.txt

   EXPOSE 8080

   CMD ["gunicorn", "--bind", "0.0.0.0:8080", "lutcomparetool_app:app"]
   ```

2. Build and run the Docker image:
   ```bash
   docker build -t lutcomparetool .
   docker run -p 8080:8080 lutcomparetool
   ```

### Self-Hosted/VPS

To deploy on your own server:

1. Set up a Python environment on your server
2. Clone the repository and install dependencies
3. Set up a production WSGI server:
   ```bash
   gunicorn --bind 0.0.0.0:8080 lutcomparetool_app:app
   ```
4. Configure Nginx/Apache as a reverse proxy (recommended for production)

### Cloud Platforms

The application can also be deployed on platforms like:
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

Each platform has its own deployment process, but they all support Python Flask applications.

## License

This project is licensed under the MIT License.

## Author

makaronz
