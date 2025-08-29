import React, { useEffect, useRef } from 'react';

const CodeDisplay = ({ 
  code, 
  onRunBacktest, 
  onRunAdvancedBacktest, 
  isBacktesting, 
  formData, 
  isStreaming, 
  streamingStatus,
  backtestConfig, 
  setBacktestConfig, 
  backtestLoading,
  partialCode 
}) => {
  const codeRef = useRef(null);
  
  // Auto-scroll to bottom when streaming
  useEffect(() => {
    if (isStreaming && codeRef.current) {
      codeRef.current.scrollTop = codeRef.current.scrollHeight;
    }
  }, [partialCode, isStreaming]);

  const displayCode = isStreaming ? (partialCode || '') : code;

  return (
    <div className="code-display">
      <div className="code-header">
        <h3>Generated Strategy Code</h3>
        {isStreaming && (
          <div className="streaming-badge">
            <div className="pulse-dot"></div>
            <span>Live Streaming</span>
          </div>
        )}
      </div>
      
      {isStreaming && (
        <div className="streaming-status">
          <div className="streaming-indicator">
            <div className="spinner"></div>
            <span>{streamingStatus || 'Generating Strategy...'}</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>
      )}
      
      {(displayCode || isStreaming) && (
        <div className="code-container">
          <div className="code-header-bar">
            <span className="code-language">Python</span>
            <button 
              className="copy-btn"
              onClick={() => navigator.clipboard.writeText(displayCode)}
              disabled={!displayCode}
            >
              Copy Code
            </button>
          </div>
          <pre className="code-block" ref={codeRef}>
            <code>{displayCode}</code>
            {isStreaming && <span className="cursor-blink">|</span>}
          </pre>
        </div>
      )}
      
      {code && !isStreaming && (
        <div className="backtest-config">
          <h4>Backtest Configuration</h4>
          <div className="config-grid">
            <div className="config-item">
              <label>Symbol:</label>
              <input
                type="text"
                value={backtestConfig.symbol}
                onChange={(e) => setBacktestConfig({...backtestConfig, symbol: e.target.value})}
                placeholder="AAPL"
              />
              <small className="symbol-note">⚠️ Real market data only - Yahoo Finance API may have rate limits</small>
            </div>
            <div className="config-item">
              <label>Start Date:</label>
              <input
                type="date"
                value={backtestConfig.start_date}
                onChange={(e) => setBacktestConfig({...backtestConfig, start_date: e.target.value})}
              />
            </div>
            <div className="config-item">
              <label>End Date:</label>
              <input
                type="date"
                value={backtestConfig.end_date}
                onChange={(e) => setBacktestConfig({...backtestConfig, end_date: e.target.value})}
              />
            </div>
            <div className="config-item">
              <label>Initial Cash:</label>
              <input
                type="number"
                value={backtestConfig.cash}
                onChange={(e) => setBacktestConfig({...backtestConfig, cash: parseFloat(e.target.value)})}
                placeholder="10000"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onRunBacktest}
              disabled={!code.trim() || isBacktesting}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isBacktesting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Running Backtest...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-10V4a1 1 0 00-1-1H5a1 1 0 00-1 1v16a1 1 0 001-1V4a1 1 0 00-1-1z" />
                  </svg>
                  Run Backtest
                </>
              )}
            </button>
            
            <button
              onClick={() => onRunAdvancedBacktest && onRunAdvancedBacktest()}
              disabled={!code.trim() || isBacktesting || !onRunAdvancedBacktest}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-2 rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              title="Phase 2: Advanced Analytics with 15+ analyzers, TA-Lib indicators, and enhanced order management"
            >
              {isBacktesting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Running...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Advanced Backtest
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeDisplay;
