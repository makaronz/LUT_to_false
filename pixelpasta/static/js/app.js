console.log('PixelPasta App Initialized');

// Zakładamy, że FileUpload.js dodał klasę FileUpload do window
// W przyszłości można to zmienić na import modułów ES6:
// import FileUpload from './components/FileUpload.js';

let curveChartInstance = null; // Zmienna do przechowywania instancji wykresu

function renderCurveChart(chartData) {
    const ctx = document.getElementById('curve-chart').getContext('2d');
    if (curveChartInstance) {
        curveChartInstance.destroy(); // Zniszcz poprzedni wykres, jeśli istnieje
    }
    curveChartInstance = new Chart(ctx, {
        type: 'line',
        data: chartData, // chartData powinno być zgodne ze strukturą danych Chart.js
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Wartość wejściowa / Ekspozycja'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Wartość wyjściowa'
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function renderComparisonTable(tableData) {
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = ''; // Wyczyść poprzednie dane

    // Założenie: tableData to tablica obiektów, np. 
    // [{ "exposure": "0%", "slog3": "X%", "rec709": "Y%", "your_lut": "Z%" }, ...]
    // Klucze obiektu powinny odpowiadać nagłówkom tabeli (lub być mapowane)
    
    // Dynamiczne tworzenie nagłówków na podstawie pierwszego obiektu danych (jeśli to konieczne)
    // lub użycie statycznych nagłówków z HTML i dopasowanie kluczy
    const headers = Object.keys(tableData[0] || {}); 
    // Można też pobrać nagłówki z HTML: document.querySelectorAll('#comparison-table th')

    tableData.forEach(rowData => {
        const row = tableBody.insertRow();
        headers.forEach(headerKey => {
            const cell = row.insertCell();
            cell.textContent = rowData[headerKey] !== undefined ? rowData[headerKey] : '-';
        });
    });
}

function displayLutInfo(lutInfo) {
    const infoContainer = document.getElementById('lut-info');
    infoContainer.innerHTML = ''; // Wyczyść poprzednie informacje

    // Założenie: lutInfo to obiekt, np. 
    // { "title": "Example LUT", "size": "33x33x33", ... }
    for (const [key, value] of Object.entries(lutInfo)) {
        const p = document.createElement('p');
        const strong = document.createElement('strong');
        strong.textContent = `${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: `;
        p.appendChild(strong);
        p.append(document.createTextNode(Array.isArray(value) ? value.join(', ') : value));
        infoContainer.appendChild(p);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    const fileUploadContainer = document.getElementById('file-upload-component-container');
    const colorSpaceSelect = document.getElementById('color-space');
    const analyzeButton = document.getElementById('analyze-button');
    const resultsSection = document.getElementById('results');
    let selectedFile = null;

    if (fileUploadContainer) {
        const fileUploadComponent = new FileUpload(fileUploadContainer, (file, error) => {
            if (error) {
                console.error('Błąd ładowania pliku:', error);
                selectedFile = null;
                analyzeButton.style.display = 'none';
                resultsSection.style.display = 'none';
            } else {
                console.log('Wybrany plik:', file.name);
                selectedFile = file;
                resultsSection.style.display = 'none'; // Ukryj poprzednie wyniki
                if (colorSpaceSelect.value) {
                    analyzeButton.style.display = 'block';
                }
            }
        });
    } else {
        console.error('Nie znaleziono kontenera dla komponentu FileUpload.');
    }

    colorSpaceSelect.addEventListener('change', () => {
        resultsSection.style.display = 'none'; // Ukryj poprzednie wyniki przy zmianie
        if (selectedFile && colorSpaceSelect.value) {
            analyzeButton.style.display = 'block';
        } else {
            analyzeButton.style.display = 'none';
        }
    });

    analyzeButton.addEventListener('click', () => {
        if (!selectedFile) {
            alert('Proszę najpierw wybrać plik .CUBE.');
            return;
        }
        if (!colorSpaceSelect.value) {
            alert('Proszę wybrać przestrzeń barwną kamery.');
            return;
        }

        console.log('Rozpoczynanie analizy dla pliku:', selectedFile.name, 'i przestrzeni:', colorSpaceSelect.value);
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Analizowanie...';

        const formData = new FormData();
        formData.append('lut_file', selectedFile);
        formData.append('curve_select', colorSpaceSelect.value);

        fetch('/analyze', { 
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Spróbuj odczytać błąd jako JSON, jeśli serwer tak go wysyła
                return response.json().then(errData => {
                    throw new Error(errData.error || `Błąd serwera: ${response.status}`);
                }).catch(() => {
                    // Jeśli odpowiedź błędu nie jest JSONem
                    throw new Error(`Błąd serwera: ${response.status} ${response.statusText}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Pełna odpowiedź z serwera:', data);
            if (data.error) {
                alert(`Błąd analizy: ${data.error}`);
                resultsSection.style.display = 'none';
            } else {
                // Walidacja czy dane istnieją przed renderowaniem
                const hasData = data.curve_data || 
                               (data.table_data && data.table_data.length > 0) || 
                               data.lut_info;
                
                if (hasData) {
                    if (data.curve_data) renderCurveChart(data.curve_data);
                    if (data.table_data && data.table_data.length > 0) renderComparisonTable(data.table_data);
                    if (data.lut_info) displayLutInfo(data.lut_info);
                    
                    // Inicjalizuj tabelę porównawczą jeśli istnieje kontener
                    if (document.getElementById('comparison-table-container')) {
                        new ComparisonTable('comparison-table-container');
                    }
                    
                    resultsSection.style.display = 'block';
                } else {
                    alert('Serwer nie zwrócił żadnych danych do wyświetlenia.');
                    resultsSection.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Błąd podczas wysyłania żądania analizy:', error);
            alert(`Wystąpił błąd: ${error.message}`);
            resultsSection.style.display = 'none';
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Analizuj';
        });
    });

    // Obsługa zakładek (tabs)
    const tabButtons = document.querySelectorAll('.tabs .tab-btn');
    const tabPanes = document.querySelectorAll('.tab-content .tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const targetTab = button.getAttribute('data-tab');
            tabPanes.forEach(pane => {
                if (pane.id === targetTab) {
                    pane.classList.add('active');
                } else {
                    pane.classList.remove('active');
                }
            });
        });
    });

    if (document.getElementById('comparison-table-container')) {
        new ComparisonTable('comparison-table-container');
    }
}); 