import React, { useEffect } from 'react';
import { XCircle, Users, Brain, Activity, Clock } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { ApiService } from '../../services/api';
import { AgentStatusGrid } from '../Analysis/AgentStatusGrid';
import { MessageFeed } from '../Analysis/MessageFeed';
import { AnalysisForm } from '../Analysis/AnalysisForm';

export const Dashboard: React.FC = () => {
  const {
    analysts,
    llmProviders,
    currentSession,
    agentStatuses,
    messages,
    wsConnected,
    loading,
    error,
    setAnalysts,
    setLLMProviders,
    setLoading,
    setError,
  } = useAppStore();

  const apiService = new ApiService();

  useEffect(() => {
    const loadConfig = async () => {
      setLoading('config', true);
      try {
        const [analystsData, providersData] = await Promise.all([
          apiService.getAnalysts(),
          apiService.getLLMProviders(),
        ]);
        setAnalysts(analystsData);
        setLLMProviders(providersData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load configuration');
      } finally {
        setLoading('config', false);
      }
    };

    loadConfig();
  }, []);

  const getStatusCounts = () => {
    const statuses = Object.values(agentStatuses);
    return {
      pending: statuses.filter(s => s.status === 'pending').length,
      running: statuses.filter(s => s.status === 'running').length,
      completed: statuses.filter(s => s.status === 'completed').length,
      failed: statuses.filter(s => s.status === 'failed').length,
    };
  };

  const statusCounts = getStatusCounts();
  const totalModels = llmProviders.reduce((acc, provider) => acc + provider.models.length, 0);

  if (loading.config) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading configuration...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <XCircle className="h-8 w-8 mx-auto mb-4 text-red-500" />
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn-primary px-4 py-2"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Monitor your trading analysis sessions and system status
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Analysts</p>
              <p className="text-2xl font-bold text-gray-900">{analysts.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Brain className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">LLM Models</p>
              <p className="text-2xl font-bold text-gray-900">{totalModels}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Connection</p>
              <p className="text-2xl font-bold text-gray-900">
                {wsConnected ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Messages</p>
              <p className="text-2xl font-bold text-gray-900">{messages.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Current Session or Analysis Form */}
      {currentSession ? (
        <div className="space-y-6">
          <AgentStatusGrid />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MessageFeed />
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Session Details</h2>
                <span className={`badge ${
                  currentSession.status === 'completed' ? 'badge-success' :
                  currentSession.status === 'running' ? 'badge-info' :
                  currentSession.status === 'failed' ? 'badge-error' :
                  'badge-warning'
                }`}>
                  {currentSession.status}
                </span>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Company</p>
                  <p className="font-medium">{currentSession.company}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Trade Date</p>
                  <p className="font-medium">{currentSession.trade_date}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Model</p>
                  <p className="font-medium">{currentSession.model}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Research Depth</p>
                  <p className="font-medium">{currentSession.research_depth} rounds</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <AnalysisForm />
      )}

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Analysts</h2>
          <div className="space-y-3">
            {analysts.slice(0, 5).map((analyst) => (
              <div key={analyst.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{analyst.name}</p>
                  <p className="text-sm text-gray-600">{analyst.team}</p>
                </div>
                <span className={`badge ${analyst.enabled ? 'badge-success' : 'badge-error'}`}>
                  {analyst.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            ))}
            {analysts.length > 5 && (
              <p className="text-sm text-gray-500 pt-2">
                +{analysts.length - 5} more analysts available
              </p>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">LLM Providers</h2>
          <div className="space-y-3">
            {llmProviders.map((provider) => (
              <div key={provider.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{provider.display_name}</p>
                  <p className="text-sm text-gray-600">{provider.models.length} models</p>
                </div>
                <span className={`badge ${provider.enabled ? 'badge-success' : 'badge-error'}`}>
                  {provider.enabled ? 'Available' : 'Unavailable'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
