import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';
import React from 'react';
import * as api from './services/api';
import { saveAs } from 'file-saver';

// Mock API calls
vi.mock('./services/api', () => ({
  calculateResults: vi.fn(),
  exportToExcel: vi.fn(),
  exportToPdf: vi.fn(),
  exportToAdvancedPdf: vi.fn(),
  calculateBreakEvenAnalysis: vi.fn(),
  calculateSensitivityAnalysis: vi.fn(),
}));

// Mock file-saver
vi.mock('file-saver', () => ({
  saveAs: vi.fn(),
}));

// Mock react-chartjs-2 components
vi.mock('react-chartjs-2', () => ({
  Chart: vi.fn(() => null), // Mock Chart component to return null
  Line: vi.fn(() => null), // Mock Line component to return null
  Bar: vi.fn(() => null), // Mock Bar component to return null
  Pie: vi.fn(() => null), // Mock Pie component to return null
}));

describe('App', () => {
  beforeEach(() => {
    // Reset mocks before each test
    api.calculateResults.mockReset();
    api.exportToExcel.mockReset();
    api.exportToPdf.mockReset();
    api.exportToAdvancedPdf.mockReset(); // Reset mock for exportToAdvancedPdf
    saveAs.mockReset();

    // Mock window.alert
    vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Default successful API response
    api.calculateResults.mockResolvedValue({
      b2b_results: { calkowita_roczna_wartosc: 120000, roczny_przychod: 150000, roczne_koszty_firmowe: 10000, roczny_zus: 10000, roczny_podatek: 10000, roczny_utracony_przychod: 0, roczne_netto_na_reke: 100000, roczna_wartosc_benefitow_od_firmy: 0, roczna_wartosc_wlasnych_korzysci: 0, miesieczne_netto: 10000 },
      uop_results: { calkowita_roczna_wartosc: 100000, roczne_brutto: 120000, roczny_zus: 10000, roczny_podatek: 10000, roczna_wartosc_benefitow: 0, roczna_wartosc_platnych_dni_wolnych: 0, roczne_netto_na_reke: 100000, miesieczne_netto: 8000 },
      break_even_faktura: 11000,
    });

    api.calculateBreakEvenAnalysis.mockResolvedValue([]);
    api.calculateSensitivityAnalysis.mockResolvedValue([]);

    api.exportToExcel.mockResolvedValue(new Blob(['excel data'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    api.exportToPdf.mockResolvedValue(new Blob(['pdf data'], { type: 'application/pdf' }));
    api.exportToAdvancedPdf.mockResolvedValue(new Blob(['advanced pdf data'], { type: 'application/pdf' })); // Mock advanced PDF export
  });

  it('renders CalculatorForm and Header initially', () => {
    render(<App />);
    expect(screen.getByTestId('header-title')).toBeInTheDocument();
    expect(screen.getByTestId('b2b-form-title')).toBeInTheDocument();
  });

  it('calls calculateResults and displays results on form submission', async () => {
    render(<App />);

    // Simulate form submission
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));

    // Expect calculateResults to be called
    expect(api.calculateResults).toHaveBeenCalledTimes(1);

    // Wait for results to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
  });

  it('displays error message if calculateResults fails', async () => {
    api.calculateResults.mockRejectedValue(new Error('API Error'));
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));

    await waitFor(() => {
      expect(screen.getByTestId('alert-message')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch results. Please check the console for more details.')).toBeInTheDocument();
    });
  });

  it('calls exportToExcel and saves the file', async () => {
    render(<App />);

    // First, calculate results to enable export buttons
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });

    // Wait for the button to appear before clicking
    await waitFor(() => {
      expect(screen.getByTestId('export-excel-button')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-excel-button'));

    await waitFor(() => expect(api.exportToExcel).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(saveAs).toHaveBeenCalledTimes(1));
    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'kalkulator_wyniki.xlsx');
  });

  it('calls exportToPdf and saves the file', async () => {
    render(<App />);

    // First, calculate results to enable export buttons
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });

    // Wait for the button to appear before clicking
    await waitFor(() => {
      expect(screen.getByTestId('export-pdf-button')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-pdf-button'));

    await waitFor(() => expect(api.exportToPdf).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(saveAs).toHaveBeenCalledTimes(1));
    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'Raport_B2B_vs_UoP.pdf');
  });

  it('calls exportToAdvancedPdf and saves the file', async () => {
    render(<App />);

    // First, calculate results to enable export buttons
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });

    // Wait for the button to appear before clicking
    await waitFor(() => {
      expect(screen.getByTestId('export-advanced-pdf-button')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-advanced-pdf-button'));

    await waitFor(() => expect(api.exportToAdvancedPdf).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(saveAs).toHaveBeenCalledTimes(1));
    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'Raport_Zaawansowany_B2B_vs_UoP.pdf');
  });

  it('handles B2B input changes correctly', async () => {
    render(<App />);
    const fakturaInput = screen.getByLabelText('Monthly Invoice (PLN)');
    fireEvent.change(fakturaInput, { target: { name: 'faktura_miesieczna', value: '15000' } });
    await waitFor(() => {
      expect(fakturaInput).toHaveValue(15000);
    });
  });

  it('handles UoP input changes correctly', async () => {
    render(<App />);
    const wynagrodzenieInput = screen.getByLabelText('Gross Monthly Salary (PLN)');
    fireEvent.change(wynagrodzenieInput, { target: { name: 'wynagrodzenie_brutto', value: '9000' } });
    await waitFor(() => {
      expect(wynagrodzenieInput).toHaveValue(9000);
    });
  });

  it('handles B2B input changes correctly for company benefits', async () => {
    render(<App />);
    const medicalCareCheckbox = screen.getByTestId('medical-care-checkbox');
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).toBeChecked();
    });

    const medicalCareInput = screen.getByTestId('medical-care-input');
    fireEvent.change(medicalCareInput, { target: { name: 'companyBenefits.medicalCare.value', value: '500' } });
    await waitFor(() => {
      expect(medicalCareInput).toHaveValue(500);
    });
  });

  it('handles UoP input changes correctly for KUP settings', async () => {
    render(<App />);
    const kupSelect = screen.getByLabelText('Type of Tax-Deductible Costs');
    fireEvent.change(kupSelect, { target: { name: 'kup_settings.type', value: 'autorskie_50' } });
    await waitFor(() => {
      expect(kupSelect).toHaveValue('autorskie_50');
    });

    const creativePercentageInput = screen.getByLabelText('Creative Work Percentage (%)');
    fireEvent.change(creativePercentageInput, { target: { name: 'kup_settings.creative_work_percentage', value: '80' } });
    await waitFor(() => {
      expect(creativePercentageInput).toHaveValue(80);
    });
  });

  it('displays SkeletonLoader when loading is true', async () => {
    api.calculateResults.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({
      b2b_results: { calkowita_roczna_wartosc: 120000, roczny_przychod: 150000, roczne_koszty_firmowe: 10000, roczny_zus: 10000, roczny_podatek: 10000, roczny_utracony_przychod: 0, roczne_netto_na_reke: 100000, roczna_wartosc_benefitow_od_firmy: 0, roczna_wartosc_wlasnych_korzysci: 0, miesieczne_netto: 10000 },
      uop_results: { calkowita_roczna_wartosc: 100000, roczne_brutto: 120000, roczny_zus: 10000, roczny_podatek: 10000, roczna_wartosc_benefitow: 0, roczna_wartosc_platnych_dni_wolnych: 0, roczne_netto_na_reke: 100000, miesieczne_netto: 8000 },
      break_even_faktura: 11000,
    }), 100))); // Simulate loading
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByTestId('skeleton-loader')).not.toBeInTheDocument());
  });

  it('displays Alert when error is present', async () => {
    api.calculateResults.mockRejectedValue(new Error('Test Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch results. Please check the console for more details.')).toBeInTheDocument();
    });
  });

  it('displays alert if exportToExcel fails', async () => {
    api.exportToExcel.mockRejectedValue(new Error('Export Excel Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-excel-button'));
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to export Excel. See console for details.');
    });
  });

  it('displays alert if exportToPdf fails', async () => {
    api.exportToPdf.mockRejectedValue(new Error('Export PDF Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-pdf-button'));
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to export PDF. See console for details.');
    });
  });

  it('displays alert if exportToAdvancedPdf fails', async () => {
    api.exportToAdvancedPdf.mockRejectedValue(new Error('Export Advanced PDF Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('export-advanced-pdf-button'));
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to export advanced PDF. See console for details.');
    });
  });
});