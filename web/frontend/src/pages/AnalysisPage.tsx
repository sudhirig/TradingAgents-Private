import React from 'react';
import { AgentStatusGrid } from '../components/Analysis/AgentStatusGrid';
import { MessageFeed } from '../components/Analysis/MessageFeed';
import { ReportRenderer } from '../components/Analysis/ReportRenderer';
import { ToolCallsViewer } from '../components/Analysis/ToolCallsViewer';
import { useAppStore } from '../store/useAppStore';

export const AnalysisPage: React.FC = () => {
  const { currentSession } = useAppStore();

  if (!currentSession) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No Active Analysis</h1>
          <p className="text-gray-600">Please start a new analysis from the dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Analysis: {currentSession.company}
          </h1>
          <p className="text-gray-600 mt-1">
            Trade Date: {currentSession.trade_date} • Model: {currentSession.model}
          </p>
        </div>
        <span className={`badge text-lg px-4 py-2 ${
          currentSession.status === 'completed' ? 'badge-success' :
          currentSession.status === 'running' ? 'badge-info' :
          currentSession.status === 'failed' ? 'badge-error' :
          'badge-warning'
        }`}>
          {currentSession.status}
        </span>
      </div>

      <AgentStatusGrid />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MessageFeed />
        <ToolCallsViewer />
      </div>

      <ReportRenderer />
    </div>
  );
};
