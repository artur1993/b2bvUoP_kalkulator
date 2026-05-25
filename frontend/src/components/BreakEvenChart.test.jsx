import React from 'react';
import { render, screen, waitFor } from '../utils/test-utils';
import BreakEvenChart from './BreakEvenChart';
import * as api from '../services/api';
import { vi } from 'vitest';

vi.mock('../services/api');
vi.mock('react-chartjs-2', () => ({
  Line: (props) => <div data-testid="mock-line-chart" {...props} />,
}));


const mockB2bData = { monthly_invoice_amount: 10000 };
const mockUopData = { wynagrodzenie_brutto: 8000 };

describe('BreakEvenChart', () => {
    test('renders loading state initially and then the chart', async () => {
        api.calculateBreakEvenAnalysis.mockResolvedValue([
            { b2b_rate: 5000, net_difference: -10000 },
            { b2b_rate: 15000, net_difference: 10000 },
        ]);

        render(<BreakEvenChart b2b={mockB2bData} uop={mockUopData} results={{}} />);

        expect(await screen.findByTestId('mock-line-chart')).toBeInTheDocument();
    });

    test('shows no data message if api returns empty array', async () => {
        api.calculateBreakEvenAnalysis.mockResolvedValue([]);

        render(<BreakEvenChart b2b={mockB2bData} uop={mockUopData} results={{}} />);

        await waitFor(() => {
            expect(screen.queryByTestId('mock-line-chart')).not.toBeInTheDocument();
        });
        expect(await screen.findByText('no_data')).toBeInTheDocument();
    });
});
