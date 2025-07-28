import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import SkeletonLoader from './SkeletonLoader';
import React from 'react';

describe('SkeletonLoader', () => {
  it('renders the skeleton loader component', () => {
    render(<SkeletonLoader />);
    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
    expect(screen.getByTestId('skeleton-loader')).toHaveClass('animate-pulse');
  });
});
