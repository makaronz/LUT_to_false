# PixelPasta – Progress

## Co działa
- Upload i analiza LUT (.cube) względem referencyjnych krzywych (Sony, ARRI, RED, Canon)
- Generowanie wykresów, raportów PDF
- Tabela porównawcza: backend generuje dane, endpoint /table-data zwraca JSON
- Komponenty frontendowe: FileUpload, ComparisonTable (JS)
- Memory bank i dokumentacja projektowa

## Co zostało do zrobienia
- Integracja tabeli porównawczej na froncie (HTML, JS, CSS)
- Rozbudowa stylów, dark mode, dostępność
- Testy e2e i matematyczne
- Prototypowanie funkcji kreatywnych (morphing, VR, analiza wideo)
- CI/CD, automatyzacja testów

## Znane błędy/ograniczenia
- Brak obsługi batch compare dla dwóch LUT-ów naraz (tylko pojedyncze porównanie)
- Brak zaawansowanego sortowania/filtrowania w tabeli porównawczej
- Brak pełnej obsługi plików wideo (planowane w Temporal LUT Analyzer) 