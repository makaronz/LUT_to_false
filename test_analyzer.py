from gemini_analyzer import GeminiAnalyzer
from config import GEMINI_API_KEY
import os

def test_analyzer():
    try:
        # Inicjalizacja analizatora
        analyzer = GeminiAnalyzer(GEMINI_API_KEY)
        
        # Testowa analiza pliku
        test_file = "example.txt"
        
        if not os.path.exists(test_file):
            print(f"Błąd: Plik {test_file} nie istnieje!")
            return
            
        results = analyzer.analyze_file(test_file, "general")
        
        if "error" in results:
            print(f"Błąd podczas analizy: {results['error']}")
            return
            
        print("\nWyniki analizy:")
        print(f"Nazwa pliku: {results.get('file_name', 'Brak')}")
        print(f"Typ analizy: {results.get('analysis_type', 'Brak')}")
        print("\nPodsumowanie:")
        print(results.get('content_summary', 'Brak podsumowania'))
        print(f"\nUżyte tokeny: {results.get('tokens_used', 'Brak informacji')}")
        
    except Exception as e:
        print(f"Nieoczekiwany błąd: {str(e)}")

if __name__ == "__main__":
    test_analyzer() 