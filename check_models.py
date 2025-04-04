import google.generativeai as genai
from config import GEMINI_API_KEY

def check_available_models():
    try:
        # Konfiguracja API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Pobranie listy dostępnych modeli
        models = genai.list_models()
        
        print("\nDostępne modele:")
        for model in models:
            print(f"\nNazwa: {model.name}")
            print(f"Opis: {model.description}")
            print(f"Wspierane generatory: {model.supported_generation_methods}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Błąd podczas sprawdzania modeli: {str(e)}")

if __name__ == "__main__":
    check_available_models() 