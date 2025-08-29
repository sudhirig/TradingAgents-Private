import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState, AnalystConfig, LLMProvider, AnalysisSession, AgentStatus, AnalysisMessage, ToolCall, Report } from '../types';

interface AppStore extends AppState {
  // Actions
  setAnalysts: (analysts: AnalystConfig[]) => void;
  setLLMProviders: (providers: LLMProvider[]) => void;
  setCurrentSession: (session: AnalysisSession | null) => void;
  updateAgentStatus: (agentName: string, status: AgentStatus) => void;
  addMessage: (message: AnalysisMessage) => void;
  addToolCall: (toolCall: ToolCall) => void;
  addReport: (report: Report) => void;
  clearAnalysisData: () => void;
  setWSConnected: (connected: boolean) => void;
  setWSReconnecting: (reconnecting: boolean) => void;
  setLoading: (key: keyof AppState['loading'], loading: boolean) => void;
  setError: (error: string | null) => void;
  updateUIConfig: (config: Partial<AppState['ui']>) => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
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

      // Actions
      setAnalysts: (analysts) => set({ analysts }),
      
      setLLMProviders: (llmProviders) => set({ llmProviders }),
      
      setCurrentSession: (currentSession) => set({ currentSession }),
      
      updateAgentStatus: (agentName, status) =>
        set((state) => ({
          agentStatuses: {
            ...state.agentStatuses,
            [agentName]: status,
          },
        })),
      
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message].slice(-1000), // Keep last 1000 messages
        })),
      
      addToolCall: (toolCall) =>
        set((state) => ({
          toolCalls: [...state.toolCalls, toolCall].slice(-500), // Keep last 500 tool calls
        })),
      
      addReport: (report) =>
        set((state) => {
          const existingIndex = state.reports.findIndex(
            (r) => r.section_name === report.section_name && r.agent === report.agent
          );
          
          if (existingIndex >= 0) {
            // Update existing report
            const updatedReports = [...state.reports];
            updatedReports[existingIndex] = report;
            return { reports: updatedReports };
          } else {
            // Add new report
            return { reports: [...state.reports, report] };
          }
        }),
      
      clearAnalysisData: () =>
        set({
          currentSession: null,
          agentStatuses: {},
          messages: [],
          toolCalls: [],
          reports: [],
        }),
      
      setWSConnected: (wsConnected) => set({ wsConnected }),
      
      setWSReconnecting: (wsReconnecting) => set({ wsReconnecting }),
      
      setLoading: (key, loading) =>
        set((state) => ({
          loading: {
            ...state.loading,
            [key]: loading,
          },
        })),
      
      setError: (error) => set({ error }),
      
      updateUIConfig: (config) =>
        set((state) => ({
          ui: {
            ...state.ui,
            ...config,
          },
        })),
    }),
    {
      name: 'trading-agents-store',
      partialize: (state) => ({
        ui: state.ui,
        // Don't persist session data or connection state
      }),
    }
  )
);
