import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, useTheme } from '../ThemeContext';

// Test component that uses theme context
const TestComponent = () => {
  const { isDarkMode, toggleTheme } = useTheme();
  
  return (
    <div>
      <span data-testid="theme-status">{isDarkMode ? 'dark' : 'light'}</span>
      <button onClick={toggleTheme} data-testid="toggle-button">
        Toggle Theme
      </button>
    </div>
  );
};

const ThemeProviderWrapper = ({ children, ...props }) => (
  <ThemeProvider {...props}>{children}</ThemeProvider>
);

describe('ThemeContext', () => {
  beforeEach(() => {
    localStorage.clear();
    // Mock document.documentElement and body
    Object.defineProperty(document, 'documentElement', {
      value: {
        classList: {
          add: jest.fn(),
          remove: jest.fn(),
        },
        setAttribute: jest.fn(),
      },
      writable: true,
    });
    
    Object.defineProperty(document, 'body', {
      value: {
        style: {},
      },
      writable: true,
    });
  });

  test('provides default dark mode', () => {
    render(
      <ThemeProviderWrapper>
        <TestComponent />
      </ThemeProviderWrapper>
    );
    
    expect(screen.getByTestId('theme-status')).toHaveTextContent('dark');
  });

  test('respects localStorage theme preference', () => {
    localStorage.setItem('theme', 'light');
    
    render(
      <ThemeProviderWrapper>
        <TestComponent />
      </ThemeProviderWrapper>
    );
    
    expect(screen.getByTestId('theme-status')).toHaveTextContent('light');
  });

  test('toggles theme correctly', () => {
    render(
      <ThemeProviderWrapper>
        <TestComponent />
      </ThemeProviderWrapper>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    const themeStatus = screen.getByTestId('theme-status');
    
    expect(themeStatus).toHaveTextContent('dark');
    
    fireEvent.click(toggleButton);
    expect(themeStatus).toHaveTextContent('light');
    
    fireEvent.click(toggleButton);
    expect(themeStatus).toHaveTextContent('dark');
  });

  test('persists theme changes to localStorage', () => {
    render(
      <ThemeProviderWrapper>
        <TestComponent />
      </ThemeProviderWrapper>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    
    fireEvent.click(toggleButton);
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
    
    fireEvent.click(toggleButton);
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  test('applies correct DOM classes and attributes', () => {
    render(
      <ThemeProviderWrapper>
        <TestComponent />
      </ThemeProviderWrapper>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    
    // Check dark mode (default)
    expect(document.documentElement.classList.add).toHaveBeenCalledWith('dark');
    expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
    
    // Toggle to light mode
    fireEvent.click(toggleButton);
    expect(document.documentElement.classList.remove).toHaveBeenCalledWith('dark');
    expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
  });
});
