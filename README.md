# PixelPasta - LUT Analysis Toolkit

## Project Overview

PixelPasta is a toolkit designed for filmmakers, colorists, and developers working with Look-Up Tables (LUTs). It provides tools to analyze `.cube` LUT files, compare their effects on exposure values across different color spaces (like S-Log3, LogC, LogC4, and Rec.709), and visualize the results.

The project currently consists of two main components:

1.  **Python LUT Analysis Core & Flask Web API (`pixelpasta`)**: A Python backend that performs the core LUT analysis and exposes this functionality through a Flask web API.
2.  **Flutter Mobile Application (`ios_app`)**: A placeholder mobile application built with Flutter (currently the default counter app template).

## Goals

*   Provide accurate analysis of 1D and 3D `.cube` LUT files.
*   Compare LUT exposure characteristics against standard color spaces (S-Log3, LogC, LogC4, Rec.709).
*   Offer multiple ways to access the analysis tools:
    *   Standalone Python script (legacy/potentially refactored into `pixelpasta.lut_processor`).
    *   Web API for integration with other applications or web frontends.
    *   (Future) A potential web interface served by the Flask app.
    *   (Future) A potential mobile application interface via the Flutter app.
*   Facilitate understanding of how different LUTs affect image exposure.

## Architecture

*   **Backend (`pixelpasta`)**:
    *   **Language**: Python
    *   **Framework**: Flask
    *   **Core Logic (`pixelpasta/lut_processor`)**: Modules for parsing `.cube` files (`cube_parser.py`) and performing color/exposure analysis (`color_analysis.py`). Uses libraries like `numpy` and `scipy` for calculations.
    *   **API (`pixelpasta/app.py`)**: Defines API endpoints (e.g., `/api/analyze`) to receive LUT files and color space selections, process them using the core logic, and return results as JSON.
    *   **Web Interface (`pixelpasta/templates/upload.html`, `pixelpasta/static/`)**: Basic HTML/CSS/JS for file uploads (likely interacts with the API).
*   **Mobile App (`ios_app`)**:
    *   **Framework**: Flutter
    *   **Current Status**: Default template application. Integration with the backend API is not yet implemented.

## Features (`pixelpasta` Backend/API)

*   **Load `.cube` Files**: Supports `.cube` files containing 1D LUTs, 3D LUTs, or both.
*   **Color Space Selection**: Allows specifying the input color space (S-Log3, LogC, LogC4) for comparison.
*   **Exposure Value Interpolation**: Accurately maps and interpolates values within the LUT data.
*   **Generate Comparative Data**: Calculates corresponding exposure percentage values for the selected Log space, Rec.709, and the loaded LUT.
*   **API Endpoint (`/api/analyze`)**:
    *   Accepts POST requests with a `.cube` file (`cube-file`) and color space (`color-space`).
    *   Returns JSON data containing:
        *   Exposure percentages arrays (`exposure_percentages`, `log_percentages`, `rec709_percentages`, `lut_percentages`).
        *   Label for the selected log curve (`log_label`).
        *   Information about the loaded LUT (`lut_info`: filename, type, size, selected color space).
    *   Accepts GET requests to retrieve the results of the *last* successful analysis.
*   **File Handling**: Uses temporary storage for uploaded files and includes basic validation (file presence, extension).

## Requirements

*   **Python 3.x**
*   **Python Libraries**:
    *   `Flask`
    *   `numpy`
    *   `pandas` (Used in `lut_analysis.py`, potentially in `pixelpasta.lut_processor`)
    *   `scipy`
    *   `matplotlib` (Used for plotting, backend set to 'Agg')
    *   `Werkzeug` (Flask dependency)
*   **(For `ios_app`)**: Flutter SDK, appropriate mobile development environment (Xcode for iOS, Android Studio/SDK for Android).

## Installation & Usage

### Backend (`pixelpasta`)

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd LUT_to_false
    ```
2.  **Set up a Virtual Environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    # Or, if requirements.txt is incomplete/missing:
    # pip install Flask numpy pandas scipy matplotlib Werkzeug
    ```
4.  **Run the Flask Development Server**:
    ```bash
    # Ensure you are in the root directory (LUT_to_false)
    export FLASK_APP=pixelpasta.app  # Or `set FLASK_APP=pixelpasta.app` on Windows
    export FLASK_ENV=development # Or `set FLASK_ENV=development` on Windows
    flask run
    ```
    The API will typically be available at `http://127.0.0.1:5000`. You can access the basic upload interface at this address in your browser or interact with the `/api/analyze` endpoint using tools like `curl` or Postman.

### Mobile App (`ios_app`)

1.  **Navigate to the App Directory**:
    ```bash
    cd ios_app
    ```
2.  **Install Flutter Dependencies**:
    ```bash
    flutter pub get
    ```
3.  **Run the App**:
    Connect a device or start an emulator/simulator.
    ```bash
    flutter run
    ```
    *(Note: This will currently run the default counter app).*

## Future Development

*   Develop a more comprehensive web frontend using the static files and potentially a JavaScript framework to interact with the API and visualize results.
*   Integrate the Flutter mobile app (`ios_app`) with the backend API (`/api/analyze`) to provide LUT analysis capabilities on mobile devices.
*   Add more sophisticated visualization options (e.g., plotting curves).
*   Expand support for other LUT formats if needed.
*   Refine error handling and user feedback.

## License

This project is likely intended to be licensed under the MIT License (based on the previous README). Please add a `LICENSE` file if one does not exist.

## Author

makaronz
