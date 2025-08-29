import React from 'react';

const Badge = ({ 
  variant = 'default',
  size = 'md',
  children,
  className = '',
  ...props 
}) => {
  const baseClasses = 'badge-base';
  
  const variantClasses = {
    default: 'badge-default',
    primary: 'badge-primary',
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    outline: 'badge-outline'
  };
  
  const sizeClasses = {
    sm: 'badge-sm',
    md: 'badge-md',
    lg: 'badge-lg'
  };

  const badgeClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className
  ].filter(Boolean).join(' ');

  return (
    <span 
      className={badgeClasses}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
