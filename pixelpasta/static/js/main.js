// main.js - Główny plik JavaScript dla aplikacji PixelPasta

document.addEventListener('DOMContentLoaded', function() {
    // Referencje do elementów DOM
    const uploadForm = document.getElementById('upload-form');
    const resultsSection = document.getElementById('results');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const downloadCsvBtn = document.getElementById('download-csv');
    const downloadPdfBtn = document.getElementById('download-pdf');
    
    // Zmienne globalne
    let analysisData = null;
    let curveChart = null;
    
    // Obsługa przesyłania formularza
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        const fileInput = document.getElementById('cube-file');
        const colorSpace = document.getElementById('color-space').value;
        
        // Walidacja formularza
        if (!fileInput.files[0]) {
            showAlert('Proszę wybrać plik .CUBE', 'error');
            return;
        }
        
        if (!colorSpace) {
            showAlert('Proszę wybrać przestrzeń barwną', 'error');
            return;
        }
        
        // Sprawdzenie rozszerzenia pliku
        const fileName = fileInput.files[0].name;
        const fileExt = fileName.split('.').pop().toLowerCase();
        
        if (fileExt !== 'cube') {
            showAlert('Proszę wybrać plik z rozszerzeniem .CUBE', 'error');
            return;
        }
        
        // Wyświetlenie komunikatu o ładowaniu
        showLoading(true);
        
        // Wysłanie danych do API
        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Błąd podczas analizy pliku');
            }
            return response.json();
        })
        .then(data => {
            // Zapisanie danych do zmiennej globalnej
            analysisData = data;
            
            // Wyświetlenie wyników
            showResults();
            
            // Ukrycie komunikatu o ładowaniu
            showLoading(false);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert(error.message, 'error');
            showLoading(false);
        });
    });
    
    // Obsługa zakładek
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Usunięcie klasy active ze wszystkich przycisków i paneli
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Dodanie klasy active do klikniętego przycisku
            this.classList.add('active');
            
            // Wyświetlenie odpowiedniego panelu
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Funkcja wyświetlająca wyniki
    function showResults() {
        // Wyświetlenie sekcji wyników
        resultsSection.style.display = 'block';
        
        // Wygenerowanie wykresu
        generateChart();
        
        // Wygenerowanie tabeli
        generateTable();
        
        // Wyświetlenie informacji o LUT
        displayLutInfo();
        
        // Przewinięcie do sekcji wyników
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Funkcja generująca wykres
    function generateChart() {
        const ctx = document.getElementById('curve-chart').getContext('2d');
        
        // Zniszczenie istniejącego wykresu, jeśli istnieje
        if (curveChart) {
            curveChart.destroy();
        }
        
        // Dane do wykresu
        const exposureValues = analysisData.exposure_percentages;
        const slog3Values = analysisData.slog3_percentages;
        const rec709Values = analysisData.rec709_percentages;
        const lutValues = analysisData.lut_percentages;
        
        // Konfiguracja wykresu
        curveChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: exposureValues,
                datasets: [
                    {
                        label: 'S-Log3',
                        data: slog3Values,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    },
                    {
                        label: 'Rec.709',
                        data: rec709Values,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    },
                    {
                        label: 'Twój LUT',
                        data: lutValues,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Ekspozycja (%)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Wartość wyjściowa (%)'
                        },
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Porównanie krzywych tonalnych',
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Funkcja generująca tabelę
    function generateTable() {
        const tableBody = document.getElementById('table-body');
        tableBody.innerHTML = '';
        
        // Dane do tabeli
        const exposureValues = analysisData.exposure_percentages;
        const slog3Values = analysisData.slog3_percentages;
        const rec709Values = analysisData.rec709_percentages;
        const lutValues = analysisData.lut_percentages;
        
        // Wygenerowanie wierszy tabeli
        for (let i = 0; i < exposureValues.length; i++) {
            const row = document.createElement('tr');
            
            const exposureCell = document.createElement('td');
            exposureCell.textContent = exposureValues[i];
            
            const slog3Cell = document.createElement('td');
            slog3Cell.textContent = slog3Values[i].toFixed(2);
            
            const rec709Cell = document.createElement('td');
            rec709Cell.textContent = rec709Values[i].toFixed(2);
            
            const lutCell = document.createElement('td');
            lutCell.textContent = lutValues[i].toFixed(2);
            
            row.appendChild(exposureCell);
            row.appendChild(slog3Cell);
            row.appendChild(rec709Cell);
            row.appendChild(lutCell);
            
            tableBody.appendChild(row);
        }
    }
    
    // Funkcja wyświetlająca informacje o LUT
    function displayLutInfo() {
        const lutInfo = document.getElementById('lut-info');
        lutInfo.innerHTML = '';
        
        // Dane o LUT
        const lutData = analysisData.lut_info;
        
        // Utworzenie listy informacji
        const infoList = document.createElement('ul');
        infoList.className = 'info-list';
        
        // Dodanie elementów listy
        const infoItems = [
            { label: 'Nazwa pliku', value: lutData.filename },
            { label: 'Typ LUT', value: lutData.lut_type },
            { label: 'Rozmiar LUT 1D', value: lutData.lut_1d_size || 'Brak' },
            { label: 'Rozmiar LUT 3D', value: lutData.lut_3d_size || 'Brak' },
            { label: 'Przestrzeń barwna', value: lutData.color_space }
        ];
        
        infoItems.forEach(item => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `<strong>${item.label}:</strong> ${item.value}`;
            infoList.appendChild(listItem);
        });
        
        lutInfo.appendChild(infoList);
    }
    
    // Obsługa pobierania CSV
    downloadCsvBtn.addEventListener('click', function() {
        if (!analysisData) return;
        
        fetch('/api/download/csv', {
            method: 'GET'
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'lut_analysis.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Błąd podczas pobierania pliku CSV', 'error');
        });
    });
    
    // Obsługa pobierania PDF
    downloadPdfBtn.addEventListener('click', function() {
        if (!analysisData) return;
        
        fetch('/api/download/pdf', {
            method: 'GET'
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'lut_analysis.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Błąd podczas pobierania pliku PDF', 'error');
        });
    });
    
    // Funkcja wyświetlająca komunikat o ładowaniu
    function showLoading(isLoading) {
        // Tutaj można dodać kod do wyświetlania/ukrywania loadera
        // Na przykład:
        // const loader = document.getElementById('loader');
        // loader.style.display = isLoading ? 'block' : 'none';
    }
    
    // Funkcja wyświetlająca alert
    function showAlert(message, type) {
        // Tutaj można dodać kod do wyświetlania alertów
        // Na przykład:
        alert(message);
    }
});
