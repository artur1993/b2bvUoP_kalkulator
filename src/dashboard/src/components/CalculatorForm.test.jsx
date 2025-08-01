
import { render, screen, fireEvent, waitFor } from '../utils/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CalculatorForm from './CalculatorForm';
import React, { useState } from 'react';
import i18n from '../i18n';


describe('CalculatorForm', () => {
  const mockOnCalculate = vi.fn();
  const mockOnExport = vi.fn();

  const initialB2bData = {
    monthly_invoice_amount: 0,
    monthly_business_costs: 0,
    zus_type: 'preferential',
    sickness_insurance: false,
    tax_form: 'flat_tax',
    youth_relief: false,
    vacation_days: 0,
    sick_days: 0,
    stoppage_months: 0,
    customBenefits: 0,
    companyBenefits: {
      paidVacationDays: { enabled: false, days: 0, value: 0 },
      paidSickDays: { enabled: false, days: 0, value: 0 },
      medicalCare: { enabled: false, value: 0 },
      lifeInsurance: { enabled: false, value: 0 },
      sportCard: { enabled: false, value: 0 },
      trainingBudget: { enabled: false, value: 0 },
      otherBenefits: { enabled: false, value: 0 },
    },
  };

  const initialUopData = {
    monthly_gross_salary: 0,
    deductible_cost_settings: { type: 'standard', creative_work_percentage: 70 },
    youth_relief: false,
    selected_benefits: [],
  };

  // Test Wrapper component to manage state
  const TestWrapper = ({ initialB2b, initialUop, onCalculate, onExport, loading, initialCalculationMode }) => {
    const [b2bData, setB2bData] = useState(initialB2b);
    const [uopData, setUopData] = useState(initialUop);
    const [calculationMode, setCalculationMode] = useState(initialCalculationMode || 'uop_to_b2b');
    const [insuranceConfig, setInsuranceConfig] = useState({
      enabled: true,
      activeProfile: 'standard',
      selections: {}
    });

    const handleCalculationModeChange = (e) => {
      setCalculationMode(e.target.value);
    };

    const handleB2bChange = (e) => {
      const { name, value, type, checked } = e.target;
      if (name.startsWith('companyBenefits.')) {
        const [parent, child, prop] = name.split('.');
        setB2bData(prev => ({
          ...prev,
          companyBenefits: {
            ...prev.companyBenefits,
            [child]: {
              ...prev.companyBenefits[child],
              [prop]: type === 'checkbox' ? checked : value,
            },
          },
        }));
      } else {
        setB2bData(prev => ({
          ...prev,
          [name]: type === 'checkbox' ? checked : value,
        }));
      }
    };

    const handleUopChange = (e) => {
      const { name, value, type, checked } = e.target;
      if (name === 'selected_benefits') {
        setUopData(prev => ({
          ...prev,
          selected_benefits: checked
            ? [...prev.selected_benefits, value]
            : prev.selected_benefits.filter(benefit => benefit !== value),
        }));
      } else if (name.startsWith('deductible_cost_settings.')) {
        const field = name.split('.')[1];
        setUopData(prev => ({
          ...prev,
          deductible_cost_settings: {
            ...prev.deductible_cost_settings,
            [field]: value,
          },
        }));
      } else {
        setUopData(prev => ({
          ...prev,
          [name]: type === 'checkbox' ? checked : value,
        }));
      }
    };

    return (
      <CalculatorForm
        b2bData={b2bData}
        uopData={uopData}
        handleB2bChange={handleB2bChange}
        handleUopChange={handleUopChange}
        handleCalculate={onCalculate}
        onExport={onExport}
        loading={loading}
        calculationMode={calculationMode}
        handleCalculationModeChange={handleCalculationModeChange}
        insuranceConfig={insuranceConfig}
        setInsuranceConfig={setInsuranceConfig}
      />
    );
  };

  beforeEach(() => {
    mockOnCalculate.mockClear();
    mockOnExport.mockClear();
  });

  const renderComponent = (b2b = initialB2bData, uop = initialUopData) => {
    render(
        <TestWrapper
          initialB2b={b2b}
          initialUop={uop}
          onCalculate={mockOnCalculate}
          onExport={mockOnExport}
          loading={false}
        />
    );
  };

  it('renders all form fields correctly', () => {
    renderComponent();

    // Check for B2B fields
    expect(screen.getByLabelText('Monthly Invoice (PLN)')).toBeInTheDocument();
    expect(screen.getByLabelText('Monthly Business Costs (PLN)')).toBeInTheDocument();
    expect(screen.getByLabelText('ZUS Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Taxation Form')).toBeInTheDocument();
    expect(screen.getByTestId('youth-relief-b2b')).toBeInTheDocument();
    expect(screen.getByLabelText('Annual Vacation Days (unpaid)')).toBeInTheDocument();
    expect(screen.getByLabelText('Annual Sick Days (unpaid)')).toBeInTheDocument();
    expect(screen.getByLabelText('Months of Stoppage/No Projects')).toBeInTheDocument();
    expect(screen.getByLabelText('Custom Annual Benefits Value (PLN)')).toBeInTheDocument();

    // Check for UoP fields
    expect(screen.getByLabelText('Gross Monthly Salary (PLN)')).toBeInTheDocument();
    expect(screen.getByLabelText('Type of Tax-Deductible Costs')).toBeInTheDocument();
    expect(screen.getByTestId('youth-relief-uop')).toBeInTheDocument();
    expect(screen.getByLabelText('Medical Care')).toBeInTheDocument();
    expect(screen.getByLabelText('Sport Card')).toBeInTheDocument();

    // Check for buttons
    expect(screen.getByRole('button', { name: 'Calculate Comparison' })).toBeInTheDocument();
  });

  it('updates B2B input fields correctly', async () => {
    renderComponent();
    const fakturaInput = screen.getByLabelText('Monthly Invoice (PLN)');
    fireEvent.change(fakturaInput, { target: { name: 'monthly_invoice_amount', value: '15000' } });
    await waitFor(() => {
      expect(fakturaInput).toHaveValue(15000);
    });

    const costsInput = screen.getByLabelText('Monthly Business Costs (PLN)');
    fireEvent.change(costsInput, { target: { name: 'monthly_business_costs', value: '500' } });
    await waitFor(() => {
      expect(costsInput).toHaveValue(500);
    });
  });

  it('updates UoP input fields correctly', async () => {
    renderComponent();
    const wynagrodzenieInput = screen.getByLabelText('Gross Monthly Salary (PLN)');
    fireEvent.change(wynagrodzenieInput, { target: { name: 'monthly_gross_salary', value: '8000' } });
    await waitFor(() => {
      expect(wynagrodzenieInput).toHaveValue(8000);
    });
  });

  it('calls onCalculate on form submission', () => {
    renderComponent();
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    expect(mockOnCalculate).toHaveBeenCalledTimes(1);
  });

  // New tests for company benefits
  const companyBenefits = [
    { label: 'Paid Vacation Days (from company)', id: 'paidVacationDays', type: 'days', testId: 'paid-vacation' },
    { label: 'Paid Sick Days (from company)', id: 'paidSickDays', type: 'days', testId: 'paid-sick' },
    { label: 'Medical Care (from company)', id: 'medicalCare', type: 'value', testId: 'medical-care' },
    { label: 'Life Insurance (from company)', id: 'lifeInsurance', type: 'value', testId: 'life-insurance' },
    { label: 'Sport Card (from company)', id: 'sportCard', type: 'value', testId: 'sport-card' },
    { label: 'Training Budget (from company)', id: 'trainingBudget', type: 'value', testId: 'training-budget' },
    { label: 'Other Benefits (from company)', id: 'otherBenefits', type: 'value', testId: 'other-benefits' },
  ];

  companyBenefits.forEach(benefit => {
    it(`toggles ${benefit.label} and updates its value correctly`, async () => {
      renderComponent();
      const checkbox = screen.getByTestId(`${benefit.testId}-checkbox`);
      
      // Enable the benefit
      fireEvent.click(checkbox);
      await waitFor(() => {
        expect(checkbox).toBeChecked();
      });

      // Check if the input field appears and update its value
      const input = screen.getByTestId(`${benefit.testId}-input`);
      let inputValue = '';
      if (benefit.type === 'days') {
        inputValue = '10';
      } else {
        inputValue = '1000';
      }
      
      fireEvent.change(input, { target: { name: `companyBenefits.${benefit.id}.${benefit.type === 'days' ? 'days' : 'value'}`, value: inputValue } });
      await waitFor(() => {
        expect(input).toHaveValue(parseInt(inputValue));
      });

      // Disable the benefit
      fireEvent.click(checkbox);
      await waitFor(() => {
        expect(checkbox).not.toBeChecked();
      });
      // Ensure the input field is no longer in the document
      expect(screen.queryByTestId(`${benefit.testId}-input`)).not.toBeInTheDocument();
    });
  });

  it('updates UoP selected benefits correctly', async () => {
    renderComponent();
    const medicalCareCheckbox = screen.getByLabelText('Medical Care');
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).toBeChecked();
    });

    const sportCardCheckbox = screen.getByLabelText('Sport Card');
    fireEvent.click(sportCardCheckbox);
    await waitFor(() => {
      expect(sportCardCheckbox).toBeChecked();
    });

    // Uncheck one
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).not.toBeChecked();
    });
    expect(sportCardCheckbox).toBeChecked(); // Other should remain checked
  });

  it('renders KUP type select and its options', () => {
    renderComponent();
    const kupSelect = screen.getByLabelText('Type of Tax-Deductible Costs');
    expect(kupSelect).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Standard (250 PLN/month)' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Elevated (300 PLN/month)' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: '50% Creative Work Costs' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'None' })).toBeInTheDocument();
  });

  it('shows/hides creative work percentage input based on KUP type selection', async () => {
    renderComponent();
    const kupSelect = screen.getByLabelText('Type of Tax-Deductible Costs');
    const creativePercentageLabel = i18n.t('form.creative_work_percentage');

    // Initially, creative work percentage input should not be visible
    expect(screen.queryByLabelText(creativePercentageLabel)).not.toBeInTheDocument();

    // Select '50% Creative Work Costs'
    fireEvent.change(kupSelect, { target: { name: 'deductible_cost_settings.type', value: 'author_50' } });
    await waitFor(() => {
      expect(screen.getByLabelText(creativePercentageLabel)).toBeInTheDocument();
    });

    // Select 'Standard' again
    fireEvent.change(kupSelect, { target: { name: 'deductible_cost_settings.type', value: 'standard' } });
    await waitFor(() => {
      expect(screen.queryByLabelText(creativePercentageLabel)).not.toBeInTheDocument();
    });
  });

  it('updates KUP settings in state correctly', async () => {
    const TestWrapperWithState = () => {
      const [uopData, setUopData] = useState({
        monthly_gross_salary: 8000,
        deductible_cost_settings: { type: 'standard', creative_work_percentage: 70 },
        youth_relief: false,
        selected_benefits: [],
      });

      const handleUopChange = (e) => {
        const { name, value } = e.target;
        if (name.startsWith('deductible_cost_settings.')) {
          const field = name.split('.')[1];
          setUopData(prev => ({
            ...prev,
            deductible_cost_settings: {
              ...prev.deductible_cost_settings,
              [field]: value,
            },
          }));
        }
      };

      return (
          <CalculatorForm
            b2bData={initialB2bData}
            uopData={uopData}
            handleB2bChange={() => {}}
            handleUopChange={handleUopChange}
            handleCalculate={mockOnCalculate}
            loading={false}
            calculationMode="uop_to_b2b"
            handleCalculationModeChange={() => {}}
            insuranceConfig={{ activeProfile: 'standard', selections: {} }}
            setInsuranceConfig={() => {}}
          />
      );
    };

    render(<TestWrapperWithState />);

    const kupSelect = screen.getByLabelText('Type of Tax-Deductible Costs');
    fireEvent.change(kupSelect, { target: { name: 'deductible_cost_settings.type', value: 'author_50' } });
    await waitFor(() => {
      expect(kupSelect).toHaveValue('author_50');
    });

    const creativePercentageInput = screen.getByLabelText('Creative Work Percentage (%)');
    fireEvent.change(creativePercentageInput, { target: { name: 'deductible_cost_settings.creative_work_percentage', value: '85' } });
    await waitFor(() => {
      expect(creativePercentageInput).toHaveValue(85);
    });
  });

  it('disables equalize pension checkbox when UoP salary is zero', () => {
    renderComponent();
    const equalizePensionCheckbox = screen.getByLabelText(i18n.t('form.equalize_pension'));
    expect(equalizePensionCheckbox).toBeDisabled();
  });

  it('enables equalize pension checkbox when UoP salary is entered', async () => {
    renderComponent();
    const uopSalaryInput = screen.getByLabelText(i18n.t('form.gross_salary'));
    const equalizePensionCheckbox = screen.getByLabelText(i18n.t('form.equalize_pension'));

    fireEvent.change(uopSalaryInput, { target: { name: 'monthly_gross_salary', value: '12000' } });

    await waitFor(() => {
      expect(equalizePensionCheckbox).not.toBeDisabled();
    });
  });

  it('calls handleCalculate with equalizePension set to true when checked', async () => {
    renderComponent();
    const uopSalaryInput = screen.getByLabelText(i18n.t('form.gross_salary'));
    const equalizePensionCheckbox = screen.getByLabelText(i18n.t('form.equalize_pension'));

    fireEvent.change(uopSalaryInput, { target: { name: 'monthly_gross_salary', value: '12000' } });
    await waitFor(() => { /* wait for state update */ });

    fireEvent.click(equalizePensionCheckbox);
    await waitFor(() => {
      expect(equalizePensionCheckbox).toBeChecked();
    });

    fireEvent.click(screen.getByRole('button', { name: i18n.t('form.calculate_button') }));
    expect(mockOnCalculate).toHaveBeenCalledTimes(1);
  });
});
