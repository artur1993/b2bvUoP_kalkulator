import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ComparisonChart from './ComparisonChart';
import React from 'react';

// Mock react-chartjs-2 components
vi.mock('react-chartjs-2', () => ({
  Bar: (props) => <div data-testid="mock-bar-chart" {...props} />,
  Pie: (props) => <div data-testid="mock-pie-chart" {...props} />,
}));

// Mock chart.js register
vi.mock('chart.js', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    Chart: {
      ...actual.Chart,
      register: vi.fn(),
    },
  };
});

describe('ComparisonChart', () => {
  const mockResults = {
    b2b_results: {
      calkowita_roczna_wartosc: 120000,
      roczne_netto_na_reke: 100000,
      roczna_wartosc_benefitow_od_firmy: 10000,
      roczna_wartosc_wlasnych_korzysci: 5000,
    },
    uop_results: {
      calkowita_roczna_wartosc: 100000,
      roczne_netto_na_reke: 80000,
      roczna_wartosc_benefitow: 15000,
      roczna_wartosc_platnych_dni_wolnych: 5000,
    },
  };

  it('renders the chart section when results are provided', () => {
    render(<ComparisonChart results={mockResults} />);
    // The component renders a div with a specific class, we can check for that
    expect(screen.getByTestId('comparison-chart-section')).toBeInTheDocument();
  });

  it('does not render if results are null', () => {
    const { container } = render(<ComparisonChart results={null} />);
    expect(container.firstChild).toBeNull();
  });
});