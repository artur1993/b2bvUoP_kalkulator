import React from 'react';
import { render, screen } from '@testing-library/react';
import WaterfallChart from './WaterfallChart';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { vi } from 'vitest';

vi.mock('react-chartjs-2', () => ({
    Bar: () => <div data-testid="mock-waterfall-chart" />,
}));

const mockResults = {
    b2b_results: {
        steps: {
            'Przychód roczny': 120000,
            'Koszty firmowe roczne': 12000,
            skladki_zus_emerytalna: 5000,
            skladki_zus_rentowa: 2000,
            skladki_zus_chorobowa: 1000,
            skladka_zdrowotna: 4000,
            podatek_prog_1: 8000,
            podatek_prog_2: 2000,
            'Utracony przychód': 5000
        }
    },
    uop_results: {
        steps: {
            'Roczne wynagrodzenie brutto': 100000,
            skladki_zus_emerytalna: 9760,
            skladki_zus_rentowa: 1500,
            skladki_zus_chorobowa: 2450,
            skladka_zdrowotna: 9000,
            podatek_prog_1: 10000,
            podatek_prog_2: 0
        }
    }
};

describe('WaterfallChart', () => {
    test('renders without crashing', () => {
        render(
            <I18nextProvider i18n={i18n}>
                <WaterfallChart results={mockResults} />
            </I18nextProvider>
        );
        expect(screen.getByTestId('mock-waterfall-chart')).toBeInTheDocument();
    });

    test('displays loading state when no results are provided', () => {
        render(
            <I18nextProvider i18n={i18n}>
                <WaterfallChart results={null} />
            </I18nextProvider>
        );
        expect(screen.queryByTestId('mock-waterfall-chart')).not.toBeInTheDocument();
    });
});
