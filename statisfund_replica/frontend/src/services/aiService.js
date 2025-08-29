// AI Service for strategy generation and analysis
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AIService {
  constructor() {
    this.apiKey = process.env.REACT_APP_OPENAI_API_KEY || '';
    this.model = 'gpt-4';
  }

  // Generate trading strategy from prompt
  async generateStrategy(prompt, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: prompt, // Updated to match backend API
          symbols: options.symbols || ['SPY'],
          start_date: options.start_date || '2023-01-01',
          end_date: options.end_date || '2023-12-31',
          model: options.model || this.model,
          strategy_type: options.type || 'momentum',
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to generate strategy`);
      }

      const data = await response.json();
      
      // Enhanced error handling for backend API responses
      if (data.success === false && data.error) {
        throw new Error(data.error);
      }
      
      return {
        success: true,
        strategy: data.strategy,
        code: data.code || data.generated_code, // Handle different response formats
        description: data.description || data.strategy_description,
        parameters: data.parameters || data.strategy_params,
        // Handle rate limiting gracefully
        rate_limited: data.error && data.error.includes('rate limit')
      };
    } catch (error) {
      console.error('AI Service Error:', error);
      return {
        success: false,
        error: error.message,
        // Provide user-friendly error messages
        user_message: this._getUserFriendlyError(error.message)
      };
    }
  }

  // Analyze strategy performance
  async analyzeStrategy(code, historicalData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze-strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_code: code,
          historical_data: historicalData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze strategy');
      }

      return await response.json();
    } catch (error) {
      console.error('Analysis Error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get AI-powered market insights
  async getMarketInsights(symbols, timeframe = '1d') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/market-insights`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols,
          timeframe
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get market insights');
      }

      return await response.json();
    } catch (error) {
      console.error('Market Insights Error:', error);
      return {
        insights: [],
        recommendations: [],
        error: error.message
      };
    }
  }

  // Generate risk recommendations
  async getRiskRecommendations(portfolio, riskProfile) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/risk-recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          portfolio,
          risk_profile: riskProfile
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get risk recommendations');
      }

      return await response.json();
    } catch (error) {
      console.error('Risk Recommendations Error:', error);
      return {
        recommendations: [],
        risk_score: 0,
        adjustments: []
      };
    }
  }

  // Optimize strategy parameters
  async optimizeStrategy(strategyCode, constraints) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/optimize-strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_code: strategyCode,
          constraints
        })
      });

      if (!response.ok) {
        throw new Error('Failed to optimize strategy');
      }

      return await response.json();
    } catch (error) {
      console.error('Optimization Error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Check remaining API credits/ideas
  async getUsageStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/usage-stats`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get usage stats');
      }

      return await response.json();
    } catch (error) {
      console.error('Usage Stats Error:', error);
      return {
        ideas_remaining: 0,
        total_ideas: 0,
        error: error.message
      };
    }
  }


  // Stream real-time suggestions
  async* streamSuggestions(context) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stream-suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context)
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        yield JSON.parse(chunk);
      }
    } catch (error) {
      console.error('Stream Error:', error);
      yield { error: error.message };
    }
  }

  // Helper method for user-friendly error messages
  _getUserFriendlyError(errorMessage) {
    if (errorMessage.includes('rate limit') || errorMessage.includes('Ideas limit reached')) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    if (errorMessage.includes('Yahoo Finance API') || errorMessage.includes('yfinance')) {
      return 'Market data temporarily unavailable. Using backup data sources.';
    }
    if (errorMessage.includes('Failed to generate strategy')) {
      return 'Unable to generate strategy. Please try a different description.';
    }
    if (errorMessage.includes('Connection refused') || errorMessage.includes('network')) {
      return 'Connection issue. Please check your internet and try again.';
    }
    return 'An unexpected error occurred. Please try again.';
  }

  // Backtest strategy with enhanced error handling
  async backtestStrategy(strategyCode, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: strategyCode,
          strategy_code: strategyCode, // Backup field name
          symbol: options.symbol || 'AAPL',
          start_date: options.start_date || '2023-01-01',
          end_date: options.end_date || '2023-12-31',
          initial_cash: options.initial_cash || 10000,
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Backtest failed`);
      }

      const data = await response.json();
      
      // Enhanced error handling for backend API responses
      if (data.success === false && data.error) {
        throw new Error(data.error);
      }
      
      return {
        success: true,
        results: data.backtest_results || data.results || data,
        performance_metrics: data.performance_metrics || data.results?.performance_metrics,
        chart_path: data.chart_path || data.chart_url,
        trades: data.trades || data.trade_history,
        // Handle different response formats from backend improvements
        enhanced_metrics: data.enhanced_metrics || {}
      };
    } catch (error) {
      console.error('Backtest Error:', error);
      return {
        success: false,
        error: error.message,
        user_message: this._getUserFriendlyError(error.message)
      };
    }
  }

  // Advanced backtest with enhanced metrics
  async advancedBacktest(strategyCode, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/advanced-backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: strategyCode,
          symbol: options.symbol || 'AAPL',
          start_date: options.start_date || '2023-01-01',
          end_date: options.end_date || '2024-01-01',
          initial_cash: options.initial_cash || 10000,
          commission: options.commission || 0.001,
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Advanced backtest failed`);
      }

      const data = await response.json();

      if (data.success === false && data.error) {
        throw new Error(data.error);
      }

      return {
        success: true,
        results: data.backtest_results || data.results || data,
        performance_metrics: data.performance_metrics || data.results?.performance_metrics,
        chart_path: data.chart_path || data.chart_url,
        trades: data.trades || data.trade_history,
        enhanced_metrics: data.enhanced_metrics || {}
      };
    } catch (error) {
      console.error('Advanced Backtest Error:', error);
      return {
        success: false,
        error: error.message,
        user_message: this._getUserFriendlyError(error.message)
      };
    }
  }

  // Get Phase 2 advanced features
  async getAdvancedFeatures() {
    try {
      const [indicators, orderTypes, assets, brokers] = await Promise.all([
        fetch(`${API_BASE_URL}/api/indicators/advanced`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/orders/types`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/assets/supported`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/trading/brokers`).then(r => r.json())
      ]);

      return {
        success: true,
        indicators: indicators.indicators || indicators,
        orderTypes: orderTypes.order_types || orderTypes,
        assets: assets.supported_assets || assets,
        brokers: brokers.brokers || brokers
      };
    } catch (error) {
      console.error('Advanced Features Error:', error);
      return {
        success: false,
        error: error.message,
        // Provide fallback data for graceful degradation
        indicators: [],
        orderTypes: ['market', 'limit', 'stop'],
        assets: ['stocks'],
        brokers: []
      };
    }
  }
}

export default new AIService();
