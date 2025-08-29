
import { useState } from 'react';

interface Message {
  id: number;
  type: 'info' | 'success' | 'warning' | 'error';
  content: string;
  timestamp: string;
}

function App() {
  const [company, setCompany] = useState('TSLA');
  const [tradeDate, setTradeDate] = useState(new Date().toISOString().split('T')[0]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStarted, setAnalysisStarted] = useState(false);
  // Configuration state
  const [selectedAnalysts, setSelectedAnalysts] = useState<string[]>(['Market Analyst', 'Social Analyst', 'News Analyst', 'Fundamentals Analyst']);
  const [researchDepth, setResearchDepth] = useState(3);
  const [llmProvider, setLlmProvider] = useState('openai');
  const [quickThinkingLlm, setQuickThinkingLlm] = useState('gpt-4o-mini');
  const [deepThinkingLlm, setDeepThinkingLlm] = useState('o1');
  const [showDashboard, setShowDashboard] = useState(false);
  const [agentStatus, setAgentStatus] = useState({
    // Analyst Team (4 agents)
    'Market Analyst': 'pending',
    'Social Analyst': 'pending', 
    'News Analyst': 'pending',
    'Fundamentals Analyst': 'pending',
    // Research Team (3 agents)
    'Bull Researcher': 'pending',
    'Bear Researcher': 'pending',
    'Research Manager': 'pending',
    // Trading Team (1 agent)
    'Trader': 'pending',
    // Risk Management Team (3 agents)
    'Risky Analyst': 'pending',
    'Neutral Analyst': 'pending',
    'Safe Analyst': 'pending',
    // Portfolio Management Team (1 agent)
    'Portfolio Manager': 'pending'
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [toolCalls, setToolCalls] = useState<Array<{id: number, timestamp: string, tool_name: string, args: any}>>([]);
  const [reports, setReports] = useState<Record<string, string>>({});
  const [showReports, setShowReports] = useState(false);
  const [currentTeam, setCurrentTeam] = useState<string>('Analyst Team');

  const handleStartAnalysis = () => {
    const config = {
      company,
      tradeDate,
      selectedAnalysts,
      researchDepth,
      llmProvider,
      quickThinkingLlm,
      deepThinkingLlm
    };
    
    console.log('🚀 Starting analysis with configuration:', config);
    console.log('📊 Button clicked at:', new Date().toISOString());
    
    setIsAnalyzing(true);
    setAnalysisStarted(true);
    setCurrentTeam('Analyst Team'); // Start with first team
    
    // Show dashboard immediately
    setTimeout(() => {
      setShowDashboard(true);
      simulateAnalysisFlow();
    }, 500);
  };

  const simulateAnalysisFlow = () => {
    // Define team structure matching CLI
    const teams = {
      'Analyst Team': ['Market Analyst', 'Social Analyst', 'News Analyst', 'Fundamentals Analyst'],
      'Research Team': ['Bull Researcher', 'Bear Researcher', 'Research Manager'],
      'Trading Team': ['Trader'],
      'Risk Management': ['Risky Analyst', 'Neutral Analyst', 'Safe Analyst'],
      'Portfolio Management': ['Portfolio Manager']
    };
    
    let currentTeamIndex = 0;
    let currentAgentIndex = 0;
    const teamNames = Object.keys(teams);
    
    const processNextAgent = () => {
      if (currentTeamIndex < teamNames.length) {
        const teamName = teamNames[currentTeamIndex];
        const teamAgents = teams[teamName as keyof typeof teams];
        
        setCurrentTeam(teamName);
        
        if (currentAgentIndex < teamAgents.length) {
          const agent = teamAgents[currentAgentIndex];
          
          // Start agent
          setAgentStatus(prev => ({ ...prev, [agent]: 'in_progress' }));
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'info',
            content: `🔄 ${agent} starting ${teamName.toLowerCase()} analysis...`,
            timestamp: new Date().toISOString()
          }]);
          
          // Add tool calls simulation
          setTimeout(() => {
            const toolCall = {
              id: Date.now() + Math.random(),
              timestamp: new Date().toISOString(),
              tool_name: getToolForAgent(agent),
              args: getArgsForAgent(agent, company)
            };
            setToolCalls(prev => [...prev, toolCall]);
            
            setMessages(prev => [...prev, {
              id: Date.now() + Math.random(),
              type: 'info',
              content: `🔧 ${agent}: Using ${toolCall.tool_name}`,
              timestamp: new Date().toISOString()
            }]);
          }, 500);
          
          // Add reasoning messages
          setTimeout(() => {
            setMessages(prev => [...prev, {
              id: Date.now() + Math.random(),
              type: 'info',
              content: getReasoningForAgent(agent, company),
              timestamp: new Date().toISOString()
            }]);
          }, 1000);
          
          // Complete agent after delay
          setTimeout(() => {
            setAgentStatus(prev => ({ ...prev, [agent]: 'completed' }));
            setMessages(prev => [...prev, {
              id: Date.now() + Math.random(),
              type: 'success',
              content: `✅ ${agent} completed analysis`,
              timestamp: new Date().toISOString()
            }]);
            
            currentAgentIndex++;
            processNextAgent();
          }, 2500 + Math.random() * 1000);
        } else {
          // Team completed, move to next team
          currentTeamIndex++;
          currentAgentIndex = 0;
          processNextAgent();
        }
      } else {
        // All teams complete
        setTimeout(() => {
          setIsAnalyzing(false);
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'success',
            content: '🎉 Analysis complete! All agents finished successfully.',
            timestamp: new Date().toISOString()
          }]);
          
          // Generate complete CLI-matching reports
          setReports({
            'market_report': generateMarketReport(company, tradeDate),
            'sentiment_report': generateSentimentReport(company),
            'news_report': generateNewsReport(company),
            'fundamentals_report': generateFundamentalsReport(company),
            'investment_plan': generateInvestmentPlan(company),
            'trader_investment_plan': generateTraderPlan(company),
            'final_trade_decision': generateFinalDecision(company)
          });
          
          // Show reports after 2 seconds
          setTimeout(() => {
            setShowReports(true);
          }, 2000);
        }, 1000);
      }
    };
    
    processNextAgent();
  };

  // Helper functions for realistic simulation
  const getToolForAgent = (agent: string): string => {
    const toolMap: Record<string, string> = {
      'Market Analyst': 'get_stock_price',
      'Social Analyst': 'get_social_sentiment',
      'News Analyst': 'get_recent_news',
      'Fundamentals Analyst': 'get_financial_data',
      'Bull Researcher': 'analyze_bullish_factors',
      'Bear Researcher': 'analyze_bearish_factors',
      'Research Manager': 'synthesize_research',
      'Trader': 'calculate_position_size',
      'Risky Analyst': 'assess_high_risk_scenarios',
      'Neutral Analyst': 'evaluate_balanced_approach',
      'Safe Analyst': 'analyze_conservative_options',
      'Portfolio Manager': 'optimize_portfolio_allocation'
    };
    return toolMap[agent] || 'generic_analysis_tool';
  };

  const getArgsForAgent = (agent: string, ticker: string): any => {
    const baseArgs = { ticker, date: tradeDate };
    const agentSpecificArgs: Record<string, any> = {
      'Market Analyst': { ...baseArgs, indicators: ['RSI', 'MACD', 'SMA'] },
      'Social Analyst': { ...baseArgs, platforms: ['twitter', 'reddit', 'stocktwits'] },
      'News Analyst': { ...baseArgs, sources: ['reuters', 'bloomberg', 'wsj'] },
      'Fundamentals Analyst': { ...baseArgs, metrics: ['P/E', 'EPS', 'Revenue'] }
    };
    return agentSpecificArgs[agent] || baseArgs;
  };

  const getReasoningForAgent = (agent: string, ticker: string): string => {
    const reasoningMap: Record<string, string> = {
      'Market Analyst': `Analyzing ${ticker} technical indicators. Current price shows strong momentum with RSI at 68.2, approaching overbought territory but still within bullish range.`,
      'Social Analyst': `Monitoring social sentiment for ${ticker}. Twitter mentions up 12% with 68% positive sentiment. Key themes: autonomous driving progress, earnings expectations.`,
      'News Analyst': `Scanning recent news for ${ticker}. Found 23 relevant articles in past 24h. Major themes: production updates, regulatory developments, analyst upgrades.`,
      'Fundamentals Analyst': `Evaluating ${ticker} fundamentals. P/E ratio of 62.4 vs industry average of 28.5. Revenue growth of 15% YoY, margins improving.`,
      'Bull Researcher': `Building bullish case for ${ticker}. Strong technical momentum, positive sentiment, growing market share in EV sector.`,
      'Bear Researcher': `Examining bearish factors for ${ticker}. High valuation concerns, regulatory risks, increased competition in EV market.`,
      'Research Manager': `Synthesizing bull and bear perspectives. Weighing technical strength against valuation concerns for balanced recommendation.`,
      'Trader': `Calculating optimal position sizing for ${ticker}. Risk-adjusted position of 2% portfolio allocation recommended.`,
      'Risky Analyst': `Assessing high-risk scenarios. Potential 20% upside if earnings beat expectations and production targets met.`,
      'Neutral Analyst': `Evaluating balanced approach. Current price fairly valued, recommend small position with tight stops.`,
      'Safe Analyst': `Analyzing conservative strategy. High volatility suggests smaller position size, focus on risk management.`,
      'Portfolio Manager': `Optimizing portfolio allocation. ${ticker} fits growth allocation, recommend 2% position with defined exit strategy.`
    };
    return reasoningMap[agent] || `${agent} analyzing ${ticker} data and market conditions.`;
  };

  // Report generation functions matching CLI structure
  const generateMarketReport = (ticker: string, date: string): string => {
    return `# Market Analysis Report for ${ticker}

## Executive Summary
The market analysis for ${ticker} on ${date} reveals significant trading opportunities based on technical indicators and market sentiment.

## Key Findings
- **Current Price**: $248.50 (+2.3%)
- **Volume**: 45.2M shares (above average)
- **Market Cap**: $789.2B
- **P/E Ratio**: 62.4

## Technical Analysis
- RSI: 68.2 (approaching overbought)
- MACD: Bullish crossover detected
- Support Level: $240.00
- Resistance Level: $255.00

## Recommendation
**BUY** - Strong upward momentum with favorable technical indicators.`;
  };

  const generateSentimentReport = (ticker: string): string => {
    return `# Social Sentiment Analysis for ${ticker}

## Overall Sentiment: BULLISH 📈

### Social Media Metrics
- **Twitter Mentions**: 15,420 (+12% vs yesterday)
- **Positive Sentiment**: 68%
- **Negative Sentiment**: 22%
- **Neutral Sentiment**: 10%

### Key Themes
1. **Autonomous Driving Progress** - High positive sentiment
2. **Q3 Earnings Expectations** - Mixed sentiment
3. **Production Targets** - Cautiously optimistic

### Influencer Activity
- Major tech influencers showing increased interest
- Institutional sentiment remains positive`;
  };

  const generateNewsReport = (ticker: string): string => {
    return `# News Analysis for ${ticker}

## Recent Headlines (Past 24 Hours)
1. **${ticker} Announces Production Milestone** - Reuters
2. **Analyst Upgrades ${ticker} Price Target** - Bloomberg
3. **Regulatory Approval for New Model** - WSJ

## Key Developments
- Production capacity increased by 15%
- New manufacturing facility approved
- Partnership with major supplier announced

## Market Impact
- Stock price up 2.3% on news
- Volume 40% above average
- Analyst sentiment improving`;
  };

  const generateFundamentalsReport = (ticker: string): string => {
    return `# Fundamentals Analysis for ${ticker}

## Financial Metrics
- **Revenue**: $96.8B (TTM, +15% YoY)
- **Net Income**: $15.0B (+29% YoY)
- **Free Cash Flow**: $7.5B (+45% YoY)
- **Gross Margin**: 19.3% (improving)

## Valuation Metrics
- **P/E Ratio**: 62.4 vs Industry 28.5
- **PEG Ratio**: 1.8 (reasonable for growth)
- **Price/Sales**: 8.2x
- **EV/EBITDA**: 45.2x

## Balance Sheet Strength
- **Cash**: $29.1B
- **Total Debt**: $9.6B
- **Debt/Equity**: 0.17 (conservative)`;
  };

  const generateInvestmentPlan = (ticker: string): string => {
    return `# Research Team Investment Plan for ${ticker}

## Bull Researcher Analysis
Strong technical momentum with RSI at 68.2 and MACD bullish crossover. Social sentiment at 68% positive with increasing institutional interest. Production milestones being met consistently.

## Bear Researcher Analysis
Valuation concerns with P/E of 62.4 vs industry average of 28.5. Regulatory risks in key markets. Increased competition in EV sector may pressure margins.

## Research Manager Decision
After weighing bull and bear perspectives, recommend **MODERATE BUY** position. Technical strength and positive sentiment outweigh valuation concerns in current market environment. Risk-adjusted approach recommended.`;
  };

  const generateTraderPlan = (ticker: string): string => {
    return `# Trading Team Plan for ${ticker}

## Position Sizing
- **Recommended Allocation**: 2% of portfolio
- **Entry Strategy**: Scale in over 2-3 days
- **Risk Management**: 5% stop loss

## Technical Levels
- **Entry Zone**: $245-250
- **Target 1**: $265 (partial profit taking)
- **Target 2**: $275 (full exit)
- **Stop Loss**: $235

## Execution Strategy
1. Enter 50% position at current levels
2. Add remaining 50% on any dip to $245
3. Monitor volume and momentum indicators
4. Adjust stops as position moves in favor`;
  };

  const generateFinalDecision = (ticker: string): string => {
    return `# Portfolio Management Final Decision for ${ticker}

## RECOMMENDATION: **STRONG BUY** 🚀

### Position Details
- **Entry Price**: $248.50
- **Target Price**: $275.00 (+10.7%)
- **Stop Loss**: $235.00 (-5.4%)
- **Position Size**: 2% of portfolio
- **Time Horizon**: 2-4 weeks

### Risk Assessment
- **Risk Level**: MODERATE
- **Confidence Score**: 8.2/10
- **Expected Return**: +10.7%
- **Risk/Reward Ratio**: 1:2

### Execution Strategy
1. Enter position at market open
2. Monitor technical indicators daily
3. Take partial profits at $265
4. Full exit at target or stop loss

**Analysis completed at ${new Date().toLocaleString()}**`;
  };

  // Show reports view after analysis completion
  if (showReports) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#0f172a', 
        color: '#e2e8f0',
        fontFamily: 'Monaco, Consolas, monospace',
        fontSize: '14px',
        padding: '1rem'
      }}>
        {/* Header */}
        <div style={{ 
          borderBottom: '1px solid #334155', 
          paddingBottom: '1rem', 
          marginBottom: '2rem' 
        }}>
          <h1 style={{ 
            color: '#38bdf8', 
            fontSize: '24px', 
            margin: 0, 
            fontWeight: 'bold' 
          }}>
            📊 Analysis Reports - {company}
          </h1>
          <p style={{ 
            color: '#94a3b8', 
            margin: '0.5rem 0 0 0' 
          }}>
            Generated on {tradeDate} | All agents completed successfully
          </p>
        </div>

        {/* Reports Grid */}
        <div style={{ display: 'grid', gap: '2rem' }}>
          {Object.entries(reports).map(([reportKey, reportContent]) => (
            <div key={reportKey} style={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '1.5rem'
            }}>
              <h2 style={{
                color: '#fbbf24',
                fontSize: '18px',
                marginBottom: '1rem',
                textTransform: 'capitalize',
                borderBottom: '1px solid #374151',
                paddingBottom: '0.5rem'
              }}>
                {reportKey.replace('_', ' ')}
              </h2>
              <div style={{
                backgroundColor: '#0f172a',
                padding: '1rem',
                borderRadius: '4px',
                border: '1px solid #1e293b',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.6',
                maxHeight: '400px',
                overflowY: 'auto'
              }}>
                {reportContent.split('\n').map((line, index) => {
                  if (line.startsWith('# ')) {
                    return (
                      <div key={index} style={{ 
                        color: '#38bdf8', 
                        fontSize: '20px', 
                        fontWeight: 'bold',
                        marginBottom: '1rem',
                        marginTop: index > 0 ? '1.5rem' : '0'
                      }}>
                        {line.replace('# ', '')}
                      </div>
                    );
                  } else if (line.startsWith('## ')) {
                    return (
                      <div key={index} style={{ 
                        color: '#fbbf24', 
                        fontSize: '16px', 
                        fontWeight: 'bold',
                        marginBottom: '0.5rem',
                        marginTop: '1rem'
                      }}>
                        {line.replace('## ', '')}
                      </div>
                    );
                  } else if (line.startsWith('### ')) {
                    return (
                      <div key={index} style={{ 
                        color: '#a78bfa', 
                        fontSize: '14px', 
                        fontWeight: 'bold',
                        marginBottom: '0.5rem',
                        marginTop: '0.5rem'
                      }}>
                        {line.replace('### ', '')}
                      </div>
                    );
                  } else if (line.startsWith('- ')) {
                    return (
                      <div key={index} style={{ 
                        color: '#e2e8f0',
                        marginLeft: '1rem',
                        marginBottom: '0.25rem'
                      }}>
                        • {line.replace('- ', '')}
                      </div>
                    );
                  } else if (line.match(/^\d+\./)) {
                    return (
                      <div key={index} style={{ 
                        color: '#e2e8f0',
                        marginLeft: '1rem',
                        marginBottom: '0.25rem'
                      }}>
                        {line}
                      </div>
                    );
                  } else if (line.includes('**') && line.includes('**')) {
                    const parts = line.split('**');
                    return (
                      <div key={index} style={{ 
                        color: '#e2e8f0',
                        marginBottom: '0.5rem'
                      }}>
                        {parts.map((part, i) => 
                          i % 2 === 1 ? (
                            <span key={i} style={{ fontWeight: 'bold', color: '#10b981' }}>
                              {part}
                            </span>
                          ) : (
                            <span key={i}>{part}</span>
                          )
                        )}
                      </div>
                    );
                  } else if (line.trim()) {
                    return (
                      <div key={index} style={{ 
                        color: '#e2e8f0',
                        marginBottom: '0.5rem'
                      }}>
                        {line}
                      </div>
                    );
                  } else {
                    return <div key={index} style={{ height: '0.5rem' }} />;
                  }
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Buttons */}
        <div style={{ 
          marginTop: '2rem', 
          textAlign: 'center',
          borderTop: '1px solid #334155',
          paddingTop: '1rem',
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center'
        }}>
          <button 
            onClick={() => {
              setShowReports(false);
            }}
            style={{ 
              backgroundColor: '#374151', 
              color: '#e2e8f0', 
              padding: '0.75rem 1.5rem', 
              borderRadius: '0.375rem', 
              border: '1px solid #4b5563', 
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            ← Back to Dashboard
          </button>
          <button 
            onClick={() => {
              setShowReports(false);
              setShowDashboard(false);
              setAnalysisStarted(false);
              setIsAnalyzing(false);
              setMessages([]);
              setReports({});
              setToolCalls([]);
              setAgentStatus({
                'Market Analyst': 'pending',
                'Social Analyst': 'pending', 
                'News Analyst': 'pending',
                'Fundamentals Analyst': 'pending',
                'Bull Researcher': 'pending',
                'Bear Researcher': 'pending',
                'Research Manager': 'pending',
                'Trader': 'pending',
                'Risky Analyst': 'pending',
                'Neutral Analyst': 'pending',
                'Safe Analyst': 'pending',
                'Portfolio Manager': 'pending'
              });
            }}
            style={{ 
              backgroundColor: '#059669', 
              color: 'white', 
              padding: '0.75rem 1.5rem', 
              borderRadius: '0.375rem', 
              border: 'none', 
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            🔄 New Analysis
          </button>
        </div>
      </div>
    );
  }

  // Show CLI-like dashboard after analysis starts
  if (showDashboard) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#0f172a', 
        color: '#e2e8f0',
        fontFamily: 'Monaco, Consolas, monospace',
        fontSize: '14px',
        padding: '1rem'
      }}>
        {/* Header */}
        <div style={{ 
          borderBottom: '1px solid #334155', 
          paddingBottom: '1rem', 
          marginBottom: '1rem' 
        }}>
          <h1 style={{ 
            color: '#38bdf8', 
            fontSize: '24px', 
            margin: 0, 
            fontWeight: 'bold' 
          }}>
            🤖 TradingAgents Analysis Dashboard
          </h1>
          <p style={{ 
            color: '#94a3b8', 
            margin: '0.5rem 0 0 0' 
          }}>
            Company: {company} | Date: {tradeDate} | Status: {isAnalyzing ? 'Running' : 'Complete'}
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Agent Status Grid */}
          <div>
            <h2 style={{ 
              color: '#fbbf24', 
              fontSize: '18px', 
              marginBottom: '1rem',
              borderBottom: '1px solid #374151',
              paddingBottom: '0.5rem'
            }}>
              📊 Agent Status
            </h2>
            <div style={{ display: 'grid', gap: '0.5rem' }}>
              {Object.entries(agentStatus).map(([agent, status]) => (
                <div key={agent} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  padding: '0.5rem',
                  backgroundColor: status === 'completed' ? '#064e3b' : 
                                 status === 'in_progress' ? '#1e3a8a' : '#374151',
                  borderRadius: '4px',
                  border: status === 'in_progress' ? '1px solid #3b82f6' : 'none'
                }}>
                  <span>{agent}</span>
                  <span style={{ 
                    color: status === 'completed' ? '#10b981' : 
                           status === 'in_progress' ? '#3b82f6' : '#9ca3af'
                  }}>
                    {status === 'completed' ? '✅' : 
                     status === 'in_progress' ? '🔄' : '⏳'} {status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Messages & Tool Calls Feed */}
          <div>
            <h2 style={{ 
              color: '#fbbf24', 
              fontSize: '18px', 
              marginBottom: '1rem',
              borderBottom: '1px solid #374151',
              paddingBottom: '0.5rem'
            }}>
              💬 Live Messages & Tool Calls
            </h2>
            <div style={{ 
              height: '400px', 
              overflowY: 'auto',
              backgroundColor: '#1e293b',
              padding: '1rem',
              borderRadius: '4px',
              border: '1px solid #334155'
            }}>
              {messages.length === 0 && toolCalls.length === 0 ? (
                <p style={{ color: '#64748b', fontStyle: 'italic' }}>
                  Waiting for messages...
                </p>
              ) : (
                // Combine and sort messages and tool calls by timestamp
                [...messages.map(m => ({...m, itemType: 'message'})), 
                 ...toolCalls.map(t => ({...t, itemType: 'tool', type: 'info', content: `🔧 ${t.tool_name}: ${JSON.stringify(t.args)}`}))]
                  .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
                  .map((item) => (
                    <div key={item.id} style={{ 
                      marginBottom: '0.5rem',
                      padding: '0.5rem',
                      borderLeft: `3px solid ${
                        item.itemType === 'tool' ? '#f59e0b' :
                        item.type === 'success' ? '#10b981' :
                        item.type === 'error' ? '#ef4444' :
                        item.type === 'warning' ? '#f59e0b' : '#3b82f6'
                      }`,
                      backgroundColor: item.itemType === 'tool' ? '#1e1b0f' : '#0f172a'
                    }}>
                      <div style={{ 
                        fontSize: '12px', 
                        color: '#64748b', 
                        marginBottom: '0.25rem' 
                      }}>
                        {new Date(item.timestamp).toLocaleTimeString()} 
                        {item.itemType === 'tool' && <span style={{ color: '#f59e0b' }}> [TOOL]</span>}
                      </div>
                      <div style={{ color: '#e2e8f0', fontSize: '13px', lineHeight: '1.4' }}>
                        {item.content}
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>
        </div>

        {/* Back to Config Button */}
        <div style={{ 
          marginTop: '2rem', 
          textAlign: 'center',
          borderTop: '1px solid #334155',
          paddingTop: '1rem'
        }}>
          <button 
            onClick={() => {
              setShowDashboard(false);
              setAnalysisStarted(false);
              setIsAnalyzing(false);
              setMessages([]);
              setToolCalls([]);
              setAgentStatus({
                'Market Analyst': 'pending',
                'Social Analyst': 'pending', 
                'News Analyst': 'pending',
                'Fundamentals Analyst': 'pending',
                'Bull Researcher': 'pending',
                'Bear Researcher': 'pending',
                'Research Manager': 'pending',
                'Trader': 'pending',
                'Risky Analyst': 'pending',
                'Neutral Analyst': 'pending',
                'Safe Analyst': 'pending',
                'Portfolio Manager': 'pending'
              });
            }}
            style={{ 
              backgroundColor: '#374151', 
              color: '#e2e8f0', 
              padding: '0.75rem 1.5rem', 
              borderRadius: '0.375rem', 
              border: '1px solid #4b5563', 
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            ← Back to Configuration
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb', 
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ 
          fontSize: '3rem', 
          fontWeight: 'bold', 
          color: '#111827', 
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          TradingAgents
        </h1>
        <p style={{ 
          fontSize: '1.25rem', 
          color: '#6b7280', 
          marginBottom: '2rem',
          textAlign: 'center'
        }}>
          Multi-Agent Financial Analysis Platform
        </p>
        
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '0.5rem', 
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', 
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '600', 
            marginBottom: '1.5rem',
            color: '#111827'
          }}>
            🔧 Analysis Configuration
          </h2>
          
          {/* Step 1 & 2: Basic Info */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '0.5rem', 
              padding: '1rem' 
            }}>
              <h3 style={{ 
                fontSize: '1rem', 
                fontWeight: '600', 
                color: '#1f2937', 
                marginBottom: '0.5rem' 
              }}>
                Step 1: Ticker Symbol
              </h3>
              <input 
                type="text" 
                value={company}
                onChange={(e) => setCompany(e.target.value.toUpperCase())}
                disabled={isAnalyzing}
                placeholder="e.g., TSLA, AAPL, SPY"
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '0.375rem',
                  fontSize: '1rem',
                  backgroundColor: isAnalyzing ? '#f3f4f6' : 'white'
                }}
              />
            </div>
            
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '0.5rem', 
              padding: '1rem' 
            }}>
              <h3 style={{ 
                fontSize: '1rem', 
                fontWeight: '600', 
                color: '#1f2937', 
                marginBottom: '0.5rem' 
              }}>
                Step 2: Analysis Date
              </h3>
              <input 
                type="date" 
                value={tradeDate}
                onChange={(e) => setTradeDate(e.target.value)}
                disabled={isAnalyzing}
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '0.375rem',
                  fontSize: '1rem',
                  backgroundColor: isAnalyzing ? '#f3f4f6' : 'white'
                }}
              />
            </div>
          </div>

          {/* Step 3: Analysts Selection */}
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ 
              fontSize: '1rem', 
              fontWeight: '600', 
              color: '#1f2937', 
              marginBottom: '1rem' 
            }}>
              Step 3: Select Analysts Team
            </h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '0.75rem' 
            }}>
              {['Market Analyst', 'Social Analyst', 'News Analyst', 'Fundamentals Analyst'].map(analyst => (
                <label key={analyst} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  padding: '0.5rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  backgroundColor: '#f9fafb'
                }}>
                  <input 
                    type="checkbox" 
                    checked={selectedAnalysts.includes(analyst)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAnalysts([...selectedAnalysts, analyst]);
                      } else {
                        setSelectedAnalysts(selectedAnalysts.filter(a => a !== analyst));
                      }
                    }}
                    disabled={isAnalyzing}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <span style={{ fontSize: '0.875rem' }}>{analyst}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Step 4: Research Depth */}
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ 
              fontSize: '1rem', 
              fontWeight: '600', 
              color: '#1f2937', 
              marginBottom: '1rem' 
            }}>
              Step 4: Research Depth
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[
                { value: 1, label: 'Shallow', desc: 'Quick research, few debate rounds' },
                { value: 3, label: 'Medium', desc: 'Moderate debate and strategy discussion' },
                { value: 5, label: 'Deep', desc: 'Comprehensive research, in-depth debate' }
              ].map(option => (
                <label key={option.value} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  backgroundColor: '#f9fafb'
                }}>
                  <input 
                    type="radio" 
                    name="researchDepth"
                    value={option.value}
                    checked={researchDepth === option.value}
                    onChange={() => setResearchDepth(option.value)}
                    disabled={isAnalyzing}
                    style={{ marginRight: '0.75rem' }}
                  />
                  <div>
                    <div style={{ fontWeight: '500', fontSize: '0.875rem' }}>
                      {option.label}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                      {option.desc}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Step 5: LLM Provider */}
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ 
              fontSize: '1rem', 
              fontWeight: '600', 
              color: '#1f2937', 
              marginBottom: '1rem' 
            }}>
              Step 5: LLM Provider
            </h3>
            <select 
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              disabled={isAnalyzing}
              style={{ 
                width: '100%', 
                padding: '0.75rem', 
                border: '1px solid #d1d5db', 
                borderRadius: '0.375rem',
                fontSize: '1rem',
                backgroundColor: isAnalyzing ? '#f3f4f6' : 'white'
              }}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
              <option value="openrouter">Openrouter</option>
              <option value="ollama">Ollama</option>
            </select>
          </div>

          {/* Step 6: Thinking Agents */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '0.5rem', 
              padding: '1rem' 
            }}>
              <h3 style={{ 
                fontSize: '1rem', 
                fontWeight: '600', 
                color: '#1f2937', 
                marginBottom: '0.5rem' 
              }}>
                Quick-Thinking LLM
              </h3>
              <select 
                value={quickThinkingLlm}
                onChange={(e) => setQuickThinkingLlm(e.target.value)}
                disabled={isAnalyzing}
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  backgroundColor: isAnalyzing ? '#f3f4f6' : 'white'
                }}
              >
                <option value="gpt-4o-mini">GPT-4o-mini - Fast and efficient</option>
                <option value="claude-3-5-haiku-latest">Claude Haiku 3.5 - Fast inference</option>
                <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash-Lite - Low latency</option>
              </select>
            </div>
            
            <div style={{ 
              border: '1px solid #e5e7eb', 
              borderRadius: '0.5rem', 
              padding: '1rem' 
            }}>
              <h3 style={{ 
                fontSize: '1rem', 
                fontWeight: '600', 
                color: '#1f2937', 
                marginBottom: '0.5rem' 
              }}>
                Deep-Thinking LLM
              </h3>
              <select 
                value={deepThinkingLlm}
                onChange={(e) => setDeepThinkingLlm(e.target.value)}
                disabled={isAnalyzing}
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  backgroundColor: isAnalyzing ? '#f3f4f6' : 'white'
                }}
              >
                <option value="o1">o1 - Premier reasoning model</option>
                <option value="claude-sonnet-4-0">Claude Sonnet 4 - High performance</option>
                <option value="gemini-2.5-pro-preview-06-05">Gemini 2.5 Pro - Advanced reasoning</option>
              </select>
            </div>
          </div>
          
          <button 
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            style={{ 
              backgroundColor: isAnalyzing ? '#9ca3af' : '#2563eb', 
              color: 'white', 
              padding: '1rem 2rem', 
              borderRadius: '0.5rem', 
              border: 'none', 
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: isAnalyzing ? 'not-allowed' : 'pointer',
              width: '100%'
            }}
          >
            {isAnalyzing ? '🔄 Analyzing...' : '🚀 Start Multi-Agent Analysis'}
          </button>
        </div>
        
        {analysisStarted && (
          <div style={{ 
            backgroundColor: isAnalyzing ? '#dbeafe' : '#ecfdf5', 
            border: `1px solid ${isAnalyzing ? '#93c5fd' : '#a7f3d0'}`, 
            borderRadius: '0.5rem', 
            padding: '1rem',
            marginBottom: '1rem'
          }}>
            <p style={{ 
              color: isAnalyzing ? '#1e40af' : '#065f46', 
              fontWeight: '500', 
              margin: 0 
            }}>
              {isAnalyzing ? '🔄 Analysis in Progress' : '✅ Analysis Complete'}
            </p>
            <p style={{ 
              color: isAnalyzing ? '#2563eb' : '#047857', 
              fontSize: '0.875rem', 
              margin: '0.25rem 0 0 0' 
            }}>
              Company: {company} | Date: {tradeDate}
            </p>
          </div>
        )}
        
        <div style={{ 
          backgroundColor: '#ecfdf5', 
          border: '1px solid #a7f3d0', 
          borderRadius: '0.5rem', 
          padding: '1rem' 
        }}>
          <p style={{ 
            color: '#065f46', 
            fontWeight: '500', 
            margin: 0 
          }}>
            ✅ React Frontend Successfully Running
          </p>
          <p style={{ 
            color: '#047857', 
            fontSize: '0.875rem', 
            margin: '0.25rem 0 0 0' 
          }}>
            Server: http://localhost:5173 | Time: {new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
