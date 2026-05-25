import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatLimit = (value) => {
  return new Intl.NumberFormat('pl-PL', {
    maximumFractionDigits: 0,
  }).format(value);
};

const ResultsDisplay = ({ results, onExportExcel, calculationMode, 'data-testid': dataTestId }) => {
  const { t } = useTranslation();

  if (!results) return null;

  const { b2b_results, uop_results, analysis, pension_limits_2026 } = results;
  const hasSolidarityTax = (b2b_results.annual_solidarity_tax || 0) > 0 || (uop_results.annual_solidarity_tax || 0) > 0;
  const break_even_invoice_amount = results.break_even_invoice_amount;
  const break_even_gross_salary = results.break_even_gross_salary;

  let breakEvenText = '';
  if (calculationMode === 'uop_to_b2b' && break_even_invoice_amount !== -1) {
    breakEvenText = t('results.break_even_b2b_title') + ': ' + formatCurrency(break_even_invoice_amount);
  } else if (calculationMode === 'b2b_to_uop' && break_even_gross_salary !== -1) {
    breakEvenText = t('results.break_even_uop_title') + ': ' + formatCurrency(break_even_gross_salary);
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      id="results-section" 
      className="mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-100 dark:border-gray-700 print:shadow-none print:border-none print:p-0 print:m-0" 
      data-testid={dataTestId}
    >
      <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-6 text-center print:text-2xl print:mb-4">
        {t('results.title')}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 print:gap-4">
        {/* B2B Results */}
        <div className="bg-gray-50 dark:bg-gray-700/50 p-6 rounded-xl border-t-4 border-primary print:bg-white print:border-gray-300">
          <h3 className="text-2xl font-semibold text-primary dark:text-blue-400 mb-4 flex items-center">
            <span>{t('form.b2b_title')}</span>
          </h3>
          <ul className="space-y-2 text-gray-700 dark:text-gray-200 print:text-black">
            <li className="flex justify-between"><span>{t('results.annual_revenue')}:</span> <span className="font-medium">{formatCurrency(b2b_results.annual_revenue)}</span></li>
            <li className="flex justify-between"><span>{t('results.annual_zus')}:</span> <span className="font-medium">{formatCurrency(b2b_results.annual_zus)}</span></li>
            <li className="flex justify-between"><span>{t('results.annual_tax')}:</span> <span className="font-medium">{formatCurrency(b2b_results.annual_tax)}</span></li>
            {(b2b_results.annual_solidarity_tax || 0) > 0 && (
              <li className="flex justify-between"><span>{t('results.solidarity_tax')}:</span> <span className="font-medium">{formatCurrency(b2b_results.annual_solidarity_tax)}</span></li>
            )}
            <li className="text-2xl font-bold text-green-600 dark:text-accent-dark mt-4 border-t pt-4 flex justify-between">
              <span>{t('results.total_b2b_value')}:</span> <span>{formatCurrency(b2b_results.total_annual_value)}</span>
            </li>
          </ul>
        </div>

        {/* UoP Results */}
        <div className="bg-gray-50 dark:bg-gray-700/50 p-6 rounded-xl border-t-4 border-gray-400 print:bg-white print:border-gray-300">
          <h3 className="text-2xl font-semibold text-gray-600 dark:text-gray-300 mb-4 flex items-center">
            <span>{t('form.uop_title')}</span>
          </h3>
          <ul className="space-y-2 text-gray-700 dark:text-gray-200 print:text-black">
            <li className="flex justify-between"><span>{t('results.annual_gross')}:</span> <span className="font-medium">{formatCurrency(uop_results.annual_gross_salary)}</span></li>
            <li className="flex justify-between"><span>{t('results.annual_zus')}:</span> <span className="font-medium">{formatCurrency(uop_results.annual_zus)}</span></li>
            <li className="flex justify-between"><span>{t('results.annual_tax')}:</span> <span className="font-medium">{formatCurrency(uop_results.annual_tax)}</span></li>
            {(uop_results.annual_solidarity_tax || 0) > 0 && (
              <li className="flex justify-between"><span>{t('results.solidarity_tax')}:</span> <span className="font-medium">{formatCurrency(uop_results.annual_solidarity_tax)}</span></li>
            )}
            <li className="text-2xl font-bold text-gray-800 dark:text-white mt-4 border-t pt-4 flex justify-between">
              <span>{t('results.total_uop_value')}:</span> <span>{formatCurrency(uop_results.total_annual_value)}</span>
            </li>
          </ul>
        </div>
      </div>

      {hasSolidarityTax && (
        <section
          data-testid="solidarity-tax-disclaimer"
          className="bg-sky-50 dark:bg-sky-900/20 p-4 rounded-lg border border-sky-200 dark:border-sky-800 mb-8 print:bg-white print:text-black"
        >
          <p className="text-sm text-sky-900 dark:text-sky-200">
            {t('results.solidarity_tax_disclaimer')}
          </p>
        </section>
      )}

      {pension_limits_2026 && (
        <section
          data-testid="pension-info-box"
          className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800 mb-8 print:bg-white print:text-black"
        >
          <h3 className="text-lg font-bold text-blue-900 dark:text-blue-300 mb-2">
            {t('results.pension_info_title')}
          </h3>
          <p className="text-sm text-blue-800 dark:text-blue-200">
            {t('results.pension_info_prefix')}{' '}
            <a
              href="https://www.knf.gov.pl"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold underline"
            >
              {t('results.pension_info_ike')}
            </a>{' '}
            {t('results.pension_info_or')}{' '}
            <a
              href="https://www.gov.pl/web/rodzina/ikze-limit-wplat"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold underline"
            >
              {t('results.pension_info_ikze')}
            </a>
            .{' '}
            {t('results.pension_info_limits', {
              ike: formatLimit(pension_limits_2026.ike),
              ikzeStandard: formatLimit(pension_limits_2026.ikze_standard),
              ikzeB2b: formatLimit(pension_limits_2026.ikze_b2b),
            })}
          </p>
        </section>
      )}

      {breakEvenText && (
        <div data-testid="break-even-section" className="text-center bg-yellow-50 dark:bg-yellow-900/30 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800 mb-8 print:bg-white print:text-black">
          <p className="text-xl font-bold text-yellow-800 dark:text-yellow-200">{breakEvenText}</p>
        </div>
      )}

      {/* Advanced Analysis */}
      {analysis && (
        <div className="space-y-6 mt-8 border-t pt-8 dark:border-gray-700">
          <section className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-xl border-l-8 border-blue-500 print:bg-white print:text-black">
            <h3 className="text-xl font-bold text-blue-900 dark:text-blue-300 mb-2">{t('analysis.summary_title')}</h3>
            <p className="italic text-blue-800 dark:text-blue-200">&quot;{analysis.summary.recommendation}&quot;</p>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <section className="bg-orange-50 dark:bg-orange-900/20 p-6 rounded-xl border border-orange-100 dark:border-orange-800 print:bg-white print:text-black">
              <h3 className="text-lg font-bold text-orange-900 dark:text-orange-300 mb-4">{t('analysis.risk_title')}</h3>
              <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                {analysis.risk && Object.entries(analysis.risk).map(([key, value]) => (
                  <li key={key} className="flex items-start"><span className="mr-2">•</span>{value}</li>
                ))}
              </ul>
            </section>

            <section className="bg-green-50 dark:bg-green-900/20 p-6 rounded-xl border border-green-100 dark:border-green-800 print:bg-white print:text-black">
              <h3 className="text-lg font-bold text-green-900 dark:text-green-300 mb-4">{analysis.checklist?.title}</h3>
              <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                {analysis.checklist?.items?.map((item, i) => (
                  <li key={i} className="flex items-center"><span className="text-green-600 mr-2">✓</span>{item}</li>
                ))}
              </ul>
            </section>
          </div>
        </div>
      )}

      <div className="flex justify-center mt-10 print:hidden">
        <button
          onClick={onExportExcel}
          data-testid="export-excel-button"
          className="bg-primary hover:bg-blue-700 text-white font-bold py-3 px-10 rounded-xl transition-all shadow-lg active:scale-95"
        >
          {t('results.export_excel')}
        </button>
      </div>
    </motion.div>
  );
};

export default ResultsDisplay;
