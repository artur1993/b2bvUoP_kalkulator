import React from 'react';
import { useTranslation } from 'react-i18next';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const ResultsDisplay = ({ results, onExportPdf, onExportAdvancedPdf, onExportExcel, calculationMode, 'data-testid': dataTestId }) => {
  const { t } = useTranslation();

  if (!results) return null;

  const { b2b_results, uop_results } = results;
  const break_even_faktura = results.break_even_faktura;
  const break_even_wynagrodzenie_brutto = results.break_even_wynagrodzenie_brutto;

  let breakEvenText = '';
  let breakEvenSubtitle = '';

  if (calculationMode === 'uop_to_b2b' && break_even_faktura !== -1) {
    breakEvenText = t('results.break_even_b2b_title') + ': ' + formatCurrency(break_even_faktura);
    breakEvenSubtitle = t('results.break_even_b2b_subtitle');
  } else if (calculationMode === 'b2b_to_uop' && break_even_wynagrodzenie_brutto !== -1) {
    breakEvenText = t('results.break_even_uop_title') + ': ' + formatCurrency(break_even_wynagrodzenie_brutto);
    breakEvenSubtitle = t('results.break_even_uop_subtitle');
  }

  return (
    <div id="results-section" className="mt-10 p-6 bg-white rounded-lg shadow-lg" data-testid={dataTestId}>
      <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">{t('results.title')}</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* B2B Results */}
        <div className="bg-surface p-6 rounded-xl shadow-lg border-t-4 border-primary">
          <h3 className="text-2xl font-semibold text-primary mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-1.04-9-2.745M9 6H7a2 2 0 00-2 2v4a2 2 0 002 2h2m7-6h-2a2 2 0 00-2 2v4a2 2 0 002 2h2m0-6a2 2 0 110 4h-2a2 2 0 00-2 2v4a2 2 0 002 2h2a2 2 0 100-4h-2a2 2 0 00-2-2V8a2 2 0 002-2h2a2 2 0 100-4z" />
            </svg>
            <span>{t('form.b2b_title')}</span>
          </h3>
          <ul className="space-y-2 text-gray-700">
            <li><span className="font-medium">{t('results.annual_revenue')}:</span> {formatCurrency(b2b_results.roczny_przychod)}</li>
            <li><span className="font-medium">{t('results.annual_costs')}:</span> {formatCurrency(b2b_results.roczne_koszty_firmowe)}</li>
            <li><span className="font-medium">{t('results.annual_zus')}:</span> {formatCurrency(b2b_results.roczny_zus)}</li>
            <li><span className="font-medium">{t('results.annual_tax')}:</span> {formatCurrency(b2b_results.roczny_podatek)}</li>
            <li><span className="font-medium">{t('results.lost_revenue')}:</span> {formatCurrency(b2b_results.roczny_utracony_przychod)}
              <span className="relative group ml-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 inline-block text-gray-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9.247a.75.75 0 01.968-.024L12 11.625l2.804-2.402a.75.75 0 11.944 1.168L12.5 13.5l3.197 2.74a.75.75 0 11-.944 1.168L12 15.375l-2.804 2.402a.75.75 0 01-1.168-.944L11.5 13.5l-3.197-2.74a.75.75 0 01.024-.968z" />
                </svg>
                <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-2 bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {t('results.lost_revenue_tooltip')}
                </span>
              </span>
            </li>
            <li><span className="font-medium">{t('results.net_income')}:</span> {formatCurrency(b2b_results.roczne_netto_na_reke)}</li>
            <li><span className="font-medium">{t('results.company_benefits_value')}:</span> {formatCurrency(b2b_results.roczna_wartosc_benefitow_od_firmy)}</li>
            <li><span className="font-medium">{t('results.custom_benefits_value')}:</span> {formatCurrency(b2b_results.roczna_wartosc_wlasnych_korzysci)}</li>
            <li className="text-2xl font-bold text-accent mt-4"><span className="font-medium text-gray-800">{t('results.total_b2b_value')}:</span> {formatCurrency(b2b_results.calkowita_roczna_wartosc)}</li>
            <li className="text-lg font-semibold text-accent"><span className="font-medium text-gray-800">{t('results.monthly_net')}:</span> {formatCurrency(b2b_results.miesieczne_netto)}</li>
          </ul>
        </div>

        {/* UoP Results */}
        <div className="bg-surface p-6 rounded-xl shadow-lg border-t-4 border-secondary">
          <h3 className="text-2xl font-semibold text-secondary mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
            <span>{t('form.uop_title')}</span>
          </h3>
          <ul className="space-y-2 text-gray-700">
            <li><span className="font-medium">{t('results.annual_gross')}:</span> {formatCurrency(uop_results.roczne_brutto)}</li>
            <li><span className="font-medium">{t('results.annual_zus')}:</span> {formatCurrency(uop_results.roczny_zus)}</li>
            <li><span className="font-medium">{t('results.annual_tax')}:</span> {formatCurrency(uop_results.roczny_podatek)}</li>
            <li><span className="font-medium">{t('results.net_income')}:</span> {formatCurrency(uop_results.roczne_netto_na_reke)}</li>
            <li><span className="font-medium">{t('results.uop_benefits_value')}:</span> {formatCurrency(uop_results.roczna_wartosc_benefitow)}</li>
            <li><span className="font-medium">{t('results.paid_days_off_value')}:</span> {formatCurrency(uop_results.roczna_wartosc_platnych_dni_wolnych)}</li>
            <li className="text-2xl font-bold text-accent mt-4"><span className="font-medium text-gray-800">{t('results.total_uop_value')}:</span> {formatCurrency(uop_results.calkowita_roczna_wartosc)}</li>
            <li className="text-lg font-semibold text-accent"><span className="font-medium text-gray-800">{t('results.monthly_net')}:</span> {formatCurrency(uop_results.miesieczne_netto)}</li>
          </ul>
        </div>
      </div>

      {breakEvenText && (
        <div className="text-center bg-yellow-50 p-4 rounded-lg shadow-md mb-8">
          <p className="text-xl font-bold text-yellow-800">
            {breakEvenText}
          </p>
          <p className="text-gray-600 text-sm">
            {breakEvenSubtitle}
          </p>
        </div>
      )}

      <div className="flex justify-center space-x-4">
        <button
          onClick={onExportPdf}
          className="bg-transparent hover:bg-secondary/10 text-secondary font-bold py-2 px-6 border border-secondary rounded-lg transition duration-300 ease-in-out transform hover:scale-105"
          data-testid="export-pdf-button"
        >
          {t('results.export_pdf_basic')}
        </button>
        <button
          onClick={onExportAdvancedPdf}
          className="bg-primary hover:bg-blue-800 text-white font-bold py-2 px-6 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 shadow-md"
          data-testid="export-advanced-pdf-button"
        >
          {t('results.export_pdf_advanced')}
        </button>
        <button
          onClick={onExportExcel}
          className="bg-transparent hover:bg-secondary/10 text-secondary font-bold py-2 px-6 border border-secondary rounded-lg transition duration-300 ease-in-out transform hover:scale-105"
          data-testid="export-excel-button"
        >
          {t('results.export_excel')}
        </button>
      </div>
    </div>
  );
};

export default ResultsDisplay;