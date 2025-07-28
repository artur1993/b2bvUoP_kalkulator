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
    saveAs.mockReset();

    // Mock window.alert
    vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Default successful API response
    api.calculateResults.mockResolvedValue({
      b2b_results: { calkowita_roczna_wartosc: 120000, roczny_przychod: 150000, roczne_koszty_firmowe: 10000, roczny_zus: 10000, roczny_podatek: 10000, roczny_utracony_przychod: 0, roczne_netto_na_reke: 100000, roczna_wartosc_benefitow_od_firmy: 0, roczna_wartosc_wlasnych_korzysci: 0, miesieczne_netto: 10000 },
      uop_results: { calkowita_roczna_wartosc: 100000, roczne_brutto: 120000, roczny_zus: 10000, roczny_podatek: 10000, roczna_wartosc_benefitow: 0, roczna_wartosc_platnych_dni_wolnych: 0, roczne_netto_na_reke: 100000, miesieczne_netto: 8000 },
      break_even_faktura: 11000,
    });

    api.exportToExcel.mockResolvedValue(new Blob(['excel data'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    api.exportToPdf.mockResolvedValue(new Blob(['pdf data'], { type: 'application/pdf' }));
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
      expect(screen.getByText('Failed to fetch results. Please try again.')).toBeInTheDocument();
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
    expect(saveAs).toHaveBeenCalledWith(expect.any(Blob), 'kalkulator_wyniki.pdf');
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

  it('toggles company benefits and updates values correctly', async () => {
    render(<App />);
    const paidVacationCheckbox = screen.getByTestId('paid-vacation-checkbox');
    fireEvent.click(paidVacationCheckbox);
    await waitFor(() => {
      expect(paidVacationCheckbox).toBeChecked();
    });

    const vacationDaysInput = screen.getByTestId('paid-vacation-input');
    fireEvent.change(vacationDaysInput, { target: { name: 'companyBenefits.paidVacationDays.days', value: '5' } });
    await waitFor(() => {
      expect(vacationDaysInput).toHaveValue(5);
    });
  });

  it('adds and removes UoP selected benefits correctly', async () => {
    render(<App />);
    const medicalCareCheckbox = screen.getByLabelText('Medical Care');
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).toBeChecked();
    });

    fireEvent.click(medicalCareCheckbox); // Click again to uncheck
    await waitFor(() => {
      expect(medicalCareCheckbox).not.toBeChecked();
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
      expect(screen.getByText('Failed to fetch results. Please try again.')).toBeInTheDocument();
    });
  });

  it('displays alert if exportToExcel fails', async () => {
    api.exportToExcel.mockRejectedValue(new Error('Export Excel Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: /Export to Excel/i }));
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to export Excel.');
    });
  });

  it('displays alert if exportToPdf fails', async () => {
    api.exportToPdf.mockRejectedValue(new Error('Export PDF Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Calculate Comparison' }));
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: /Export to PDF/i }));
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to export PDF.');
    });
  });
});