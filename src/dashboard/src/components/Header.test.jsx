import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import Header from './Header';
import React from 'react';
import i18n from '../i18n'; // Import the i18n configuration

describe('Header', () => {
  beforeEach(() => {
    // Reset i18n language before each test to ensure a clean state
    i18n.changeLanguage('en');
  });

  it('renders in default language (English) correctly', () => {
    render(<Header />);
    expect(screen.getByText('B2B vs UoP Calculator 2025')).toBeInTheDocument();
    expect(screen.getByText('Compare your earnings and choose the best option')).toBeInTheDocument();
  });

  it('changes language to Polish when PL button is clicked', async () => {
    render(<Header />);
    const plButton = screen.getByRole('button', { name: 'PL' });
    fireEvent.click(plButton);

    await waitFor(() => {
      expect(screen.getByText('Kalkulator B2B vs UoP 2025')).toBeInTheDocument();
      expect(screen.getByText('Porównaj swoje zarobki i wybierz najlepszą opcję')).toBeInTheDocument();
    });
  });

  it('changes language back to English when EN button is clicked', async () => {
    render(<Header />);
    const plButton = screen.getByRole('button', { name: 'PL' });
    fireEvent.click(plButton);

    await waitFor(() => {
      expect(screen.getByText('Kalkulator B2B vs UoP 2025')).toBeInTheDocument();
    });

    const enButton = screen.getByRole('button', { name: 'EN' });
    fireEvent.click(enButton);

    await waitFor(() => {
      expect(screen.getByText('B2B vs UoP Calculator 2025')).toBeInTheDocument();
      expect(screen.getByText('Compare your earnings and choose the best option')).toBeInTheDocument();
    });
  });

  it('applies correct styles to active language button', async () => {
    render(<Header />);
    const plButton = screen.getByRole('button', { name: 'PL' });
    const enButton = screen.getByRole('button', { name: 'EN' });

    // Initially EN should be active
    expect(enButton).toHaveClass('bg-primary text-white');
    expect(plButton).not.toHaveClass('bg-primary text-white');

    fireEvent.click(plButton);

    await waitFor(() => {
      expect(plButton).toHaveClass('bg-primary text-white');
      expect(enButton).not.toHaveClass('bg-primary text-white');
    });

    fireEvent.click(enButton);

    await waitFor(() => {
      expect(enButton).toHaveClass('bg-primary text-white');
      expect(plButton).not.toHaveClass('bg-primary text-white');
    });
  });
});