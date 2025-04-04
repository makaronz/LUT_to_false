import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Konfiguracja Gemini
# UWAGA: Ustaw klucz API w zmiennej środowiskowej GOOGLE_API_KEY
# Przykład: export GOOGLE_API_KEY='twój_klucz_api'
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "models/gemini-2.0-flash-001"

# Konfiguracja analizy
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FILE_TYPES = ['.txt', '.py', '.json', '.csv', '.md', '.yaml', '.yml']
ANALYSIS_TYPES = {
    'general': 'Ogólna analiza zawartości',
    'code': 'Analiza kodu źródłowego',
    'text': 'Analiza tekstu',
    'data': 'Analiza danych'
}

# Konfiguracja wyjścia
OUTPUT_DIR = "analysis_results"
LOG_FILE = "gemini_analyzer.log" 