document.addEventListener('DOMContentLoaded', initialize);

// --- Configuration for Company-Provided B2B Benefits ---
const companyBenefitsConfig = {
    paidVacationDays: { label: 'Płatne dni urlopowe', type: 'days', defaultValue: 26, tooltip: 'Liczba dni płatnego urlopu oferowanego przez firmę.' },
    paidSickDays: { label: 'Płatne dni chorobowe', type: 'days', defaultValue: 10, tooltip: 'Liczba dni płatnego chorobowego (L4) oferowanego przez firmę.' },
    privateHealthcare: { label: 'Prywatna opieka medyczna', type: 'currency', defaultValue: 2400, tooltip: 'Roczna wartość pakietu medycznego.' },
    lifeInsurance: { label: 'Ubezpieczenie na życie', type: 'currency', defaultValue: 800, tooltip: 'Roczna składka na ubezpieczenie na życie.' },
    sportCard: { label: 'Karta sportowa', type: 'currency', defaultValue: 1200, tooltip: 'Roczny koszt karty sportowej (np. MultiSport).' },
    trainingBudget: { label: 'Budżet szkoleniowy', type: 'currency', defaultValue: 3000, tooltip: 'Roczna kwota do wykorzystania na szkolenia i konferencje.' },
    equipmentProvided: { label: 'Zapewniony sprzęt', type: 'currency', defaultValue: 4000, tooltip: 'Roczna wartość amortyzacji sprzętu dostarczonego przez firmę.' },
    // Add more benefits as needed
};

function renderCompanyBenefits() {
    const container = document.getElementById('company-benefits-container');
    if (!container) return;

    let html = '';
    for (const [key, config] of Object.entries(companyBenefitsConfig)) {
        const inputType = config.type === 'days' ? 'number' : 'number';
        const step = config.type === 'currency' ? '100' : '1';
        const unit = config.type === 'currency' ? 'PLN' : 'dni';

        html += `
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" id="${key}_enabled">
                <label class="form-check-label" for="${key}_enabled">${config.label}</label>
                <div class="input-group input-group-sm mt-1">
                    <input type="${inputType}" class="form-control" id="${key}_value" value="${config.defaultValue}" step="${step}" data-bs-toggle="tooltip" title="${config.tooltip}" disabled>
                    <span class="input-group-text">${unit}</span>
                </div>
            </div>
        `;
    }
    container.innerHTML = html;

    // Add event listeners to enable/disable inputs
    for (const key in companyBenefitsConfig) {
        const checkbox = document.getElementById(`${key}_enabled`);
        const input = document.getElementById(`${key}_value`);
        checkbox.addEventListener('change', () => {
            input.disabled = !checkbox.checked;
        });
    }
}

function getFormValues() {
    const companyBenefits = {};
    for (const key in companyBenefitsConfig) {
        const checkbox = document.getElementById(`${key}_enabled`);
        const input = document.getElementById(`${key}_value`);
        companyBenefits[key] = {
            enabled: checkbox.checked,
            value: parseFloat(input.value) || 0,
            days: companyBenefitsConfig[key].type === 'days' ? parseInt(input.value) || 0 : undefined
        };
    }

    const b2b_faktura_rocznie = (parseFloat(document.getElementById('b2b_faktura').value) || 0) * 12;
    const totalBenefitValue = Object.values(companyBenefits).reduce((sum, benefit) => sum + (benefit.enabled ? benefit.value : 0), 0) + (parseFloat(document.getElementById('customBenefits').value) || 0);

    if (totalBenefitValue > 0.5 * b2b_faktura_rocznie) {
        alert('Ostrzeżenie: Całkowita wartość benefitów przekracza 50% rocznego przychodu B2B. Wyniki mogą być nierealistyczne.');
    }

    return {
        b2b: {
            faktura_miesieczna: parseFloat(document.getElementById('b2b_faktura').value) || 0,
            forma_opodatkowania: document.getElementById('b2b_opodatkowanie').value,
            zus_rodzaj: document.getElementById('b2b_zus').value,
            zus_chorobowe: document.getElementById('b2b_chorobowe').checked,
            koszty_firmowe_miesieczne: parseFloat(document.getElementById('b2b_koszty').value) || 0,
            urlop_dni: parseInt(document.getElementById('b2b_urlop').value) || 0,
            przestoje_miesiace: parseFloat(document.getElementById('b2b_przestoje').value) || 0,
            wiek: parseInt(document.getElementById('wiek').value) || 0,
            ulga_dla_mlodych: document.getElementById('ulga_dla_mlodych').checked,
            customBenefits: parseFloat(document.getElementById('customBenefits').value) || 0,
            companyBenefits: companyBenefits
        },
        uop: {
            wynagrodzenie_brutto: parseFloat(document.getElementById('uop_brutto').value) || 0,
            koszty_uzyskania_przychodu: parseFloat(document.getElementById('uop_koszty_przychodu').value) || 0,
            wybrane_benefity: Array.from(document.querySelectorAll('#calculator-form [id^="uop_benefit_"]:checked')).map(el => el.value),
            wiek: parseInt(document.getElementById('wiek').value) || 0,
            ulga_dla_mlodych: document.getElementById('ulga_dla_mlodych').checked
        }
    };
}

