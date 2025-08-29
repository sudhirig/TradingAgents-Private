import { act, renderHook } from '@testing-library/react';
import { useAppStore } from '../../store/useAppStore';

describe('useAppStore', () => {
  beforeEach(() => {
    // Reset store state
    useAppStore.setState({
      analysts: [],
      llmProviders: [],
      currentSession: null,
      agentStatuses: {},
      messages: [],
      toolCalls: [],
      reports: [],
      wsConnected: false,
      wsReconnecting: false,
      ui: {
        theme: 'light',
        sidebarCollapsed: false,
        autoScroll: true,
        messageFilter: [],
      },
      loading: {
        config: false,
        analysis: false,
      },
      error: null,
    });
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useAppStore());

    expect(result.current.analysts).toEqual([]);
    expect(result.current.llmProviders).toEqual([]);
    expect(result.current.currentSession).toBeNull();
    expect(result.current.wsConnected).toBe(false);
    expect(result.current.ui.theme).toBe('light');
  });

  it('sets analysts', () => {
    const { result } = renderHook(() => useAppStore());
    const analysts = [
      {
        id: 'market-analyst',
        name: 'Market Analyst',
        description: 'Analyzes market trends',
        team: 'Analysis Team',
        capabilities: ['market_analysis'],
        enabled: true,
      },
    ];

    act(() => {
      result.current.setAnalysts(analysts);
    });

    expect(result.current.analysts).toEqual(analysts);
  });

  it('updates agent status', () => {
    const { result } = renderHook(() => useAppStore());
    const agentStatus = {
      agent_name: 'Market Analyst',
      status: 'running' as const,
      progress: 50,
      current_task: 'Analyzing data',
    };

    act(() => {
      result.current.updateAgentStatus('Market Analyst', agentStatus);
    });

    expect(result.current.agentStatuses['Market Analyst']).toEqual(agentStatus);
  });

  it('adds messages with limit', () => {
    const { result } = renderHook(() => useAppStore());

    // Add messages up to limit
    act(() => {
      for (let i = 0; i < 1005; i++) {
        result.current.addMessage({
          timestamp: new Date().toISOString(),
          agent: 'Test Agent',
          message_type: 'info',
          content: `Message ${i}`,
        });
      }
    });

    // Should be limited to 1000 messages
    expect(result.current.messages).toHaveLength(1000);
    expect(result.current.messages[0].content).toBe('Message 5');
  });

  it('adds and updates reports', () => {
    const { result } = renderHook(() => useAppStore());
    const report1 = {
      section_name: 'market_report',
      content: 'Initial market analysis',
      agent: 'Market Analyst',
      timestamp: '2025-08-28T03:40:00Z',
    };

    act(() => {
      result.current.addReport(report1);
    });

    expect(result.current.reports).toHaveLength(1);
    expect(result.current.reports[0]).toEqual(report1);

    // Update existing report
    const report2 = {
      section_name: 'market_report',
      content: 'Updated market analysis',
      agent: 'Market Analyst',
      timestamp: '2025-08-28T03:45:00Z',
    };

    act(() => {
      result.current.addReport(report2);
    });

    expect(result.current.reports).toHaveLength(1);
    expect(result.current.reports[0].content).toBe('Updated market analysis');
  });

  it('clears analysis data', () => {
    const { result } = renderHook(() => useAppStore());

    // Set some data first
    act(() => {
      result.current.updateAgentStatus('Test Agent', {
        agent_name: 'Test Agent',
        status: 'running',
      });
      result.current.addMessage({
        timestamp: new Date().toISOString(),
        agent: 'Test Agent',
        message_type: 'info',
        content: 'Test message',
      });
    });

    expect(result.current.agentStatuses).not.toEqual({});
    expect(result.current.messages).toHaveLength(1);

    act(() => {
      result.current.clearAnalysisData();
    });

    expect(result.current.currentSession).toBeNull();
    expect(result.current.agentStatuses).toEqual({});
    expect(result.current.messages).toEqual([]);
    expect(result.current.toolCalls).toEqual([]);
    expect(result.current.reports).toEqual([]);
  });

  it('updates UI config', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.updateUIConfig({
        theme: 'dark',
        sidebarCollapsed: true,
      });
    });

    expect(result.current.ui.theme).toBe('dark');
    expect(result.current.ui.sidebarCollapsed).toBe(true);
    expect(result.current.ui.autoScroll).toBe(true); // Should preserve other values
  });

  it('sets loading states', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setLoading('config', true);
    });

    expect(result.current.loading.config).toBe(true);
    expect(result.current.loading.analysis).toBe(false);

    act(() => {
      result.current.setLoading('analysis', true);
    });

    expect(result.current.loading.config).toBe(true);
    expect(result.current.loading.analysis).toBe(true);
  });

  it('sets WebSocket connection states', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setWSConnected(true);
    });

    expect(result.current.wsConnected).toBe(true);

    act(() => {
      result.current.setWSReconnecting(true);
    });

    expect(result.current.wsReconnecting).toBe(true);
  });

  it('sets and clears errors', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setError('Test error');
    });

    expect(result.current.error).toBe('Test error');

    act(() => {
      result.current.setError(null);
    });

    expect(result.current.error).toBeNull();
  });
});
