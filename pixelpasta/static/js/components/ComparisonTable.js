class ComparisonTable {
    constructor(targetElementId, data, logLabel) {
        this.targetElement = document.getElementById(targetElementId);
        this.data = data || [];
        this.logLabel = logLabel || 'Camera Log (%)';
        this.render();
    }

    render() {
        if (!this.data.length) {
            this.targetElement.innerHTML = '<p class="error-message">Brak danych do wyświetlenia w tabeli.</p>';
            return;
        }

        let html = `<table class="comparison-table">
            <thead>
                <tr>
                    <th>Ekspozycja (%)</th>
                    <th>${this.logLabel}</th>
                    <th>Rec.709 (%)</th>
                    <th>Twój LUT (%)</th>
                    <th>Delta (%)</th>
                </tr>
            </thead>
            <tbody>`;

        for (const row of this.data) {
            const delta = row.lut - row.rec709;
            const deltaClass = delta > 0.5 ? 'delta-pos' : delta < -0.5 ? 'delta-neg' : '';
            const deltaSign = delta > 0 ? '+' : '';

            html += `<tr>
                <td>${row.exposure}%</td>
                <td>${row.log.toFixed(2)}%</td>
                <td>${row.rec709.toFixed(2)}%</td>
                <td>${row.lut.toFixed(2)}%</td>
                <td class="${deltaClass}">${deltaSign}${delta.toFixed(2)}%</td>
            </tr>`;
        }

        html += '</tbody></table>';
        this.targetElement.innerHTML = html;
    }
}

// Export to global scope
window.ComparisonTable = ComparisonTable;
export default ComparisonTable;