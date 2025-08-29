import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const TechnicalIndicatorsDashboard = ({ selectedIndicators, onIndicatorSelect, marketData }) => {
  const [activeCategory, setActiveCategory] = useState('overlap');
  const [searchTerm, setSearchTerm] = useState('');
  const [indicatorSettings, setIndicatorSettings] = useState({});

  const indicatorCategories = {
    overlap: {
      name: 'Overlap Studies',
      icon: '📊',
      indicators: [
        { id: 'SMA', name: 'Simple Moving Average', params: ['period'], popular: true },
        { id: 'EMA', name: 'Exponential Moving Average', params: ['period'], popular: true },
        { id: 'WMA', name: 'Weighted Moving Average', params: ['period'] },
        { id: 'DEMA', name: 'Double Exponential Moving Average', params: ['period'] },
        { id: 'TEMA', name: 'Triple Exponential Moving Average', params: ['period'] },
        { id: 'TRIMA', name: 'Triangular Moving Average', params: ['period'] },
        { id: 'KAMA', name: 'Kaufman Adaptive Moving Average', params: ['period'] },
        { id: 'MAMA', name: 'MESA Adaptive Moving Average', params: ['fastlimit', 'slowlimit'] },
        { id: 'BBANDS', name: 'Bollinger Bands', params: ['period', 'nbdevup', 'nbdevdn'], popular: true },
        { id: 'HT_TRENDLINE', name: 'Hilbert Transform - Instantaneous Trendline', params: [] },
        { id: 'MIDPOINT', name: 'MidPoint over period', params: ['period'] },
        { id: 'MIDPRICE', name: 'MidPoint Price over period', params: ['period'] },
        { id: 'SAR', name: 'Parabolic SAR', params: ['acceleration', 'maximum'] },
        { id: 'SAREXT', name: 'Parabolic SAR Extended', params: ['startvalue', 'offsetonreverse'] },
        { id: 'T3', name: 'Triple Exponential Moving Average (T3)', params: ['period', 'vfactor'] }
      ]
    },
    momentum: {
      name: 'Momentum Indicators',
      icon: '🚀',
      indicators: [
        { id: 'RSI', name: 'Relative Strength Index', params: ['period'], popular: true },
        { id: 'STOCH', name: 'Stochastic', params: ['fastk_period', 'slowk_period', 'slowd_period'], popular: true },
        { id: 'STOCHF', name: 'Stochastic Fast', params: ['fastk_period', 'fastd_period'] },
        { id: 'STOCHRSI', name: 'Stochastic RSI', params: ['period', 'fastk_period', 'fastd_period'] },
        { id: 'MACD', name: 'MACD', params: ['fastperiod', 'slowperiod', 'signalperiod'], popular: true },
        { id: 'MACDEXT', name: 'MACD Extended', params: ['fastperiod', 'slowperiod', 'signalperiod'] },
        { id: 'MACDFIX', name: 'MACD Fix', params: ['signalperiod'] },
        { id: 'ADX', name: 'Average Directional Index', params: ['period'], popular: true },
        { id: 'ADXR', name: 'ADX Rating', params: ['period'] },
        { id: 'APO', name: 'Absolute Price Oscillator', params: ['fastperiod', 'slowperiod'] },
        { id: 'AROON', name: 'Aroon', params: ['period'] },
        { id: 'AROONOSC', name: 'Aroon Oscillator', params: ['period'] },
        { id: 'BOP', name: 'Balance of Power', params: [] },
        { id: 'CCI', name: 'Commodity Channel Index', params: ['period'], popular: true },
        { id: 'CMO', name: 'Chande Momentum Oscillator', params: ['period'] },
        { id: 'DX', name: 'Directional Movement Index', params: ['period'] },
        { id: 'MFI', name: 'Money Flow Index', params: ['period'] },
        { id: 'MINUS_DI', name: 'Minus Directional Indicator', params: ['period'] },
        { id: 'MINUS_DM', name: 'Minus Directional Movement', params: ['period'] },
        { id: 'MOM', name: 'Momentum', params: ['period'] },
        { id: 'PLUS_DI', name: 'Plus Directional Indicator', params: ['period'] },
        { id: 'PLUS_DM', name: 'Plus Directional Movement', params: ['period'] },
        { id: 'PPO', name: 'Percentage Price Oscillator', params: ['fastperiod', 'slowperiod'] },
        { id: 'ROC', name: 'Rate of Change', params: ['period'] },
        { id: 'ROCP', name: 'Rate of Change Percentage', params: ['period'] },
        { id: 'ROCR', name: 'Rate of Change Ratio', params: ['period'] },
        { id: 'ROCR100', name: 'Rate of Change Ratio 100 Scale', params: ['period'] },
        { id: 'TRIX', name: 'Triple Smooth EMA', params: ['period'] },
        { id: 'ULTOSC', name: 'Ultimate Oscillator', params: ['period1', 'period2', 'period3'] },
        { id: 'WILLR', name: 'Williams %R', params: ['period'] }
      ]
    },
    volume: {
      name: 'Volume Indicators',
      icon: '📈',
      indicators: [
        { id: 'AD', name: 'Accumulation/Distribution', params: [] },
        { id: 'ADOSC', name: 'Accumulation/Distribution Oscillator', params: ['fastperiod', 'slowperiod'] },
        { id: 'OBV', name: 'On Balance Volume', params: [], popular: true }
      ]
    },
    volatility: {
      name: 'Volatility Indicators',
      icon: '📉',
      indicators: [
        { id: 'ATR', name: 'Average True Range', params: ['period'], popular: true },
        { id: 'NATR', name: 'Normalized ATR', params: ['period'] },
        { id: 'TRANGE', name: 'True Range', params: [] }
      ]
    },
    price: {
      name: 'Price Transform',
      icon: '💹',
      indicators: [
        { id: 'AVGPRICE', name: 'Average Price', params: [] },
        { id: 'MEDPRICE', name: 'Median Price', params: [] },
        { id: 'TYPPRICE', name: 'Typical Price', params: [] },
        { id: 'WCLPRICE', name: 'Weighted Close Price', params: [] }
      ]
    },
    cycle: {
      name: 'Cycle Indicators',
      icon: '🔄',
      indicators: [
        { id: 'HT_DCPERIOD', name: 'Hilbert Transform - Dominant Cycle Period', params: [] },
        { id: 'HT_DCPHASE', name: 'Hilbert Transform - Dominant Cycle Phase', params: [] },
        { id: 'HT_PHASOR', name: 'Hilbert Transform - Phasor Components', params: [] },
        { id: 'HT_SINE', name: 'Hilbert Transform - SineWave', params: [] },
        { id: 'HT_TRENDMODE', name: 'Hilbert Transform - Trend vs Cycle Mode', params: [] }
      ]
    },
    pattern: {
      name: 'Pattern Recognition',
      icon: '🎯',
      indicators: [
        { id: 'CDL2CROWS', name: 'Two Crows', params: [] },
        { id: 'CDL3BLACKCROWS', name: 'Three Black Crows', params: [] },
        { id: 'CDL3INSIDE', name: 'Three Inside Up/Down', params: [] },
        { id: 'CDL3LINESTRIKE', name: 'Three-Line Strike', params: [] },
        { id: 'CDL3OUTSIDE', name: 'Three Outside Up/Down', params: [] },
        { id: 'CDL3STARSINSOUTH', name: 'Three Stars In The South', params: [] },
        { id: 'CDL3WHITESOLDIERS', name: 'Three Advancing White Soldiers', params: [] },
        { id: 'CDLABANDONEDBABY', name: 'Abandoned Baby', params: ['penetration'] },
        { id: 'CDLADVANCEBLOCK', name: 'Advance Block', params: [] },
        { id: 'CDLBELTHOLD', name: 'Belt-hold', params: [] },
        { id: 'CDLBREAKAWAY', name: 'Breakaway', params: [] },
        { id: 'CDLCLOSINGMARUBOZU', name: 'Closing Marubozu', params: [] },
        { id: 'CDLCONCEALBABYSWALL', name: 'Concealing Baby Swallow', params: [] },
        { id: 'CDLCOUNTERATTACK', name: 'Counterattack', params: [] },
        { id: 'CDLDARKCLOUDCOVER', name: 'Dark Cloud Cover', params: ['penetration'] },
        { id: 'CDLDOJI', name: 'Doji', params: [] },
        { id: 'CDLDOJISTAR', name: 'Doji Star', params: [] },
        { id: 'CDLDRAGONFLYDOJI', name: 'Dragonfly Doji', params: [] },
        { id: 'CDLENGULFING', name: 'Engulfing Pattern', params: [] },
        { id: 'CDLEVENINGDOJISTAR', name: 'Evening Doji Star', params: ['penetration'] },
        { id: 'CDLEVENINGSTAR', name: 'Evening Star', params: ['penetration'] },
        { id: 'CDLGAPSIDESIDEWHITE', name: 'Up/Down-gap side-by-side white lines', params: [] },
        { id: 'CDLGRAVESTONEDOJI', name: 'Gravestone Doji', params: [] },
        { id: 'CDLHAMMER', name: 'Hammer', params: [] },
        { id: 'CDLHANGINGMAN', name: 'Hanging Man', params: [] },
        { id: 'CDLHARAMI', name: 'Harami Pattern', params: [] },
        { id: 'CDLHARAMICROSS', name: 'Harami Cross Pattern', params: [] },
        { id: 'CDLHIGHWAVE', name: 'High-Wave Candle', params: [] },
        { id: 'CDLHIKKAKE', name: 'Hikkake Pattern', params: [] },
        { id: 'CDLHIKKAKEMOD', name: 'Modified Hikkake Pattern', params: [] },
        { id: 'CDLHOMINGPIGEON', name: 'Homing Pigeon', params: [] },
        { id: 'CDLIDENTICAL3CROWS', name: 'Identical Three Crows', params: [] },
        { id: 'CDLINNECK', name: 'In-Neck Pattern', params: [] },
        { id: 'CDLINVERTEDHAMMER', name: 'Inverted Hammer', params: [] },
        { id: 'CDLKICKING', name: 'Kicking', params: [] },
        { id: 'CDLKICKINGBYLENGTH', name: 'Kicking - bull/bear determined by the longer marubozu', params: [] },
        { id: 'CDLLADDERBOTTOM', name: 'Ladder Bottom', params: [] },
        { id: 'CDLLONGLEGGEDDOJI', name: 'Long Legged Doji', params: [] },
        { id: 'CDLLONGLINE', name: 'Long Line Candle', params: [] },
        { id: 'CDLMARUBOZU', name: 'Marubozu', params: [] },
        { id: 'CDLMATCHINGLOW', name: 'Matching Low', params: [] },
        { id: 'CDLMATHOLD', name: 'Mat Hold', params: ['penetration'] },
        { id: 'CDLMORNINGDOJISTAR', name: 'Morning Doji Star', params: ['penetration'] },
        { id: 'CDLMORNINGSTAR', name: 'Morning Star', params: ['penetration'] },
        { id: 'CDLONNECK', name: 'On-Neck Pattern', params: [] },
        { id: 'CDLPIERCING', name: 'Piercing Pattern', params: [] },
        { id: 'CDLRICKSHAWMAN', name: 'Rickshaw Man', params: [] },
        { id: 'CDLRISEFALL3METHODS', name: 'Rising/Falling Three Methods', params: [] },
        { id: 'CDLSEPARATINGLINES', name: 'Separating Lines', params: [] },
        { id: 'CDLSHOOTINGSTAR', name: 'Shooting Star', params: [] },
        { id: 'CDLSHORTLINE', name: 'Short Line Candle', params: [] },
        { id: 'CDLSPINNINGTOP', name: 'Spinning Top', params: [] },
        { id: 'CDLSTALLEDPATTERN', name: 'Stalled Pattern', params: [] },
        { id: 'CDLSTICKSANDWICH', name: 'Stick Sandwich', params: [] },
        { id: 'CDLTAKURI', name: 'Takuri', params: [] },
        { id: 'CDLTASUKIGAP', name: 'Tasuki Gap', params: [] },
        { id: 'CDLTHRUSTING', name: 'Thrusting Pattern', params: [] },
        { id: 'CDLTRISTAR', name: 'Tristar Pattern', params: [] },
        { id: 'CDLUNIQUE3RIVER', name: 'Unique 3 River', params: [] },
        { id: 'CDLUPSIDEGAP2CROWS', name: 'Upside Gap Two Crows', params: [] },
        { id: 'CDLXSIDEGAP3METHODS', name: 'Upside/Downside Gap Three Methods', params: [] }
      ]
    }
  };

  const filteredIndicators = () => {
    if (!searchTerm) return indicatorCategories[activeCategory].indicators;
    
    const allIndicators = Object.values(indicatorCategories).flatMap(cat => cat.indicators);
    return allIndicators.filter(ind => 
      ind.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ind.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const handleIndicatorToggle = (indicator) => {
    if (selectedIndicators.find(i => i.id === indicator.id)) {
      onIndicatorSelect(selectedIndicators.filter(i => i.id !== indicator.id));
    } else {
      const defaultSettings = {};
      indicator.params.forEach(param => {
        defaultSettings[param] = param === 'period' ? 14 : 2;
      });
      onIndicatorSelect([...selectedIndicators, { ...indicator, settings: defaultSettings }]);
    }
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            📊 Technical Indicators
          </h1>
          <div className="text-sm text-gray-400">
            122+ TA-Lib Indicators
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          Configure and analyze professional-grade technical indicators with real-time market data
        </p>
      </motion.div>

      {/* Search and Stats */}
      <div className="grid lg:grid-cols-4 gap-4 mb-6">
        <div className="lg:col-span-3">
          <div className="relative group">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search RSI, MACD, Bollinger Bands..."
              className="w-full px-4 py-2.5 pl-11 bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-400 focus:bg-white/10 transition-all duration-200 text-sm"
            />
            <svg className="absolute left-3.5 top-2.5 w-4 h-4 text-gray-500 group-focus-within:text-purple-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-2.5 w-4 h-4 text-gray-400 hover:text-white transition-colors"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-lg p-3 text-center backdrop-blur-sm">
          <div className="text-xl font-bold text-white mb-0.5">
            {selectedIndicators.length}
          </div>
          <div className="text-purple-300 text-xs font-medium">Active</div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex space-x-1.5 mb-5 overflow-x-auto pb-1 scrollbar-hide">
        {Object.entries(indicatorCategories).map(([key, category]) => {
          const isActive = activeCategory === key;
          const indicatorCount = category.indicators.length;
          return (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              className={`group px-3 py-2 rounded-md font-medium whitespace-nowrap transition-all duration-200 text-sm relative ${
                isActive
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 border border-white/5 hover:border-white/20'
              }`}
            >
              <span className="mr-1.5 text-sm">{category.icon}</span>
              <span className="hidden sm:inline">{category.name}</span>
              <span className="sm:hidden">{category.name.split(' ')[0]}</span>
              <span className={`ml-1.5 px-1.5 py-0.5 rounded text-xs font-medium ${
                isActive ? 'bg-white/20' : 'bg-white/10 text-gray-500'
              }`}>
                {indicatorCount}
              </span>
            </button>
          );
        })}
      </div>

      {/* Indicators Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Indicators List */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-5 border border-white/10">
            {searchTerm && (
              <div className="mb-4 px-3 py-2 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                <p className="text-sm text-purple-300">
                  Found {filteredIndicators().length} indicator(s) matching "{searchTerm}"
                </p>
              </div>
            )}
            {filteredIndicators().length === 0 ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">🔍</div>
                <h3 className="text-white font-medium mb-2">No indicators found</h3>
                <p className="text-gray-400 text-sm">Try adjusting your search terms or browse categories</p>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 gap-3">
                {filteredIndicators().map((indicator, index) => {
                  const isSelected = selectedIndicators.some(i => i.id === indicator.id);
                  return (
                    <motion.div
                      key={indicator.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.01 }}
                      onClick={() => handleIndicatorToggle(indicator)}
                      className={`group cursor-pointer p-3 rounded-lg border transition-all duration-200 ${
                        isSelected
                          ? 'bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/40 shadow-lg shadow-purple-500/10'
                          : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`mt-0.5 w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
                          isSelected 
                            ? 'bg-purple-500 border-purple-500'
                            : 'border-gray-500 group-hover:border-gray-400'
                        }`}>
                          {isSelected && (
                            <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className={`font-medium text-sm truncate ${
                              isSelected ? 'text-white' : 'text-gray-200 group-hover:text-white'
                            }`}>
                              {indicator.name}
                            </span>
                            {indicator.popular && (
                              <span className="ml-2 px-2 py-0.5 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-300 text-xs rounded-full border border-yellow-500/30">
                                ⭐ Hot
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-400 font-mono mb-1">{indicator.id}</div>
                          {indicator.params.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {indicator.params.slice(0, 3).map(param => (
                                <span key={param} className="px-1.5 py-0.5 bg-white/10 text-gray-400 text-xs rounded border border-white/20">
                                  {param}
                                </span>
                              ))}
                              {indicator.params.length > 3 && (
                                <span className="text-xs text-gray-500">+{indicator.params.length - 3}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Selected Indicators Configuration */}
        <div>
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-5 border border-white/10 h-fit">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                ⚙️ Configuration
              </h3>
              {selectedIndicators.length > 0 && (
                <button
                  onClick={() => onIndicatorSelect([])}
                  className="text-red-400 hover:text-red-300 text-sm font-medium transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>
            {selectedIndicators.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-3xl mb-3">📊</div>
                <p className="text-gray-400 text-sm mb-2">No indicators selected</p>
                <p className="text-gray-500 text-xs">Click any indicator to configure its parameters</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-white/5">
                {selectedIndicators.map((indicator) => (
                  <motion.div
                    key={indicator.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gradient-to-br from-white/10 to-white/5 rounded-lg p-3 border border-white/10 group"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <span className="text-white font-medium text-sm block">{indicator.name}</span>
                        <span className="text-xs text-gray-400 font-mono">{indicator.id}</span>
                      </div>
                      <button
                        onClick={() => onIndicatorSelect(selectedIndicators.filter(i => i.id !== indicator.id))}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10 p-1 rounded transition-all"
                        title="Remove indicator"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    {indicator.params && indicator.params.length > 0 ? (
                      <div className="space-y-2">
                        {indicator.params.map((param) => (
                          <div key={param} className="flex items-center justify-between">
                            <label className="text-xs text-gray-300 capitalize font-medium min-w-0 flex-1">
                              {param.replace('_', ' ')}
                            </label>
                            <input
                              type="number"
                              defaultValue={indicator.settings?.[param] || (param.includes('period') ? 14 : 2)}
                              className="w-16 px-2 py-1 bg-white/10 border border-white/20 rounded text-white text-xs focus:border-purple-400 focus:outline-none transition-colors"
                              min="1"
                              max="200"
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500 italic">No parameters required</p>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalIndicatorsDashboard;
