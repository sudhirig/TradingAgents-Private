import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../store/useAppStore';

interface PerformanceMetrics {
  websocketConnections: number;
  activeSessions: number;
  messageRatePerSecond: number;
  errorRatePerSecond: number;
  averageResponseTimeMs: number;
  totalMessagesInWindow: number;
  totalErrorsInWindow: number;
  memoryUsage?: {
    used: number;
    total: number;
    percentage: number;
  };
}

interface PerformanceMonitorProps {
  className?: string;
  refreshInterval?: number;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  className = '',
  refreshInterval = 5000
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { wsConnected } = useAppStore();

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/metrics/performance');
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
          setError(null);
        } else {
          throw new Error('Failed to fetch metrics');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up interval
    const interval = setInterval(fetchMetrics, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const formatNumber = (num: number, decimals: number = 1): string => {
    return num.toFixed(decimals);
  };


  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    unit?: string;
    status?: 'good' | 'warning' | 'error';
    icon: string;
  }> = ({ title, value, unit = '', status = 'good', icon }) => {
    const statusColors = {
      good: 'border-green-200 bg-green-50',
      warning: 'border-yellow-200 bg-yellow-50',
      error: 'border-red-200 bg-red-50'
    };

    const textColors = {
      good: 'text-green-700',
      warning: 'text-yellow-700',
      error: 'text-red-700'
    };

    return (
      <div className={`p-4 rounded-lg border ${statusColors[status]}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">{title}</span>
          <span className="text-lg">{icon}</span>
        </div>
        <div className={`text-2xl font-bold ${textColors[status]}`}>
          {value}{unit}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-700">
            <span>❌</span>
            <span className="font-medium">Performance Monitoring Error</span>
          </div>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <span className="text-4xl">📊</span>
          <p>No performance data available</p>
        </div>
      </div>
    );
  }

  // Determine status based on metrics
  const connectionStatus = wsConnected ? 'good' : 'error';
  const messageRateStatus = metrics.messageRatePerSecond > 10 ? 'warning' : 'good';
  const errorRateStatus = metrics.errorRatePerSecond > 1 ? 'error' : 
                         metrics.errorRatePerSecond > 0.1 ? 'warning' : 'good';
  const responseTimeStatus = metrics.averageResponseTimeMs > 1000 ? 'error' :
                            metrics.averageResponseTimeMs > 500 ? 'warning' : 'good';

  return (
    <div className={`p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Performance Monitor</h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          title="WebSocket Connections"
          value={metrics.websocketConnections}
          status={connectionStatus}
          icon="🔌"
        />
        <MetricCard
          title="Active Sessions"
          value={metrics.activeSessions}
          status="good"
          icon="👥"
        />
        <MetricCard
          title="Message Rate"
          value={formatNumber(metrics.messageRatePerSecond)}
          unit="/sec"
          status={messageRateStatus}
          icon="💬"
        />
        <MetricCard
          title="Error Rate"
          value={formatNumber(metrics.errorRatePerSecond, 2)}
          unit="/sec"
          status={errorRateStatus}
          icon="❌"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <MetricCard
          title="Avg Response Time"
          value={formatNumber(metrics.averageResponseTimeMs)}
          unit="ms"
          status={responseTimeStatus}
          icon="⏱️"
        />
        <MetricCard
          title="Messages (Window)"
          value={metrics.totalMessagesInWindow}
          status="good"
          icon="📨"
        />
        <MetricCard
          title="Errors (Window)"
          value={metrics.totalErrorsInWindow}
          status={metrics.totalErrorsInWindow > 0 ? 'warning' : 'good'}
          icon="⚠️"
        />
      </div>

      {metrics.memoryUsage && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Memory Usage</h4>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    metrics.memoryUsage.percentage > 80 ? 'bg-red-500' :
                    metrics.memoryUsage.percentage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${metrics.memoryUsage.percentage}%` }}
                ></div>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              {formatNumber(metrics.memoryUsage.used / 1024 / 1024)} MB / 
              {formatNumber(metrics.memoryUsage.total / 1024 / 1024)} MB
              ({formatNumber(metrics.memoryUsage.percentage)}%)
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleTimeString()} • 
        Refreshes every {refreshInterval / 1000}s
      </div>
    </div>
  );
};
