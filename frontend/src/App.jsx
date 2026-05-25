import React, { useReducer, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import CalculatorForm from './components/CalculatorForm';
import ResultsDisplay from './components/ResultsDisplay';
import ComparisonChart from './components/ComparisonChart';
import WaterfallChart from './components/WaterfallChart';
import BreakEvenChart from './components/BreakEvenChart';
import Header from './components/Header';
import SkeletonLoader from './components/SkeletonLoader';
import Alert from './components/Alert';
import { calculateResults, exportToExcel } from './services/api';
import { saveAs } from 'file-saver';
import { calculatorReducer, initialState } from './state/calculatorReducer';

function App() {
  const { i18n } = useTranslation();
  const [state, dispatch] = useReducer(calculatorReducer, initialState);
  const { b2bData, uopData, calculationMode, results, loading, error } = state;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const payload = {};
    if (params.has('mode')) payload.calculationMode = params.get('mode');
    if (params.has('b2b_invoice')) {
      payload.b2bData = {
        monthly_invoice_amount: parseFloat(params.get('b2b_invoice')) || initialState.b2bData.monthly_invoice_amount,
        tax_form: params.get('b2b_tax') || initialState.b2bData.tax_form,
        zus_type: params.get('b2b_zus') || initialState.b2bData.zus_type,
      };
    }
    if (params.has('uop_salary')) {
      payload.uopData = {
        monthly_gross_salary: parseFloat(params.get('uop_salary')) || initialState.uopData.monthly_gross_salary,
      };
    }
    if (Object.keys(payload).length > 0) {
      dispatch({ type: 'HYDRATE_FROM_URL', payload });
    }
  }, []);

  const handleCalculate = async () => {
    dispatch({ type: 'CALCULATE_START' });
    try {
      const data = { b2b: b2bData, uop: uopData, calculation_mode: calculationMode, language: i18n.language };
      const params = new URLSearchParams();
      params.set('mode', calculationMode);
      params.set('b2b_invoice', b2bData.monthly_invoice_amount);
      params.set('b2b_tax', b2bData.tax_form);
      params.set('b2b_zus', b2bData.zus_type);
      params.set('uop_salary', uopData.monthly_gross_salary);
      window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
      const res = await calculateResults(data);
      dispatch({ type: 'CALCULATE_SUCCESS', payload: res });
    } catch {
      dispatch({ type: 'CALCULATE_FAILURE', payload: 'Failed to fetch results. Please check the console for more details.' });
    }
  };

  const handleExportExcel = async () => {
    try {
      const data = { b2b_results: results.b2b_results, uop_results: results.uop_results };
      const blob = await exportToExcel(data);
      saveAs(blob, 'kalkulator_wyniki.xlsx');
    } catch {
      alert('Failed to export Excel. See console for details.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <Header />
      <main className="container mx-auto p-4 md:p-8 w-full max-w-7xl">
        <div className="bg-white dark:bg-gray-800 p-6 md:p-8 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 print:shadow-none print:border-none">
          <div className="print:hidden">
            <CalculatorForm
              state={state}
              dispatch={dispatch}
              handleCalculate={handleCalculate}
            />
          </div>
          {loading && <div className="print:hidden"><SkeletonLoader /></div>}
          {error && <div className="print:hidden"><Alert message={error} type="error" /></div>}
          {!loading && results && (
            <div className="mt-8">
              <ResultsDisplay results={results} onExportExcel={handleExportExcel} calculationMode={calculationMode} data-testid="results-display" />
              <div className="print:hidden space-y-8">
                <ComparisonChart results={results} />
                <WaterfallChart results={results} />
                <BreakEvenChart b2b={b2bData} uop={uopData} results={results} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
