import React, { useState } from 'react';
import { Wrench, ChevronDown, ChevronRight, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const ToolCallsViewer: React.FC = () => {
  const { toolCalls } = useAppStore();
  const [expandedCalls, setExpandedCalls] = useState<Set<number>>(new Set());

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedCalls);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedCalls(newExpanded);
  };

  if (toolCalls.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-32 text-gray-500">
          <div className="text-center">
            <Wrench className="h-8 w-8 mx-auto mb-2 text-gray-300" />
            <p>No tool calls yet</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-4">
        <Wrench className="h-5 w-5 text-gray-600" />
        <h2 className="text-xl font-semibold text-gray-900">Tool Calls</h2>
        <span className="badge badge-info">{toolCalls.length}</span>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {toolCalls.map((toolCall, index) => (
          <div key={index} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleExpanded(index)}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  {expandedCalls.has(index) ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </button>
                
                <div className="flex items-center space-x-2">
                  {toolCall.result ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <Clock className="h-4 w-4 text-yellow-500" />
                  )}
                  <span className="font-medium text-gray-900">{toolCall.tool_name}</span>
                  <span className="text-sm text-gray-600">by {toolCall.agent}</span>
                </div>
              </div>
              
              <span className="text-xs text-gray-500">{toolCall.timestamp}</span>
            </div>

            {expandedCalls.has(index) && (
              <div className="mt-3 space-y-3">
                {/* Parameters */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Parameters:</h4>
                  <pre className="bg-gray-800 text-green-400 p-2 rounded text-xs overflow-x-auto font-mono">
                    {JSON.stringify(toolCall.parameters, null, 2)}
                  </pre>
                </div>

                {/* Result */}
                {toolCall.result && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Result:</h4>
                    <pre className="bg-gray-800 text-blue-400 p-2 rounded text-xs overflow-x-auto font-mono max-h-32">
                      {typeof toolCall.result === 'string' 
                        ? toolCall.result 
                        : JSON.stringify(toolCall.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
