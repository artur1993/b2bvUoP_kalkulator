import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import InsuranceConfigurator from './InsuranceConfigurator';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('InsuranceConfigurator', () => {
  const mockSetInsuranceConfig = vi.fn();

  const initialConfig = {
    enabled: true,
    activeProfile: 'standard',
    selections: {
      income_protection: { enabled: true, level: 'uop_equivalent' },
      professional_liability: { enabled: true, level: 'standard' },
      private_health: { enabled: true, level: 'standard' },
      equipment: { enabled: true, level: 'standard' },
      zus_voluntary: { enabled: true, level: 'enabled' },
      legal_protection: { enabled: true, level: 'basic' },
      cyber_insurance: { enabled: false, level: 'basic' },
    },
  };

  beforeEach(() => {
    render(
      <I18nextProvider i18n={i18n}>
        <InsuranceConfigurator 
          insuranceConfig={initialConfig} 
          setInsuranceConfig={mockSetInsuranceConfig} 
          b2bMonthlyInvoice={10000} 
        />
      </I18nextProvider>
    );
  });

  test('renders with standard profile and calculates initial cost', async () => {
    expect(await screen.findByText('B2B Insurance Configurator')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /standard/i })).toHaveClass('bg-primary');
    expect(screen.getByText(/680.97/)).toBeInTheDocument();
  });

  test('displays individual module costs and tooltips', async () => {
    // Check for professional liability cost
    const ocZawodowe = await screen.findByText('OC zawodowe');
    const ocCost = ocZawodowe.closest('.module-header').querySelector('.module-cost');
    expect(ocCost).toHaveTextContent('66.67 zł/mies.');

    // Check that cyber insurance has no cost
    const cyberInsurance = await screen.findByText('Ubezpieczenie cyber');
    const cyberCost = cyberInsurance.closest('.module-header').querySelector('.module-cost');
    expect(cyberCost).toBeNull();

    // Check for tooltip
    const tooltipIcon = ocZawodowe.closest('.module-title-wrapper').querySelector('.info-tooltip');
    expect(tooltipIcon).toBeInTheDocument();
    expect(tooltipIcon).toHaveAttribute('data-tooltip-content');
  });

  test('updates module cost on interaction', async () => {
    const cyberInsuranceCheckbox = screen.getByLabelText('Ubezpieczenie cyber');
    fireEvent.click(cyberInsuranceCheckbox);
    expect(mockSetInsuranceConfig).toHaveBeenCalled();
  });

  test('switches to minimal profile and recalculates cost', () => {
    fireEvent.click(screen.getByRole('button', { name: /minimal/i }));
    expect(mockSetInsuranceConfig).toHaveBeenCalled();
  });

  test('switches to custom profile on manual change', () => {
    fireEvent.click(screen.getByLabelText(/OC zawodowe/i));
    expect(mockSetInsuranceConfig).toHaveBeenCalledWith(expect.any(Function));
  });
});