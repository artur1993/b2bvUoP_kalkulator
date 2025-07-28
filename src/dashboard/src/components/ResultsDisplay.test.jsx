import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ResultsDisplay from './ResultsDisplay';
import '@testing-library/jest-dom';

// Mock data for the tests
const mockResults = {
  b2b_results: {
    roczny_przychod: 120000,
    roczne_koszty_firmowe: 12000,
    roczny_zus: 24000,
    roczny_podatek: 10000,
    roczny_utracony_przychod: 5000,
    roczne_netto_na_reke: 69000,
    roczna_wartosc_benefitow_od_firmy: 1000,
    roczna_wartosc_wlasnych_korzysci: 2000,
    calkowita_roczna_wartosc: 72000,
    miesieczne_netto: 6000,
  },
  uop_results: {
    roczne_brutto: 100000,
    roczny_zus: 20000,
    roczny_podatek: 8000,
    roczne_netto_na_reke: 72000,
    roczna_wartosc_benefitow: 3000,
    roczna_wartosc_platnych_dni_wolnych: 4000,
    calkowita_roczna_wartosc: 79000,
    miesieczne_netto: 6583.33,
  },
  break_even_faktura: 8500,
};

// Helper to format currency for assertions, handling non-breaking spaces
const formatCurrencyForTest = (value) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(value);
  };

describe('ResultsDisplay Component', () => {
  // Test 5: Handling no results
  it('should render null when no results are provided', () => {
    const { container } = render(<ResultsDisplay />);
    expect(container.firstChild).toBeNull();
  });

  // Test 1: Correct rendering of all key data
  it('should render all key data correctly', () => {
    render(<ResultsDisplay results={mockResults} />);

    expect(screen.getByText('Calculation Results')).toBeInTheDocument();
    expect(screen.getByText('B2B Contract')).toBeInTheDocument();
    expect(screen.getByText('Employment Contract (UoP)')).toBeInTheDocument();

    // Check for key labels
    expect(screen.getByText('Annual Revenue:')).toBeInTheDocument();
    expect(screen.getByText('Annual Gross Salary:')).toBeInTheDocument();
  });

  // Test 2: Correct currency formatting
  it('should format numerical values as PLN currency', () => {
    render(<ResultsDisplay results={mockResults} />);
    
    const expectedRevenue = formatCurrencyForTest(120000);
    const expectedGrossSalary = formatCurrencyForTest(100000);

    // Use regex for partial match
    const revenueLabel = screen.getByText('Annual Revenue:');
    expect(revenueLabel.parentElement).toHaveTextContent(new RegExp(expectedRevenue.replace(/\s/g, '\\s')));

    const grossSalaryLabel = screen.getByText('Annual Gross Salary:');
    expect(grossSalaryLabel.parentElement).toHaveTextContent(new RegExp(expectedGrossSalary.replace(/\s/g, '\\s')));
  });

  // Test 3: Conditional logic for "Break-Even Point"
  describe('Break-Even Point Logic', () => {
    it('should display the break-even section when break_even_faktura is not -1', () => {
      render(<ResultsDisplay results={mockResults} />);
      const expectedBreakEven = formatCurrencyForTest(8500);
      
      // Find the parent element and check its content
      const breakEvenLabel = screen.getByText(/Break-Even Monthly B2B Invoice:/);
      expect(breakEvenLabel.parentElement).toHaveTextContent(new RegExp(expectedBreakEven.replace(/\s/g, '\\s')));
    });

    it('should not display the break-even section when break_even_faktura is -1', () => {
      const resultsWithNoBreakEven = { ...mockResults, break_even_faktura: -1 };
      render(<ResultsDisplay results={resultsWithNoBreakEven} />);
      expect(screen.queryByText(/Break-Even Monthly B2B Invoice:/)).not.toBeInTheDocument();
    });
  });

  // Test 4: Rendering of export buttons
  it('should always render export buttons when results are provided', () => {
    const handleExportPdf = vi.fn();
    const handleExportExcel = vi.fn();

    render(
      <ResultsDisplay
        results={mockResults}
        onExportPdf={handleExportPdf}
        onExportExcel={handleExportExcel}
      />
    );

    expect(screen.getByRole('button', { name: /Export to PDF/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Export to Excel/i })).toBeInTheDocument();
  });
});
