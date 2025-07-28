import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import CalculatorForm from './CalculatorForm';
import React, { useState } from 'react';

describe('CalculatorForm', () => {
  const mockOnCalculate = vi.fn();
  const mockOnExport = vi.fn();

  const initialB2bData = {
    faktura_miesieczna: 0,
    koszty_firmowe_miesieczne: 0,
    zus_rodzaj: 'mala_firma',
    zus_chorobowe: false,
    forma_opodatkowania: 'liniowy',
    ulga_dla_mlodych: false,
    urlop_dni: 0,
    chorobowe_dni: 0,
    przestoje_miesiace: 0,
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
    wynagrodzenie_brutto: 0,
    koszty_uzyskania_przychodu: 0,
    ulga_dla_mlodych: false,
    wybrane_benefity: [],
  };

  // Test Wrapper component to manage state
  const TestWrapper = ({ initialB2b, initialUop, onCalculate, onExport, loading }) => {
    const [b2bData, setB2bData] = useState(initialB2b);
    const [uopData, setUopData] = useState(initialUop);

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
      if (name === 'wybrane_benefity') {
        setUopData(prev => ({
          ...prev,
          wybrane_benefity: checked
            ? [...prev.wybrane_benefity, value]
            : prev.wybrane_benefity.filter(benefit => benefit !== value),
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
    expect(screen.getByLabelText(/Monthly Invoice \(PLN\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Monthly Business Costs \(PLN\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ZUS Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Taxation Form/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Youth Tax Relief \(Ulga dla Młodych\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Annual Vacation Days \(unpaid\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Annual Sick Days \(unpaid\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Months of Stoppage\/No Projects/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Custom Annual Benefits Value \(PLN\)/i)).toBeInTheDocument();

    // Check for UoP fields
    expect(screen.getByLabelText(/Gross Monthly Salary \(PLN\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Annual Tax-Deductible Costs \(PLN\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Youth Tax Relief \(Ulga dla Młodych\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Opieka Medyczna/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Karta Sportowa/i)).toBeInTheDocument();

    // Check for buttons
    expect(screen.getByRole('button', { name: /Calculate Comparison/i })).toBeInTheDocument();
  });

  it('updates B2B input fields correctly', async () => {
    renderComponent();
    const fakturaInput = screen.getByLabelText(/Monthly Invoice \(PLN\)/i);
    fireEvent.change(fakturaInput, { target: { name: 'faktura_miesieczna', value: '15000' } });
    await waitFor(() => {
      expect(fakturaInput).toHaveValue(15000);
    });

    const costsInput = screen.getByLabelText(/Monthly Business Costs \(PLN\)/i);
    fireEvent.change(costsInput, { target: { name: 'koszty_firmowe_miesieczne', value: '500' } });
    await waitFor(() => {
      expect(costsInput).toHaveValue(500);
    });
  });

  it('updates UoP input fields correctly', async () => {
    renderComponent();
    const wynagrodzenieInput = screen.getByLabelText(/Gross Monthly Salary \(PLN\)/i);
    fireEvent.change(wynagrodzenieInput, { target: { name: 'wynagrodzenie_brutto', value: '8000' } });
    await waitFor(() => {
      expect(wynagrodzenieInput).toHaveValue(8000);
    });

    const taxDeductibleCostsInput = screen.getByLabelText(/Annual Tax-Deductible Costs \(PLN\)/i);
    fireEvent.change(taxDeductibleCostsInput, { target: { name: 'koszty_uzyskania_przychodu', value: '250' } });
    await waitFor(() => {
      expect(taxDeductibleCostsInput).toHaveValue(250);
    });
  });

  it('calls onCalculate on form submission', () => {
    renderComponent();
    fireEvent.click(screen.getByRole('button', { name: /Calculate Comparison/i }));
    expect(mockOnCalculate).toHaveBeenCalledTimes(1);
  });

  // New tests for company benefits
  const companyBenefits = [
    { label: 'Paid Vacation Days (from company)', id: 'paidVacationDays', type: 'days' },
    { label: 'Paid Sick Days (from company)', id: 'paidSickDays', type: 'days' },
    { label: 'Medical Care (from company)', id: 'medicalCare', type: 'value' },
    { label: 'Life Insurance (from company)', id: 'lifeInsurance', type: 'value' },
    { label: 'Sport Card (from company)', id: 'sportCard', type: 'value' },
    { label: 'Training Budget (from company)', id: 'trainingBudget', type: 'value' },
    { label: 'Other Benefits (from company)', id: 'otherBenefits', type: 'value' },
  ];

  companyBenefits.forEach(benefit => {
    it(`toggles ${benefit.label} and updates its value correctly`, async () => {
      renderComponent();
      const checkbox = screen.getByLabelText(benefit.label);
      
      // Enable the benefit
      fireEvent.click(checkbox);
      await waitFor(() => {
        expect(checkbox).toBeChecked();
      });

      // Check if the input field appears and update its value
      let inputLabel = '';
      let inputValue = '';
      if (benefit.type === 'days') {
        inputLabel = `Number of ${benefit.label.replace(' (from company)', '')}`;
        inputValue = '10';
      } else {
        inputLabel = `${benefit.label.replace(' (from company)', '')} Value (PLN/year)`;
        inputValue = '1000';
      }
      
      const input = screen.getByLabelText(inputLabel);
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
      expect(screen.queryByLabelText(inputLabel)).not.toBeInTheDocument();
    });
  });

  it('updates UoP selected benefits correctly', async () => {
    renderComponent();
    const medicalCareCheckbox = screen.getByLabelText('Opieka Medyczna');
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).toBeChecked();
    });

    const sportCardCheckbox = screen.getByLabelText('Karta Sportowa');
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
});
