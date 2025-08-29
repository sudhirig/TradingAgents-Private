import { Activity, Settings, Wifi, WifiOff } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const Header: React.FC = () => {
  const { wsConnected, wsReconnecting, currentSession, ui, updateUIConfig } = useAppStore();

  const getConnectionStatus = () => {
    if (wsReconnecting) return { icon: Activity, color: 'text-yellow-500', text: 'Reconnecting...' };
    if (wsConnected) return { icon: Wifi, color: 'text-green-500', text: 'Connected' };
    return { icon: WifiOff, color: 'text-red-500', text: 'Disconnected' };
  };

  const connectionStatus = getConnectionStatus();
  const ConnectionIcon = connectionStatus.icon;

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">TradingAgents</h1>
          {currentSession && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">•</span>
              <span className="text-sm font-medium text-gray-700">
                {currentSession.company} ({currentSession.trade_date})
              </span>
              <span className={`badge ${
                currentSession.status === 'completed' ? 'badge-success' :
                currentSession.status === 'running' ? 'badge-info' :
                currentSession.status === 'failed' ? 'badge-error' :
                'badge-warning'
              }`}>
                {currentSession.status}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <ConnectionIcon className={`h-4 w-4 ${connectionStatus.color}`} />
            <span className={`text-sm ${connectionStatus.color}`}>
              {connectionStatus.text}
            </span>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={() => updateUIConfig({ theme: ui.theme === 'light' ? 'dark' : 'light' })}
            className="btn-outline px-3 py-2"
            title="Toggle theme"
          >
            {ui.theme === 'light' ? '🌙' : '☀️'}
          </button>

          {/* Settings */}
          <button className="btn-outline px-3 py-2" title="Settings">
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
