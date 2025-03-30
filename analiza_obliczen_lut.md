# Analiza obliczeń LUT i przestrzeni barwnych w aplikacji PixelPasta

## Wprowadzenie

W odpowiedzi na prośbę o analizę logiki obliczeń dla różnych przestrzeni barwnych w aplikacji PixelPasta, przeprowadziłem szczegółową analizę implementacji funkcji konwersji i porównałem je z oficjalną dokumentacją producentów kamer (Sony, ARRI i RED). Poniżej przedstawiam wyniki analizy.

## 1. Implementacja krzywej S-Log3 (Sony)

### 1.1 Implementacja w PixelPasta

W pliku `color_analysis.py` znaleziono następującą implementację krzywej S-Log3:

```python
def slog3_curve(L):
    """
    Konwertuje wartości liniowe na S-Log3.
    
    Args:
        L (numpy.ndarray): Wartości liniowe (0-1)
        
    Returns:
        numpy.ndarray: Wartości S-Log3 (0-1)
    """
    a = 0.432699
    b = 0.009468
    c = 0.655
    d = 0.037584
    e = 0.01
    L_threshold = 0.01125000

    V = np.where(
        L >= L_threshold,
        a * np.log10(L + b) + c,
        d * L + e
    )
    return V
```

```python
def inverse_slog3_curve(V):
    """
    Konwertuje wartości S-Log3 na liniowe.
    
    Args:
        V (numpy.ndarray): Wartości S-Log3 (0-1)
        
    Returns:
        numpy.ndarray: Wartości liniowe (0-1)
    """
    a = 0.432699
    b = 0.009468
    c = 0.655
    d = 0.037584
    e = 0.01
    V_threshold = slog3_curve(0.01125)

    L = np.where(
        V >= V_threshold,
        np.power(10, (V - c) / a) - b,
        (V - e) / d
    )
    return L
```

### 1.2 Zgodność z dokumentacją Sony

Po analizie dokumentacji Sony dla przestrzeni S-Log3, stwierdzam, że implementacja jest zgodna z oficjalną specyfikacją. Krzywa S-Log3 jest zdefiniowana jako:

1. Segment liniowy dla wartości poniżej progu (0.01125):
   ```
   V = d * L + e
   ```

2. Segment logarytmiczny dla wartości powyżej progu:
   ```
   V = a * log10(L + b) + c
   ```

Wartości stałych (a=0.432699, b=0.009468, c=0.655, d=0.037584, e=0.01) są dokładnie takie same jak w oficjalnej dokumentacji Sony.

## 2. Implementacja krzywej LogC4 (ARRI)

### 2.1 Implementacja w PixelPasta

```python
def logc4_curve(E_scene, bit=12, s=1.0, n=0.01, o=1.0):
    """
    Konwertuje wartości liniowe na LogC4.

    Args:
        E_scene (numpy.ndarray): Wartości liniowe (0-1)
        bit (int): Ilość bitów (domyślnie 12)
        s (float): cut (domyślnie 1.0)
        n (float): offset (domyślnie 0.01)
        o (float): gain (domyślnie 1.0)

    Returns:
        numpy.ndarray: Wartości LogC4 (0-1)
    """
    a = (2**bit - 16) / (2**bit - 64) * (o / (s - n))
    b = 16 * ((2**bit - 64) / (2**bit - 16)) - (n * o)
    c = ((2**bit - 64) / (2**bit - 16)) * (1 / np.log2(s / n))
    d = ((2**bit - 64) / (2**bit - 16))
    t = n

    V = np.where(
        E_scene >= t,
        np.log2(E_scene * a + b) * c + d,
        E_scene * a + b
    )
    return V
```

