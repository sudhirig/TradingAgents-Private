import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaPlay, FaPause, FaStop, FaChartLine, FaDollarSign, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';

const LiveTrading = ({ strategy, onStop }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [positions, setPositions] = useState([]);
  const [pnl, setPnl] = useState(0);
  const [trades, setTrades] = useState([]);
  const [logs, setLogs] = useState([]);
  const [accountBalance, setAccountBalance] = useState(100000);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    // Simulate WebSocket connection
    const connectToMarket = () => {
      setConnectionStatus('connecting');
      setTimeout(() => {
        setConnectionStatus('connected');
      }, 1500);
    };

    if (isRunning) {
      connectToMarket();
      
      // Simulate live trading updates
      const interval = setInterval(() => {
        if (!isPaused) {
          simulateTradingUpdate();
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [isRunning, isPaused]);

  const simulateTradingUpdate = () => {
    // Simulate position updates
    const newTrade = {
      id: Date.now(),
      symbol: ['AAPL', 'GOOGL', 'MSFT', 'TSLA'][Math.floor(Math.random() * 4)],
      side: Math.random() > 0.5 ? 'BUY' : 'SELL',
      quantity: Math.floor(Math.random() * 100) + 1,
      price: Math.random() * 200 + 100,
      time: new Date().toLocaleTimeString(),
      pnl: (Math.random() - 0.5) * 1000
    };

    setTrades(prev => [newTrade, ...prev].slice(0, 20));
    setPnl(prev => prev + newTrade.pnl);
    setAccountBalance(prev => prev + newTrade.pnl);

    // Add log entry
    const logEntry = {
      time: new Date().toLocaleTimeString(),
      message: `${newTrade.side} ${newTrade.quantity} ${newTrade.symbol} @ $${newTrade.price.toFixed(2)}`,
      type: newTrade.pnl > 0 ? 'success' : 'warning'
    };
    setLogs(prev => [logEntry, ...prev].slice(0, 50));
  };

  const handleStart = () => {
    setIsRunning(true);
    setIsPaused(false);
    setLogs([{
      time: new Date().toLocaleTimeString(),
      message: 'Live trading started',
      type: 'info'
    }]);
  };

  const handlePause = () => {
    setIsPaused(!isPaused);
    setLogs(prev => [{
      time: new Date().toLocaleTimeString(),
      message: isPaused ? 'Trading resumed' : 'Trading paused',
      type: 'info'
    }, ...prev]);
  };

  const handleStop = () => {
    setIsRunning(false);
    setIsPaused(false);
    setConnectionStatus('disconnected');
    setLogs(prev => [{
      time: new Date().toLocaleTimeString(),
      message: 'Live trading stopped',
      type: 'info'
    }, ...prev]);
    if (onStop) onStop();
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
            🚀 Live Trading Dashboard
          </h1>
          <div className="text-sm text-gray-400">
            Real-Time Execution
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed mb-6">
          Execute live trading strategies with real-time monitoring and risk management
        </p>
      </motion.div>
      
      <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' :
                connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                'bg-red-500'
              }`} />
              <span className="text-sm text-gray-300">
                {connectionStatus === 'connected' ? 'Market Connected' :
                 connectionStatus === 'connecting' ? 'Connecting...' :
                 'Disconnected'}
              </span>
            </div>

            {/* Control Buttons */}
            <div className="flex gap-2">
              {!isRunning ? (
                <button
                  onClick={handleStart}
                  className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 transition-colors"
                >
                  <FaPlay className="inline mr-2" />
                  Start Trading
                </button>
              ) : (
                <>
                  <button
                    onClick={handlePause}
                    className="px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-colors"
                  >
                    {isPaused ? <FaPlay className="inline mr-2" /> : <FaPause className="inline mr-2" />}
                    {isPaused ? 'Resume' : 'Pause'}
                  </button>
                  <button
                    onClick={handleStop}
                    className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:from-red-600 hover:to-pink-600 transition-colors"
                  >
                    <FaStop className="inline mr-2" />
                    Stop
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/10"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Account Balance</p>
              <p className="text-2xl font-bold text-white">
                ${accountBalance.toLocaleString()}
              </p>
            </div>
            <FaDollarSign className="text-3xl text-blue-500 opacity-50" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`backdrop-blur-lg rounded-lg p-4 border border-white/10 ${pnl >= 0 ? 'bg-green-500/10' : 'bg-red-500/10'}`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">P&L Today</p>
              <p className={`text-2xl font-bold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${pnl.toFixed(2)}
              </p>
            </div>
            <FaChartLine className={`text-3xl opacity-50 ${pnl >= 0 ? 'text-green-500' : 'text-red-500'}`} />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/10"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Open Positions</p>
              <p className="text-2xl font-bold text-white">
                {positions.length}
              </p>
            </div>
            <FaChartLine className="text-3xl text-purple-500 opacity-50" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/10"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Trades</p>
              <p className="text-2xl font-bold text-white">
                {trades.length}
              </p>
            </div>
            <FaCheckCircle className="text-3xl text-indigo-500 opacity-50" />
          </div>
        </motion.div>
      </div>

      {/* Trading Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Trades */}
        <div className="bg-white/5 backdrop-blur-lg rounded-lg p-4 border border-white/10">
          <h3 className="font-semibold text-lg mb-3 text-white">
            Recent Trades
          </h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {trades.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No trades yet</p>
            ) : (
              trades.map((trade) => (
                <motion.div
                  key={trade.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-white/10 backdrop-blur-lg rounded p-3 border border-white/10"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <span className={`font-semibold ${trade.side === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.side}
                      </span>
                      <span className="mx-2 text-white">
                        {trade.quantity} {trade.symbol}
                      </span>
                      <span className="text-gray-400">
                        @ ${trade.price.toFixed(2)}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className={`font-semibold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.pnl >= 0 ? '+' : ''}{trade.pnl.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400">{trade.time}</div>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>

        {/* Activity Log */}
        <div className="bg-white/5 backdrop-blur-lg rounded-lg p-4 border border-white/10">
          <h3 className="font-semibold text-lg mb-3 text-white">
            Activity Log
          </h3>
          <div className="space-y-1 max-h-80 overflow-y-auto font-mono text-sm">
            {logs.map((log, index) => (
              <div
                key={index}
                className={`p-2 rounded ${
                  log.type === 'success' ? 'bg-green-500/20 text-green-400' :
                  log.type === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                  log.type === 'error' ? 'bg-red-500/20 text-red-400' :
                  'bg-white/10 text-gray-300'
                }`}
              >
                <span className="text-xs opacity-75">[{log.time}]</span>
                <span className="ml-2">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Warning */}
      {isRunning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg backdrop-blur-lg"
        >
          <div className="flex items-start gap-3">
            <FaExclamationTriangle className="text-yellow-600 mt-1" />
            <div>
              <p className="font-semibold text-yellow-400">
                Live Trading Active
              </p>
              <p className="text-sm text-yellow-300">
                Real money is at risk. Monitor your positions carefully and ensure proper risk management is in place.
              </p>
            </div>
          </div>
        </motion.div>
      )}
      </div>
    </div>
  );
};

export default LiveTrading;
