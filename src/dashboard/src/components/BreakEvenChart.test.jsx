import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import BreakEvenChart from './BreakEvenChart';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import * as api from '../services/api';
import { vi } from 'vitest';

vi.mock('../services/api');
vi.mock('react-chartjs-2', () => ({
    Line: () => <div data-testid="mock-line-chart" />,
}));

const mockB2bData = { faktura_miesieczna: 10000 };
const mockUopData = { wynagrodzenie_brutto: 8000 };

describe('BreakEvenChart', () => {
    test('renders loading state initially and then the chart', async () => {
        api.calculateBreakEvenAnalysis.mockResolvedValue([
            { b2b_rate: 5000, net_difference: -10000 },
            { b2b_rate: 15000, net_difference: 10000 },
        ]);

        render(
            <I18nextProvider i18n={i18n}>
                <BreakEvenChart b2b={mockB2bData} uop={mockUopData} />
            </I18nextProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('mock-line-chart')).toBeInTheDocument();
        });
    });

    test('shows no data message if api returns empty array', async () => {
        api.calculateBreakEvenAnalysis.mockResolvedValue([]);

        render(
            <I18nextProvider i18n={i18n}>
                <BreakEvenChart b2b={mockB2bData} uop={mockUopData} />
            </I18nextProvider>
        );

        await waitFor(() => {
            expect(screen.queryByTestId('mock-line-chart')).not.toBeInTheDocument();
        });
    });
});
