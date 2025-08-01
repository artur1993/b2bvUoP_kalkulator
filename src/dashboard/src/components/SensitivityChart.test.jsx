import React from 'react';
import { render, screen, waitFor } from '../utils/test-utils';
import SensitivityChart from './SensitivityChart';
import * as api from '../services/api';
import { vi } from 'vitest';

vi.mock('../services/api');
vi.mock('react-chartjs-2', () => ({
  Bar: (props) => <div data-testid="mock-bar-chart" {...props} />,
}));

const mockB2bData = { monthly_invoice_amount: 10000 };
const mockUopData = { wynagrodzenie_brutto: 8000 };

describe('SensitivityChart', () => {
    test('renders loading state initially and then the chart', async () => {
        api.calculateSensitivityAnalysis.mockResolvedValue([
            { parameter: 'koszty_firmowe_miesieczne', impact: 5000 },
            { parameter: 'urlop_dni', impact: -2000 },
        ]);

        render(<SensitivityChart b2b={mockB2bData} uop={mockUopData} results={{}} />);

        expect(await screen.findByTestId('mock-bar-chart')).toBeInTheDocument();
    });

    test('shows no data message if api returns empty array', async () => {
        api.calculateSensitivityAnalysis.mockResolvedValue([]);

        render(<SensitivityChart b2b={mockB2bData} uop={mockUopData} results={{}} />);

        await waitFor(() => {
            expect(screen.queryByTestId('mock-bar-chart')).not.toBeInTheDocument();
        });
        expect(await screen.findByText('no_data')).toBeInTheDocument();
    });
});
