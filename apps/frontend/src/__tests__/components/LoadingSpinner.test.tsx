import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders the loading spinner', () => {
    render(<LoadingSpinner />);
    // LoadingSpinner uses Loader2 icon from lucide-react
    const spinner = screen.getByRole('img', { hidden: true }) || document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('displays custom text when provided', () => {
    render(<LoadingSpinner text="Custom loading message" />);
    expect(screen.getByText('Custom loading message')).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector('.w-12');
    expect(spinner).toBeInTheDocument();
  });
});

