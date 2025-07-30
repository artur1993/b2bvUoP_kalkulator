import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SensitivityChart from './SensitivityChart';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../i18n';
import * as api from '../services/api';

jest.mock('../services/api');

const mockB2bData = { faktura_miesieczna: 10000 };
const mockUopData = { wynagrodzenie_brutto: 8000 };

describe('SensitivityChart', () => {
    test('renders loading state initially and then the chart', async () => {
        api.calculateSensitivityAnalysis.mockResolvedValue([
            { parameter: 'koszty_firmowe_miesieczne', impact: 5000 },
            { parameter: 'urlop_dni', impact: -2000 },
        ]);

        render(
            <I18nextProvider i18n={i18n}>
                <SensitivityChart b2b={mockB2bData} uop={mockUopData} />
            </I18nextProvider>
        );

        expect(screen.getByText(/loading/i)).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(/Sensitivity Analysis/i)).toBeInTheDocument();
        });
    });

    test('shows no data message if api returns empty array', async () => {
        api.calculateSensitivityAnalysis.mockResolvedValue([]);

        render(
            <I18nextProvider i18n={i18n}>
                <SensitivityChart b2b={mockB2bData} uop={mockUopData} />
            </I18nextProvider>
        );

        await waitFor(() => {
            expect(screen.getByText(/no_data/i)).toBeInTheDocument();
        });
    });
});
