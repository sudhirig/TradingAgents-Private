import React, { useState } from 'react';
import { motion } from 'framer-motion';

const AdvancedOrderManagement = ({ orderSettings, onSettingsChange }) => {
  const [activeOrderType, setActiveOrderType] = useState('market');
  
  const orderTypes = [
    { id: 'market', name: 'Market Order', icon: '⚡', description: 'Execute immediately at current price' },
    { id: 'limit', name: 'Limit Order', icon: '🎯', description: 'Execute at specific price or better' },
    { id: 'stop', name: 'Stop Order', icon: '🛑', description: 'Trigger when price hits threshold' },
    { id: 'stop_limit', name: 'Stop Limit', icon: '🎪', description: 'Limit order triggered by stop price' },
    { id: 'trailing_stop', name: 'Trailing Stop', icon: '📈', description: 'Dynamic stop that follows price' },
    { id: 'bracket', name: 'Bracket Order', icon: '🔄', description: 'Entry with profit target and stop loss' },
    { id: 'oco', name: 'OCO Order', icon: '👥', description: 'One cancels the other' },
    { id: 'iceberg', name: 'Iceberg Order', icon: '🧊', description: 'Hide large order size' }
  ];

  const [orderConfig, setOrderConfig] = useState({
    market: { size: 100, timeInForce: 'DAY' },
    limit: { price: 0, size: 100, timeInForce: 'GTC' },
    stop: { stopPrice: 0, size: 100, timeInForce: 'DAY' },
    stop_limit: { stopPrice: 0, limitPrice: 0, size: 100, timeInForce: 'GTC' },
    trailing_stop: { trailAmount: 5, trailPercent: false, size: 100 },
    bracket: { entryPrice: 0, profitTarget: 10, stopLoss: 5, size: 100 },
    oco: { order1Type: 'limit', order2Type: 'stop', size: 100 },
    iceberg: { totalSize: 1000, displaySize: 100, price: 0 }
  });

  const timeInForceOptions = [
    { value: 'DAY', label: 'Day', description: 'Valid for current trading day' },
    { value: 'GTC', label: 'Good Till Canceled', description: 'Valid until canceled' },
    { value: 'IOC', label: 'Immediate or Cancel', description: 'Execute immediately or cancel' },
    { value: 'FOK', label: 'Fill or Kill', description: 'Execute entirely or cancel' }
  ];

  const handleConfigChange = (type, field, value) => {
    setOrderConfig(prev => ({
      ...prev,
      [type]: { ...prev[type], [field]: value }
    }));
    onSettingsChange({ ...orderConfig, [type]: { ...orderConfig[type], [field]: value } });
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-white mb-4">
          Advanced Order Management
        </h1>
        <p className="text-gray-300">
          Configure and execute sophisticated order types for precise trade execution
        </p>
      </motion.div>

      {/* Order Types Grid */}
      <div className="grid lg:grid-cols-4 gap-4 mb-8">
        {orderTypes.map((order, index) => (
          <motion.button
            key={order.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.05 }}
            onClick={() => setActiveOrderType(order.id)}
            className={`p-4 rounded-xl border transition-all ${
              activeOrderType === order.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 border-transparent'
                : 'bg-white/5 border-white/10 hover:bg-white/10'
            }`}
          >
            <div className="text-2xl mb-2">{order.icon}</div>
            <div className="font-semibold text-white">{order.name}</div>
            <div className="text-xs text-gray-400 mt-1">{order.description}</div>
          </motion.button>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Order Configuration */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <h2 className="text-xl font-semibold text-white mb-6">
              {orderTypes.find(o => o.id === activeOrderType)?.name} Configuration
            </h2>

            {activeOrderType === 'market' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Order Size</label>
                  <input
                    type="number"
                    value={orderConfig.market.size}
                    onChange={(e) => handleConfigChange('market', 'size', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2">Time in Force</label>
                  <select
                    value={orderConfig.market.timeInForce}
                    onChange={(e) => handleConfigChange('market', 'timeInForce', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  >
                    {timeInForceOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {activeOrderType === 'limit' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Limit Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={orderConfig.limit.price}
                    onChange={(e) => handleConfigChange('limit', 'price', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2">Order Size</label>
                  <input
                    type="number"
                    value={orderConfig.limit.size}
                    onChange={(e) => handleConfigChange('limit', 'size', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2">Time in Force</label>
                  <select
                    value={orderConfig.limit.timeInForce}
                    onChange={(e) => handleConfigChange('limit', 'timeInForce', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  >
                    {timeInForceOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {activeOrderType === 'stop' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Stop Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={orderConfig.stop.stopPrice}
                    onChange={(e) => handleConfigChange('stop', 'stopPrice', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block text-white mb-2">Order Size</label>
                  <input
                    type="number"
                    value={orderConfig.stop.size}
                    onChange={(e) => handleConfigChange('stop', 'size', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
              </div>
            )}

            {activeOrderType === 'trailing_stop' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Trail Amount</label>
                  <div className="flex space-x-4">
                    <input
                      type="number"
                      step="0.01"
                      value={orderConfig.trailing_stop.trailAmount}
                      onChange={(e) => handleConfigChange('trailing_stop', 'trailAmount', e.target.value)}
                      className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                    <button
                      onClick={() => handleConfigChange('trailing_stop', 'trailPercent', !orderConfig.trailing_stop.trailPercent)}
                      className={`px-4 py-2 rounded-lg font-semibold ${
                        orderConfig.trailing_stop.trailPercent
                          ? 'bg-purple-500 text-white'
                          : 'bg-white/10 text-gray-400'
                      }`}
                    >
                      {orderConfig.trailing_stop.trailPercent ? '%' : '$'}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-white mb-2">Order Size</label>
                  <input
                    type="number"
                    value={orderConfig.trailing_stop.size}
                    onChange={(e) => handleConfigChange('trailing_stop', 'size', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
              </div>
            )}

            {activeOrderType === 'bracket' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Entry Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={orderConfig.bracket.entryPrice}
                    onChange={(e) => handleConfigChange('bracket', 'entryPrice', e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-white mb-2">Profit Target (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={orderConfig.bracket.profitTarget}
                      onChange={(e) => handleConfigChange('bracket', 'profitTarget', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-white mb-2">Stop Loss (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={orderConfig.bracket.stopLoss}
                      onChange={(e) => handleConfigChange('bracket', 'stopLoss', e.target.value)}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-white/10">
              <button className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all">
                Execute {orderTypes.find(o => o.id === activeOrderType)?.name}
              </button>
            </div>
          </div>
        </div>

        {/* Order Summary & Risk */}
        <div className="space-y-6">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Order Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Type</span>
                <span className="text-white font-semibold">
                  {orderTypes.find(o => o.id === activeOrderType)?.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Size</span>
                <span className="text-white">
                  {orderConfig[activeOrderType]?.size || 0} shares
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Estimated Cost</span>
                <span className="text-white">$0.00</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Risk Analysis</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-300">Max Loss</span>
                <span className="text-red-400">-$0.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Max Profit</span>
                <span className="text-green-400">+$0.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Risk/Reward</span>
                <span className="text-white">1:2</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedOrderManagement;
