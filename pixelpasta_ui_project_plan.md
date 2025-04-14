# Plan Projektu Interfejsu Użytkownika (UI) dla Aplikacji PixelPasta

## 1. Cel i Grupa Docelowa

*   **Cel aplikacji:** Głównym celem PixelPasta jest umożliwienie profesjonalistom z branży filmowej (filmowcom, kolorystom, operatorom DIT) łatwej i precyzyjnej analizy oraz porównywania plików LUT (.CUBE). Aplikacja ma na celu wizualizację charakterystyki transformacji kolorystycznej LUT i jej wpływu na wartości ekspozycji w różnych przestrzeniach barwnych (S-Log3, LogC, LogC4, Rec.709).
*   **Grupa docelowa:**
    *   **Główni użytkownicy:** Koloryści, Asystenci Kolorystów, Operatorzy DIT (Digital Imaging Technician), Operatorzy kamer, Postprodukcyjni Supervisorzy.
    *   **Charakterystyka:** Użytkownicy techniczni, zaznajomieni z terminologią związaną z kolorem, przestrzeniami barwnymi i formatami plików LUT. Cenią precyzję, szybkość działania i czytelność prezentowanych danych. Mogą pracować zarówno w studiu, jak i w terenie.
    *   **Potrzeby:** Potrzebują narzędzia do szybkiej weryfikacji LUT-ów, porównania różnych wersji "looków", zrozumienia wpływu LUT na sygnał z kamery i przygotowania materiałów do dalszej postprodukcji.
    *   **Kontekst użycia:** Aplikacja będzie używana głównie na komputerach stacjonarnych lub laptopach podczas pracy nad materiałem filmowym, w fazie preprodukcji, na planie lub w postprodukcji.

## 2. Kluczowe Funkcjonalności i Przepływy Użytkownika

*   **Kluczowe Funkcjonalności:**
    1.  Wczytywanie pliku LUT w formacie .CUBE (obsługa 1D i 3D).
    2.  Wybór wejściowej przestrzeni barwnej/krzywej gamma (np. S-Gamut3/S-Log3, ARRI LogC, LogC4).
    3.  Automatyczna analiza pliku LUT.
    4.  Generowanie i wyświetlanie tabeli porównawczej wartości ekspozycji (wejściowe vs Rec.709 vs LUT).
    5.  Generowanie i wyświetlanie wykresu krzywej tonalnej (Tone Curve).
    6.  (Potencjalne rozszerzenia): Porównanie wielu LUT-ów, eksport wyników (np. do PDF/CSV), wizualizacja na obrazie testowym, zapisywanie/wczytywanie analiz.
*   **Główny Przepływ Użytkownika (User Flow):**
    1.  **Start:** Użytkownik otwiera aplikację webową.
    2.  **Wczytanie LUT:** Użytkownik klika przycisk "Wczytaj LUT" / przeciąga plik .CUBE na wyznaczony obszar.
    3.  **Wybór Przestrzeni Barwnej:** Użytkownik wybiera z listy rozwijanej wejściową przestrzeń barwną/gamma.
    4.  **Analiza:** System automatycznie przetwarza plik (UI informuje o postępie).
    5.  **Prezentacja Wyników:** Aplikacja wyświetla wyniki: Tabela porównawcza, Wykres krzywej tonalnej, (Opcjonalnie) Metadane LUT.
    6.  **(Opcjonalnie) Interakcja z Wynikami:** Analiza danych, (przyszłość) eksport, porównanie.
    7.  **(Opcjonalnie) Nowa Analiza:** Użytkownik wczytuje nowy plik LUT.

## 3. Architektura Informacji i Nawigacja

*   **Struktura:** Prosta, jednostronicowa aplikacja (SPA) lub minimalna liczba widoków.
    *   **Widok Główny/Startowy:** Wczytywanie pliku, wybór parametrów.
    *   **Widok Wyników:** Tabela, wykres (dynamicznie aktualizowany lub osobny widok).
*   **Nawigacja:**
    *   Minimalna. Stały nagłówek (logo, linki "O aplikacji"/"Pomoc").
    *   Wyraźne przyciski akcji.

## 4. Wireframes (Opisy Ekranów)