let comparisonChart = null;
let b2bDistributionChart = null;

function formatPLN(value) {
    return new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(value);
}

function renderResults(data) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    resultsDiv.style.display = 'block';

    const { b2b_results, uop_results, break_even_faktura } = data;

    // Destroy previous chart instances if they exist
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    if (b2bDistributionChart) {
        b2bDistributionChart.destroy();
    }

    resultsDiv.innerHTML = `
        <h2 class="text-center mb-4">Podsumowanie</h2>
        <div class="row text-center">
            <div class="col-md-6">
                <div class="card h-100 ${b2b_results.calkowita_roczna_wartosc > uop_results.calkowita_roczna_wartosc ? 'border-success' : 'border-danger'}">
                    <div class="card-header"><h3>B2B</h3></div>
                    <div class="card-body">
                        <h4 class="card-title">${formatPLN(b2b_results.miesieczne_netto)} / msc</h4>
                        <p class="card-text">Rocznie: <strong>${formatPLN(b2b_results.calkowita_roczna_wartosc)}</strong></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100 ${uop_results.calkowita_roczna_wartosc > b2b_results.calkowita_roczna_wartosc ? 'border-success' : 'border-danger'}">
                    <div class="card-header"><h3>UoP</h3></div>
                    <div class="card-body">
                        <h4 class="card-title">${formatPLN(uop_results.miesieczne_netto)} / msc</h4>
                        <p class="card-text">Całkowita roczna wartość: <strong>${formatPLN(uop_results.calkowita_roczna_wartosc)}</strong></p>
                    </div>
                </div>
            </div>
        </div>

        <h3 class="mt-5">Szczegółowe Porównanie Roczne</h3>
        <table class="table table-bordered">
            <thead class="table-light">
                <tr>
                    <th>Kategoria</th>
                    <th>B2B</th>
                    <th>UoP</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Przychód / Brutto</td>
                    <td>${formatPLN(b2b_results.roczny_przychod)}</td>
                    <td>${formatPLN(uop_results.roczne_brutto)}</td>
                </tr>
                <tr class="table-danger">
                    <td>Koszty (firmowe, ZUS, podatki)</td>
                    <td>-${formatPLN(b2b_results.roczne_koszty_firmowe + b2b_results.roczny_zus + b2b_results.roczny_podatek)}</td>
                    <td>-${formatPLN(uop_results.roczny_zus + uop_results.roczny_podatek)}</td>
                </tr>
                 <tr>
                    <td><em>- w tym ZUS</em></td>
                    <td><em>${formatPLN(b2b_results.roczny_zus)}</em></td>
                    <td><em>${formatPLN(uop_results.roczny_zus)}</em></td>
                </tr>
                 <tr>
                    <td><em>- w tym Podatek</em></td>
                    <td><em>${formatPLN(b2b_results.roczny_podatek)}</em></td>
                    <td><em>${formatPLN(uop_results.roczny_podatek)}</em></td>
                </tr>
                <tr class="table-warning">
                    <td>Utracony przychód (urlop, przestoje)</td>
                    <td>-${formatPLN(b2b_results.roczny_utracony_przychod)}</td>
                    <td class="text-success">Brak (płatne)</td>
                </tr>
                <tr class="table-success">
                    <td>Wartość benefitów od firmy</td>
                    <td>+${formatPLN(b2b_results.roczna_wartosc_benefitow_od_firmy)}</td>
                    <td>+${formatPLN(uop_results.roczna_wartosc_benefitow)}</td>
                </tr>
                <tr class="table-success">
                    <td>Wartość własnych korzyści B2B</td>
                    <td>+${formatPLN(b2b_results.roczna_wartosc_wlasnych_korzysci)}</td>
                    <td>-</td>
                </tr>
                <tr class="table-info">
                    <td><strong>Całkowita roczna wartość</strong></td>
                    <td><strong>${formatPLN(b2b_results.calkowita_roczna_wartosc)}</strong></td>
                    <td><strong>${formatPLN(uop_results.calkowita_roczna_wartosc)}</strong></td>
                </tr>
            </tbody>
        </table>
        
        <div class="alert alert-info mt-4">
            <h4>Próg rentowności (Break-even)</h4>
            <p>Minimalna miesięczna faktura na B2B, aby zrównać całkowitą roczną wartość z UoP, to około: <strong>${formatPLN(break_even_faktura)}</strong></p>
        </div>

        <div class="row mt-5">
            <div class="col-md-8">
                <canvas id="comparisonChart"></canvas>
            </div>
            <div class="col-md-4">
                <canvas id="b2bDistributionChart"></canvas>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12 text-center">
                <button id="exportPdfBtn" class="btn btn-danger me-2">Eksportuj do PDF</button>
                <button id="exportExcelBtn" class="btn btn-success">Eksportuj do Excel</button>
            </div>
        </div>

        <pre id="json-output" class="bg-light p-3 rounded mt-4"></pre>
    `;

    // --- Grouped Bar Chart: Comparison ---
    const compCtx = document.getElementById('comparisonChart').getContext('2d');
    comparisonChart = new Chart(compCtx, {
        type: 'bar',
        data: {
            labels: ['Roczna wartość całkowita'],
            datasets: [
                {
                    label: 'UoP',
                    data: [uop_results.calkowita_roczna_wartosc],
                    backgroundColor: '#0052cc',
                },
                {
                    label: 'B2B (Standard)',
                    data: [b2b_results.roczne_netto_na_reke],
                    backgroundColor: '#36b37e',
                },
                {
                    label: 'B2B (z benefitami)',
                    data: [b2b_results.calkowita_roczna_wartosc],
                    backgroundColor: '#ff8b00',
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Porównanie całkowitej rocznej wartości' }
            }
        }
    });

    // --- Pie Chart: B2B Distribution ---
    const pieCtx = document.getElementById('b2bDistributionChart').getContext('2d');
    b2bDistributionChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: ['Netto na rękę', 'Podatki', 'ZUS', 'Utracony przychód', 'Koszty firmowe'],
            datasets: [{
                data: [
                    b2b_results.roczne_netto_na_reke,
                    b2b_results.roczny_podatek,
                    b2b_results.roczny_zus,
                    b2b_results.roczny_utracony_przychod,
                    b2b_results.roczne_koszty_firmowe
                ],
                backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#fd7e14', '#6c757d']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Rozkład przychodu B2B' }
            }
        }
    });

    // Add event listeners for export buttons
    document.getElementById('exportPdfBtn').addEventListener('click', async () => {
        try {
            const response = await fetch('/export/pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data) // Send all results data
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'kalkulator_wyniki.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting PDF:', error);
            alert('Wystąpił błąd podczas eksportu do PDF.');
        }
    });

    document.getElementById('exportExcelBtn').addEventListener('click', async () => {
        try {
            const response = await fetch('/export/excel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data) // Send all results data
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'kalkulator_wyniki.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting Excel:', error);
            alert('Wystąpił błąd podczas eksportu do Excela.');
        }
    });

    // Display raw JSON for debugging
    document.getElementById('json-output').textContent = JSON.stringify(data, null, 2);
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const payload = getFormValues();

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        renderResults(data);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = `<div class="alert alert-danger">Wystąpił błąd: ${error.message}</div>`;
    }
}

function initialize() {
    renderCompanyBenefits();
    const form = document.getElementById('calculator-form');
    form.addEventListener('submit', handleFormSubmit);

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}
