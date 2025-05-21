# LUT Analyzer API Documentation

## Spis treści
- [Wprowadzenie](#wprowadzenie)
- [Uwierzytelnianie](#uwierzytelnianie)
- [Limity i zabezpieczenia](#limity-i-zabezpieczenia)
- [Endpointy](#endpointy)
- [Przykłady użycia](#przykłady-użycia)
- [Obsługa błędów](#obsługa-błędów)
- [Dobre praktyki](#dobre-praktyki)

## Wprowadzenie

LUT Analyzer API udostępnia pełną funkcjonalność analizy LUT poprzez interfejs RESTful. API jest dostępne pod adresem `http://localhost:8080/api`.

## Uwierzytelnianie

API używa uwierzytelniania poprzez tokeny JWT. Tokeny można uzyskać poprzez endpoint `/api/auth`:

```http
POST /api/auth
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Otrzymany token należy dołączać w nagłówku `Authorization`:
```http
Authorization: Bearer your_jwt_token
```

## Limity i zabezpieczenia

- Limit rozmiaru pliku LUT: 50MB
- Rate limiting: 100 requestów/minutę
- Maksymalna liczba plików w batch analysis: 10
- Timeout analizy: 30 sekund
- Wymagane formaty plików: .cube
- Wspierane formaty odpowiedzi: JSON, XML

## Endpointy

### Analiza pojedynczego LUT
#### `POST /api/analyze`

Analizuje pojedynczy plik LUT.

**Parametry:**
- `file`: Plik LUT (.cube)
- `source_colorspace` (opcjonalny): Przestrzeń kolorów źródłowych
- `target_colorspace` (opcjonalny): Przestrzeń kolorów docelowych
- `detailed` (opcjonalny): Czy generować szczegółową analizę (default: false)

**Odpowiedź:**
```json
{
  "analysis": {
    "colorSpaceInfo": {
      "source": "S-Log3",
      "target": "Rec.709",
      "gamut": "S-Gamut3"
    },
    "transformationMetrics": {
      "contrast": 0.85,
      "saturation": 1.2,
      "colorBalance": {
        "r": 1.0,
        "g": 0.98,
        "b": 1.02
      }
    },
    "qualityMetrics": {
      "banding": 0.02,
      "smoothness": 0.95,
      "accuracy": 0.99
    }
  },
  "visualizations": {
    "rgbDistribution": "base64...",
    "colorCurves": "base64...",
    "gradientRamps": "base64..."
  }
}
```

### Analiza wsadowa
#### `POST /api/analyze/batch`

Analizuje wiele plików LUT jednocześnie.

**Parametry:**
- `files[]`: Pliki LUT (.cube)
- `detailed` (opcjonalny): Czy generować szczegółową analizę
- `aggregate` (opcjonalny): Czy generować zagregowane statystyki

**Odpowiedź:**
```json
{
  "results": [
    {
      "filename": "lut1.cube",
      "analysis": { ... }
    }
  ],
  "summary": {
    "totalFiles": 2,
    "averageMetrics": {
      "contrast": 0.87,
      "saturation": 1.15
    },
    "recommendations": [
      "Zwiększ kontrast w lut2.cube"
    ]
  }
}
```

### Informacje o przestrzeniach kolorów
#### `GET /api/colorspaces`

Zwraca listę wspieranych przestrzeni kolorów.

**Odpowiedź:**
```json
{
  "supported": [
    {
      "name": "S-Log3/S-Gamut3",
      "type": "log",
      "gamut": "S-Gamut3",
      "details": {
        "blackLevel": 95,
        "whiteLevel": 1000
      }
    }
  ],
  "combinations": [
    {
      "source": "S-Log3/S-Gamut3",
      "target": "Rec.709",
      "recommended": true
    }
  ]
}
```

## Przykłady użycia

### cURL
```bash
# Autoryzacja
curl -X POST http://localhost:8080/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Analiza z autoryzacją
curl -X POST http://localhost:8080/api/analyze \
  -H "Authorization: Bearer your_token" \
  -F "file=@path/to/lut.cube" \
  -F "detailed=true"
```

### Python
```python
import requests

class LUTAnalyzer:
    def __init__(self, api_url, auth_token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {auth_token}"}
    
    def analyze_lut(self, lut_path, detailed=False):
        with open(lut_path, 'rb') as f:
            files = {'file': f}
            data = {'detailed': detailed}
            response = requests.post(
                f"{self.api_url}/analyze",
                headers=self.headers,
                files=files,
                data=data
            )
            return response.json()
    
    def batch_analyze(self, lut_paths, aggregate=True):
        files = [('files', open(path, 'rb')) for path in lut_paths]
        data = {'aggregate': aggregate}
        response = requests.post(
            f"{self.api_url}/analyze/batch",
            headers=self.headers,
            files=files,
            data=data
        )
        return response.json()

# Użycie
analyzer = LUTAnalyzer("http://localhost:8080/api", "your_token")
result = analyzer.analyze_lut("path/to/lut.cube", detailed=True)
```

### JavaScript
```javascript
class LUTAnalyzer {
  constructor(apiUrl, authToken) {
    this.apiUrl = apiUrl;
    this.headers = {
      Authorization: `Bearer ${authToken}`
    };
  }

  async analyzeLUT(file, detailed = false) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('detailed', detailed);

    const response = await fetch(`${this.apiUrl}/analyze`, {
      method: 'POST',
      headers: this.headers,
      body: formData
    });

    return await response.json();
  }

  async batchAnalyze(files, aggregate = true) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('aggregate', aggregate);

    const response = await fetch(`${this.apiUrl}/analyze/batch`, {
      method: 'POST',
      headers: this.headers,
      body: formData
    });

    return await response.json();
  }
}

// Użycie
const analyzer = new LUTAnalyzer('http://localhost:8080/api', 'your_token');
const fileInput = document.querySelector('input[type="file"]');
const result = await analyzer.analyzeLUT(fileInput.files[0], true);
```

### Go
```go
package main

import (
    "bytes"
    "encoding/json"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

type LUTAnalyzer struct {
    ApiURL    string
    AuthToken string
}

func NewLUTAnalyzer(apiURL, authToken string) *LUTAnalyzer {
    return &LUTAnalyzer{
        ApiURL:    apiURL,
        AuthToken: authToken,
    }
}

func (a *LUTAnalyzer) AnalyzeLUT(filePath string, detailed bool) (map[string]interface{}, error) {
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    part, err := writer.CreateFormFile("file", filePath)
    if err != nil {
        return nil, err
    }
    
    _, err = io.Copy(part, file)
    if err != nil {
        return nil, err
    }
    
    writer.WriteField("detailed", fmt.Sprintf("%v", detailed))
    writer.Close()
    
    req, err := http.NewRequest("POST", a.ApiURL+"/analyze", body)
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("Authorization", "Bearer "+a.AuthToken)
    req.Header.Set("Content-Type", writer.FormDataContentType())
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    
    return result, nil
}

// Użycie
func main() {
    analyzer := NewLUTAnalyzer("http://localhost:8080/api", "your_token")
    result, err := analyzer.AnalyzeLUT("path/to/lut.cube", true)
    if err != nil {
        panic(err)
    }
    fmt.Printf("%+v\n", result)
}
```

## Obsługa błędów

API używa standardowych kodów HTTP oraz zwraca szczegółowe komunikaty błędów:

```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Niewspierany format pliku. Wspierane formaty: .cube",
    "details": {
      "filename": "test.wrong",
      "supportedFormats": [".cube"]
    }
  }
}
```

### Kody błędów
- `400 Bad Request`: Nieprawidłowe parametry
- `401 Unauthorized`: Brak lub nieprawidłowy token
- `403 Forbidden`: Brak uprawnień
- `404 Not Found`: Zasób nie istnieje
- `413 Payload Too Large`: Przekroczony limit rozmiaru pliku
- `429 Too Many Requests`: Przekroczony limit requestów
- `500 Internal Server Error`: Błąd serwera

## Dobre praktyki

1. **Obsługa błędów**
   - Zawsze sprawdzaj kody odpowiedzi
   - Implementuj retry logic dla błędów 5xx
   - Loguj szczegóły błędów

2. **Optymalizacja**
   - Używaj batch analysis dla wielu plików
   - Ustawiaj detailed=false jeśli nie potrzebujesz szczegółowej analizy
   - Implementuj caching odpowiedzi

3. **Bezpieczeństwo**
   - Przechowuj token w bezpiecznym miejscu
   - Używaj HTTPS w produkcji
   - Regularnie rotuj tokeny

4. **Monitorowanie**
   - Śledź rate limiting
   - Monitoruj czasy odpowiedzi
   - Implementuj health checks 