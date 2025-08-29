import React, { useState, useEffect } from 'react';
import './App.css';
import './App.modern.css';
import LandingPage from './components/LandingPage';
import AIStrategyBuilderNew from './components/AIStrategyBuilderNew';
import BacktestResults from './components/BacktestResults';
import SavedStrategies from './components/SavedStrategies';
import LiveTrading from './components/LiveTrading';
import MarketDataDashboard from './components/MarketDataDashboard';
import TechnicalIndicatorsDashboard from './components/TechnicalIndicatorsDashboard';
import PerformanceAnalytics from './components/PerformanceAnalytics';
import RiskManagement from './components/RiskManagement';
import AdvancedOrderManagement from './components/AdvancedOrderManagement';
import ManualTestSuite from './test/ManualTestSuite';
import ComponentTester from './test/ComponentTester';
import { ThemeProvider } from './context/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import aiService from './services/aiService';

// Normalize API backtest response into simplified shape for AIStrategyBuilder UI
const normalizeBacktestForUI = (apiResp) => {
  const perf = apiResp?.performance_metrics || apiResp?.results?.performance_metrics || {};
  const summary = apiResp?.results || apiResp || {};
  return {
    total_return: ((perf.total_return ?? summary.total_return ?? 0) * 100),
    sharpe_ratio: (perf.sharpe_ratio ?? summary.sharpe_ratio ?? 0),
    max_drawdown: (Math.abs(perf.max_drawdown ?? summary.max_drawdown ?? 0) * 100),
    win_rate: ((perf.win_rate ?? summary.win_rate ?? 0) * 100),
    total_trades: (perf.total_trades ?? summary.total_trades ?? 0),
    final_value: (summary.final_value ?? 0)
  };
};

