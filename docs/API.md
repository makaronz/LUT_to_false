# API / interfejsy aplikacji

> **Uwaga:** wcześniejsza wersja tego pliku opisywała rozbudowane REST API
> (autoryzacja JWT `/api/auth`, `/api/colorspaces`, `/api/analyze/batch`,
> limity zapytań, odpowiedzi XML, SDK w Pythonie/JS/Go). **Takie API nigdy nie
> istniało w kodzie.** Poniżej udokumentowano to, co aplikacje faktycznie
> udostępniają.

## 1. Web app — `lutcomparetool_app.py` (port 8080)

Aplikacja Flask oparta o formularze HTML (bez autoryzacji, bez JSON REST API).
Pełna lista tras znajduje się w [README](../README.md#web-application-lutcomparetool_apppy).
Kluczowa trasa:

- `POST /analyze` — pola formularza `lut_file` (plik `.cube`) oraz
  `curve_select` (np. `slog3`, `logc3`, `logc4`, `rec709`, ...).
  Zwraca JSON: `{ "status", "curve_data", "table_data", "lut_info" }`.

Przykład:
```bash
curl -X POST -F "lut_file=@path/to/lut.cube" -F "curve_select=slog3" \
     http://localhost:8080/analyze
```

## 2. Eksperymentalna app — `pixelpasta/app.py` (port 5000)

- `POST /api/analyze` — pola `cube-file` (plik `.cube`) oraz `color-space`
  (`S-Gamut3`, `S-Gamut3.Cine`, `LogC4`, `LogC`).
  Zwraca JSON z listami procentowymi:
  `{ "exposure_percentages", "log_percentages", "rec709_percentages", "lut_percentages", "lut_info" }`.

## 3. CLI — `cube_analyzer.py`

```bash
python cube_analyzer.py input.cube -s slog3 -t rec709 -o output_dir
```
Zobacz sekcję CLI w [README](../README.md).
