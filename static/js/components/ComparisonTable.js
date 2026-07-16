class ComparisonTable {
    constructor(targetElementId, preloadedData) {
        this.targetElement = document.getElementById(targetElementId);
        this.data = Array.isArray(preloadedData) ? preloadedData : [];
        this.init();
    }

    async init() {
        if (!this.data.length) {
            await this.fetchData();
        }
        this.render();
    }

    async fetchData() {
        try {
            const response = await fetch('/table-data');
            if (!response.ok) throw new Error('Failed to fetch table data');
            this.data = await response.json();
        } catch (err) {
            this.data = [];
            this.targetElement.innerHTML = '<p class="text-danger">Could not load comparison table data.</p>';
        }
    }

    render() {
        if (!this.data.length) {
            this.targetElement.innerHTML = '<p class="text-warning">No comparison data available.</p>';
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
                <td>${Number(row.input).toFixed(5)}</td>
                <td>${Number(row.curve).toFixed(5)}</td>
                <td>${Number(row.lut).toFixed(5)}</td>
                <td class="${deltaClass}">${Number(row.delta).toFixed(5)}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        this.targetElement.innerHTML = html;
    }
}

window.ComparisonTable = ComparisonTable;
