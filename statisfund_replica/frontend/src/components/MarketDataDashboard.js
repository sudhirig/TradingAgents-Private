import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const MarketDataDashboard = ({ marketData, onDataUpdate }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');
  const [selectedMarket, setSelectedMarket] = useState('stocks');
  const [watchlist, setWatchlist] = useState([
    { symbol: 'SPY', name: 'S&P 500', price: 445.67, change: 1.23, changePercent: 0.28, volume: '82.3M' },
    { symbol: 'QQQ', name: 'NASDAQ 100', price: 385.42, change: -2.15, changePercent: -0.55, volume: '45.7M' },
    { symbol: 'AAPL', name: 'Apple Inc.', price: 182.34, change: 3.45, changePercent: 1.93, volume: '54.2M' },
    { symbol: 'TSLA', name: 'Tesla Inc.', price: 245.78, change: -8.92, changePercent: -3.50, volume: '112.8M' },
    { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 482.15, change: 12.34, changePercent: 2.63, volume: '38.9M' }
  ]);

  const [marketIndices] = useState([
    { name: 'Dow Jones', value: 35678.45, change: 125.67, changePercent: 0.35, status: 'up' },
    { name: 'S&P 500', value: 4567.89, change: -23.45, changePercent: -0.51, status: 'down' },
    { name: 'NASDAQ', value: 14234.56, change: 89.12, changePercent: 0.63, status: 'up' },
    { name: 'Russell 2000', value: 1987.65, change: -12.34, changePercent: -0.62, status: 'down' }
  ]);

  const [sectorPerformance] = useState([
    { name: 'Technology', performance: 2.45, volume: '2.3B', leaders: 'AAPL, MSFT, NVDA' },
    { name: 'Healthcare', performance: -0.82, volume: '1.8B', leaders: 'JNJ, PFE, UNH' },
    { name: 'Finance', performance: 1.23, volume: '1.5B', leaders: 'JPM, BAC, WFC' },
    { name: 'Energy', performance: 3.67, volume: '982M', leaders: 'XOM, CVX, COP' },
    { name: 'Consumer', performance: -1.45, volume: '1.2B', leaders: 'AMZN, WMT, HD' }
  ]);

  const timeframes = ['1M', '5M', '15M', '1H', '4H', '1D', '1W', '1Mo'];
  const markets = ['stocks', 'crypto', 'forex', 'commodities', 'bonds'];

  const [livePrice, setLivePrice] = useState(445.67);
  useEffect(() => {
    const interval = setInterval(() => {
      setLivePrice(prev => prev + (Math.random() - 0.5) * 0.5);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const addToWatchlist = (symbol) => {
    // Implementation for adding symbol to watchlist
    console.log('Adding', symbol, 'to watchlist');
  };

  return (
    <div className="container mx-auto max-w-7xl px-6 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            📈 Real-Time Market Data
          </h1>
          <div className="text-sm text-gray-400">
            Live Data Feed
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          Live market data, indices, and sector performance tracking with real-time updates
        </p>
      </motion.div>

      {/* Market Indices */}
      <div className="grid lg:grid-cols-4 gap-4 mb-8">
        {marketIndices.map((index, i) => (
          <motion.div
            key={index.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
          >
            <div className="text-gray-400 text-sm">{index.name}</div>
            <div className="text-2xl font-bold text-white mt-1">
              {index.value.toLocaleString()}
            </div>
            <div className={`flex items-center mt-2 text-sm ${
              index.status === 'up' ? 'text-green-400' : 'text-red-400'
            }`}>
              <span className="mr-1">{index.status === 'up' ? '▲' : '▼'}</span>
              <span>{Math.abs(index.change).toFixed(2)}</span>
              <span className="ml-2">({Math.abs(index.changePercent).toFixed(2)}%)</span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Market Selection and Timeframe */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex space-x-2">
          {markets.map(market => (
            <button
              key={market}
              onClick={() => setSelectedMarket(market)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all ${
                selectedMarket === market
                  ? 'bg-purple-500 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {market}
            </button>
          ))}
        </div>
        <div className="flex space-x-1 ml-auto">
          {timeframes.map(tf => (
            <button
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                selectedTimeframe === tf
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Chart Area */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-semibold text-white">SPY - S&P 500 ETF</h2>
                <div className="flex items-center mt-1">
                  <span className="text-3xl font-bold text-white">
                    ${livePrice.toFixed(2)}
                  </span>
                  <span className="ml-3 text-green-400 flex items-center">
                    <span className="mr-1">▲</span>
                    <span>1.23 (0.28%)</span>
                  </span>
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-white/10 rounded-lg text-white hover:bg-white/20">
                  Buy
                </button>
                <button className="px-4 py-2 bg-white/10 rounded-lg text-white hover:bg-white/20">
                  Sell
                </button>
              </div>
            </div>

            {/* Placeholder for Chart */}
            <div className="h-80 bg-gradient-to-b from-purple-900/20 to-pink-900/20 rounded-xl flex items-center justify-center">
              <div className="text-gray-400">
                <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1-1H5a1 1 0 01-1-1V4z" />
                </svg>
                <p>Real-time chart will be rendered here</p>
              </div>
            </div>

            {/* Volume and Stats */}
            <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
              <div>
                <div className="text-gray-400 text-sm">Volume</div>
                <div className="text-white font-semibold">82.3M</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Day Range</div>
                <div className="text-white font-semibold">444.12 - 447.89</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">52W Range</div>
                <div className="text-white font-semibold">380.45 - 479.98</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Market Cap</div>
                <div className="text-white font-semibold">412.5B</div>
              </div>
            </div>
          </div>

          {/* Sector Performance */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 mt-6">
            <h3 className="text-lg font-semibold text-white mb-4">Sector Performance</h3>
            <div className="space-y-3">
              {sectorPerformance.map(sector => (
                <div key={sector.name} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-white font-medium">{sector.name}</span>
                      <span className={`text-sm ${
                        sector.performance > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {sector.performance > 0 ? '+' : ''}{sector.performance}%
                      </span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all ${
                          sector.performance > 0 ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(Math.abs(sector.performance) * 20, 100)}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-gray-400">Vol: {sector.volume}</span>
                      <span className="text-xs text-gray-400">{sector.leaders}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Watchlist and Orders */}
        <div className="space-y-6">
          {/* Watchlist */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">Watchlist</h3>
              <button className="text-purple-400 hover:text-purple-300 text-sm">
                + Add Symbol
              </button>
            </div>
            <div className="space-y-3">
              {watchlist.map(stock => (
                <div 
                  key={stock.symbol}
                  className="flex justify-between items-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                >
                  <div>
                    <div className="text-white font-semibold">{stock.symbol}</div>
                    <div className="text-xs text-gray-400">{stock.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-white">${stock.price}</div>
                    <div className={`text-xs ${
                      stock.change > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {stock.change > 0 ? '+' : ''}{stock.changePercent}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Movers */}
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Top Movers</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">NVDA</span>
                <span className="text-green-400">+5.23%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">AMD</span>
                <span className="text-green-400">+4.15%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">TSLA</span>
                <span className="text-red-400">-3.50%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">META</span>
                <span className="text-green-400">+2.87%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">GOOGL</span>
                <span className="text-red-400">-1.92%</span>
              </div>
            </div>
          </div>

          {/* Market Status */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Market Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">NYSE</span>
                <span className="text-green-400 font-semibold">OPEN</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">NASDAQ</span>
                <span className="text-green-400 font-semibold">OPEN</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Crypto</span>
                <span className="text-green-400 font-semibold">24/7</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Forex</span>
                <span className="text-green-400 font-semibold">OPEN</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="text-sm text-gray-400">Next Close</div>
              <div className="text-white font-semibold">4:00 PM EST</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketDataDashboard;
