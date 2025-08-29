import React from 'react';
import { ChevronLeft, ChevronRight, Home, Play, History, Settings, Users, Brain } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const Sidebar: React.FC = () => {
  const { ui, updateUIConfig, currentSession } = useAppStore();

  const toggleSidebar = () => {
    updateUIConfig({ sidebarCollapsed: !ui.sidebarCollapsed });
  };

  const menuItems = [
    { icon: Home, label: 'Dashboard', active: true },
    { icon: Play, label: 'New Analysis', active: false },
    { icon: History, label: 'History', active: false },
    { icon: Users, label: 'Analysts', active: false },
    { icon: Brain, label: 'Models', active: false },
    { icon: Settings, label: 'Settings', active: false },
  ];

  return (
    <aside className={`bg-gray-50 border-r border-gray-200 transition-all duration-300 ${
      ui.sidebarCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!ui.sidebarCollapsed && (
            <h2 className="text-lg font-semibold text-gray-900">Menu</h2>
          )}
          <button
            onClick={toggleSidebar}
            className="p-1 rounded-md hover:bg-gray-200 transition-colors"
            title={ui.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {ui.sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="p-2">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.label}>
                <button
                  className={`w-full flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    item.active
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                  title={ui.sidebarCollapsed ? item.label : undefined}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!ui.sidebarCollapsed && (
                    <span className="ml-3">{item.label}</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Current Session Info */}
      {currentSession && !ui.sidebarCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-500 mb-1">Current Session</div>
          <div className="text-sm font-medium text-gray-900 truncate">
            {currentSession.company}
          </div>
          <div className="text-xs text-gray-500">
            {currentSession.trade_date}
          </div>
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Progress</span>
              <span className="text-gray-700">{currentSession.progress || 0}%</span>
            </div>
            <div className="mt-1 bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-primary-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${currentSession.progress || 0}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
