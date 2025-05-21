# PixelPasta – Product Context

## Dlaczego ten projekt powstał?
Branża filmowa wymaga precyzyjnych narzędzi do analizy i kontroli LUT, które są kluczowe dla spójności obrazu na planie, w postprodukcji i podczas masteringu. Istniejące narzędzia są często nieintuicyjne, zamknięte lub nie spełniają wymagań profesjonalistów DIT/kolorystów.

## Problemy, które rozwiązuje PixelPasta
- Brak transparentnej analizy LUT względem referencyjnych krzywych kamer
- Trudność w porównywaniu LUT-ów i ocenie ich wpływu na obraz
- Niska ergonomia i dostępność narzędzi dla technicznych użytkowników
- Brak możliwości szybkiego generowania raportów i dzielenia się wynikami

## Jak to powinno działać?
- Użytkownik wgrywa plik LUT, wybiera krzywą referencyjną i otrzymuje interaktywną analizę (wykres, tabela, raport PDF)
- Może porównać dwa LUT-y, zobaczyć różnice (delta), eksportować wyniki
- Interfejs jest szybki, czytelny, zrozumiały dla profesjonalistów i dostępny na każdym urządzeniu

## Cele UX
- Minimalistyczny, techniczny design (dark mode, wysokie kontrasty)
- Szybka ścieżka: upload → analiza → raport
- Wysoka dostępność (klawiatura, screen reader, WCAG 2.1 AA)
- Tooltipy, dokumentacja, onboarding dla nowych użytkowników

## User Stories
- „Jako kolorysta chcę porównać LUT z S-Log3, by ocenić jego wpływ na cienie i światła.”
- „Jako DIT chcę wygenerować raport PDF z analizy LUT, by przekazać go do postprodukcji.”
- „Jako ekspert QC chcę zobaczyć różnice (delta) pomiędzy LUT-ami na wykresie i w tabeli.” 