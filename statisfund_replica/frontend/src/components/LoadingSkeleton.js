import React from 'react';

const LoadingSkeleton = ({ 
  type = 'text', 
  lines = 1, 
  width = '100%', 
  height = '1em',
  className = '' 
}) => {
  const baseClasses = 'skeleton-base';
  
  if (type === 'text') {
    return (
      <div className={`skeleton-text ${className}`}>
        {Array.from({ length: lines }, (_, index) => (
          <div 
            key={index}
            className={baseClasses}
            style={{ 
              width: index === lines - 1 ? '70%' : width,
              height: height
            }}
          />
        ))}
      </div>
    );
  }

  if (type === 'card') {
    return (
      <div className={`skeleton-card ${className}`}>
        <div className="skeleton-header">
          <div className={`${baseClasses} skeleton-avatar`} />
          <div className="skeleton-title">
            <div className={`${baseClasses} skeleton-title-line`} />
            <div className={`${baseClasses} skeleton-subtitle-line`} />
          </div>
        </div>
        <div className="skeleton-content">
          {Array.from({ length: 3 }, (_, index) => (
            <div key={index} className={`${baseClasses} skeleton-content-line`} />
          ))}
        </div>
      </div>
    );
  }

  if (type === 'chart') {
    return (
      <div className={`skeleton-chart ${className}`}>
        <div className={`${baseClasses} skeleton-chart-header`} />
        <div className="skeleton-chart-body">
          <div className="skeleton-chart-bars">
            {Array.from({ length: 8 }, (_, index) => (
              <div 
                key={index}
                className={`${baseClasses} skeleton-bar`}
                style={{ height: `${30 + Math.random() * 40}%` }}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`${baseClasses} ${className}`}
      style={{ width, height }}
    />
  );
};

export default LoadingSkeleton;
