import { render, screen, fireEvent, waitFor } from './utils/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';
import React from 'react';
import * as api from './services/api';
import { saveAs } from 'file-saver';

// Mock API calls
vi.mock('./services/api', () => ({
  calculateResults: vi.fn(),
  exportToExcel: vi.fn(),
  calculateBreakEvenAnalysis: vi.fn(),
}));

// Mock file-saver
vi.mock('file-saver', () => ({
  saveAs: vi.fn(),
}));

// Mock react-chartjs-2 components
vi.mock('react-chartjs-2', () => ({
  Chart: vi.fn(() => null),
  Line: vi.fn(() => null),
  Bar: vi.fn(() => null),
  Pie: vi.fn(() => null),
}));

describe('App Phase 2', () => {
  beforeEach(() => {
    api.calculateResults.mockReset();
    api.exportToExcel.mockReset();
    saveAs.mockReset();
    vi.spyOn(window, 'alert').mockImplementation(() => {});

    api.calculateResults.mockResolvedValue({
      b2b_results: { total_annual_value: 120000, annual_revenue: 150000, annual_zus: 10000, annual_tax: 10000 },
      uop_results: { total_annual_value: 100000, annual_gross_salary: 120000, annual_zus: 10000, annual_tax: 10000 },
      break_even_invoice_amount: 11000,
      analysis: {
        summary: { recommendation: "Test recommendation" },
        risk: { point1: "Risk point 1" },
        methodology: "Test methodology",
        checklist: { title: "Test Checklist", items: ["Item 1"] }
      }
    });

    api.calculateBreakEvenAnalysis.mockResolvedValue([]);
    api.exportToExcel.mockResolvedValue(new Blob(['excel'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
  });

  it('renders dark mode toggle and responds to clicks', () => {
    render(<App />);
    const toggle = screen.getByTestId('theme-toggle');
    expect(toggle).toBeInTheDocument();
    
    fireEvent.click(toggle);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('updates the URL when calculation is performed', async () => {
    render(<App />);
    const calculateButton = screen.getByRole('button', { name: /calculate/i });
    
    fireEvent.click(calculateButton);

    await waitFor(() => {
      // Use current default value from App.jsx (10000)
      expect(window.location.search).toContain('b2b_invoice=10000');
      expect(window.location.search).toContain('mode=uop_to_b2b');
    });
  });

  it('calls calculateResults and displays results', async () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    await waitFor(() => {
      expect(screen.getByTestId('results-display')).toBeInTheDocument();
      expect(screen.getByText(/Test recommendation/i)).toBeInTheDocument();
    });
  });

  it('displays error message if calculateResults fails', async () => {
    api.calculateResults.mockRejectedValue(new Error('API Error'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch results/i)).toBeInTheDocument();
    });
  });
});
