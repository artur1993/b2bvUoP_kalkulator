import { render, screen, cleanup } from '@testing-library/react';
import { describe, it, expect, afterEach } from 'vitest';
import Alert from './Alert';
import React from 'react';

describe('Alert', () => {
  afterEach(() => {
    cleanup(); // Cleans up the DOM after each test to prevent multiple alerts
  });

  it('renders a success alert with the correct message', () => {
    render(<Alert message="Success message" type="success" />);
    const alertElement = screen.getByRole('alert');
    expect(alertElement).toBeInTheDocument();
    expect(alertElement).toHaveTextContent('Success message');
    expect(alertElement).toHaveClass('bg-green-100');
    expect(alertElement).toHaveClass('border-green-400');
    expect(alertElement).toHaveClass('text-green-700');
  });

  it('renders an error alert with the correct message', () => {
    render(<Alert message="Error message" type="error" />);
    const alertElement = screen.getByRole('alert');
    expect(alertElement).toBeInTheDocument();
    expect(alertElement).toHaveTextContent('Error message');
    expect(alertElement).toHaveClass('bg-red-100');
    expect(alertElement).toHaveClass('border-red-400');
    expect(alertElement).toHaveClass('text-red-700');
  });

  it('renders a warning alert with the correct message', () => {
    render(<Alert message="Warning message" type="warning" />);
    const alertElement = screen.getByRole('alert');
    expect(alertElement).toBeInTheDocument();
    expect(alertElement).toHaveTextContent('Warning message');
    expect(alertElement).toHaveClass('bg-yellow-100');
    expect(alertElement).toHaveClass('border-yellow-400');
    expect(alertElement).toHaveClass('text-yellow-700');
  });

  it('renders a default info alert if type is not specified or unknown', () => {
    render(<Alert message="Info message" />);
    const alertElement = screen.getByRole('alert');
    expect(alertElement).toBeInTheDocument();
    expect(alertElement).toHaveTextContent('Info message');
    expect(alertElement).toHaveClass('bg-blue-100');
    expect(alertElement).toHaveClass('border-blue-400');
    expect(alertElement).toHaveClass('text-blue-700');

    cleanup(); // Clean up previous render

    render(<Alert message="Unknown type" type="unknown" />);
    const alertElementUnknown = screen.getByRole('alert');
    expect(alertElementUnknown).toBeInTheDocument();
    expect(alertElementUnknown).toHaveTextContent('Unknown type');
    expect(alertElementUnknown).toHaveClass('bg-blue-100');
    expect(alertElementUnknown).toHaveClass('border-blue-400');
    expect(alertElementUnknown).toHaveClass('text-blue-700');
  });

  it('does not render if message is null or empty', () => {
    const { container } = render(<Alert message={null} type="success" />);
    expect(container.firstChild).toBeNull();

    const { container: emptyContainer } = render(<Alert message="" type="success" />);
    expect(emptyContainer.firstChild).toBeNull();
  });
});