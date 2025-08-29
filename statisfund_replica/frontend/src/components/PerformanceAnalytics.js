import React, { useState } from 'react';
import { motion } from 'framer-motion';

const PerformanceAnalytics = ({ backtestResults }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1Y');
  
  const timeframes = ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'All'];
  
  const mockMetrics = {
    totalReturn: 156.34,
    annualizedReturn: 42.67,
    sharpeRatio: 2.34,
    sortinoRatio: 3.12,
    calmarRatio: 1.89,
    maxDrawdown: -18.45,
    winRate: 62.5,
    profitFactor: 2.15,
    avgWin: 3.45,
    avgLoss: -1.23,
    bestTrade: 18.67,
    worstTrade: -8.34,
    totalTrades: 342,
    winningTrades: 214,
    losingTrades: 128,
    volatility: 15.67,
    beta: 1.12,
    alpha: 8.34,
    sqn: 3.45,
    vwr: 0.89
  };

  const [metrics] = useState(backtestResults?.performance_metrics || mockMetrics);

  const getColorForMetric = (value, type = 'default') => {
    if (type === 'return') {
      return value > 0 ? 'text-green-400' : 'text-red-400';
    } else if (type === 'ratio') {
      if (value > 2) return 'text-green-400';
      if (value > 1) return 'text-yellow-400';
      return 'text-red-400';
    }
    return 'text-white';
  };

  const formatPercentage = (value) => {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatCurrency = (value) => {
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-white mb-4">
          Performance Analytics
        </h1>
        <p className="text-gray-300">
          Comprehensive analysis of strategy performance and risk metrics
        </p>
      </motion.div>

      {/* Key Metrics Overview */}
      <div className="grid lg:grid-cols-4 gap-4 mb-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl p-4"
        >
          <div className="text-white/80 text-sm">Total Return</div>
          <div className="text-3xl font-bold text-white">
            {formatPercentage(metrics.totalReturn || backtestResults?.summary?.total_return || 0)}
          </div>
          <div className="text-white/60 text-xs mt-1">Since inception</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Sharpe Ratio</div>
          <div className={`text-3xl font-bold ${getColorForMetric(metrics.sharpeRatio || backtestResults?.performance_metrics?.sharpe_ratio || 0, 'ratio')}`}>
            {(metrics.sharpeRatio || backtestResults?.performance_metrics?.sharpe_ratio || 0).toFixed(2)}
          </div>
          <div className="text-gray-500 text-xs mt-1">Risk-adjusted return</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Max Drawdown</div>
          <div className="text-3xl font-bold text-red-400">
            {(metrics.maxDrawdown || backtestResults?.performance_metrics?.max_drawdown || 0).toFixed(2)}%
          </div>
          <div className="text-gray-500 text-xs mt-1">Worst peak-to-trough</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Win Rate</div>
          <div className={`text-3xl font-bold ${(metrics.winRate || backtestResults?.performance_metrics?.win_rate || 0) > 50 ? 'text-green-400' : 'text-orange-400'}`}>
            {(metrics.winRate || backtestResults?.performance_metrics?.win_rate || 0).toFixed(1)}%
          </div>
          <div className="text-gray-500 text-xs mt-1">{metrics.winningTrades || 0} / {metrics.totalTrades || backtestResults?.performance_metrics?.total_trades || 0} trades</div>
        </motion.div>
      </div>

      {/* Tabs and Content */}
      <div className="flex space-x-4 mb-6">
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'risk', label: 'Risk Analysis' },
          { id: 'trades', label: 'Trade Statistics' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
        {activeTab === 'overview' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Performance Overview</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/5 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Annualized Return</div>
                <div className={`text-2xl font-bold ${getColorForMetric(metrics.annualizedReturn, 'return')}`}>
                  {formatPercentage(metrics.annualizedReturn)}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Profit Factor</div>
                <div className={`text-2xl font-bold ${metrics.profitFactor > 1 ? 'text-green-400' : 'text-red-400'}`}>
                  {metrics.profitFactor.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'risk' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Risk Analysis</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Sortino Ratio</span>
                  <span className={`font-semibold ${getColorForMetric(metrics.sortinoRatio, 'ratio')}`}>
                    {metrics.sortinoRatio.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Beta</span>
                  <span className="text-white font-semibold">{metrics.beta.toFixed(2)}</span>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Alpha</span>
                  <span className={`font-semibold ${getColorForMetric(metrics.alpha, 'return')}`}>
                    {formatPercentage(metrics.alpha)}
                  </span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Volatility</span>
                  <span className="text-white font-semibold">{metrics.volatility.toFixed(2)}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trades' && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6">Trade Statistics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-900/20 rounded-lg p-4 border border-green-500/20">
                <div className="text-green-400 font-semibold mb-2">Winning Trades</div>
                <div className="text-3xl font-bold text-white">{metrics.winningTrades}</div>
                <div className="text-gray-400 text-sm mt-1">Avg Win: {formatPercentage(metrics.avgWin)}</div>
              </div>
              <div className="bg-red-900/20 rounded-lg p-4 border border-red-500/20">
                <div className="text-red-400 font-semibold mb-2">Losing Trades</div>
                <div className="text-3xl font-bold text-white">{metrics.losingTrades}</div>
                <div className="text-gray-400 text-sm mt-1">Avg Loss: {formatPercentage(metrics.avgLoss)}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceAnalytics;
