from gemini_analyzer import GeminiAnalyzer
from config import GEMINI_API_KEY
import os


def test_analyzer():
    """Test basic file analysis using GeminiAnalyzer."""

    analyzer = GeminiAnalyzer(GEMINI_API_KEY)
    test_file = "example.txt"

    # Plik testowy musi istnieć
    assert os.path.exists(test_file), f"Plik {test_file} nie istnieje"

    # Wykonaj analizę
    results = analyzer.analyze_file(test_file, "general")

    # Sprawdzenie poprawności wyników
    assert "error" not in results, f"Błąd podczas analizy: {results.get('error')}"
    assert results.get("file_name") == os.path.basename(test_file)
    assert results.get("analysis_type") == "general"
    assert "content_summary" in results


if __name__ == "__main__":
    test_analyzer()
