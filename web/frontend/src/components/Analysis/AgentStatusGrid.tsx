import React from 'react';
import { CheckCircle, Clock, Activity, XCircle, User } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const AgentStatusGrid: React.FC = () => {
  const { agentStatuses, currentSession } = useAppStore();

  if (!currentSession || Object.keys(agentStatuses).length === 0) {
    return null;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'running':
        return <Activity className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'pending':
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'running':
        return 'border-blue-200 bg-blue-50';
      case 'failed':
        return 'border-red-200 bg-red-50';
      case 'pending':
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Agent Status</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <User className="h-4 w-4" />
          <span>{Object.keys(agentStatuses).length} agents</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Object.entries(agentStatuses).map(([agentName, status]) => (
          <div
            key={agentName}
            className={`p-4 rounded-lg border-2 transition-all duration-300 ${getStatusColor(status.status)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.status)}
                <span className="font-medium text-gray-900 text-sm">{agentName}</span>
              </div>
              <span className={`badge ${
                status.status === 'completed' ? 'badge-success' :
                status.status === 'running' ? 'badge-info' :
                status.status === 'failed' ? 'badge-error' :
                'badge-warning'
              }`}>
                {status.status}
              </span>
            </div>

            {status.current_task && (
              <div className="mb-2">
                <p className="text-xs text-gray-600 mb-1">Current Task:</p>
                <p className="text-xs text-gray-800 truncate" title={status.current_task}>
                  {status.current_task}
                </p>
              </div>
            )}

            {status.progress !== undefined && (
              <div>
                <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{status.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      status.status === 'completed' ? 'bg-green-500' :
                      status.status === 'running' ? 'bg-blue-500' :
                      status.status === 'failed' ? 'bg-red-500' :
                      'bg-gray-400'
                    }`}
                    style={{ width: `${status.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
