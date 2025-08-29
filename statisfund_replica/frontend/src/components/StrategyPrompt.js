import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaRobot, FaMagic, FaChartLine, FaBrain, FaLightbulb } from 'react-icons/fa';

const StrategyPrompt = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [strategyType, setStrategyType] = useState('momentum');

  const examplePrompts = [
    "Create a momentum strategy using RSI and MACD for tech stocks",
    "Build a mean reversion strategy with Bollinger Bands",
    "Design a pairs trading strategy for correlated assets",
    "Develop a sentiment-based strategy using news data",
    "Create a volatility arbitrage strategy with options"
  ];

  const strategyTypes = [
    { id: 'momentum', label: 'Momentum', icon: <FaChartLine /> },
    { id: 'meanReversion', label: 'Mean Reversion', icon: <FaBrain /> },
    { id: 'arbitrage', label: 'Arbitrage', icon: <FaMagic /> },
    { id: 'sentiment', label: 'Sentiment', icon: <FaLightbulb /> }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) {
      onSubmit({
        prompt,
        model: selectedModel,
        type: strategyType
      });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
    >
      <div className="flex items-center mb-6">
        <FaRobot className="text-3xl text-blue-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          AI Strategy Generator
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Strategy Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Strategy Type
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {strategyTypes.map((type) => (
              <button
                key={type.id}
                type="button"
                onClick={() => setStrategyType(type.id)}
                className={`p-3 rounded-lg border-2 transition-all ${
                  strategyType === type.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex flex-col items-center">
                  <div className="text-2xl mb-1">{type.icon}</div>
                  <span className="text-sm">{type.label}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Model Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            AI Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="gpt-4">GPT-4 (Most Advanced)</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
            <option value="claude">Claude (Analytical)</option>
          </select>
        </div>

        {/* Prompt Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Strategy Description
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your trading strategy idea..."
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 min-h-[120px] dark:bg-gray-700 dark:border-gray-600"
            disabled={isLoading}
          />
        </div>

        {/* Example Prompts */}
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Example prompts:
          </p>
          <div className="flex flex-wrap gap-2">
            {examplePrompts.map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setPrompt(example)}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-full transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            isLoading || !prompt.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Generating Strategy...
            </div>
          ) : (
            'Generate Strategy'
          )}
        </button>
      </form>
    </motion.div>
  );
};

export default StrategyPrompt;