*   **Ekran Startowy / Wczytywania:**
    *   Nagłówek: Logo/Nazwa.
    *   Obszar Główny: Obszar "Przeciągnij i upuść" / Przycisk "Wybierz plik", Lista rozwijana "Wybierz przestrzeń barwną/gamma", Przycisk "Analizuj" (nieaktywny do czasu spełnienia warunków).
    *   Stopka (Opcjonalnie): Linki.
*   **Ekran Wyników Analizy:**
    *   Nagłówek.
    *   Sekcja Podsumowania (Opcjonalnie): Nazwa pliku, wybrana przestrzeń.
    *   Sekcja Tabeli Porównawczej: Tytuł, Kolumny (np. "Wartość Wejściowa (Stopnie EV)", "Wartość Wejściowa (Kod Liniowy)", "Wartość Rec.709 (Kod)", "Wartość po LUT (Kod)"), Wiersze (kluczowe punkty ekspozycji), Przewijanie.
    *   Sekcja Wykresu Krzywej Tonalnej: Tytuł, Opisane osie, Krzywa danych, Legenda, (Innowacja) Interaktywność (tooltipy, zoom).
    *   Sekcja Akcji (Opcjonalnie): Przyciski "Analizuj kolejny LUT", "Eksportuj wyniki" (przyszłość).
    *   Komunikaty o Stanie: Wskaźnik postępu, komunikaty o błędach.

## 5. Komponenty UI

*   **Przyciski:** Główny, Drugorzędny (Stany: Domyślny, Hover, Aktywny, Nieaktywny).
*   **Formularze:** Pole wyboru pliku, Lista rozwijana (Stany: Domyślny, Fokus, Błąd).
*   **Tabela:** Stylizacja nagłówków, wierszy, komórek, formatowanie danych.
*   **Wykres:** Stylizacja osi, etykiet, siatki, krzywej, legendy.
*   **Komunikaty/Powiadomienia:** Informacyjne, Sukcesu, Ostrzeżenia, Błędu.
*   **Ikony:** Spójny zestaw (np. wczytywanie, błędy, ostrzeżenia, eksport).
*   **Wskaźnik Postępu:** Pasek lub spinner.

## 6. Styl Wizualny i Branding

*   **Ogólna Estetyka:** Profesjonalny, Techniczny, Czysty, Minimalistyczny, Nowoczesny.
*   **Paleta Kolorów:** Neutralna baza (szarości, biel, opcjonalnie ciemny motyw), 1-2 kolory akcentujące (niezakłócające percepcji danych).
*   **Typografia:** Czytelny krój bezszeryfowy (np. Inter, Roboto), hierarchia typograficzna.
*   **Ikonografia:** Spójny zestaw ikon (liniowe lub wypełnione).
*   **Branding:** Do zaproponowania przez grafika (logo, spójne elementy).

## 7. Dostępność

*   **Wymagany Poziom:** WCAG 2.1, poziom AA.
*   **Kluczowe Aspekty:** Kontrast, nawigacja klawiaturą, struktura semantyczna HTML, teksty alternatywne, etykiety formularzy, dostępne komunikaty, projektowanie z myślą o dostępności.

## 8. Platforma i Ograniczenia

*   **Platforma Docelowa:** Aplikacja webowa, responsywna (RWD).
*   **Ograniczenia:** Wydajność (UI informuje o postępie analizy), Zależność od backendu (obsługa błędów komunikacji).

## 9. Analiza Konkurencji

*   Grafik powinien przeanalizować UI/UX podobnych narzędzi (np. DaVinci Resolve, Lattice, IWLTBAP LUT Previewer).
*   **Cel:** Identyfikacja dobrych praktyk, wzorców interakcji, inspiracji, elementów do uniknięcia.

## 10. Oczekiwane Rezultaty (Dostarczane przez Grafika)

*   **Mockupy High-Fidelity:** Projekty graficzne kluczowych ekranów i stanów (np. Figma, Sketch, XD).
*   **Klikalny Prototyp (Zalecane):** Pokazujący przepływy i interakcje.
*   **Biblioteka Komponentów UI:** Zdefiniowane komponenty i ich stany.
*   **Style Guide:** Dokumentacja stylu (kolory, typografia, ikony, layout, logo).
*   **Wytyczne dotyczące Dostępności:** Podsumowanie zastosowanych rozwiązań.