import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ResultsDisplay from './ResultsDisplay';
import '@testing-library/jest-dom';
import i18n from '../i18n.js'; // Import i18n instance

// Mock data for the tests
const mockResultsUopToB2b = {
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
  break_even_wynagrodzenie_brutto: -1,
};

const mockResultsB2bToUop = {
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
  break_even_faktura: -1,
  break_even_wynagrodzenie_brutto: 9000,
};

// Helper to format currency for assertions, handling non-breaking spaces
const formatCurrencyForTest = (value) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(value).replace(/\s/g, ' ');
  };

describe('ResultsDisplay Component', () => {
  // Test 5: Handling no results
  it('should render null when no results are provided', () => {
    const { container } = render(<ResultsDisplay />);
    expect(container.firstChild).toBeNull();
  });

  // Test 1: Correct rendering of all key data
  it('should render all key data correctly', () => {
    render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);

    expect(screen.getByText(i18n.t('results.title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.b2b_title'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('form.uop_title'))).toBeInTheDocument();

    // Check for key labels
    expect(screen.getByText(i18n.t('results.annual_revenue') + ':')).toBeInTheDocument();
    expect(screen.getByText(i18n.t('results.annual_gross') + ':')).toBeInTheDocument();
  });

  // Test 2: Correct currency formatting
  it('should format numerical values as PLN currency', () => {
    render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);
    
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
    it('should display the break-even section when break_even_faktura is not -1 (UoP to B2B mode)', () => {
      render(<ResultsDisplay results={mockResultsUopToB2b} calculationMode="uop_to_b2b" />);
      const expectedBreakEven = formatCurrencyForTest(8500);
      
      const breakEvenLabel = screen.getByText(i18n.t('results.break_even_b2b_title') + ': ' + expectedBreakEven);
      expect(breakEvenLabel).toBeInTheDocument();
      expect(screen.getByText(i18n.t('results.break_even_b2b_subtitle'))).toBeInTheDocument();
    });

    it('should display the break-even section when break_even_wynagrodzenie_brutto is not -1 (B2B to UoP mode)', () => {
      render(<ResultsDisplay results={mockResultsB2bToUop} calculationMode="b2b_to_uop" />);
      const expectedBreakEven = formatCurrencyForTest(9000);
      
      const breakEvenLabel = screen.getByText(i18n.t('results.break_even_uop_title') + ': ' + expectedBreakEven);
      expect(breakEvenLabel).toBeInTheDocument();
      expect(screen.getByText(i18n.t('results.break_even_uop_subtitle'))).toBeInTheDocument();
    });

    it('should not display the break-even section when break_even_faktura is -1 (UoP to B2B mode)', () => {
      const resultsWithNoBreakEven = { ...mockResultsUopToB2b, break_even_faktura: -1 };
      render(<ResultsDisplay results={resultsWithNoBreakEven} calculationMode="uop_to_b2b" />);
      expect(screen.queryByText(new RegExp(i18n.t('results.break_even_b2b_title')))).not.toBeInTheDocument();
    });

    it('should not display the break-even section when break_even_wynagrodzenie_brutto is -1 (B2B to UoP mode)', () => {
      const resultsWithNoBreakEven = { ...mockResultsB2bToUop, break_even_wynagrodzenie_brutto: -1 };
      render(<ResultsDisplay results={resultsWithNoBreakEven} calculationMode="b2b_to_uop" />);
      expect(screen.queryByText(new RegExp(i18n.t('results.break_even_uop_title')))).not.toBeInTheDocument();
    });
  });

  // Test 4: Rendering of export buttons
  it('should always render export buttons when results are provided', () => {
    const handleExportPdf = vi.fn();
    const handleExportExcel = vi.fn();

    render(
      <ResultsDisplay
        results={mockResultsUopToB2b}
        onExportPdf={handleExportPdf}
        onExportExcel={handleExportExcel}
        calculationMode="uop_to_b2b"
      />
    );

    expect(screen.getByRole('button', { name: i18n.t('results.export_pdf_basic') })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: i18n.t('results.export_pdf_advanced') })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: i18n.t('results.export_excel') })).toBeInTheDocument();
  });
});
