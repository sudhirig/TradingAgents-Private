import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ModernCard from './ModernCard';

const AIStrategyBuilderNew = ({
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
  const [chatHistory, setChatHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const chatEndRef = useRef(null);
  const [advancedSettings, setAdvancedSettings] = useState({
    timeframe: '1d',
    symbols: ['AAPL'],
    riskPerTrade: 2,
    maxPositions: 3,
    stopLoss: 5,
    takeProfit: 10
  });

  const examplePrompts = [
    "Create a momentum strategy using RSI and MACD indicators for AAPL",
    "Build a mean reversion strategy with Bollinger Bands and volume confirmation",
    "Design a breakout strategy that buys on high volume price breakouts above resistance",
    "Make a pairs trading strategy for correlated tech stocks like AAPL and MSFT",
    "Create a swing trading strategy using moving average crossovers with stop losses",
    "Build a scalping strategy for intraday trading with tight risk management"
  ];

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isTyping]);

  const handleGenerate = async () => {
    if (!strategyPrompt.trim()) {
      return;
    }

    // Add user message to chat
    const userMessage = { 
      type: 'user', 
      content: strategyPrompt, 
      timestamp: Date.now() 
    };
    setChatHistory(prev => [...prev, userMessage]);
    
    setIsTyping(true);
    
    const formData = {
      description: strategyPrompt,
      template: 'custom',
      symbols: advancedSettings.symbols,
      start_date: "2023-01-01",
      end_date: "2023-12-31",
      ...advancedSettings
    };
    
    try {
      await onGenerate(formData);
      // Add AI response to chat
      const aiMessage = { 
        type: 'ai', 
        content: `✅ Strategy generated successfully! I've created a professional Backtrader strategy based on your requirements. You can now run a backtest to see how it performs with historical data.`,
        timestamp: Date.now()
      };
      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = { 
        type: 'ai', 
        content: `❌ Sorry, I encountered an error generating your strategy: ${error.message || 'Unknown error'}. Please try rephrasing your request or check your settings.`,
        timestamp: Date.now()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setStrategyPrompt('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const handleExampleClick = (example) => {
    setStrategyPrompt(example);
  };

  const handleBacktestWithChat = async (isAdvanced = false) => {
    const backtestMessage = { 
      type: 'user', 
      content: `Run ${isAdvanced ? 'advanced' : 'basic'} backtest on the generated strategy`, 
      timestamp: Date.now() 
    };
    setChatHistory(prev => [...prev, backtestMessage]);
    
    setIsTyping(true);
    
    try {
      if (isAdvanced) {
        await onAdvancedBacktest();
      } else {
        await onBacktest();
      }
      
      const resultMessage = { 
        type: 'ai', 
        content: `📊 Backtest completed! Check the results below to see how your strategy performed.`,
        timestamp: Date.now()
      };
      setChatHistory(prev => [...prev, resultMessage]);
    } catch (error) {
      const errorMessage = { 
        type: 'ai', 
        content: `❌ Backtest failed: ${error.message || 'Unknown error'}. Please check your strategy code and try again.`,
        timestamp: Date.now()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent mb-4">
          🤖 AI Trading Strategy Assistant
        </h1>
        <p className="text-xl text-gray-300 mb-4">
          Describe your trading idea in plain English and I'll generate professional code
        </p>
        <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full border border-purple-500/30">
          <span className="w-3 h-3 bg-green-400 rounded-full mr-3 animate-pulse"></span>
          <span className="text-sm text-purple-300 font-medium">GPT-4 Powered • Real-time Code Generation • Professional Backtesting</span>
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-4 gap-8">
        {/* Main Chat Interface */}
        <div className="lg:col-span-3">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 h-[700px] flex flex-col">
            {/* Chat Header */}
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-xl">
                    🤖
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">AI Strategy Assistant</h3>
                    <p className="text-sm text-gray-400">Ready to help you build profitable trading strategies</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setShowSettings(!showSettings)}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm transition-all"
                  >
                    ⚙️ Settings
                  </button>
                  <div className="text-xs text-gray-500 bg-green-500/20 text-green-400 px-3 py-1 rounded-full">
                    ● Online
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {chatHistory.length === 0 && (
                <div className="text-center py-16">
                  <div className="text-8xl mb-6">💬</div>
                  <h3 className="text-2xl font-semibold text-white mb-4">Let's Build Your Trading Strategy</h3>
                  <p className="text-gray-400 mb-8 max-w-md mx-auto">
                    Describe your trading idea in natural language and I'll generate professional Backtrader code for you
                  </p>
                  
                  {/* Example Prompts */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
                    {examplePrompts.map((example, idx) => (
                      <motion.button
                        key={idx}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleExampleClick(example)}
                        className="text-left p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-all group"
                      >
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg flex items-center justify-center text-sm flex-shrink-0">
                            💡
                          </div>
                          <div>
                            <p className="text-sm text-gray-300 group-hover:text-white transition-colors leading-relaxed">
                              "{example}"
                            </p>
                          </div>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}
              
              <AnimatePresence>
                {chatHistory.map((message, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[85%] ${message.type === 'user' ? 'ml-12' : 'mr-12'}`}>
                      <div className={`p-4 rounded-2xl ${
                        message.type === 'user' 
                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
                          : 'bg-white/10 text-gray-100'
                      }`}>
                        <div className="flex items-start space-x-3">
                          {message.type === 'ai' && (
                            <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-sm flex-shrink-0 mt-0.5">
                              🤖
                            </div>
                          )}
                          <div className="flex-1">
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                            <div className="text-xs opacity-60 mt-2">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-white/10 text-gray-100 p-4 rounded-2xl mr-12">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-sm">
                        🤖
                      </div>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-6 border-t border-white/10">
              <div className="flex space-x-4">
                <div className="flex-1 relative">
                  <textarea
                    value={strategyPrompt}
                    onChange={(e) => setStrategyPrompt(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your trading strategy... (Press Enter to send, Shift+Enter for new line)"
                    className="w-full px-6 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-base"
                    rows={3}
                    disabled={isLoading || isTyping}
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-gray-500">
                    {strategyPrompt.length}/1000
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGenerate}
                  disabled={isLoading || isTyping || !strategyPrompt.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-2 self-end"
                >
                  {isLoading || isTyping ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <span>Generate</span>
                      <span>🚀</span>
                    </>
                  )}
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Sidebar */}
        <div className="space-y-6">
          {/* Quick Settings */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">⚙️</span>
              Strategy Settings
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-white mb-2 text-sm font-medium">Target Symbols</label>
                <div className="flex flex-wrap gap-2">
                  {['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA', 'AMZN'].map(symbol => (
                    <button
                      key={symbol}
                      onClick={() => {
                        const newSymbols = advancedSettings.symbols.includes(symbol)
                          ? advancedSettings.symbols.filter(s => s !== symbol)
                          : [...advancedSettings.symbols, symbol];
                        setAdvancedSettings({...advancedSettings, symbols: newSymbols});
                      }}
                      className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        advancedSettings.symbols.includes(symbol)
                          ? 'bg-purple-500 text-white shadow-lg'
                          : 'bg-white/10 text-gray-300 hover:bg-white/20'
                      }`}
                    >
                      {symbol}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-white mb-2 text-sm font-medium">Risk Per Trade</label>
                <input
                  type="range"
                  min="0.5"
                  max="5"
                  step="0.5"
                  value={advancedSettings.riskPerTrade}
                  onChange={(e) => setAdvancedSettings({...advancedSettings, riskPerTrade: parseFloat(e.target.value)})}
                  className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>0.5%</span>
                  <span className="text-purple-400 font-semibold">{advancedSettings.riskPerTrade}%</span>
                  <span>5%</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-white mb-2 text-sm font-medium">Stop Loss (%)</label>
                  <input
                    type="number"
                    value={advancedSettings.stopLoss}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, stopLoss: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2 text-sm font-medium">Take Profit (%)</label>
                  <input
                    type="number"
                    value={advancedSettings.takeProfit}
                    onChange={(e) => setAdvancedSettings({...advancedSettings, takeProfit: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-white mb-2 text-sm font-medium">Timeframe</label>
                <select
                  value={advancedSettings.timeframe}
                  onChange={(e) => setAdvancedSettings({...advancedSettings, timeframe: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="1m">1 Minute</option>
                  <option value="5m">5 Minutes</option>
                  <option value="15m">15 Minutes</option>
                  <option value="1h">1 Hour</option>
                  <option value="4h">4 Hours</option>
                  <option value="1d">Daily</option>
                </select>
              </div>
            </div>
          </motion.div>

          {/* Generated Code Display */}
          {code && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <span className="mr-2">📝</span>
                Generated Code
              </h3>
              <div className="bg-black/50 rounded-xl p-4 mb-4 max-h-40 overflow-y-auto">
                <code className="text-green-400 text-xs font-mono">{code.slice(0, 300)}...</code>
              </div>
              <div className="space-y-3">
                <button
                  onClick={() => handleBacktestWithChat(false)}
                  disabled={isLoading}
                  className="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
                >
                  <span>📊</span>
                  <span>Run Backtest</span>
                </button>
                <button
                  onClick={() => handleBacktestWithChat(true)}
                  disabled={isLoading}
                  className="w-full px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-lg font-semibold disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
                >
                  <span>🚀</span>
                  <span>Advanced Backtest</span>
                </button>
              </div>
            </motion.div>
          )}

          {/* Backtest Results */}
          {backtestResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <span className="mr-2">📈</span>
                Results
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-xs">Total Return</div>
                  <div className="text-lg font-bold text-green-400">
                    {backtestResults.total_return?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-xs">Sharpe Ratio</div>
                  <div className="text-lg font-bold text-white">
                    {backtestResults.sharpe_ratio?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-xs">Max Drawdown</div>
                  <div className="text-lg font-bold text-red-400">
                    {backtestResults.max_drawdown?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="text-gray-400 text-xs">Win Rate</div>
                  <div className="text-lg font-bold text-white">
                    {backtestResults.win_rate?.toFixed(1)}%
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Error Display */}
          {backtestError && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-900/30 border border-red-500/50 rounded-xl p-4"
            >
              <div className="flex items-center mb-2">
                <span className="text-red-400 mr-2">⚠️</span>
                <span className="font-semibold text-red-400">Error</span>
              </div>
              <p className="text-red-300 text-sm">{backtestError}</p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIStrategyBuilderNew;
