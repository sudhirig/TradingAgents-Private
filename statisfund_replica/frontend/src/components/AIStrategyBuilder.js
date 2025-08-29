import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ModernCard from './ModernCard';
import MetricCard from './MetricCard';
import ChartComponent from './ChartComponent';

const AIStrategyBuilder = ({
  onIndicatorSelect,
  onOrderSettingsChange,
  onRiskSettingsChange,
  onGenerate,
  isLoading,
  code,
  onBacktest,
  onAdvancedBacktest,
  backtestResults,
  backtestError
}) => {
  const [strategyPrompt, setStrategyPrompt] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('momentum');
  const [activeTab, setActiveTab] = useState('prompt');
  const [advancedSettings, setAdvancedSettings] = useState({
    timeframe: '1h',
    symbols: ['AAPL', 'MSFT', 'GOOGL'],
    riskPerTrade: 2,
    maxPositions: 3,
    stopLoss: 5,
    takeProfit: 10
  });

  const strategyTemplates = [
    { id: 'momentum', name: 'Momentum Strategy', icon: '🚀', description: 'Trend following with RSI & MACD' },
    { id: 'meanreversion', name: 'Mean Reversion', icon: '🔄', description: 'Bollinger Bands & RSI oversold' },
    { id: 'breakout', name: 'Breakout Trading', icon: '📈', description: 'Volume & price breakout detection' },
    { id: 'pairs', name: 'Pairs Trading', icon: '👥', description: 'Statistical arbitrage strategy' },
    { id: 'ml', name: 'ML Prediction', icon: '🤖', description: 'Machine learning based signals' },
    { id: 'custom', name: 'Custom Strategy', icon: '⚙️', description: 'Build from scratch with AI' }
  ];

  const tabs = [
    { id: 'prompt', label: 'Strategy Prompt' },
    { id: 'indicators', label: 'Indicators' },
    { id: 'risk', label: 'Risk Management' }
  ];

  const handleGenerate = async () => {
    const formData = {
      description: strategyPrompt, // Updated to match backend API
      template: selectedTemplate,
      symbols: advancedSettings.symbols,
      start_date: "2023-01-01",
      end_date: "2023-12-31",
      ...advancedSettings
    };
    onGenerate(formData);
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            🤖 AI Strategy Builder
          </h1>
          <div className="text-sm text-gray-400">
            GPT-4 Powered
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed mb-6">
          Use natural language to describe your trading strategy and let AI generate professional code
        </p>
      </motion.div>

      {/* Strategy Templates */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4 text-white">Strategy Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {strategyTemplates.map((template) => (
            <motion.div
              key={template.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedTemplate(template.id)}
              className={`template-card ${
                selectedTemplate === template.id ? 'selected' : ''
              }`}
            >
              <div className="text-4xl mb-4">{template.icon}</div>
              <h4 className="text-xl font-bold mb-2 text-white">{template.name}</h4>
              <p className="text-sm text-gray-400">{template.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Panel - Configuration */}
        <div>
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            {/* Tabs */}
            <div className="tab-nav mb-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'prompt' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Strategy Description</label>
                  <textarea
                    value={strategyPrompt}
                    onChange={(e) => setStrategyPrompt(e.target.value)}
                    className="input-modern h-32"
                    placeholder="Describe your trading strategy in natural language..."
                  />
                </div>
                <ModernCard className="p-6">
                  <div className="flex items-center mb-2">
                    <span className="text-purple-400 mr-2">💡</span>
                    <span className="text-sm font-semibold text-purple-300">AI Suggestions</span>
                  </div>
                  <ul className="text-xs text-gray-300 space-y-1">
                    <li>• Include entry and exit conditions</li>
                    <li>• Specify risk management rules</li>
                    <li>• Mention preferred indicators</li>
                    <li>• Define position sizing logic</li>
                  </ul>
                </ModernCard>
              </div>
            )}

            {activeTab === 'indicators' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  {['SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic', 'ATR', 'Volume'].map((indicator) => (
                    <label key={indicator} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        className="rounded text-purple-500 focus:ring-purple-500"
                        onChange={(e) => {
                          if (e.target.checked) {
                            onIndicatorSelect(prev => [...prev, indicator]);
                          } else {
                            onIndicatorSelect(prev => prev.filter(i => i !== indicator));
                          }
                        }}
                      />
                      <span className="text-white text-sm">{indicator}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'risk' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Risk Per Trade (%)</label>
                  <input
                    type="range"
                    min="0.5"
                    max="5"
                    step="0.5"
                    value={advancedSettings.riskPerTrade}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, riskPerTrade: parseFloat(e.target.value)})}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-400">
                    <span>0.5%</span>
                    <span className="text-purple-400 font-semibold">{advancedSettings.riskPerTrade}%</span>
                    <span>5%</span>
                  </div>
                </div>
                <div>
                  <label className="block text-white mb-2">Stop Loss (%)</label>
                  <input
                    type="number"
                    value={advancedSettings.stopLoss}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, stopLoss: parseFloat(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2">Take Profit (%)</label>
                  <input
                    type="number"
                    value={advancedSettings.takeProfit}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, takeProfit: parseFloat(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
              </div>
            )}

            {activeTab === 'advanced' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Timeframe</label>
                  <select
                    value={advancedSettings.timeframe}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, timeframe: e.target.value})}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  >
                    <option value="1m">1 Minute</option>
                    <option value="5m">5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="1h">1 Hour</option>
                    <option value="4h">4 Hours</option>
                    <option value="1d">Daily</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white mb-2">Max Positions</label>
                  <input
                    type="number"
                    value={advancedSettings.maxPositions}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, maxPositions: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleGenerate}
              className="mt-8 w-full btn-gradient py-4 text-lg font-semibold"
            >
              🚀 Generate Strategy
            </motion.button>
          </div>
        </div>

        {/* Right Panel - Code & Results */}
        <div className="space-y-6">
          {code && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
            >
              <h3 className="text-xl font-semibold text-white mb-4">Generated Strategy Code</h3>
              <pre className="bg-black/50 rounded-xl p-4 overflow-x-auto">
                <code className="text-green-400 text-sm">{code}</code>
              </pre>
              <div className="flex space-x-4 mt-4">
                <button
                  onClick={onBacktest}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 transition-all"
                >
                  Run Backtest
                </button>
                <button
                  onClick={onAdvancedBacktest}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 transition-all"
                >
                  Advanced Backtest
                </button>
              </div>
            </motion.div>
          )}

          {backtestError && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-900/30 border border-red-500/50 rounded-xl p-4"
            >
              <div className="flex items-center mb-2">
                <span className="text-red-400 mr-2">⚠️</span>
                <span className="font-semibold text-red-400">Backtest Error</span>
              </div>
              <p className="text-red-300 text-sm">{backtestError}</p>
            </motion.div>
          )}

          {backtestResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
            >
              <h3 className="text-xl font-semibold text-white mb-4">Backtest Results</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-sm">Total Return</div>
                  <div className="text-2xl font-bold text-green-400">
                    {backtestResults.total_return?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-sm">Sharpe Ratio</div>
                  <div className="text-2xl font-bold text-white">
                    {backtestResults.sharpe_ratio?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-sm">Max Drawdown</div>
                  <div className="text-2xl font-bold text-red-400">
                    {backtestResults.max_drawdown?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-sm">Win Rate</div>
                  <div className="text-2xl font-bold text-white">
                    {backtestResults.win_rate?.toFixed(1)}%
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIStrategyBuilder;
