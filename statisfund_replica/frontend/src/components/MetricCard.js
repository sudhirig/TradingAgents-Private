import React from 'react';
import { motion } from 'framer-motion';

const MetricCard = ({ label, value, change, icon, color = 'purple' }) => {
  const isPositive = change && change > 0;
  const gradients = {
    purple: 'from-purple-400 to-pink-400',
    green: 'from-green-400 to-teal-400',
    blue: 'from-blue-400 to-cyan-400',
    orange: 'from-orange-400 to-red-400'
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.05 }}
      className="metric-card"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="metric-label">{label}</span>
        {icon && <span className="text-2xl opacity-50">{icon}</span>}
      </div>
      <div className={`metric-value bg-gradient-to-r ${gradients[color]} bg-clip-text text-transparent`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {change !== undefined && (
        <div className={`metric-change ${isPositive ? 'positive' : 'negative'}`}>
          <span>{isPositive ? '↑' : '↓'}</span>
          <span className="ml-1">{Math.abs(change).toFixed(2)}%</span>
        </div>
      )}
    </motion.div>
  );
};

export default MetricCard;
