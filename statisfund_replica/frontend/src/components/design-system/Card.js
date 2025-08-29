import React from 'react';

const Card = ({ 
  variant = 'default',
  size = 'md',
  padding = true,
  border = true,
  shadow = true,
  hover = false,
  children,
  className = '',
  ...props 
}) => {
  const baseClasses = 'card-base';
  
  const variantClasses = {
    default: 'card-default',
    glass: 'card-glass',
    elevated: 'card-elevated',
    outline: 'card-outline'
  };
  
  const sizeClasses = {
    sm: 'card-sm',
    md: 'card-md',
    lg: 'card-lg'
  };

  const cardClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    !padding && 'card-no-padding',
    !border && 'card-no-border',
    !shadow && 'card-no-shadow',
    hover && 'card-hover',
    className
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={cardClasses}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
