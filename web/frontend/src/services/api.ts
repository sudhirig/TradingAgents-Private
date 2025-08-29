import type { AnalystConfig, LLMProvider, AnalysisRequest, AnalysisSession } from '../types';

const API_BASE_URL = 'http://localhost:8003/api';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
    }

    return response.json();
  }

  // Configuration endpoints
  async getAnalysts(): Promise<AnalystConfig[]> {
    return this.request<AnalystConfig[]>('/config/analysts');
  }

  async getLLMProviders(): Promise<LLMProvider[]> {
    return this.request<LLMProvider[]>('/config/llm-providers');
  }

  async getFullConfig(): Promise<{
    analysts: AnalystConfig[];
    llm_providers: LLMProvider[];
    system: any;
    ui: any;
  }> {
    return this.request('/config/full');
  }

  // Analysis endpoints
  async startAnalysis(request: AnalysisRequest): Promise<{ session_id: string }> {
    return this.request('/analysis/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getAnalysisStatus(sessionId: string): Promise<AnalysisSession> {
    return this.request<AnalysisSession>(`/analysis/${sessionId}/status`);
  }

  async cancelAnalysis(sessionId: string): Promise<{ message: string }> {
    return this.request(`/analysis/${sessionId}/cancel`, {
      method: 'POST',
    });
  }

  async deleteAnalysis(sessionId: string): Promise<{ message: string }> {
    return this.request(`/analysis/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async retryAnalysis(sessionId: string): Promise<{ message: string }> {
    return this.request(`/analysis/${sessionId}/retry`, {
      method: 'POST',
    });
  }

  async listAnalysisSessions(): Promise<AnalysisSession[]> {
    return this.request<AnalysisSession[]>('/analysis/');
  }

  async getAnalysisReports(sessionId: string): Promise<any> {
    return this.request(`/analysis/${sessionId}/reports`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch('http://localhost:8003/health');
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    return this.healthCheck();
  }

  // WebSocket stats
  async getWebSocketStats(): Promise<{ active_connections: number; total_messages: number }> {
    return this.request('/ws/stats');
  }
}

export const apiService = new ApiService();
export { ApiService };
