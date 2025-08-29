import React, { useEffect, useRef } from 'react';
import { MessageCircle, Filter, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const MessageFeed: React.FC = () => {
  const { messages, ui, updateUIConfig } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (ui.autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'info':
      default:
        return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-l-green-500 bg-green-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'error':
        return 'border-l-red-500 bg-red-50';
      case 'info':
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const filteredMessages = messages.filter(message => {
    if (ui.messageFilter.length === 0) return true;
    return ui.messageFilter.includes(message.message_type);
  });

  const messageTypes = ['info', 'success', 'warning', 'error'];
  const toggleFilter = (type: string) => {
    const newFilter = ui.messageFilter.includes(type)
      ? ui.messageFilter.filter(t => t !== type)
      : [...ui.messageFilter, type];
    updateUIConfig({ messageFilter: newFilter });
  };

  return (
    <div className="card h-96 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <MessageCircle className="h-5 w-5 text-gray-600" />
          <h2 className="text-xl font-semibold text-gray-900">Live Messages</h2>
          <span className="badge badge-info">{filteredMessages.length}</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Message Type Filters */}
          <div className="flex items-center space-x-1">
            <Filter className="h-4 w-4 text-gray-500" />
            {messageTypes.map(type => (
              <button
                key={type}
                onClick={() => toggleFilter(type)}
                className={`px-2 py-1 text-xs rounded-md transition-colors ${
                  ui.messageFilter.length === 0 || ui.messageFilter.includes(type)
                    ? `badge-${type === 'info' ? 'info' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'error'}`
                    : 'bg-gray-100 text-gray-400'
                }`}
                title={`Toggle ${type} messages`}
              >
                {type}
              </button>
            ))}
          </div>
          
          {/* Auto-scroll Toggle */}
          <button
            onClick={() => updateUIConfig({ autoScroll: !ui.autoScroll })}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              ui.autoScroll ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'
            }`}
            title="Toggle auto-scroll"
          >
            Auto-scroll
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-2">
        {filteredMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <MessageCircle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p>No messages to display</p>
              {ui.messageFilter.length > 0 && (
                <p className="text-sm mt-1">Try adjusting your filters</p>
              )}
            </div>
          </div>
        ) : (
          filteredMessages.map((message, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border-l-4 ${getMessageColor(message.message_type)} animate-fade-in`}
            >
              <div className="flex items-start space-x-2">
                {getMessageIcon(message.message_type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {message.agent}
                    </span>
                    <span className="text-xs text-gray-500">
                      {message.timestamp}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 break-words">
                    {message.content}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
