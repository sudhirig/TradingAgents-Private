import { vi } from 'vitest';
import { ApiService } from '../../services/api';

// Mock fetch
global.fetch = vi.fn();

describe('ApiService', () => {
  let apiService: ApiService;

  beforeEach(() => {
    apiService = new ApiService();
    vi.clearAllMocks();
  });

  describe('getAnalysts', () => {
    it('fetches analysts successfully', async () => {
      const mockAnalysts = [
        {
          id: 'market-analyst',
          name: 'Market Analyst',
          description: 'Analyzes market trends',
          team: 'Analysis Team',
          capabilities: ['market_analysis'],
          enabled: true,
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysts,
      });

      const result = await apiService.getAnalysts();

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8003/api/config/analysts');
      expect(result).toEqual(mockAnalysts);
    });

    it('throws error on failed request', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      await expect(apiService.getAnalysts()).rejects.toThrow('HTTP error! status: 500');
    });
  });

  describe('getLLMProviders', () => {
    it('fetches LLM providers successfully', async () => {
      const mockProviders = [
        {
          id: 'openai',
          display_name: 'OpenAI',
          models: [
            {
              id: 'gpt-4',
              display_name: 'GPT-4',
              context_window: 8192,
              max_tokens: 4096,
            },
          ],
          enabled: true,
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockProviders,
      });

      const result = await apiService.getLLMProviders();

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8003/api/config/llm-providers');
      expect(result).toEqual(mockProviders);
    });
  });

  describe('startAnalysis', () => {
    it('starts analysis successfully', async () => {
      const analysisRequest = {
        company: 'TSLA',
        trade_date: '2025-08-28',
        selected_analysts: ['market-analyst'],
        llm_provider: 'openai',
        llm_model: 'gpt-4',
        research_depth: 'comprehensive' as const,
      };

      const mockResponse = {
        session_id: 'test-session-123',
        status: 'started',
        message: 'Analysis started successfully',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.startAnalysis(analysisRequest);

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8003/api/analysis/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getAnalysisStatus', () => {
    it('gets analysis status successfully', async () => {
      const sessionId = 'test-session-123';
      const mockStatus = {
        session_id: sessionId,
        status: 'running',
        progress: 50,
        agents: {},
        start_time: '2025-08-28T03:40:00Z',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatus,
      });

      const result = await apiService.getAnalysisStatus(sessionId);

      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8003/api/analysis/${sessionId}/status`);
      expect(result).toEqual(mockStatus);
    });
  });

  describe('getAnalysisReports', () => {
    it('gets analysis reports successfully', async () => {
      const sessionId = 'test-session-123';
      const mockReports = [
        {
          section_name: 'market_report',
          content: '# Market Analysis\n\nTSLA analysis...',
          agent: 'Market Analyst',
          timestamp: '2025-08-28T03:40:00Z',
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockReports,
      });

      const result = await apiService.getAnalysisReports(sessionId);

      expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8003/api/analysis/${sessionId}/reports`);
      expect(result).toEqual(mockReports);
    });
  });

  describe('getHealth', () => {
    it('gets health status successfully', async () => {
      const mockHealth = {
        status: 'healthy',
        timestamp: '2025-08-28T03:40:00Z',
        version: '1.0.0',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      });

      const result = await apiService.getHealth();

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8003/health');
      expect(result).toEqual(mockHealth);
    });
  });

  describe('getWebSocketStats', () => {
    it('gets WebSocket stats successfully', async () => {
      const mockStats = {
        active_connections: 2,
        total_messages_sent: 150,
        uptime_seconds: 3600,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      });

      const result = await apiService.getWebSocketStats();

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8003/api/websocket/stats');
      expect(result).toEqual(mockStats);
    });
  });

  describe('error handling', () => {
    it('handles network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.getHealth()).rejects.toThrow('Network error');
    });

    it('handles JSON parsing errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(apiService.getHealth()).rejects.toThrow('Invalid JSON');
    });
  });
});
