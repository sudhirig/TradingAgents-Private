import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAppStore } from '../../store/useAppStore';

// Mock the store
vi.mock('../../store/useAppStore');

const mockUseAppStore = vi.mocked(useAppStore);

// Mock WebSocket
class MockWebSocket {
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState = 1; // WebSocket.OPEN

  constructor(public url: string) {}

  send = vi.fn();
  close = vi.fn();

  // Helper methods for testing
  simulateOpen() {
    this.readyState = 1; // WebSocket.OPEN
    this.onopen?.(new Event('open'));
  }

  simulateMessage(data: any) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  simulateClose() {
    this.readyState = 3; // WebSocket.CLOSED
    this.onclose?.(new CloseEvent('close'));
  }
}

// Store reference to mock instance
let mockWebSocketInstance: MockWebSocket;

describe('useWebSocket', () => {
  let mockWebSocket: MockWebSocket;
  const mockStore = {
    setWSConnected: vi.fn(),
    setWSReconnecting: vi.fn(),
    updateAgentStatus: vi.fn(),
    addMessage: vi.fn(),
    addToolCall: vi.fn(),
    addReport: vi.fn(),
    setError: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAppStore.mockReturnValue(mockStore as any);
    
    // Setup WebSocket mock
    global.WebSocket = vi.fn().mockImplementation((url) => {
      mockWebSocketInstance = new MockWebSocket(url);
      mockWebSocket = mockWebSocketInstance;
      return mockWebSocketInstance;
    }) as any;
  });

  it('establishes WebSocket connection', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8003/ws');
    expect(result.current.isConnected).toBe(false);
  });

  it('establishes WebSocket connection with session ID', () => {
    const { result } = renderHook(() => useWebSocket('test-session-123'));

    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8003/ws/test-session-123');
  });

  it('handles connection open', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
    });

    expect(mockStore.setWSConnected).toHaveBeenCalledWith(true);
    expect(mockStore.setWSReconnecting).toHaveBeenCalledWith(false);
  });

  it('handles agent status messages', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateMessage({
        type: 'agent_status',
        session_id: 'test-session',
        timestamp: '2025-08-28T03:40:00Z',
        data: {
          agent_name: 'Market Analyst',
          status: 'running',
          progress: 50,
          current_task: 'Analyzing market data',
        },
      });
    });

    expect(mockStore.updateAgentStatus).toHaveBeenCalledWith('Market Analyst', {
      agent_name: 'Market Analyst',
      status: 'running',
      progress: 50,
      current_task: 'Analyzing market data',
    });
  });

  it('handles analysis messages', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateMessage({
        type: 'message',
        session_id: 'test-session',
        timestamp: '2025-08-28T03:40:00Z',
        data: {
          timestamp: '2025-08-28T03:40:00Z',
          agent: 'Market Analyst',
          message_type: 'info',
          content: 'Starting market analysis...',
        },
      });
    });

    expect(mockStore.addMessage).toHaveBeenCalledWith({
      timestamp: '2025-08-28T03:40:00Z',
      agent: 'Market Analyst',
      message_type: 'info',
      content: 'Starting market analysis...',
    });
  });

  it('handles tool call messages', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateMessage({
        type: 'tool_call',
        session_id: 'test-session',
        timestamp: '2025-08-28T03:40:00Z',
        data: {
          timestamp: '2025-08-28T03:40:00Z',
          agent: 'Market Analyst',
          tool_name: 'get_stock_price',
          parameters: { ticker: 'TSLA' },
          result: { price: 250.50 },
        },
      });
    });

    expect(mockStore.addToolCall).toHaveBeenCalledWith({
      timestamp: '2025-08-28T03:40:00Z',
      agent: 'Market Analyst',
      tool_name: 'get_stock_price',
      parameters: { ticker: 'TSLA' },
      result: { price: 250.50 },
    });
  });

  it('handles report messages', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateMessage({
        type: 'report',
        session_id: 'test-session',
        timestamp: '2025-08-28T03:40:00Z',
        data: {
          section_name: 'market_report',
          content: '# Market Analysis\n\nTSLA is showing strong momentum...',
          agent: 'Market Analyst',
          timestamp: '2025-08-28T03:40:00Z',
        },
      });
    });

    expect(mockStore.addReport).toHaveBeenCalledWith({
      section_name: 'market_report',
      content: '# Market Analysis\n\nTSLA is showing strong momentum...',
      agent: 'Market Analyst',
      timestamp: '2025-08-28T03:40:00Z',
    });
  });

  it('handles error messages', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateMessage({
        type: 'error',
        session_id: 'test-session',
        timestamp: '2025-08-28T03:40:00Z',
        data: {
          error: 'Analysis failed',
          details: 'Connection timeout',
        },
      });
    });

    expect(mockStore.setError).toHaveBeenCalledWith('Analysis failed');
  });

  it('handles connection close', () => {
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateClose();
    });

    expect(mockStore.setWSConnected).toHaveBeenCalledWith(false);
  });

  it('sends messages when connected', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
    });

    const testMessage = { type: 'ping', data: 'test' };
    
    act(() => {
      result.current.sendMessage(testMessage);
    });

    expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(testMessage));
  });

  it('handles invalid JSON messages gracefully', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    renderHook(() => useWebSocket());

    act(() => {
      mockWebSocket.simulateOpen();
      mockWebSocket.onmessage?.(new MessageEvent('message', { data: 'invalid json' }));
    });

    expect(consoleSpy).toHaveBeenCalledWith('Failed to parse WebSocket message:', expect.any(Error));
    consoleSpy.mockRestore();
  });
});
