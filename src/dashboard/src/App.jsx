import React, { useState, useEffect, useRef } from 'react';
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
import { calculateResults, exportToExcel } from './services/api';
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
  const [calculationMode, setCalculationMode] = useState('uop_to_b2b');
  const [age, setAge] = useState(30);

  const [b2bData, setB2bData] = useState({
    monthly_invoice_amount: 10000,
    monthly_business_costs: 500,
    zus_type: 'preferential',
    sickness_insurance: false,
    tax_form: 'lump_sum_it',
    youth_relief: false,
    vacation_days: 20,
    sick_days: 5,
    stoppage_months: 0,
    age: 30,
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

  const [baseBusinessCosts, setBaseBusinessCosts] = useState(500);

  const [insuranceConfig, setInsuranceConfig] = useState({
    enabled: true,
    activeProfile: 'standard',
    selections: insuranceProfiles.standard
  });

  const [uopData, setUopData] = useState({
    monthly_gross_salary: 8000,
    deductible_cost_settings: { type: 'standard', creative_work_percentage: 70 },
    youth_relief: false,
    selected_benefits: [],
    age: 30,
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const comparisonChartRef = useRef(null);
  const b2bStackedBarRef = useRef(null);
  const uopStackedBarRef = useRef(null);
  const waterfallChartRef = useRef(null);
  const breakEvenChartRef = useRef(null);
  const sensitivityChartRef = useRef(null);

  const handleB2bChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name === 'monthly_business_costs') {
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

    if (name === 'selected_benefits') {
      setUopData((prevData) => ({
        ...prevData,
        selected_benefits: checked
          ? [...prevData.selected_benefits, value]
          : prevData.selected_benefits.filter((benefit) => benefit !== value),
      }));
    } else if (name.startsWith('deductible_cost_settings.')) {
      const field = name.split('.')[1];
      setUopData((prevData) => ({
        ...prevData,
        deductible_cost_settings: {
          ...prevData.deductible_cost_settings,
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

  const handleAgeChange = (e) => {
    const newAge = parseInt(e.target.value, 10);
    setAge(newAge);
    const isYouthReliefApplicable = newAge < 26;
    setB2bData(prev => ({ ...prev, age: newAge, youth_relief: isYouthReliefApplicable }));
    setUopData(prev => ({ ...prev, age: newAge, youth_relief: isYouthReliefApplicable }));
  };

  useEffect(() => {
    let totalInsuranceCost = 0;
    if (insuranceConfig.enabled) {
      totalInsuranceCost = calculateTotalInsuranceCost(insuranceConfig.selections, b2bData.monthly_invoice_amount);
    }
    
    setB2bData(prevData => ({
      ...prevData,
      monthly_business_costs: Number(baseBusinessCosts) + totalInsuranceCost
    }));
  }, [insuranceConfig, baseBusinessCosts, b2bData.monthly_invoice_amount]);

  const handleCalculationModeChange = (e) => {
    setCalculationMode(e.target.value);
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = { 
        b2b: b2bData, 
        uop: uopData, 
        calculation_mode: calculationMode,
        language: i18n.language 
      };
      const res = await calculateResults(data);
      if (res.pension_details) {
        setB2bData(prevData => ({
          ...prevData,
          monthly_invoice_amount: prevData.monthly_invoice_amount + res.pension_details.invoice_increase
        }));
      }
      setResults(res);
      console.log("API Results for charting:", res);
    } catch (err) {
      setError('Failed to fetch results. Please check the console for more details.');
      console.error('Calculation error:', err);
      
    } finally {
      setLoading(false);
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
            handleAgeChange={handleAgeChange}
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
                onExportExcel={handleExportExcel} 
                calculationMode={calculationMode} 
                data-testid="results-display" 
              />
              <ComparisonChart 
                results={results} 
                comparisonChartRef={comparisonChartRef}
                b2bStackedBarRef={b2bStackedBarRef}
                uopStackedBarRef={uopStackedBarRef}
              />
              <WaterfallChart results={results} ref={waterfallChartRef} />
              <BreakEvenChart b2b={b2bData} uop={uopData} results={results} ref={breakEvenChartRef} />
              <SensitivityChart b2b={b2bData} uop={uopData} results={results} ref={sensitivityChartRef} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
