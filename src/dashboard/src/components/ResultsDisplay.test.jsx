import React from 'react';
import { render, screen } from '../utils/test-utils';
import { describe, it, expect, vi } from 'vitest';
import ResultsDisplay from './ResultsDisplay';
import '@testing-library/jest-dom';
import i18n from '../i18n.js';


// Mock data for the tests
const mockResultsUopToB2b = {
  b2b_results: {
    annual_revenue: 120000,
    annual_business_costs: 12000,
    annual_zus: 24000,
    annual_tax: 10000,
    annual_lost_revenue: 5000,
    annual_net_income: 69000,
    annual_company_benefits_value: 1000,
    annual_custom_benefits_value: 2000,
    total_annual_value: 72000,
    monthly_net_income: 6000,
  },
  uop_results: {
    annual_gross_salary: 100000,
    annual_zus: 20000,
    annual_tax: 8000,
    annual_net_income: 72000,
    annual_benefits_value: 3000,
    annual_paid_days_off_value: 4000,
    total_annual_value: 79000,
    monthly_net_income: 6583.33,
  },
  break_even_invoice_amount: 8500,
  break_even_gross_salary: -1,
  analysis: {
    summary: { recommendation: "Test recommendation" },
    risk: { point1: "Risk point 1" },
    methodology: "Test methodology",
    checklist: { title: "Test Checklist", items: ["Item 1", "Item 2"] }
  }
};

const mockResultsB2bToUop = {
  ...mockResultsUopToB2b,
  break_even_invoice_amount: -1,
  break_even_gross_salary: 9000,
};

// Helper to format currency for assertions, handling non-breaking spaces
const formatCurrencyForTest = (value) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(value).replace(/\s/g, ' ');
  };

describe('ResultsDisplay Component', () => {
  // Test: Handling no results
  it('should render null when no results are provided', () => {
    const { container } = render(
        <ResultsDisplay />
    );
    expect(container.firstChild).toBeNull();
  });

  // Test 1: Correct rendering of all key data
  it('should render all key data correctly', () => {
    render(
        <ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />
    );

    expect(screen.getByText(i18n.t('results.title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.b2b_title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.uop_title'))).toBeInTheDocument();

    // Check for key labels
    expect(screen.getByText(i18n.t('results.annual_revenue') + ':')).toBeInTheDocument();
    expect(screen.getByText(i18n.t('results.annual_gross') + ':')).toBeInTheDocument();
  });

  // Test 2: Correct currency formatting
  it('should format numerical values as PLN currency', () => {
    render(
        <ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />
    );
    
    const expectedRevenue = formatCurrencyForTest(120000);
    const expectedGrossSalary = formatCurrencyForTest(100000);

    // Use regex for partial match
    const revenueLabel = screen.getByText(i18n.t('results.annual_revenue') + ':');
    expect(revenueLabel.parentElement).toHaveTextContent(new RegExp(expectedRevenue.replace(/\s/g, '\\s')));

    const grossSalaryLabel = screen.getByText(i18n.t('results.annual_gross') + ':');
    expect(grossSalaryLabel.parentElement).toHaveTextContent(new RegExp(expectedGrossSalary.replace(/\s/g, '\\s')));
  });

  // Test 3: Conditional logic for "Break-Even Point"
  describe('Break-Even Point Logic', () => {
    it('should display the break-even section when break_even_invoice_amount is not -1 (UoP to B2B mode)', () => {
      render(
          <ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />
      );
      const breakEvenSection = screen.getByTestId('break-even-section');
      expect(breakEvenSection).toBeInTheDocument();
      expect(breakEvenSection).toHaveTextContent(i18n.t('results.break_even_b2b_title'));
    });

    it('should display the break-even section when break_even_gross_salary is not -1 (B2B to UoP mode)', () => {
      render(
          <ResultsDisplay results={mockResultsB2bToUop} calculationMode="b2b_to_uop" />
      );
      const breakEvenSection = screen.getByTestId('break-even-section');
      expect(breakEvenSection).toBeInTheDocument();
      expect(breakEvenSection).toHaveTextContent(i18n.t('results.break_even_uop_title'));
    });

    it('should not display the break-even section when break_even_invoice_amount is -1 (UoP to B2B mode)', () => {
      const resultsWithNoBreakEven = { ...mockResultsUopToB2b, break_even_invoice_amount: -1 };
      render(
          <ResultsDisplay results={resultsWithNoBreakEven} calculationMode="uop_to_b2b" />
      );
      expect(screen.queryByTestId('break-even-section')).not.toBeInTheDocument();
    });

    it('should not display the break-even section when break_even_gross_salary is -1 (B2B to UoP mode)', () => {
      const resultsWithNoBreakEven = { ...mockResultsB2bToUop, break_even_gross_salary: -1 };
      render(
          <ResultsDisplay results={resultsWithNoBreakEven} calculationMode="b2b_to_uop" />
      );
      expect(screen.queryByTestId('break-even-section')).not.toBeInTheDocument();
    });
  });

  // Test 4: Rendering of analysis sections
  it('should render advanced analysis sections', () => {
    render(
        <ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />
    );

    expect(screen.getByText("Test recommendation")).toBeInTheDocument();
    expect(screen.getByText("Risk point 1")).toBeInTheDocument();
    expect(screen.getByText("Test methodology")).toBeInTheDocument();
    expect(screen.getByText("Test Checklist")).toBeInTheDocument();
    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
  });

  // Test 5: Rendering of export buttons
  it('should render excel export button but not PDF buttons', () => {
    const handleExportExcel = vi.fn();

    render(
        <ResultsDisplay
          results={mockResultsUopToB2b}
          onExportExcel={handleExportExcel}
          calculationMode="uop_to_b2b"
        />
    );

    expect(screen.queryByText(i18n.t('results.export_pdf_basic'))).not.toBeInTheDocument();
    expect(screen.queryByText(i18n.t('results.export_pdf_advanced'))).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: i18n.t('results.export_excel') })).toBeInTheDocument();
  });
});