function App() {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backtestResults, setBacktestResults] = useState(null);
  const [backtestError, setBacktestError] = useState(null);
  const [savedStrategies, setSavedStrategies] = useState([]);
  const [showTester, setShowTester] = useState(false);
  const [currentView, setCurrentView] = useState('landing');
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const [orderSettings, setOrderSettings] = useState({});
  const [riskSettings, setRiskSettings] = useState({});
  const [marketData, setMarketData] = useState({});

  useEffect(() => {
    // Initialize app - removed ideas count fetch to prevent console errors
    console.log('Statis AI Fund initialized');
  }, []);

  const loadStrategy = (strategy) => {
    setCode(strategy.code);
    setCurrentView('ai-builder');
    toast.success('Strategy loaded successfully!');
  };

  const deleteStrategy = async (id) => {
    try {
      const updatedStrategies = savedStrategies.filter(s => s.id !== id);
      setSavedStrategies(updatedStrategies);
      toast.success('Strategy deleted successfully!');
    } catch (error) {
      console.error('Error deleting strategy:', error);
      toast.error('Failed to delete strategy');
    }
  };

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    try {
      const response = await aiService.generateStrategy(formData.description || formData.prompt || '', formData);
      if (response.success) {
        setCode(response.code);
        toast.success('Strategy generated successfully!');
      } else {
        toast.error('Failed to generate strategy');
      }
    } catch (error) {
      console.error('Error generating strategy:', error);
      toast.error('Error generating strategy');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBacktest = async () => {
    if (!code) {
      alert('Please generate a strategy first');
      return;
    }

    setIsLoading(true);
    try {
      const resp = await aiService.backtestStrategy(code, {
        symbol: 'AAPL',
        start_date: '2023-01-01',
        end_date: '2024-01-01',
        initial_cash: 10000
      });
      if (!resp.success) {
        throw new Error(resp.user_message || resp.error || 'Backtest failed');
      }
      setBacktestResults({
        ...resp,
        ...normalizeBacktestForUI(resp),
        summary: resp.results || resp.backtest_results || resp,
        returns_over_time: resp.results?.returns_over_time || resp.returns_over_time,
        portfolio_value: resp.results?.portfolio_value || resp.portfolio_value
      });
      toast.success('Backtest completed successfully!');
    } catch (error) {
      console.error('Backtest error:', error);
      setBacktestError('Backtest failed: ' + error.message);
      toast.error(`Failed to run backtest: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdvancedBacktest = async () => {
    if (!code) {
      alert('Please generate a strategy first');
      return;
    }

    setIsLoading(true);
    setBacktestResults(null);
    setBacktestError(null);

    try {
      const resp = await aiService.advancedBacktest(code, {
        symbol: 'AAPL',
        start_date: '2023-01-01',
        end_date: '2024-01-01',
        initial_cash: 10000,
        commission: 0.001
      });
      if (!resp.success) {
        throw new Error(resp.user_message || resp.error || 'Advanced backtest failed');
      }
      setBacktestResults({
        ...resp,
        ...normalizeBacktestForUI(resp),
        summary: resp.results || resp.backtest_results || resp,
        returns_over_time: resp.results?.returns_over_time || resp.returns_over_time,
        portfolio_value: resp.results?.portfolio_value || resp.portfolio_value
      });
      toast.success('Advanced backtest completed successfully!');
    } catch (error) {
      console.error('Advanced backtest error:', error);
      setBacktestError('Failed to run advanced backtest: ' + error.message);
      toast.error('Failed to run advanced backtest: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNavigation = (view) => {
    setCurrentView(view);
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen text-white">
        <div className="animated-bg"></div>
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
        
        {showTester ? (
          <>
            <ComponentTester />
            <button
              onClick={() => setShowTester(false)}
              className="fixed top-4 right-4 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg shadow-lg z-50 text-sm font-medium transition-all"
            >
              ✕ Close Tester
            </button>
          </>
        ) : (
          <>
            {/* Modern Navigation Bar */}
            <nav className="modern-nav relative z-50">
              <div className="container mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <h1 className="text-lg font-semibold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Statis AI Fund
                      </h1>
                      <span className="px-2 py-0.5 text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-medium">
                        LLM Powered
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button 
                      onClick={() => handleNavigation('landing')}
                      className={`nav-btn ${currentView === 'landing' ? 'nav-btn-active' : ''}`}
                      aria-label="Navigate to home page"
                    >
                      Home
                    </button>
                    <button 
                      onClick={() => handleNavigation('ai-builder')}
                      className={`nav-btn ${currentView === 'ai-builder' ? 'nav-btn-active' : ''}`}
                      aria-label="Navigate to AI strategy builder"
                    >
                      AI Builder
                    </button>
                    <button 
                      onClick={() => handleNavigation('indicators')}
                      className={`nav-btn ${currentView === 'indicators' ? 'nav-btn-active' : ''}`}
                      aria-label="Navigate to technical indicators"
                    >
                      Indicators
                    </button>
                    <button 
                      onClick={() => handleNavigation('analytics')}
                      className={`nav-btn ${currentView === 'analytics' ? 'nav-btn-active' : ''}`}
                      aria-label="Navigate to performance analytics"
                    >
                      Analytics
                    </button>
                    <button 
                      onClick={() => handleNavigation('saved')}
                      className={`nav-btn ${currentView === 'saved' ? 'nav-btn-active' : ''}`}
                      aria-label="Navigate to saved strategies"
                    >
                      Saved
                    </button>
                    <ThemeToggle className="ml-2" />
                    <button 
                      onClick={() => handleNavigation('live')}
                      className={`btn-gradient nav-btn-primary ${currentView === 'live' ? 'nav-btn-primary-active' : ''}`}
                      aria-label="Navigate to live trading"
                    >
                      Live Trading
                    </button>
                    <button 
                      onClick={() => handleNavigation('test')}
                      className={`btn-outline nav-btn-primary ${currentView === 'test' ? 'nav-btn-primary-active' : ''}`}
                      aria-label="Navigate to UI test suite"
                    >
                      🧪 Test Suite
                    </button>
                  </div>
                </div>
              </div>
            </nav>

            <main className="relative z-10">
              {/* Dynamic Content Based on View */}
              {currentView === 'landing' ? (
                <LandingPage onNavigate={handleNavigation} />
              ) : currentView === 'test' ? (
                <ManualTestSuite />
              ) : (
                <MainInterface currentView={currentView} onNavigate={handleNavigation} />
              )}
            </main>
            {/* Test Components Button */}
            <button
              onClick={() => setShowTester(true)}
              className="fixed bottom-4 right-4 px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg shadow-lg z-50 text-xs font-medium transition-all transform hover:scale-105"
            >
              🧪 Test
            </button>
            <ToastContainer position="bottom-right" theme="dark" />
          </>
        )}
      </div>
    </ThemeProvider>
  );
}

// Main Interface Component
function MainInterface({ currentView, onNavigate }) {
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const [orderSettings, setOrderSettings] = useState({});
  const [riskSettings, setRiskSettings] = useState({});
  const [marketData, setMarketData] = useState({});
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backtestResults, setBacktestResults] = useState(null);
  const [backtestError, setBacktestError] = useState(null);
  const [savedStrategies, setSavedStrategies] = useState([]);

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    setBacktestError(null);
    try {
      const resp = await aiService.generateStrategy(formData.description || formData.prompt || '', formData);
      if (!resp.success || !resp.code) {
        throw new Error(resp.user_message || resp.error || 'Failed to generate strategy');
      }
      setCode(resp.code);
      toast.success('Strategy generated successfully!');
    } catch (error) {
      setBacktestError('Failed to generate strategy: ' + error.message);
      toast.error('Error generating strategy');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBacktest = async () => {
    if (!code) {
      setBacktestError('Please generate a strategy first');
      return;
    }
    setIsLoading(true);
    setBacktestError(null);
    try {
      const resp = await aiService.backtestStrategy(code, {
        symbol: 'AAPL',
        start_date: '2023-01-01',
        end_date: '2024-01-01',
        initial_cash: 10000
      });
      if (!resp.success) {
        throw new Error(resp.user_message || resp.error || 'Backtest failed');
      }
      setBacktestResults({
        ...resp,
        ...normalizeBacktestForUI(resp),
        summary: resp.results || resp.backtest_results || resp,
        returns_over_time: resp.results?.returns_over_time || resp.returns_over_time,
        portfolio_value: resp.results?.portfolio_value || resp.portfolio_value
      });
      toast.success('Backtest completed successfully!');
    } catch (error) {
      setBacktestError('Backtest failed: ' + error.message);
      toast.error('Failed to run backtest: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdvancedBacktest = async () => {
    if (!code) {
      setBacktestError('Please generate a strategy first');
      return;
    }
    setIsLoading(true);
    setBacktestError(null);
    try {
      const resp = await aiService.advancedBacktest(code, {
        symbol: 'AAPL',
        start_date: '2023-01-01',
        end_date: '2024-01-01',
        initial_cash: 10000,
        commission: 0.001
      });
      if (!resp.success) {
        throw new Error(resp.user_message || resp.error || 'Advanced backtest failed');
      }
      setBacktestResults({
        ...resp,
        ...normalizeBacktestForUI(resp),
        summary: resp.results || resp.backtest_results || resp,
        returns_over_time: resp.results?.returns_over_time || resp.returns_over_time,
        portfolio_value: resp.results?.portfolio_value || resp.portfolio_value
      });
      toast.success('Advanced backtest completed successfully!');
    } catch (error) {
      setBacktestError('Advanced backtest failed: ' + error.message);
      toast.error('Failed to run advanced backtest: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStrategy = (strategy) => {
    setCode(strategy.code || '');
    setBacktestResults(strategy.results || null);
    onNavigate('ai-builder');
  };

  const deleteStrategy = (id) => {
    setSavedStrategies(prev => prev.filter(s => s.id !== id));
  };

  return (
    <div className="container mx-auto px-6 py-8">
      {currentView === 'ai-builder' && (
        <AIStrategyBuilderNew 
          onIndicatorSelect={setSelectedIndicators}
          onOrderSettingsChange={setOrderSettings}
          onRiskSettingsChange={setRiskSettings}
          onGenerate={handleGenerate}
          isLoading={isLoading}
          code={code}
          onBacktest={handleBacktest}
          onAdvancedBacktest={handleAdvancedBacktest}
          backtestResults={backtestResults}
          backtestError={backtestError}
        />
      )}

      {currentView === 'indicators' && (
        <TechnicalIndicatorsDashboard 
          selectedIndicators={selectedIndicators}
          onIndicatorSelect={setSelectedIndicators}
          marketData={marketData}
        />
      )}

      {currentView === 'analytics' && (
        <PerformanceAnalytics 
          backtestResults={backtestResults}
          marketData={marketData}
        />
      )}

      {currentView === 'orders' && (
        <AdvancedOrderManagement 
          orderSettings={orderSettings}
          onSettingsChange={setOrderSettings}
        />
      )}

      {currentView === 'risk' && (
        <RiskManagement 
          riskSettings={riskSettings}
          onSettingsChange={setRiskSettings}
        />
      )}

      {currentView === 'market' && (
        <MarketDataDashboard 
          data={marketData}
          onDataUpdate={setMarketData}
        />
      )}

      {currentView === 'saved' && (
        <SavedStrategies 
          strategies={savedStrategies}
          onSelectStrategy={loadStrategy}
          onDeleteStrategy={deleteStrategy}
          onRunBacktest={(strategy) => {
            setCode(strategy.code || '');
            handleBacktest();
          }}
        />
      )}

      {currentView === 'live' && (
        <LiveTrading />
      )}
    </div>
  );
}

export default App;
