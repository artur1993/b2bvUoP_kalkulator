import React from 'react';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const ResultsDisplay = ({ results, onExportPdf, onExportExcel }) => {
  if (!results) return null;

  const { b2b_results, uop_results, break_even_faktura } = results;

  return (
    <div className="mt-10 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Calculation Results</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* B2B Results */}
        <div className="bg-blue-50 p-6 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold text-blue-800 mb-4">B2B Contract</h3>
          <ul className="space-y-2 text-gray-700">
            <li><span className="font-medium">Annual Revenue:</span> {formatCurrency(b2b_results.roczny_przychod)}</li>
            <li><span className="font-medium">Annual Business Costs:</span> {formatCurrency(b2b_results.roczne_koszty_firmowe)}</li>
            <li><span className="font-medium">Annual ZUS:</span> {formatCurrency(b2b_results.roczny_zus)}</li>
            <li><span className="font-medium">Annual Tax:</span> {formatCurrency(b2b_results.roczny_podatek)}</li>
            <li><span className="font-medium">Annual Lost Revenue:</span> {formatCurrency(b2b_results.roczny_utracony_przychod)}</li>
            <li><span className="font-medium">Annual Net Income (Hand):</span> {formatCurrency(b2b_results.roczne_netto_na_reke)}</li>
            <li><span className="font-medium">Annual Company Benefits Value:</span> {formatCurrency(b2b_results.roczna_wartosc_benefitow_od_firmy)}</li>
            <li><span className="font-medium">Annual Custom Benefits Value:</span> {formatCurrency(b2b_results.roczna_wartosc_wlasnych_korzysci)}</li>
            <li className="text-xl font-bold text-blue-900"><span className="font-medium">Total Annual B2B Value:</span> {formatCurrency(b2b_results.calkowita_roczna_wartosc)}</li>
            <li className="text-lg font-semibold text-blue-700"><span className="font-medium">Monthly Net (Total Value):</span> {formatCurrency(b2b_results.miesieczne_netto)}</li>
          </ul>
        </div>

        {/* UoP Results */}
        <div className="bg-green-50 p-6 rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold text-green-800 mb-4">Employment Contract (UoP)</h3>
          <ul className="space-y-2 text-gray-700">
            <li><span className="font-medium">Annual Gross Salary:</span> {formatCurrency(uop_results.roczne_brutto)}</li>
            <li><span className="font-medium">Annual ZUS:</span> {formatCurrency(uop_results.roczny_zus)}</li>
            <li><span className="font-medium">Annual Tax:</span> {formatCurrency(uop_results.roczny_podatek)}</li>
            <li><span className="font-medium">Annual Net Income (Hand):</span> {formatCurrency(uop_results.roczne_netto_na_reke)}</li>
            <li><span className="font-medium">Annual Benefits Value:</span> {formatCurrency(uop_results.roczna_wartosc_benefitow)}</li>
            <li><span className="font-medium">Annual Paid Days Off Value:</span> {formatCurrency(uop_results.roczna_wartosc_platnych_dni_wolnych)}</li>
            <li className="text-xl font-bold text-green-900"><span className="font-medium">Total Annual UoP Value:</span> {formatCurrency(uop_results.calkowita_roczna_wartosc)}</li>
            <li className="text-lg font-semibold text-green-700"><span className="font-medium">Monthly Net (Total Value):</span> {formatCurrency(uop_results.miesieczne_netto)}</li>
          </ul>
        </div>
      </div>

      {break_even_faktura !== -1 && (
        <div className="text-center bg-yellow-50 p-4 rounded-lg shadow-md mb-8">
          <p className="text-xl font-bold text-yellow-800">
            Break-Even Monthly B2B Invoice: {formatCurrency(break_even_faktura)}
          </p>
          <p className="text-gray-600 text-sm">
            (This is the monthly B2B invoice amount needed to match the total annual value of the UoP contract)
          </p>
        </div>
      )}

      <div className="flex justify-center space-x-4">
        <button
          onClick={onExportPdf}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105"
        >
          Export to PDF
        </button>
        <button
          onClick={onExportExcel}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105"
        >
          Export to Excel
        </button>
      </div>
    </div>
  );
};

export default ResultsDisplay;