import React from 'react';
import { motion } from 'framer-motion';

const ModernCard = ({ 
  children, 
  className = '', 
  gradient = false,
  glow = false,
  title,
  subtitle,
  icon,
  action
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`glass-card ${glow ? 'glow-effect' : ''} ${className}`}
      whileHover={{ scale: 1.02 }}
    >
      {(title || subtitle || icon || action) && (
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            {icon && (
              <div className="text-2xl">{icon}</div>
            )}
            <div>
              {title && (
                <h3 className="text-xl font-bold text-white mb-1">
                  {gradient ? (
                    <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                      {title}
                    </span>
                  ) : title}
                </h3>
              )}
              {subtitle && (
                <p className="text-gray-400 text-sm">{subtitle}</p>
              )}
            </div>
          </div>
          {action && (
            <div>{action}</div>
          )}
        </div>
      )}
      {children}
    </motion.div>
  );
};

export default ModernCard;
