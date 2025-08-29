// API Types
export interface AnalystConfig {
  id: string;
  name: string;
  description: string;
  team: string;
  capabilities: string[];
  enabled: boolean;
}

export interface LLMProvider {
  id: string;
  display_name: string;
  models: LLMModel[];
  enabled: boolean;
}

export interface LLMModel {
  id: string;
  display_name: string;
  context_window: number;
  max_tokens: number;
}

export interface AnalysisRequest {
  company: string;
  trade_date: string;
  selected_analysts: string[];
  llm_provider: string;
  llm_model: string;
  research_depth: string;
}

export interface AnalysisSession {
  session_id: string;
  company: string;
  trade_date: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  selected_analysts: string[];
  llm_provider: string;
  model: string;
  research_depth: number;
  created_at: string;
  updated_at: string;
  progress?: number;
}

export interface AgentStatus {
  agent_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  current_task?: string;
}

export interface AnalysisMessage {
  timestamp: string;
  agent: string;
  message_type: 'info' | 'warning' | 'error' | 'success';
  content: string;
}

export interface ToolCall {
  timestamp: string;
  agent: string;
  tool_name: string;
  parameters: Record<string, any>;
  result?: any;
}

export interface Report {
  section_name: string;
  content: string;
  agent: string;
  timestamp: string;
}

// WebSocket Message Types
export interface WSMessage {
  type: 'agent_status' | 'message' | 'tool_call' | 'report' | 'error' | 'heartbeat';
  session_id: string;
  timestamp: string;
  data: any;
}

export interface WSAgentStatusMessage extends WSMessage {
  type: 'agent_status';
  data: AgentStatus;
}

export interface WSAnalysisMessage extends WSMessage {
  type: 'message';
  data: AnalysisMessage;
}

export interface WSToolCallMessage extends WSMessage {
  type: 'tool_call';
  data: ToolCall;
}

export interface WSReportMessage extends WSMessage {
  type: 'report';
  data: Report;
}

export interface WSErrorMessage extends WSMessage {
  type: 'error';
  data: {
    error: string;
    details?: string;
  };
}

export interface WSHeartbeatMessage extends WSMessage {
  type: 'heartbeat';
  data: {
    timestamp: string;
  };
}

// UI State Types
export interface UIConfig {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  autoScroll: boolean;
  messageFilter: string[];
}

export interface AppState {
  // Configuration
  analysts: AnalystConfig[];
  llmProviders: LLMProvider[];
  
  // Current Analysis
  currentSession: AnalysisSession | null;
  agentStatuses: Record<string, AgentStatus>;
  messages: AnalysisMessage[];
  toolCalls: ToolCall[];
  reports: Report[];
  
  // WebSocket
  wsConnected: boolean;
  wsReconnecting: boolean;
  
  // UI
  ui: UIConfig;
  
  // Loading states
  loading: {
    config: boolean;
    analysis: boolean;
  };
  
  // Error states
  error: string | null;
}
