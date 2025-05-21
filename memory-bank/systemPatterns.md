# PixelPasta – System Patterns

## Architektura
- Backend: Python (Flask), modularny, REST API, generowanie raportów, obsługa plików
- Frontend: Vanilla JS + @21st-dev/magic (komponenty UI), HTML5, CSS3
- Komunikacja: JSON (endpointy API), session (przekazywanie danych do wyników)

## Wzorce projektowe
- Separation of Concerns: oddzielenie logiki analitycznej, prezentacji i warstwy API
- Komponentowość: FileUpload, ComparisonTable, wykresy (Chart.js lub magic)
- Dependency Injection: łatwa podmiana algorytmów interpolacji, krzywych, raportowania
- Testowalność: funkcje matematyczne i API pokryte testami jednostkowymi

## Integracje
- @21st-dev/magic – nowoczesne komponenty UI, szybki prototyping
- Chart.js (lub alternatywa) – wykresy interaktywne
- Możliwość integracji z narzędziami DIT/postprodukcji (export PDF, CSV, ZIP)

## Moduły
- lutcomparetool_app.py – główny backend Flask
- lut_analyzer_package/ – logika analizy, interpolacji, raportowania
- pixelpasta/static/js/components/ – frontendowe komponenty UI
- memory-bank/ – dokumentacja, kontekst, roadmapa 