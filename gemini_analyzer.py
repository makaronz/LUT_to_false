import google.generativeai as genai
import os
from typing import List, Dict, Any

class GeminiAnalyzer:
    def __init__(self, api_key: str):
        """
        Inicjalizacja analizatora Gemini 2.0 Flash
        
        Args:
            api_key (str): Klucz API Google AI
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        
    def analyze_file(self, file_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analizuje zawartość pliku
        
        Args:
            file_path (str): Ścieżka do pliku do analizy
            analysis_type (str): Typ analizy (general, code, text, data)
            
        Returns:
            Dict[str, Any]: Wyniki analizy
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            prompt = self._generate_prompt(content, analysis_type)
            response = self.model.generate_content(prompt)
            
            # Sprawdź, czy odpowiedź jest poprawna
            if not response or not hasattr(response, 'text'):
                raise Exception("Nie otrzymano poprawnej odpowiedzi od modelu")
                
            return {
                "file_name": os.path.basename(file_path),
                "analysis_type": analysis_type,
                "content_summary": response.text,
                "status": "success",
                "model_version": "gemini-2.0-flash-001"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "file_name": os.path.basename(file_path),
                "status": "error",
                "model_version": "gemini-2.0-flash-001"
            }
    
    def _generate_prompt(self, content: str, analysis_type: str) -> str:
        """
        Generuje prompt dla modelu w zależności od typu analizy
        
        Args:
            content (str): Zawartość pliku
            analysis_type (str): Typ analizy
            
        Returns:
            str: Sformatowany prompt
        """
        base_prompt = f"""
        Przeanalizuj poniższą zawartość pliku używając Gemini 2.0 Flash. 
        Typ analizy: {analysis_type}
        
        Zawartość:
        {content}
        
        Proszę o:
        1. Szczegółowe podsumowanie głównych punktów
        2. Identyfikację kluczowych elementów i zależności
        3. Zaawansowane sugestie dotyczące potencjalnych problemów lub optymalizacji
        4. Szczegółowe rekomendacje dotyczące dalszych działań
        5. Analizę potencjalnych ryzyk i ograniczeń
        """
        
        return base_prompt

# Przykład użycia:
if __name__ == "__main__":
    # Pobierz klucz API ze zmiennej środowiskowej
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Błąd: Nie znaleziono klucza API Google. Ustaw zmienną środowiskową GOOGLE_API_KEY")
        exit(1)
        
    analyzer = GeminiAnalyzer(api_key)
    
    # Przykładowa analiza pliku
    results = analyzer.analyze_file("example.txt", "general")
    print(results) 