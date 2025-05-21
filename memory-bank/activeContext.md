# PixelPasta – Active Context

## Aktualny stan
- Backend Flask obsługuje upload, analizę i porównanie LUT (.cube) względem referencyjnych krzywych (Sony, ARRI, RED, Canon)
- Generowanie wykresów, raportów PDF, tabele porównawcze (dane przekazywane przez session)
- Endpoint `/table-data` zwraca dane do tabeli porównawczej w formacie JSON
- Frontend modularny (JS, @21st-dev/magic), komponenty FileUpload i ComparisonTable

## Ostatnie zmiany
- Refaktoryzacja repozytorium, usunięcie zbędnych plików
- Dodanie i integracja komponentu ComparisonTable.js
- Rozbudowa memory bank i dokumentacji

## Najbliższe kroki
- Integracja tabeli porównawczej na froncie (HTML, JS, CSS)
- Rozbudowa stylów i dostępności (WCAG, dark mode)
- Testy funkcjonalne i matematyczne
- Prototypowanie jednej z koncepcji: LUT Morphing Gallery, Color Memory Palace lub Temporal LUT Analyzer 