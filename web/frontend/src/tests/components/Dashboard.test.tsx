import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { Dashboard } from '../../components/Dashboard/Dashboard';
import { useAppStore } from '../../store/useAppStore';

// Mock the store
vi.mock('../../store/useAppStore');
vi.mock('../../services/api');

const mockUseAppStore = vi.mocked(useAppStore);

describe('Dashboard', () => {
  beforeEach(() => {
    mockUseAppStore.mockReturnValue({
      analysts: [
        {
          id: 'market-analyst',
          name: 'Market Analyst',
          description: 'Analyzes market trends',
          team: 'Analysis Team',
          capabilities: ['market_analysis'],
          enabled: true,
        },
      ],
      llmProviders: [
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
      ],
      currentSession: null,
      agentStatuses: {},
      messages: [],
      wsConnected: true,
      loading: { config: false, analysis: false },
      error: null,
      setAnalysts: vi.fn(),
      setLLMProviders: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
    } as any);
  });

  it('renders dashboard with stats cards', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Analysts')).toBeInTheDocument();
      expect(screen.getByText('LLM Models')).toBeInTheDocument();
      expect(screen.getByText('Connection')).toBeInTheDocument();
    });
  });

  it('shows analysis form when no active session', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Start New Analysis')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    mockUseAppStore.mockReturnValue({
      ...mockUseAppStore(),
      loading: { config: true, analysis: false },
    } as any);

    render(<Dashboard />);
    
    expect(screen.getByText('Loading configuration...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockUseAppStore.mockReturnValue({
      ...mockUseAppStore(),
      error: 'Failed to load data',
    } as any);

    render(<Dashboard />);
    
    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
  });
});
