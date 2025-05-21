# Change Log 2025

## 📌 Task List
- [x] ✅ Done: Integracja tabeli porównawczej na froncie (HTML, JS, CSS)
- [x] ✅ Done: Implementacja podstawowego trybu ciemnego (Dark Mode)
- [ ] Rozbudowa dostępności (WCAG) dla kluczowych komponentów
- [ ] Testy funkcjonalne i matematyczne
- [ ] Prototypowanie jednej z koncepcji: LUT Morphing Gallery, Color Memory Palace lub Temporal LUT Analyzer

---

## 🔍 Analysis
Integracja tabeli porównawczej wymagała modyfikacji `results.html` w celu usunięcia tabeli generowanej po stronie serwera i zastąpienia jej kontenerem dla komponentu `ComparisonTable.js`. Należało również zapewnić ładowanie i inicjalizację tego komponentu.

Implementacja trybu ciemnego objęła dodanie przełącznika w `base.html` oraz odpowiednich stylów CSS w `static/css/style.css` do obsługi dwóch motywów (jasnego i ciemnego) z wykorzystaniem atrybutu `data-bs-theme` i `localStorage` do zapamiętywania wyboru użytkownika.

## 🛠️ Functions / Components
**Zmodyfikowane pliki:**
- `templates/results.html`: Usunięto tabelę generowaną przez serwer, dodano `div#comparison-table-container`, dodano ładowanie i inicjalizację `ComparisonTable.js`.
- `templates/base.html`: Dodano blok `scripts` dla skryptów specyficznych dla strony, dodano przełącznik trybu ciemnego i logikę JavaScript do jego obsługi.
- `static/css/style.css`: Dodano style dla przełącznika trybu ciemnego oraz style dla trybu ciemnego.

**Kluczowe komponenty/logika:**
- `pixelpasta/static/js/components/ComparisonTable.js`: Komponent JS do renderowania tabeli porównawczej po stronie klienta.
- Przełącznik trybu ciemnego w `base.html` i powiązany z nim skrypt JS.
- Style CSS dla trybu ciemnego w `static/css/style.css`.

## 🚀 Action Plan
1. **Integracja tabeli porównawczej (ukończone):**
    - Zmodyfikowano `results.html` w celu użycia `ComparisonTable.js`.
    - Dodano ładowanie `ComparisonTable.js` w `results.html`.
    - Dodano blok `scripts` w `base.html`.
2. **Implementacja trybu ciemnego (ukończone):**
    - Dodano przełącznik trybu ciemnego w `base.html`.
    - Dodano logikę JS do obsługi przełącznika i zapamiętywania wyboru w `localStorage`.
    - Dodano style CSS dla trybu ciemnego w `static/css/style.css`.
3. **Następne kroki:**
    - Rozbudowa dostępności (WCAG).
    - Testy.
    - Prototypowanie nowych funkcji.

## ⚠️ Problems & Risks
- Potencjalne konflikty stylów między Bootstrapem a niestandardowymi stylami trybu ciemnego (wydaje się być rozwiązane przez użycie `data-bs-theme`).
- Konieczność dokładnego przetestowania działania tabeli porównawczej po zmianach.
- Zapewnienie spójnego wyglądu wszystkich elementów interfejsu w obu trybach.

## 💡 Recommendations
- Regularne testowanie na różnych przeglądarkach i urządzeniach.
- Rozważenie użycia biblioteki do zarządzania stanem, jeśli frontend stanie się bardziej złożony.
- Stopniowe wprowadzanie ulepszeń dostępności, zaczynając od najważniejszych komponentów. 