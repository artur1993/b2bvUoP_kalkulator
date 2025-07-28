import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Header from './Header';
import React from 'react';

describe('Header', () => {
  it('renders the header with correct title and description', () => {
    render(<Header />);
    expect(screen.getByText(/B2B vs UoP Calculator 2025/i)).toBeInTheDocument();
    expect(screen.getByText(/Porównaj swoje zarobki i wybierz najlepszą opcję/i)).toBeInTheDocument();
  });
});
