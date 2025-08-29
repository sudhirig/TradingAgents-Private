import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Card, Input, Badge } from '../design-system';

describe('Design System Components', () => {
  describe('Card Component', () => {
    test('renders with default props', () => {
      render(<Card>Card Content</Card>);
      const card = screen.getByText('Card Content');
      
      expect(card).toHaveClass('card-base', 'card-default', 'card-md');
    });

    test('applies variant classes correctly', () => {
      const { rerender } = render(<Card variant="glass">Glass Card</Card>);
      expect(screen.getByText('Glass Card')).toHaveClass('card-glass');
      
      rerender(<Card variant="elevated">Elevated Card</Card>);
      expect(screen.getByText('Elevated Card')).toHaveClass('card-elevated');
    });

    test('applies hover class when hover prop is true', () => {
      render(<Card hover>Hover Card</Card>);
      expect(screen.getByText('Hover Card')).toHaveClass('card-hover');
    });
  });

  describe('Input Component', () => {
    test('renders input with label', () => {
      render(<Input label="Test Label" id="test-input" />);
      
      expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
      expect(screen.getByText('Test Label')).toHaveClass('input-label');
    });

    test('shows helper text', () => {
      render(<Input helperText="Helper text" id="test-input" />);
      
      expect(screen.getByText('Helper text')).toHaveClass('input-helper');
    });

    test('applies error state', () => {
      render(<Input error helperText="Error message" id="test-input" />);
      const input = screen.getByRole('textbox');
      
      expect(input).toHaveClass('input-error');
      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText('Error message')).toHaveClass('input-helper-error');
    });

    test('applies success state', () => {
      render(<Input success helperText="Success message" id="test-input" />);
      const input = screen.getByRole('textbox');
      
      expect(input).toHaveClass('input-success');
      expect(screen.getByText('Success message')).toHaveClass('input-helper-success');
    });
  });

  describe('Badge Component', () => {
    test('renders with correct classes', () => {
      render(<Badge>Default Badge</Badge>);
      const badge = screen.getByText('Default Badge');
      
      expect(badge).toHaveClass('badge-base', 'badge-default', 'badge-md');
    });

    test('applies variant classes', () => {
      const { rerender } = render(<Badge variant="success">Success</Badge>);
      expect(screen.getByText('Success')).toHaveClass('badge-success');
      
      rerender(<Badge variant="error">Error</Badge>);
      expect(screen.getByText('Error')).toHaveClass('badge-error');
    });

    test('applies size classes', () => {
      const { rerender } = render(<Badge size="sm">Small</Badge>);
      expect(screen.getByText('Small')).toHaveClass('badge-sm');
      
      rerender(<Badge size="lg">Large</Badge>);
      expect(screen.getByText('Large')).toHaveClass('badge-lg');
    });
  });
});
