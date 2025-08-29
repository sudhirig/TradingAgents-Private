import React from 'react';
import { motion } from 'framer-motion';

const LandingPage = ({ onNavigate }) => {
  const features = [
    {
      title: "AI-Powered Strategy Generation",
      description: "Leverage GPT-4 and advanced LLMs to generate sophisticated trading strategies",
      icon: "🤖",
      color: "from-purple-500 to-pink-500"
    },
    {
      title: "122+ Technical Indicators",
      description: "Full TA-Lib integration with advanced technical analysis capabilities",
      icon: "📊",
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "Advanced Backtesting Engine",
      description: "15+ performance analyzers including Sharpe, Sortino, and Calmar ratios",
      icon: "⚡",
      color: "from-green-500 to-emerald-500"
    },
    {
      title: "Real-time Market Data",
      description: "Live integration with Alpha Vantage and Yahoo Finance APIs",
      icon: "📈",
      color: "from-orange-500 to-red-500"
    }
  ];

  const stats = [
    { label: "Strategies Generated", value: "10,000+", trend: "+12%" },
    { label: "Total Volume Traded", value: "$2.5M", trend: "+25%" },
    { label: "Average Returns", value: "18.5%", trend: "+5%" },
    { label: "Active Users", value: "1,200+", trend: "+30%" }
  ];

  return (
    <div className="relative min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-6">
        <div className="container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                AI-Powered
              </span>
              <br />
              <span className="text-white">Algorithmic Trading</span>
            </h1>
            
            <p className="text-base md:text-lg text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
              Harness the power of Large Language Models to create, backtest, and deploy 
              sophisticated trading strategies with institutional-grade analytics
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <button
                onClick={() => onNavigate('ai-builder')}
                className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold text-base hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 hover:shadow-2xl transition-all duration-300 shadow-lg"
              >
                🚀 Start Building Strategies
              </button>
              <button
                className="px-8 py-4 bg-transparent border-2 border-purple-400/50 text-purple-400 rounded-xl font-semibold text-base hover:bg-purple-400/10 hover:border-purple-400 hover:shadow-xl transition-all duration-300"
              >
                📹 Watch Demo
              </button>
              <button
                onClick={() => onNavigate('indicators')}
                className="px-8 py-4 bg-white/10 backdrop-blur-lg text-white rounded-xl font-semibold text-base hover:bg-white/20 hover:shadow-xl transition-all duration-300 border border-white/20"
              >
                📊 Explore Indicators
              </button>
            </div>

            {/* Live Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10"
                >
                  <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-xs text-gray-400 mb-2">{stat.label}</div>
                  <div className="text-xs text-green-400">📈 {stat.trend}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-7xl">
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-3xl font-bold text-center text-white mb-8"
          >
            Institutional-Grade Features
          </motion.h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="bg-white/5 backdrop-blur-lg rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition-all cursor-pointer"
                onClick={() => {
                  if (index === 0) onNavigate('ai-builder');
                  if (index === 1) onNavigate('indicators');
                  if (index === 2) onNavigate('analytics');
                  if (index === 3) onNavigate('market');
                }}
              >
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className={`text-lg font-semibold bg-gradient-to-r ${feature.color} bg-clip-text text-transparent mb-2`}>
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Technology Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-7xl">
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-3xl p-12 backdrop-blur-xl border border-white/10">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold text-white mb-4">
                  Powered by Advanced AI
                </h2>
                <p className="text-gray-300 mb-4 text-base leading-relaxed">
                  Our platform integrates cutting-edge Large Language Models to understand 
                  market dynamics, generate sophisticated strategies, and provide intelligent 
                  insights that adapt to changing market conditions.
                </p>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    GPT-4 powered strategy generation
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Natural language strategy descriptions
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    AI-optimized risk management
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Automated code generation and validation
                  </li>
                </ul>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-3xl opacity-30"></div>
                <div className="relative bg-black/50 backdrop-blur-xl rounded-2xl p-8 border border-white/10">
                  <pre className="text-green-400 text-sm overflow-x-auto">
{`# AI-Generated Strategy Example
class AIOptimizedStrategy(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('rsi_period', 14),
        ('risk_per_trade', 0.02),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.p.sma_period)
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)
        
    def next(self):
        if self.rsi < 30 and self.data.close[0] > self.sma[0]:
            size = self.broker.getcash() * self.p.risk_per_trade
            self.buy(size=size)`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 shadow-2xl"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Trade with AI?
            </h2>
            <p className="text-white/90 text-lg mb-8">
              Join thousands of traders using AI to build profitable strategies
            </p>
            <button
              onClick={() => onNavigate('ai-builder')}
              className="px-8 py-4 bg-white text-purple-600 rounded-xl font-bold text-lg hover:bg-gray-100 transform hover:scale-105 transition-all shadow-xl"
            >
              Get Started Now - It's Free
            </button>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
