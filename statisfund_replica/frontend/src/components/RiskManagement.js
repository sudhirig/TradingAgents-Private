import React, { useState } from 'react';
import { motion } from 'framer-motion';

const RiskManagement = ({ riskSettings, onSettingsChange }) => {
  const [activeTab, setActiveTab] = useState('position');
  
  const [settings, setSettings] = useState({
    positionSizing: {
      method: 'fixed',
      fixedSize: 100,
      percentageRisk: 2,
      kellyFraction: 0.25,
      volatilityPeriod: 20,
      maxPositions: 5
    },
    riskLimits: {
      maxDrawdown: 20,
      dailyLossLimit: 5,
      maxExposure: 80,
      correlationLimit: 0.7,
      sectorConcentration: 30
    },
    stopLoss: {
      enabled: true,
      type: 'percentage',
      percentage: 5,
      atr_multiplier: 2,
      trailing: false,
      trailingPercent: 3
    },
    portfolioRisk: {
      var_confidence: 95,
      var_period: 1,
      stress_scenarios: ['market_crash', 'flash_crash', 'black_swan'],
      rebalancing_frequency: 'monthly'
    }
  });

  const positionSizingMethods = [
    { id: 'fixed', name: 'Fixed Size', description: 'Fixed number of shares/contracts', icon: '🔢' },
    { id: 'percentage', name: 'Percentage Risk', description: 'Risk fixed % of capital per trade', icon: '💰' },
    { id: 'kelly', name: 'Kelly Criterion', description: 'Optimal size based on edge and odds', icon: '📊' },
    { id: 'volatility', name: 'Volatility-Based', description: 'Scale position by volatility', icon: '📈' },
    { id: 'optimal_f', name: 'Optimal F', description: 'Ralph Vince optimal fraction', icon: '🎯' }
  ];

  const handleSettingChange = (category, field, value) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [field]: value
      }
    };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-white mb-4">
          Risk Management & Position Sizing
        </h1>
        <p className="text-gray-300">
          Configure sophisticated risk controls and position sizing algorithms
        </p>
      </motion.div>

      {/* Risk Metrics Overview */}
      <div className="grid lg:grid-cols-4 gap-4 mb-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl p-4"
        >
          <div className="text-white/80 text-sm">Portfolio Risk Score</div>
          <div className="text-3xl font-bold text-white">7.2/10</div>
          <div className="text-white/60 text-xs mt-1">Moderate Risk</div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Max Drawdown</div>
          <div className="text-3xl font-bold text-red-400">{settings.riskLimits.maxDrawdown}%</div>
          <div className="text-gray-500 text-xs mt-1">Limit</div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Daily Loss Limit</div>
          <div className="text-3xl font-bold text-orange-400">{settings.riskLimits.dailyLossLimit}%</div>
          <div className="text-gray-500 text-xs mt-1">Max per day</div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
        >
          <div className="text-gray-400 text-sm">Risk per Trade</div>
          <div className="text-3xl font-bold text-purple-400">{settings.positionSizing.percentageRisk}%</div>
          <div className="text-gray-500 text-xs mt-1">Capital at risk</div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        {[
          { id: 'position', label: 'Position Sizing' },
          { id: 'limits', label: 'Risk Limits' },
          { id: 'stops', label: 'Stop Loss' },
          { id: 'portfolio', label: 'Portfolio Risk' }
        ].map((tab) => (
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

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Configuration */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            {activeTab === 'position' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-6">Position Sizing Method</h2>
                
                <div className="grid sm:grid-cols-2 gap-4 mb-6">
                  {positionSizingMethods.map((method) => (
                    <button
                      key={method.id}
                      onClick={() => handleSettingChange('positionSizing', 'method', method.id)}
                      className={`p-4 rounded-xl border text-left transition-all ${
                        settings.positionSizing.method === method.id
                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 border-transparent'
                          : 'bg-white/5 border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center mb-2">
                        <span className="text-2xl mr-2">{method.icon}</span>
                        <span className="font-semibold text-white">{method.name}</span>
                      </div>
                      <div className="text-xs text-gray-400">{method.description}</div>
                    </button>
                  ))}
                </div>

                {settings.positionSizing.method === 'fixed' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-white mb-2">Fixed Position Size</label>
                      <input
                        type="number"
                        value={settings.positionSizing.fixedSize}
                        onChange={(e) => handleSettingChange('positionSizing', 'fixedSize', e.target.value)}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                      />
                    </div>
                  </div>
                )}

                {settings.positionSizing.method === 'percentage' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-white mb-2">Risk Percentage per Trade (%)</label>
                      <input
                        type="range"
                        min="0.5"
                        max="5"
                        step="0.5"
                        value={settings.positionSizing.percentageRisk}
                        onChange={(e) => handleSettingChange('positionSizing', 'percentageRisk', e.target.value)}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-gray-400 mt-1">
                        <span>0.5%</span>
                        <span className="text-purple-400 font-semibold">{settings.positionSizing.percentageRisk}%</span>
                        <span>5%</span>
                      </div>
                    </div>
                  </div>
                )}

                {settings.positionSizing.method === 'kelly' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-white mb-2">Kelly Fraction</label>
                      <input
                        type="range"
                        min="0.1"
                        max="1"
                        step="0.05"
                        value={settings.positionSizing.kellyFraction}
                        onChange={(e) => handleSettingChange('positionSizing', 'kellyFraction', e.target.value)}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-gray-400 mt-1">
                        <span>10%</span>
                        <span className="text-purple-400 font-semibold">{(settings.positionSizing.kellyFraction * 100).toFixed(0)}%</span>
                        <span>100%</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        Using fractional Kelly (25% of full Kelly) for safety
                      </p>
                    </div>
                  </div>
                )}

                <div className="mt-6 pt-6 border-t border-white/10">
                  <div>
                    <label className="block text-white mb-2">Max Positions</label>
                    <input
                      type="number"
                      value={settings.positionSizing.maxPositions}
                      onChange={(e) => handleSettingChange('positionSizing', 'maxPositions', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'limits' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-6">Risk Limits Configuration</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-white mb-2">Maximum Drawdown (%)</label>
                    <input
                      type="number"
                      value={settings.riskLimits.maxDrawdown}
                      onChange={(e) => handleSettingChange('riskLimits', 'maxDrawdown', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                    <p className="text-xs text-gray-400 mt-1">Stop trading when drawdown exceeds this limit</p>
                  </div>
                  <div>
                    <label className="block text-white mb-2">Daily Loss Limit (%)</label>
                    <input
                      type="number"
                      value={settings.riskLimits.dailyLossLimit}
                      onChange={(e) => handleSettingChange('riskLimits', 'dailyLossLimit', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-white mb-2">Maximum Portfolio Exposure (%)</label>
                    <input
                      type="number"
                      value={settings.riskLimits.maxExposure}
                      onChange={(e) => handleSettingChange('riskLimits', 'maxExposure', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-white mb-2">Correlation Limit</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={settings.riskLimits.correlationLimit}
                      onChange={(e) => handleSettingChange('riskLimits', 'correlationLimit', e.target.value)}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-gray-400 mt-1">
                      <span>0.0</span>
                      <span className="text-purple-400 font-semibold">{settings.riskLimits.correlationLimit}</span>
                      <span>1.0</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-white mb-2">Sector Concentration Limit (%)</label>
                    <input
                      type="number"
                      value={settings.riskLimits.sectorConcentration}
                      onChange={(e) => handleSettingChange('riskLimits', 'sectorConcentration', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'stops' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-6">Stop Loss Configuration</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-white font-medium">Enable Stop Loss</span>
                    <button
                      onClick={() => handleSettingChange('stopLoss', 'enabled', !settings.stopLoss.enabled)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.stopLoss.enabled ? 'bg-purple-500' : 'bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          settings.stopLoss.enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {settings.stopLoss.enabled && (
                    <>
                      <div>
                        <label className="block text-white mb-2">Stop Loss Type</label>
                        <select
                          value={settings.stopLoss.type}
                          onChange={(e) => handleSettingChange('stopLoss', 'type', e.target.value)}
                          className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                        >
                          <option value="percentage">Percentage</option>
                          <option value="atr">ATR-Based</option>
                          <option value="fixed">Fixed Dollar</option>
                        </select>
                      </div>

                      {settings.stopLoss.type === 'percentage' && (
                        <div>
                          <label className="block text-white mb-2">Stop Loss Percentage (%)</label>
                          <input
                            type="number"
                            step="0.5"
                            value={settings.stopLoss.percentage}
                            onChange={(e) => handleSettingChange('stopLoss', 'percentage', e.target.value)}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                          />
                        </div>
                      )}

                      {settings.stopLoss.type === 'atr' && (
                        <div>
                          <label className="block text-white mb-2">ATR Multiplier</label>
                          <input
                            type="number"
                            step="0.5"
                            value={settings.stopLoss.atr_multiplier}
                            onChange={(e) => handleSettingChange('stopLoss', 'atr_multiplier', e.target.value)}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                          />
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <span className="text-white font-medium">Use Trailing Stop</span>
                        <button
                          onClick={() => handleSettingChange('stopLoss', 'trailing', !settings.stopLoss.trailing)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            settings.stopLoss.trailing ? 'bg-purple-500' : 'bg-gray-600'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              settings.stopLoss.trailing ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>

                      {settings.stopLoss.trailing && (
                        <div>
                          <label className="block text-white mb-2">Trailing Stop Distance (%)</label>
                          <input
                            type="number"
                            step="0.5"
                            value={settings.stopLoss.trailingPercent}
                            onChange={(e) => handleSettingChange('stopLoss', 'trailingPercent', e.target.value)}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                          />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'portfolio' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-6">Portfolio Risk Analysis</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-white mb-2">VaR Confidence Level (%)</label>
                    <select
                      value={settings.portfolioRisk.var_confidence}
                      onChange={(e) => handleSettingChange('portfolioRisk', 'var_confidence', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    >
                      <option value="90">90%</option>
                      <option value="95">95%</option>
                      <option value="99">99%</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-white mb-2">VaR Period (days)</label>
                    <input
                      type="number"
                      value={settings.portfolioRisk.var_period}
                      onChange={(e) => handleSettingChange('portfolioRisk', 'var_period', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-white mb-2">Stress Test Scenarios</label>
                    <div className="space-y-2">
                      {['market_crash', 'flash_crash', 'black_swan', 'inflation_spike', 'liquidity_crisis'].map((scenario) => (
                        <label key={scenario} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.portfolioRisk.stress_scenarios.includes(scenario)}
                            onChange={(e) => {
                              const scenarios = e.target.checked
                                ? [...settings.portfolioRisk.stress_scenarios, scenario]
                                : settings.portfolioRisk.stress_scenarios.filter(s => s !== scenario);
                              handleSettingChange('portfolioRisk', 'stress_scenarios', scenarios);
                            }}
                            className="rounded text-purple-500 focus:ring-purple-500"
                          />
                          <span className="text-white text-sm capitalize">{scenario.replace('_', ' ')}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-white mb-2">Rebalancing Frequency</label>
                    <select
                      value={settings.portfolioRisk.rebalancing_frequency}
                      onChange={(e) => handleSettingChange('portfolioRisk', 'rebalancing_frequency', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Risk Analysis Sidebar */}
        <div className="space-y-6">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Risk Metrics</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400 text-sm">Value at Risk (95%)</span>
                  <span className="text-red-400 text-sm">-$2,450</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400 text-sm">Expected Shortfall</span>
                  <span className="text-orange-400 text-sm">-$3,100</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div className="bg-orange-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400 text-sm">Beta to Market</span>
                  <span className="text-purple-400 text-sm">1.2</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">AI Risk Recommendations</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-green-400 mr-2">✓</span>
                <span className="text-gray-300">Consider reducing position size in correlated assets</span>
              </li>
              <li className="flex items-start">
                <span className="text-yellow-400 mr-2">⚠</span>
                <span className="text-gray-300">Portfolio beta is above target range</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-400 mr-2">💡</span>
                <span className="text-gray-300">Enable trailing stops for volatile positions</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManagement;
