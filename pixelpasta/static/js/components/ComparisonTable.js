class ComparisonTable {
    constructor(targetElementId) {
        this.targetElement = document.getElementById(targetElementId);
        this.data = [];
        this.init();
    }

    async init() {
        await this.fetchData();
        this.render();
    }

    async fetchData() {
        try {
            const response = await fetch('/table-data');
            if (!response.ok) throw new Error('Błąd pobierania danych');
            this.data = await response.json();
        } catch (err) {
            this.data = [];
            this.targetElement.innerHTML = '<p class="text-danger">Nie udało się pobrać danych do tabeli porównawczej.</p>';
        }
    }

    render() {
        if (!this.data.length) {
            this.targetElement.innerHTML = '<p class="text-warning">Brak danych do porównania.</p>';
            return;
        }
        let html = `<table class="comparison-table">
            <thead>
                <tr>
                    <th>Input</th>
                    <th>Reference Curve</th>
                    <th>LUT Output</th>
                    <th>Delta</th>
                </tr>
            </thead>
            <tbody>`;
        for (const row of this.data) {
            const deltaClass = row.delta > 0.01 ? 'delta-pos' : row.delta < -0.01 ? 'delta-neg' : '';
            html += `<tr>
                <td>${row.input.toFixed(5)}</td>
                <td>${row.curve.toFixed(5)}</td>
                <td>${row.lut.toFixed(5)}</td>
                <td class="${deltaClass}">${row.delta.toFixed(5)}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        this.targetElement.innerHTML = html;
    }
}

// Eksport do globalnego scope, by można było użyć w app.js
window.ComparisonTable = ComparisonTable; 