// Design System Components
export { default as Button } from '../Button';
export { default as LoadingSkeleton } from '../LoadingSkeleton';
export { default as ThemeToggle } from '../ThemeToggle';
export { default as Card } from './Card';
export { default as Input } from './Input';
export { default as Badge } from './Badge';

// Design System Tokens Documentation
export const DesignTokens = {
  colors: {
    primary: 'var(--interactive-primary)',
    secondary: 'var(--interactive-secondary)',
    success: 'var(--brand-success)',
    warning: 'var(--brand-warning)',
    error: 'var(--brand-error)',
    background: {
      primary: 'var(--bg-primary)',
      surface: 'var(--bg-surface)',
      elevated: 'var(--bg-elevated)'
    },
    text: {
      primary: 'var(--text-primary)',
      secondary: 'var(--text-secondary)',
      muted: 'var(--text-muted)'
    }
  },
  spacing: {
    xs: 'var(--spacing-xs)',
    sm: 'var(--spacing-sm)', 
    md: 'var(--spacing-md)',
    lg: 'var(--spacing-lg)',
    xl: 'var(--spacing-xl)'
  },
  radius: {
    sm: 'var(--radius-sm)',
    md: 'var(--radius-md)',
    lg: 'var(--radius-lg)',
    xl: 'var(--radius-xl)',
    full: 'var(--radius-full)'
  },
  shadows: {
    sm: 'var(--shadow-sm)',
    md: 'var(--shadow-md)',
    lg: 'var(--shadow-lg)',
    xl: 'var(--shadow-xl)',
    glow: 'var(--shadow-glow)'
  },
  typography: {
    xs: 'var(--font-size-xs)',
    sm: 'var(--font-size-sm)',
    base: 'var(--font-size-base)',
    lg: 'var(--font-size-lg)',
    xl: 'var(--font-size-xl)',
    '2xl': 'var(--font-size-2xl)',
    '3xl': 'var(--font-size-3xl)'
  }
};