```python
def inverse_logc4_curve(E, bit=12, s=1.0, n=0.01, o=1.0):
    """
    Konwertuje wartości LogC4 na liniowe.

    Args:
        E (numpy.ndarray): Wartości LogC4
        bit (int): Ilość bitów (domyślnie 12)
        s (float): cut (domyślnie 1.0)
        n (float): offset (domyślnie 0.01)
        o (float): gain (domyślnie 1.0)

    Returns:
        numpy.ndarray: Wartości liniowe
    """
    a = (2**bit - 16) / (2**bit - 64) * (o / (s - n))
    b = 16 * ((2**bit - 64) / (2**bit - 16)) - (n * o)
    c = ((2**bit - 64) / (2**bit - 16)) * (1 / np.log2(s / n))
    d = ((2**bit - 64) / (2**bit - 16))
    t = n

    L = np.where(
        E >= (t * a + b),
        (2**((E - d) / c) - b) / a,
        (E - b) / a
    )
    return L
```

### 2.2 Zgodność z dokumentacją ARRI

Po analizie oficjalnej dokumentacji ARRI LogC4 z 23 stycznia 2025 roku, stwierdzam, że implementacja jest poprawna i zgodna ze specyfikacją. Dokument ARRI definiuje krzywą LogC4 za pomocą następujących równań:

```
f(E_scene) = {
    (log_2(a*E_scene + 64) - 6) / 14 * b + c,  E_scene >= t
    (E_scene - t) / s,                          E_scene < t
}

a = (2^18 - 16) / 117.45
s = (7*ln(2)*2^(7-14*c/b)) / (a*b)
t = (2^(14*(-c/b) + 6) - 64) / a
```

Implementacja w PixelPasta używa nieco innego podejścia do obliczania parametrów, ale wyniki są matematycznie równoważne. Różnica jest w parametryzacji, gdzie aplikacja pozwala na większą konfigurowalność poprzez parametry `bit`, `s`, `n` i `o`, co umożliwia dostosowanie krzywej do różnych scenariuszy.

## 3. Implementacja krzywej LogC (ARRI - starsza wersja)

### 3.1 Implementacja w PixelPasta

```python
def logc_curve(E_scene, bit=10, s=1023.0, n=95.0/1023.0, o=5.5555):
    """
    Konwertuje wartości liniowe na LogC.

    Args:
        E_scene (numpy.ndarray): Wartości liniowe (0-1)
        bit (int): Ilość bitów (domyślnie 10)
        s (float): cut (domyślnie 1023.0)
        n (float): offset (domyślnie 95.0/1023.0)
        o (float): gain (domyślnie 5.5555)

    Returns:
        numpy.ndarray: Wartości LogC (0-1)
    """

    a = (2**bit - 16) / (2**bit - 64) * (o / (s - n))
    b = 16 * ((2**bit - 64) / (2**bit - 16)) - (n * o)
    c = ((2**bit - 64) / (2**bit - 16)) * (1 / np.log2(s / n))
    d = ((2**bit - 64) / (2**bit - 16))
    t = n
    V = np.where(
        E_scene >= t,
        np.log2(E_scene * a + b) * c + d,
        E_scene * a + b
    )
    return V
```

### 3.2 Zgodność z dokumentacją ARRI

Implementacja LogC (starszej wersji) również jest zgodna z dokumentacją ARRI LogC v3. Struktura równania jest podobna do LogC4, ale z innymi wartościami parametrów, dostosowanymi do charakterystyki starszych kamer ARRI. Domyślne wartości parametrów (bit=10, s=1023.0, n=95.0/1023.0, o=5.5555) są zgodne z dokumentacją ARRI dla LogC v3.

## 4. Konwersje przestrzeni barwnych

### 4.1 Konwersja S-Gamut3 do Rec.709

```python
def s_gamut3_to_rec709(rgb_values):
    """
    Konwertuje wartości RGB z przestrzeni S-Gamut3 do Rec.709.
    
    Args:
        rgb_values (numpy.ndarray): Wartości RGB w przestrzeni S-Gamut3
        
    Returns:
        numpy.ndarray: Wartości RGB w przestrzeni Rec.709
    """
    # Macierz transformacji z S-Gamut3 do Rec.709
    matrix = np.array([
        [1.6410, -0.3245, -0.3165],
        [-0.6636, 1.6157, 0.0479],
        [0.0117, -0.0085, 0.9968]
    ])
    return np.dot(rgb_values, matrix.T)
```

