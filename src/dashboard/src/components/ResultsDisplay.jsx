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

const ResultsDisplay = ({ results, onExportExcel, calculationMode, 'data-testid': dataTestId }) => {
  const { t } = useTranslation();

  if (!results) return null;

  const { b2b_results, uop_results, analysis } = results;
  const break_even_invoice_amount = results.break_even_invoice_amount;
  const break_even_gross_salary = results.break_even_gross_salary;

  let breakEvenText = '';
  let breakEvenSubtitle = '';

  if (calculationMode === 'uop_to_b2b' && break_even_invoice_amount !== -1) {
    breakEvenText = t('results.break_even_b2b_title') + ': ' + formatCurrency(break_even_invoice_amount);
    breakEvenSubtitle = t('results.break_even_b2b_subtitle');
  } else if (calculationMode === 'b2b_to_uop' && break_even_gross_salary !== -1) {
    breakEvenText = t('results.break_even_uop_title') + ': ' + formatCurrency(break_even_gross_salary);
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
            <li><span className="font-medium">{t('results.annual_revenue')}:</span> {formatCurrency(b2b_results.annual_revenue)}</li>
            <li><span className="font-medium">{t('results.annual_costs')}:</span> {formatCurrency(b2b_results.annual_business_costs)}</li>
            <li><span className="font-medium">{t('results.annual_zus')}:</span> {formatCurrency(b2b_results.annual_zus)}</li>
            <li><span className="font-medium">{t('results.annual_tax')}:</span> {formatCurrency(b2b_results.annual_tax)}</li>
            <li><span className="font-medium">{t('results.lost_revenue')}:</span> {formatCurrency(b2b_results.annual_lost_revenue)}
              <span className="relative group ml-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 inline-block text-gray-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9.247a.75.75 0 01.968-.024L12 11.625l2.804-2.402a.75.75 0 11.944 1.168L12.5 13.5l3.197 2.74a.75.75 0 11-.944 1.168L12 15.375l-2.804 2.402a.75.75 0 01-1.168-.944L11.5 13.5l-3.197-2.74a.75.75 0 01.024-.968z" />
                </svg>
                <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-2 bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {t('results.lost_revenue_tooltip')}
                </span>
              </span>
            </li>
            <li><span className="font-medium">{t('results.net_income')}:</span> {formatCurrency(b2b_results.annual_net_income)}</li>
            <li><span className="font-medium">{t('results.company_benefits_value')}:</span> {formatCurrency(b2b_results.annual_company_benefits_value)}</li>
            <li><span className="font-medium">{t('results.custom_benefits_value')}:</span> {formatCurrency(b2b_results.annual_custom_benefits_value)}</li>
            <li className="text-2xl font-bold text-accent mt-4"><span className="font-medium text-gray-800">{t('results.total_b2b_value')}:</span> {formatCurrency(b2b_results.total_annual_value)}</li>
            <li className="text-lg font-semibold text-accent"><span className="font-medium text-gray-800">{t('results.monthly_net')}:</span> {formatCurrency(b2b_results.monthly_net_income)}</li>
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
            <li><span className="font-medium">{t('results.annual_gross')}:</span> {formatCurrency(uop_results.annual_gross_salary)}</li>
            <li><span className="font-medium">{t('results.annual_zus')}:</span> {formatCurrency(uop_results.annual_zus)}</li>
            <li><span className="font-medium">{t('results.annual_tax')}:</span> {formatCurrency(uop_results.annual_tax)}</li>
            <li><span className="font-medium">{t('results.net_income')}:</span> {formatCurrency(uop_results.annual_net_income)}</li>
            <li><span className="font-medium">{t('results.uop_benefits_value')}:</span> {formatCurrency(uop_results.annual_benefits_value)}</li>
            <li><span className="font-medium">{t('results.paid_days_off_value')}:</span> {formatCurrency(uop_results.annual_paid_days_off_value)}</li>
            <li className="text-2xl font-bold text-accent mt-4"><span className="font-medium text-gray-800">{t('results.total_uop_value')}:</span> {formatCurrency(uop_results.total_annual_value)}</li>
            <li className="text-lg font-semibold text-accent"><span className="font-medium text-gray-800">{t('results.monthly_net')}:</span> {formatCurrency(uop_results.monthly_net_income)}</li>
          </ul>
        </div>
      </div>

      {breakEvenText && (
        <div data-testid="break-even-section" className="text-center bg-yellow-50 p-4 rounded-lg shadow-md mb-8 border border-yellow-200">
          <p className="text-xl font-bold text-yellow-800">
            {breakEvenText}
          </p>
          <p className="text-gray-600 text-sm">
            {breakEvenSubtitle}
          </p>
        </div>
      )}

      {/* Advanced Analysis Sections */}
      {analysis && (
        <div className="space-y-8 mt-10">
          {/* Executive Summary */}
          {analysis.summary && (
            <section className="bg-blue-50 p-6 rounded-xl border-l-8 border-blue-500 shadow-sm">
              <h3 className="text-2xl font-bold text-blue-900 mb-3 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {t('analysis.summary_title', 'Podsumowanie biznesowe')}
              </h3>
              <p className="text-lg text-blue-800 leading-relaxed italic">
                "{analysis.summary.recommendation}"
              </p>
            </section>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Risk Analysis */}
            {analysis.risk && (
              <section className="bg-orange-50 p-6 rounded-xl border border-orange-100 shadow-sm">
                <h3 className="text-xl font-bold text-orange-900 mb-4 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  {t('analysis.risk_title', 'Analiza Ryzyka')}
                </h3>
                <div className="space-y-4">
                  {Object.entries(analysis.risk).map(([key, value]) => (
                    <div key={key} className="flex items-start">
                      <span className="text-orange-500 mr-2 mt-1">•</span>
                      <p className="text-gray-700 text-sm">{value}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* B2B Checklist */}
            {analysis.checklist && (
              <section className="bg-green-50 p-6 rounded-xl border border-green-100 shadow-sm">
                <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  {analysis.checklist.title || t('analysis.checklist_title', 'Checklista B2B')}
                </h3>
                <ul className="space-y-2">
                  {analysis.checklist.items && analysis.checklist.items.map((item, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-700">
                      <svg className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>

          {/* Methodology */}
          {analysis.methodology && (
            <section className="bg-gray-50 p-6 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {t('analysis.methodology_title', 'Metodologia obliczeń')}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {analysis.methodology}
              </p>
            </section>
          )}
        </div>
      )}

      {results.pension_details && (
        <div className="mt-10 p-6 bg-blue-50 rounded-lg shadow-lg border-t-4 border-blue-300">
          <h3 className="text-2xl font-semibold text-blue-800 mb-4">{t('pension.analysis_title')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-bold text-lg text-gray-700">{t('pension.comparison_title')}</h4>
              <p><strong>{t('pension.uop_pension')}:</strong> {formatCurrency(results.pension_details.uop_pension_monthly)}/mies.</p>
              <p><strong>{t('pension.b2b_pension')}:</strong> {formatCurrency(results.pension_details.b2b_pension_monthly)}/mies.</p>
              <p className="font-bold text-red-600"><strong>{t('pension.gap_to_cover')}:</strong> {formatCurrency(results.pension_details.pension_gap_monthly)}/mies.</p>
            </div>
            <div>
              <h4 className="font-bold text-lg text-gray-700">{t('pension.savings_title')}</h4>
              <p><strong>{t('pension.required_monthly_savings')}:</strong> {formatCurrency(results.pension_details.required_monthly_savings)}</p>
              <p className="text-green-700 font-semibold"><strong>{t('pension.invoice_increase')}:</strong> {formatCurrency(results.pension_details.invoice_increase)}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center mt-8">
        <button
          onClick={onExportExcel}
          className="bg-transparent hover:bg-secondary/10 text-secondary font-bold py-2 px-8 border-2 border-secondary rounded-lg transition duration-300 ease-in-out transform hover:scale-105 shadow-sm"
          data-testid="export-excel-button"
        >
          {t('results.export_excel')}
        </button>
      </div>
    </div>
  );
};

export default ResultsDisplay;