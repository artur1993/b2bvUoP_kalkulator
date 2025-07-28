import React, { useState } from 'react';
import CalculatorForm from './components/CalculatorForm';
import ResultsDisplay from './components/ResultsDisplay';
import ComparisonChart from './components/ComparisonChart';
import Header from './components/Header';
import SkeletonLoader from './components/SkeletonLoader';
import Alert from './components/Alert';
import { calculateResults, exportToExcel, exportToPdf } from './services/api';
import { saveAs } from 'file-saver';

function App() {
  const [b2bData, setB2bData] = useState({
    faktura_miesieczna: 10000,
    koszty_firmowe_miesieczne: 500,
    zus_rodzaj: 'mala_firma',
    zus_chorobowe: false,
    forma_opodatkowania: 'ryczalt_IT',
    ulga_dla_mlodych: false,
    urlop_dni: 20,
    chorobowe_dni: 5,
    przestoje_miesiace: 0,
    customBenefits: 0,
    companyBenefits: {
      paidVacationDays: { enabled: false, days: 0 },
      paidSickDays: { enabled: false, days: 0 },
      medicalCare: { enabled: false, value: 0 },
      lifeInsurance: { enabled: false, value: 0 },
      sportCard: { enabled: false, value: 0 },
      trainingBudget: { enabled: false, value: 0 },
      otherBenefits: { enabled: false, value: 0 },
    },
  });

  const [uopData, setUopData] = useState({
    wynagrodzenie_brutto: 8000,
    koszty_uzyskania_przychodu: 250,
    ulga_dla_mlodych: false,
    wybrane_benefity: [],
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleB2bChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name.startsWith('companyBenefits.')) {
      const [benefitType, field] = name.split('.').slice(1);
      setB2bData((prevData) => ({
        ...prevData,
        companyBenefits: {
          ...prevData.companyBenefits,
          [benefitType]: {
            ...prevData.companyBenefits[benefitType],
            [field]: type === 'checkbox' ? checked : value,
          },
        },
      }));
    } else {
      setB2bData((prevData) => ({
        ...prevData,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  const handleUopChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'wybrane_benefity') {
      setUopData((prevData) => ({
        ...prevData,
        wybrane_benefity: checked
          ? [...prevData.wybrane_benefity, value]
          : prevData.wybrane_benefity.filter((benefit) => benefit !== value),
      }));
    } else {
      setUopData((prevData) => ({
        ...prevData,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = { b2b: b2bData, uop: uopData };
      const res = await calculateResults(data);
      setResults(res);
    } catch (err) {
      setError('Failed to fetch results. Please try again.');
      
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = async () => {
    try {
      const data = { b2b_results: results.b2b_results, uop_results: results.uop_results };
      const blob = await exportToPdf(data);
      saveAs(blob, 'kalkulator_wyniki.pdf');
    } catch (err) {

      alert('Failed to export PDF.');
    }
  };

  const handleExportExcel = async () => {
    try {
      const data = { b2b_results: results.b2b_results, uop_results: results.uop_results };
      const blob = await exportToExcel(data);
      saveAs(blob, 'kalkulator_wyniki.xlsx');
    } catch (err) {
      
      alert('Failed to export Excel.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-background">
      <Header />
      <main className="container mx-auto p-4 md:p-8 w-full max-w-7xl">
        <div className="bg-surface p-6 md:p-8 rounded-xl shadow-lg">
          <CalculatorForm
            b2bData={b2bData}
            uopData={uopData}
            handleB2bChange={handleB2bChange}
            handleUopChange={handleUopChange}
            handleCalculate={handleCalculate}
            loading={loading}
          />

          {loading && <SkeletonLoader />}
          {error && <Alert message={error} type="error" />}

          {!loading && results && (
            <div className="mt-8">
              <ResultsDisplay results={results} onExportPdf={handleExportPdf} onExportExcel={handleExportExcel} data-testid="results-display" />
              <ComparisonChart results={results} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
