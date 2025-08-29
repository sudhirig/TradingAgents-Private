import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaPlay, FaTrash, FaEdit, FaCopy, FaStar, FaChartBar, FaClock, FaCode } from 'react-icons/fa';

const SavedStrategies = ({ onSelectStrategy, onDeleteStrategy, onRunBacktest }) => {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Load saved strategies from localStorage or API
    const loadStrategies = () => {
      const saved = localStorage.getItem('savedStrategies');
      if (saved) {
        setStrategies(JSON.parse(saved));
      } else {
        setStrategies([]);
      }
    };
    loadStrategies();
  }, []);

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      const updated = strategies.filter(s => s.id !== id);
      setStrategies(updated);
      localStorage.setItem('savedStrategies', JSON.stringify(updated));
      if (onDeleteStrategy) onDeleteStrategy(id);
    }
  };

  const handleToggleFavorite = (id) => {
    const updated = strategies.map(s => 
      s.id === id ? { ...s, isFavorite: !s.isFavorite } : s
    );
    setStrategies(updated);
    localStorage.setItem('savedStrategies', JSON.stringify(updated));
  };

  const handleDuplicate = (strategy) => {
    const duplicate = {
      ...strategy,
      id: Date.now().toString(),
      name: `${strategy.name} (Copy)`,
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      isFavorite: false
    };
    const updated = [...strategies, duplicate];
    setStrategies(updated);
    localStorage.setItem('savedStrategies', JSON.stringify(updated));
  };

  const filteredStrategies = strategies.filter(s => {
    if (filter === 'all') return true;
    if (filter === 'favorites') return s.isFavorite;
    return s.type === filter;
  });

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            💾 Saved Strategies
          </h1>
          <div className="text-sm text-gray-400">
            {filteredStrategies.length} Strategies
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed mb-4">
          Manage and deploy your saved trading strategies with performance tracking
        </p>
      </motion.div>
      
      <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
        <div className="flex justify-between items-center mb-6">
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-400 text-sm"
          >
            <option value="all">All Strategies</option>
            <option value="favorites">Favorites</option>
            <option value="momentum">Momentum</option>
            <option value="meanReversion">Mean Reversion</option>
            <option value="arbitrage">Arbitrage</option>
            <option value="sentiment">Sentiment</option>
          </select>
        </div>
      </div>

        {filteredStrategies.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">💾</div>
            <h3 className="text-white font-medium mb-2">No saved strategies found</h3>
            <p className="text-gray-400 text-sm">Create your first strategy using the AI Generator</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredStrategies.map((strategy) => (
              <motion.div
                key={strategy.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.02 }}
                className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-all cursor-pointer"
                onClick={() => setSelectedStrategy(strategy)}
              >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-lg text-white">
                  {strategy.name}
                </h3>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleToggleFavorite(strategy.id);
                  }}
                  className={`${
                    strategy.isFavorite ? 'text-yellow-500' : 'text-gray-400'
                  } hover:text-yellow-500 transition-colors`}
                >
                  <FaStar />
                </button>
              </div>

              <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                {strategy.description}
              </p>

              {/* Performance Metrics */}
              <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
                <div className="text-center">
                  <div className="font-semibold text-green-600">
                    {strategy.performance.returns}%
                  </div>
                  <div className="text-gray-400">Returns</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-blue-600">
                    {strategy.performance.sharpe}
                  </div>
                  <div className="text-gray-400">Sharpe</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-purple-600">
                    {strategy.performance.winRate}%
                  </div>
                  <div className="text-gray-400">Win Rate</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 mt-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onRunBacktest) onRunBacktest(strategy);
                  }}
                  className="flex-1 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded hover:from-purple-600 hover:to-pink-600 transition-colors text-sm"
                >
                  <FaPlay className="inline mr-1" /> Run
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onSelectStrategy) onSelectStrategy(strategy);
                  }}
                  className="px-3 py-1.5 border border-white/20 rounded hover:bg-white/10 transition-colors text-sm text-white"
                >
                  <FaEdit />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDuplicate(strategy);
                  }}
                  className="px-3 py-1.5 border border-white/20 rounded hover:bg-white/10 transition-colors text-sm text-white"
                >
                  <FaCopy />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(strategy.id);
                  }}
                  className="px-3 py-1.5 border border-red-400/30 text-red-400 rounded hover:bg-red-500/10 transition-colors text-sm"
                >
                  <FaTrash />
                </button>
              </div>

              {/* Timestamp */}
              <div className="flex items-center gap-1 mt-3 text-xs text-gray-400">
                <FaClock />
                <span>Modified {new Date(strategy.lastModified).toLocaleDateString()}</span>
              </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Strategy Detail Modal */}
      {selectedStrategy && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedStrategy(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold text-white mb-4">{selectedStrategy.name}</h2>
            <p className="text-gray-300 mb-4">
              {selectedStrategy.description}
            </p>
            
            <div className="bg-white/5 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-white mb-2">Performance Metrics</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {selectedStrategy.performance.returns}%
                  </div>
                  <div className="text-sm text-gray-400">Total Returns</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {selectedStrategy.performance.sharpe}
                  </div>
                  <div className="text-sm text-gray-400">Sharpe Ratio</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {selectedStrategy.performance.winRate}%
                  </div>
                  <div className="text-sm text-gray-400">Win Rate</div>
                </div>
              </div>
            </div>

            <div className="bg-black/50 text-green-400 rounded-lg p-4 mb-4 font-mono text-sm overflow-x-auto">
              <pre>{selectedStrategy.code?.substring(0, 500) || 'No code available'}...</pre>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  if (onRunBacktest) onRunBacktest(selectedStrategy);
                  setSelectedStrategy(null);
                }}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-colors"
              >
                <FaChartBar className="inline mr-2" />
                Run Backtest
              </button>
              <button
                onClick={() => {
                  if (onSelectStrategy) onSelectStrategy(selectedStrategy);
                  setSelectedStrategy(null);
                }}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 transition-colors"
              >
                <FaEdit className="inline mr-2" />
                Edit Strategy
              </button>
              <button
                onClick={() => setSelectedStrategy(null)}
                className="px-4 py-2 border border-white/20 rounded-lg hover:bg-white/10 transition-colors text-white"
              >
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default SavedStrategies;
