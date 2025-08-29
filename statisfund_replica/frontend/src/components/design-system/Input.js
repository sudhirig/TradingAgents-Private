import React, { forwardRef } from 'react';

const Input = forwardRef(({ 
  variant = 'default',
  size = 'md',
  error = false,
  success = false,
  leftIcon,
  rightIcon,
  label,
  helperText,
  className = '',
  ...props 
}, ref) => {
  const baseClasses = 'input-base';
  
  const variantClasses = {
    default: 'input-default',
    filled: 'input-filled',
    outline: 'input-outline'
  };
  
  const sizeClasses = {
    sm: 'input-sm',
    md: 'input-md',
    lg: 'input-lg'
  };

  const inputClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    error && 'input-error',
    success && 'input-success',
    leftIcon && 'input-with-left-icon',
    rightIcon && 'input-with-right-icon',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="input-wrapper">
      {label && (
        <label className="input-label" htmlFor={props.id}>
          {label}
        </label>
      )}
      <div className="input-container">
        {leftIcon && (
          <div className="input-icon input-icon-left">
            {leftIcon}
          </div>
        )}
        <input 
          ref={ref}
          className={inputClasses}
          aria-invalid={error}
          aria-describedby={helperText ? `${props.id}-helper` : undefined}
          {...props}
        />
        {rightIcon && (
          <div className="input-icon input-icon-right">
            {rightIcon}
          </div>
        )}
      </div>
      {helperText && (
        <div 
          id={`${props.id}-helper`}
          className={`input-helper ${error ? 'input-helper-error' : success ? 'input-helper-success' : ''}`}
        >
          {helperText}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
