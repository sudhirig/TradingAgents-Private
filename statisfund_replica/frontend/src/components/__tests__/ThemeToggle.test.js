import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ThemeToggle from '../ThemeToggle';

// Mock the useTheme hook
const mockToggleTheme = jest.fn();
const mockUseTheme = jest.fn();

jest.mock('../../context/ThemeContext', () => ({
  useTheme: () => mockUseTheme()
}));

beforeEach(() => {
  mockToggleTheme.mockClear();
  mockUseTheme.mockClear();
});

describe('ThemeToggle Component', () => {
  test('renders theme toggle button in dark mode', () => {
    mockUseTheme.mockReturnValue({
      isDarkMode: true,
      toggleTheme: mockToggleTheme
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
    expect(button).toHaveTextContent('🌙');
  });

  test('renders theme toggle button in light mode', () => {
    mockUseTheme.mockReturnValue({
      isDarkMode: false,
      toggleTheme: mockToggleTheme
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    expect(button).toHaveTextContent('☀️');
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  test('calls toggleTheme on click', () => {
    mockUseTheme.mockReturnValue({
      isDarkMode: true,
      toggleTheme: mockToggleTheme
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  test('has proper accessibility attributes', () => {
    mockUseTheme.mockReturnValue({
      isDarkMode: true,
      toggleTheme: mockToggleTheme
    });

    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    expect(button).toHaveAttribute('title', 'Switch to light mode');
    expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
  });
});
