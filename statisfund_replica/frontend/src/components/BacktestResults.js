import React from 'react';
import { motion } from 'framer-motion';
import ModernCard from './ModernCard';
import MetricCard from './MetricCard';
import ChartComponent from './ChartComponent';

const BacktestResults = ({ results }) => {
  if (!results) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-400">No backtest results available</p>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (!value && value !== 0) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0.00%';
    const absValue = Math.abs(value);
    const sign = value >= 0 ? '+' : '-';
    return `${sign}${absValue.toFixed(2)}%`;
  };

  const formatMetric = (value, suffix = '') => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    return `${value}${suffix}`;
  };

  // Handle the new API response format from backend improvements
  const performance = results.performance_metrics || results.results?.performance_metrics || {};
  const summary = results.summary || results.backtest_results || {};
  const enhancedMetrics = results.enhanced_metrics || {};

  const isAdvancedBacktest = performance && 
    (performance.sortino_ratio !== undefined || 
     performance.calmar_ratio !== undefined ||
     performance.calmar !== undefined ||
     performance.sortino !== undefined);

  // Prepare chart data from results
  const returnsData = results.returns_over_time ? {
    labels: Object.keys(results.returns_over_time),
    datasets: [{
      label: 'Cumulative Returns',
      data: Object.values(results.returns_over_time),
      borderColor: 'rgba(102, 126, 234, 1)',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true
    }]
  } : null;

  const portfolioData = results.portfolio_value ? {
    labels: Array.from({length: results.portfolio_value.length}, (_, i) => `Day ${i+1}`),
    datasets: [{
      label: 'Portfolio Value',
      data: results.portfolio_value,
      borderColor: 'rgba(34, 197, 94, 1)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true
    }]
  } : null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <h3 className="text-2xl font-bold text-white mb-6">📊 Backtest Results</h3>
      <p className="text-sm text-gray-400 mb-6">
        📊 Real market data via yfinance + Alpha Vantage fallback - No synthetic data used.
      </p>

      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard 
          label="Total Return" 
          value={formatPercent((performance.total_return || summary.total_return || 0) * 100)}
          change={(performance.total_return || summary.total_return || 0) * 100}
          icon="📈"
          color="green"
        />
        <MetricCard 
          label="Sharpe Ratio" 
          value={(performance.sharpe_ratio || 0).toFixed(2)}
          icon="⚡"
          color="purple"
        />
        <MetricCard 
          label="Max Drawdown" 
          value={formatPercent(Math.abs(performance.max_drawdown || 0) * 100)}
          change={-(Math.abs(performance.max_drawdown || 0) * 100)}
          icon="📉"
          color="orange"
        />
        <MetricCard 
          label="Win Rate" 
          value={formatPercent((performance.win_rate || 0) * 100)}
          icon="🎯"
          color="blue"
        />
      </div>

      {/* Charts Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {returnsData && (
          <ModernCard 
            title="Returns Over Time" 
            icon="📊"
            gradient={true}
          >
            <ChartComponent type="line" data={returnsData} height={250} />
          </ModernCard>
        )}
        
        {portfolioData && (
          <ModernCard 
            title="Portfolio Value" 
            icon="💰"
            gradient={true}
          >
            <ChartComponent type="line" data={portfolioData} height={250} />
          </ModernCard>
        )}
      </div>

      {/* Trade Statistics */}
      <ModernCard 
        title="Trade Statistics" 
        subtitle="Detailed trading performance breakdown"
        icon="📊"
      >
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="text-center p-4 glass-card">
            <div className="text-3xl font-bold text-purple-400">{performance.total_trades || 0}</div>
            <div className="text-sm text-gray-400 mt-1">Total Trades</div>
          </div>
          <div className="text-center p-4 glass-card">
            <div className="text-3xl font-bold text-green-400">{performance.winning_trades || 0}</div>
            <div className="text-sm text-gray-400 mt-1">Winning</div>
          </div>
          <div className="text-center p-4 glass-card">
            <div className="text-3xl font-bold text-red-400">{performance.losing_trades || 0}</div>
            <div className="text-sm text-gray-400 mt-1">Losing</div>
          </div>
          <div className="text-center p-4 glass-card">
            <div className="text-2xl font-bold text-green-400">{formatCurrency(performance.avg_win || 0)}</div>
            <div className="text-sm text-gray-400 mt-1">Avg Win</div>
          </div>
          <div className="text-center p-4 glass-card">
            <div className="text-2xl font-bold text-red-400">{formatCurrency(Math.abs(performance.avg_loss || 0))}</div>
            <div className="text-sm text-gray-400 mt-1">Avg Loss</div>
          </div>
          <div className="text-center p-4 glass-card">
            <div className="text-2xl font-bold text-purple-400">{(performance.profit_factor || 0).toFixed(2)}</div>
            <div className="text-sm text-gray-400 mt-1">Profit Factor</div>
          </div>
        </div>
      </ModernCard>

      {/* Portfolio Summary */}
      <ModernCard 
        title="Portfolio Summary" 
        icon="💼"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-400">Initial Cash</div>
            <div className="text-xl font-bold text-white mt-1">{formatCurrency(summary.initial_value || 10000)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Final Value</div>
            <div className="text-xl font-bold text-white mt-1">{formatCurrency(summary.final_value || 10000)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Symbol</div>
            <div className="text-xl font-bold text-white mt-1">{summary.symbol_used || 'N/A'}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Data Points</div>
            <div className="text-xl font-bold text-white mt-1">{summary.data_points || 0}</div>
          </div>
        </div>
      </ModernCard>

      {/* Advanced Metrics */}
      {isAdvancedBacktest && performance && (
        <ModernCard 
          title="Advanced Metrics" 
          subtitle="Professional-grade performance indicators"
          icon="🎯"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard 
              label="Sortino Ratio" 
              value={(performance.sortino_ratio || 0).toFixed(2)}
              icon="📊"
              color="purple"
            />
            <MetricCard 
              label="Calmar Ratio" 
              value={(performance.calmar_ratio || 0).toFixed(2)}
              icon="📈"
              color="blue"
            />
            <MetricCard 
              label="SQN" 
              value={(performance.sqn || 0).toFixed(2)}
              icon="⚙️"
              color="green"
            />
            <MetricCard 
              label="VWR" 
              value={(performance.vwr || 0).toFixed(2)}
              icon="💎"
              color="orange"
            />
          </div>
        </ModernCard>
      )}

      {/* Data Source Info */}
      <ModernCard 
        title="Data Source Information" 
        icon="📡"
      >
        <div className="flex items-center justify-between p-4 glass-card">
          <div>
            <div className="text-sm text-gray-400 mb-1">Real Market Data</div>
            <div className="text-lg font-semibold text-white">
              <span className="text-green-400">Primary:</span> Yahoo Finance • 
              <span className="text-blue-400 ml-2">Fallback:</span> Alpha Vantage
            </div>
          </div>
          <div className="text-center">
            {performance.total_return >= 0 ? (
              <span className="text-2xl">✅</span>
            ) : (
              <span className="text-2xl">⚠️</span>
            )}
            <div className="text-sm text-gray-400 mt-1">
              {performance.total_return >= 0 ? 'Profitable' : 'Loss-making'}
            </div>
          </div>
        </div>
      </ModernCard>
    </motion.div>
  );
};

export default BacktestResults;