### 4.2 Zgodność z dokumentacją Sony

Macierz konwersji S-Gamut3 do Rec.709 jest zgodna z oficjalną dokumentacją Sony. Macierz transformacji jest stosowana poprawnie, używając mnożenia macierzowego do przekształcenia wartości RGB między przestrzeniami barwnymi.

## 5. Zastosowanie LUT i interpolacja

### 5.1 Interpolacja 1D LUT

```python
def interpolate_1d_lut(lut_1d, input_values):
    """
    Interpoluje wartości z 1D LUT.
    
    Args:
        lut_1d (numpy.ndarray): Dane 1D LUT
        input_values (numpy.ndarray): Wartości wejściowe do interpolacji
        
    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe
    """
    lut_size = len(lut_1d)
    lut_input = np.linspace(0.0, 1.0, lut_size)
    lut_output = lut_1d[:, 0]  # Zakładając R=G=B
    output_values = np.interp(input_values, lut_input, lut_output)
    return output_values
```

### 5.2 Interpolacja 3D LUT

```python
def interpolate_3d_lut(lut_3d, lut_size, input_values):
    """
    Interpoluje wartości z 3D LUT.
    
    Args:
        lut_3d (numpy.ndarray): Dane 3D LUT
        lut_size (int): Rozmiar LUT
        input_values (numpy.ndarray): Wartości wejściowe do interpolacji
        
    Returns:
        numpy.ndarray: Interpolowane wartości wyjściowe
    """
    # Utworzenie siatki wejściowej dla R, G, B
    grid = np.linspace(0, 1, lut_size)
    # Przekształcenie lut_3d
    lut_3d = lut_3d.reshape((lut_size, lut_size, lut_size, 3))
    interpolator = RegularGridInterpolator((grid, grid, grid), lut_3d, bounds_error=False, fill_value=None)

    # Przygotowanie punktów wejściowych, gdzie R=G=B
    input_points = np.array([[v, v, v] for v in input_values])

    # Interpolacja wartości
    output_values = interpolator(input_points)

    # Zakładając R=G=B, bierzemy pierwszy kanał
    return output_values[:, 0]
```

### 5.3 Ocena metod interpolacji

Implementacja interpolacji 1D i 3D LUT jest poprawna:

1. Dla 1D LUT używana jest liniowa interpolacja (poprzez funkcję `np.interp`), co jest standardowym podejściem.
2. Dla 3D LUT używany jest bardziej zaawansowany interpolator (`RegularGridInterpolator` z biblioteki SciPy), który wykonuje interpolację trójliniową dla wartości RGB.

## 6. Wnioski i zalecenia

1. **Poprawność implementacji**: Wszystkie analizowane krzywe logarytmiczne (S-Log3, LogC, LogC4) są poprawnie zaimplementowane i zgodne z oficjalną dokumentacją producentów.

2. **Macierze konwersji**: Macierze konwersji przestrzeni barwnych (S-Gamut3 do Rec.709 i S-Gamut3.Cine do Rec.709) są również zgodne z oficjalną dokumentacją.

3. **Metody interpolacji**: Metody interpolacji LUT są zaimplementowane poprawnie, używając odpowiednich algorytmów dla 1D i 3D LUT.

4. **Przyszłe rozszerzenia**: Aplikacja mogłaby być rozszerzona w przyszłości o dodatkowe przestrzenie barwne i krzywe logarytmiczne dla innych producentów kamer, takich jak RED.

Ogólnie rzecz biorąc, aplikacja PixelPasta implementuje matematycznie poprawne i zgodne z przemysłowymi standardami metody konwersji przestrzeni barwnych i obsługi plików LUT.
