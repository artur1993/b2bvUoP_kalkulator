function formatPLN(value) {
    return new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(value);
}

function getFormValues() {
    const b2b_benefits = Array.from(document.querySelectorAll('#calculator-form [id^="b2b_benefit_"]:checked')).map(el => el.value);
    const uop_benefits = Array.from(document.querySelectorAll('#calculator-form [id^="uop_benefit_"]:checked')).map(el => el.value);

    return {
        b2b: {
            faktura_miesieczna: parseFloat(document.getElementById('b2b_faktura').value) || 0,
            forma_opodatkowania: document.getElementById('b2b_opodatkowanie').value,
            zus_rodzaj: document.getElementById('b2b_zus').value,
            zus_chorobowe: document.getElementById('b2b_chorobowe').checked,
            vat: true,
            koszty_firmowe_miesieczne: parseFloat(document.getElementById('b2b_koszty').value) || 0,
            wybrane_benefity: b2b_benefits,
            przestoje_miesiace: parseFloat(document.getElementById('b2b_przestoje').value) || 0,
            urlop_dni: parseInt(document.getElementById('b2b_urlop').value) || 0,
            wiek: parseInt(document.getElementById('wiek').value) || 0,
            dzieci: 0,
            ulga_dla_mlodych: document.getElementById('ulga_dla_mlodych').checked
        },
        uop: {
            wynagrodzenie_brutto: parseFloat(document.getElementById('uop_brutto').value) || 0,
            koszty_uzyskania_przychodu: parseFloat(document.getElementById('uop_koszty_przychodu').value) || 0,
            wybrane_benefity: uop_benefits,
            wiek: parseInt(document.getElementById('wiek').value) || 0,
            dzieci: 0,
            ulga_dla_mlodych: document.getElementById('ulga_dla_mlodych').checked
        },
        ogolne: {
            scenariusz: 'realistyczny',
            analiza_zdolnosci_kredytowej: false
        }
    };
}

function renderResults(data) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    resultsDiv.style.display = 'block';

    const { b2b_results, uop_results, break_even_faktura } = data;

    resultsDiv.innerHTML = `
        <h2 class="text-center mb-4">Podsumowanie</h2>
        <div class="row text-center">
            <div class="col-md-6">
                <div class="card h-100 ${b2b_results.roczne_netto > uop_results.calkowita_roczna_wartosc ? 'border-success' : 'border-danger'}">
                    <div class="card-header"><h3>B2B</h3></div>
                    <div class="card-body">
                        <h4 class="card-title">${formatPLN(b2b_results.miesieczne_netto)} / msc</h4>
                        <p class="card-text">Rocznie: <strong>${formatPLN(b2b_results.roczne_netto)}</strong></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100 ${uop_results.calkowita_roczna_wartosc > b2b_results.roczne_netto ? 'border-success' : 'border-danger'}">
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
                    <td>-${formatPLN(b2b_results.roczne_koszty + b2b_results.roczny_zus + b2b_results.roczny_podatek)}</td>
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
                <tr class="table-warning">
                    <td>Koszt benefitów</td>
                    <td>-${formatPLN(b2b_results.roczny_koszt_benefitow)}</td>
                    <td class="text-success">Sponsorowane</td>
                </tr>
                <tr class="table-success">
                    <td><strong>Rocznie na rękę (Netto)</strong></td>
                    <td><strong>${formatPLN(b2b_results.roczne_netto)}</strong></td>
                    <td><strong>${formatPLN(uop_results.roczne_netto)}</strong></td>
                </tr>
                <tr>
                    <td>Wartość benefitów i płatnych dni wolnych</td>
                    <td class="text-danger">Brak</td>
                    <td>+${formatPLN(uop_results.roczna_wartosc_benefitow + uop_results.roczna_wartosc_platnych_dni_wolnych)}</td>
                </tr>
                <tr class="table-info">
                    <td><strong>Całkowita roczna wartość</strong></td>
                    <td><strong>${formatPLN(b2b_results.roczne_netto)}</strong></td>
                    <td><strong>${formatPLN(uop_results.calkowita_roczna_wartosc)}</strong></td>
                </tr>
            </tbody>
        </table>
        
        <div class="alert alert-info mt-4">
            <h4>Próg rentowności (Break-even)</h4>
            <p>Minimalna miesięczna faktura na B2B, aby zrównać całkowitą roczną wartość z UoP, to około: <strong>${formatPLN(break_even_faktura)}</strong></p>
        </div>
    `;
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
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        renderResults(data);
    } catch (error) {
        console.error('Error:', error);
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = `<div class="alert alert-danger">Wystąpił błąd: ${error.message}</div>`;
        }
    }
}

function initialize() {
    const form = document.getElementById('calculator-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
}

// Initialize the form when the DOM is ready
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initialize);
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatPLN,
        getFormValues,
        renderResults,
        handleFormSubmit,
        initialize
    };
}