import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import CalculatorForm from './components/CalculatorForm';
import ResultsDisplay from './components/ResultsDisplay';
import ComparisonChart from './components/ComparisonChart';
import WaterfallChart from './components/WaterfallChart';
import BreakEvenChart from './components/BreakEvenChart';
import SensitivityChart from './components/SensitivityChart';
import Header from './components/Header';
import SkeletonLoader from './components/SkeletonLoader';
import Alert from './components/Alert';
import { calculateResults, exportToExcel, exportToPdf, exportToAdvancedPdf } from './services/api';
import { saveAs } from 'file-saver';
import { insuranceProfiles, insuranceModules } from './data/insuranceOptions';

const calculateTotalInsuranceCost = (selections, b2bMonthlyInvoice) => {
  let totalCost = 0;
  for (const moduleId in selections) {
    const config = selections[moduleId];
    const module = insuranceModules[moduleId];
    if (config.enabled && module) {
      const option = module.options[config.level];
      let cost = 0;
      if (module.type === 'dynamic') {
        const annualIncome = b2bMonthlyInvoice * 12;
        cost = (annualIncome * option.multiplier) / 12;
      } else {
        cost = option.cost;
      }
      totalCost += cost;
    }
  }
  return totalCost;
};

function App() {
  const { i18n } = useTranslation();
  const [calculationMode, setCalculationMode] = useState('uop_to_b2b'); // 'uop_to_b2b' or 'b2b_to_uop'
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
  const [baseBusinessCosts, setBaseBusinessCosts] = useState(500); // User-inputted cost
  const [insuranceConfig, setInsuranceConfig] = useState({
    enabled: true, // Configurator is enabled by default
    activeProfile: 'standard',
    selections: insuranceProfiles.standard
  });

  const [uopData, setUopData] = useState({
    wynagrodzenie_brutto: 8000,
    kup_settings: { type: 'standard', creative_work_percentage: 70 },
    ulga_dla_mlodych: false,
    wybrane_benefity: [],
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleB2bChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'koszty_firmowe_miesieczne') {
      setBaseBusinessCosts(value);
    } else if (name.startsWith('companyBenefits.')) {
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
    } else if (name.startsWith('kup_settings.')) {
      const field = name.split('.')[1];
      setUopData((prevData) => ({
        ...prevData,
        kup_settings: {
          ...prevData.kup_settings,
          [field]: value,
        },
      }));
    } else {
      setUopData((prevData) => ({
        ...prevData,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  useEffect(() => {
    let totalInsuranceCost = 0;
    if (insuranceConfig.enabled) {
      totalInsuranceCost = calculateTotalInsuranceCost(insuranceConfig.selections, b2bData.faktura_miesieczna);
    }
    
    setB2bData(prevData => ({
      ...prevData,
      koszty_firmowe_miesieczne: Number(baseBusinessCosts) + totalInsuranceCost
    }));
  }, [insuranceConfig, baseBusinessCosts, b2bData.faktura_miesieczna]);

  const handleCalculationModeChange = (e) => {
    setCalculationMode(e.target.value);
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = { b2b: b2bData, uop: uopData, calculation_mode: calculationMode };
      const res = await calculateResults(data);
      if (res.pension_details) {
        setB2bData(prevData => ({
          ...prevData,
          faktura_miesieczna: prevData.faktura_miesieczna + res.pension_details.invoice_increase
        }));
      }
      setResults(res);
    } catch (err) {
      setError('Failed to fetch results. Please check the console for more details.');
      console.error('Calculation error:', err);
      
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = async () => {
    if (!results) return;
    try {
      const data = {
        b2b_results: results.b2b_results,
        uop_results: results.uop_results,
        input_data: {
          b2b: b2bData,
          uop: uopData,
        },
        language: i18n.language, // <-- DODANO
      };
      const blob = await exportToPdf(data);
      saveAs(blob, 'Raport_B2B_vs_UoP.pdf');
    } catch (err) {
      console.error('Error exporting PDF:', err);
      alert('Failed to export PDF. See console for details.');
    }
  };

  const handleExportExcel = async () => {
    try {
      const data = { b2b_results: results.b2b_results, uop_results: results.uop_results };
      const blob = await exportToExcel(data);
      saveAs(blob, 'kalkulator_wyniki.xlsx');
    } catch (err) {
      
      console.error('Error exporting Excel:', err);
      alert('Failed to export Excel. See console for details.');
    }
  };

  const handleExportAdvancedPdf = async () => {
    if (!results) return;

    // Prepare detailed insurance data for the report
    const insuranceDetailsForReport = {
      ...insuranceConfig,
      totalMonthlyCost: calculateTotalInsuranceCost(insuranceConfig.selections, b2bData.faktura_miesieczna),
      breakdown: Object.entries(insuranceConfig.selections)
        .filter(([, config]) => config.enabled)
        .map(([moduleId, config]) => {
          const module = insuranceModules[moduleId];
          const option = module.options[config.level];
          const cost = module.type === 'dynamic' 
            ? (b2bData.faktura_miesieczna * 12 * option.multiplier) / 12 
            : option.cost;
          
          return {
            name: module.name,
            level: config.level,
            cost: cost,
            details: option.details || '',
            uop_comparison: option.uop_comparison || ''
          };
        })
    };

    try {
      const data = {
        b2b_results: results.b2b_results,
        uop_results: results.uop_results,
        input_data: { b2b: b2bData, uop: uopData },
        language: i18n.language,
        break_even_faktura: results.break_even_faktura,
        insurance_details: insuranceDetailsForReport, // <-- NEW OBJECT
      };
      const blob = await exportToAdvancedPdf(data);
      saveAs(blob, 'Raport_Zaawansowany_B2B_vs_UoP.pdf');
    } catch (err) {
      console.error('Error exporting advanced PDF:', err);
      alert('Failed to export advanced PDF. See console for details.');
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
            calculationMode={calculationMode}
            handleCalculationModeChange={handleCalculationModeChange}
            insuranceConfig={insuranceConfig}
            setInsuranceConfig={setInsuranceConfig}
          />

          {loading && <SkeletonLoader />}
          {error && <Alert message={error} type="error" />}

          {!loading && results && (
            <div className="mt-8">
              <ResultsDisplay 
                results={results} 
                onExportPdf={handleExportPdf} 
                onExportAdvancedPdf={handleExportAdvancedPdf} 
                onExportExcel={handleExportExcel} 
                calculationMode={calculationMode} 
                data-testid="results-display" 
              />
              <ComparisonChart results={results} />
              <WaterfallChart results={results} />
              <BreakEvenChart b2b={b2bData} uop={uopData} />
              <SensitivityChart b2b={b2bData} uop={uopData} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
