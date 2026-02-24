import React from 'react';
import { render, screen, waitFor } from '../utils/test-utils';
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
  it('should render null when no results are provided', () => {
    const { container } = render(<ResultsDisplay />);
    expect(container.firstChild).toBeNull();
  });

  it('should render all key data correctly', async () => {
    render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);
    
    // Wait for animation
    expect(await screen.findByText(i18n.t('results.title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.b2b_title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.uop_title'))).toBeInTheDocument();
  });

  describe('Break-Even Point Logic', () => {
    it('should display the break-even section when break_even_invoice_amount is not -1', async () => {
      render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);
      const breakEvenSection = await screen.findByTestId('break-even-section');
      expect(breakEvenSection).toBeInTheDocument();
      expect(breakEvenSection).toHaveTextContent(i18n.t('results.break_even_b2b_title'));
    });

    it('should display the break-even section when break_even_gross_salary is not -1', async () => {
      render(<ResultsDisplay results={mockResultsB2bToUop} calculationMode="b2b_to_uop" />);
      const breakEvenSection = await screen.findByTestId('break-even-section');
      expect(breakEvenSection).toBeInTheDocument();
      expect(breakEvenSection).toHaveTextContent(i18n.t('results.break_even_uop_title'));
    });
  });

  it('should render advanced analysis sections', async () => {
    render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);

    // Match recommendation text (case insensitive, partial match to ignore quotes)
    expect(await screen.findByText(/Test recommendation/i)).toBeInTheDocument();
    expect(screen.getByText(/Risk point 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Test Checklist/i)).toBeInTheDocument();
    expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
  });

  it('should render excel export button', async () => {
    const handleExportExcel = vi.fn();
    render(<ResultsDisplay results={mockResultsUopToB2b} onExportExcel={handleExportExcel} calculationMode="uop_to_b2b" />);

    expect(await screen.findByTestId('export-excel-button')).toBeInTheDocument();
  });
});
