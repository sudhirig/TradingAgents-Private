import React, { useMemo, useCallback, useRef, useEffect } from 'react';
import { FixedSizeList as List } from 'react-window';
import { useAppStore } from '../../store/useAppStore';

interface Message {
  id: string;
  type: string;
  content: string | any;
  timestamp: string;
  agent?: string;
}

interface VirtualizedMessageFeedProps {
  height?: number;
  className?: string;
}

interface MessageItemProps {
  index: number;
  style: React.CSSProperties;
  data: Message[];
}

const MessageItem: React.FC<MessageItemProps> = ({ index, style, data }) => {
  const message = data[index];
  
  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'info': return '💬';
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'tool_call': return '🔧';
      case 'reasoning': return '🧠';
      default: return '📝';
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'info': return 'text-blue-600 bg-blue-50';
      case 'success': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'error': return 'text-red-600 bg-red-50';
      case 'tool_call': return 'text-purple-600 bg-purple-50';
      case 'reasoning': return 'text-indigo-600 bg-indigo-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div style={style} className="px-4">
      <div className={`p-3 rounded-lg border ${getMessageColor(message.type)} mb-2`}>
        <div className="flex items-start gap-3">
          <span className="text-lg flex-shrink-0 mt-0.5">
            {getMessageIcon(message.type)}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium capitalize">
                {message.type.replace('_', ' ')}
              </span>
              <span className="text-xs opacity-75">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="text-sm break-words">
              {typeof message.content === 'string' ? (
                <p>{message.content}</p>
              ) : (
                <pre className="whitespace-pre-wrap font-mono text-xs bg-black/5 p-2 rounded">
                  {JSON.stringify(message.content, null, 2)}
                </pre>
              )}
            </div>
            {message.agent && (
              <div className="mt-2 text-xs opacity-75">
                Agent: {message.agent}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export const VirtualizedMessageFeed: React.FC<VirtualizedMessageFeedProps> = ({
  height = 400,
  className = ''
}) => {
  const { messages, ui } = useAppStore();
  const listRef = useRef<List>(null);
  
  // Filter messages based on UI filter settings
  const filteredMessages = useMemo(() => {
    if (!ui.messageFilter || ui.messageFilter.length === 0) {
      return messages;
    }
    return messages.filter((message) => ui.messageFilter.includes(message.message_type));
  }, [messages, ui.messageFilter]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (ui.autoScroll && listRef.current && filteredMessages.length > 0) {
      listRef.current.scrollToItem(filteredMessages.length - 1, 'end');
    }
  }, [filteredMessages.length, ui.autoScroll]);

  // Memoized item size calculation
  const getItemSize = useCallback(() => {
    return 120; // Base height for message items
  }, []);

  if (filteredMessages.length === 0) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">💬</div>
          <p>No messages yet</p>
          <p className="text-sm">Messages will appear here during analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <List
        ref={listRef}
        height={height}
        itemCount={filteredMessages.length}
        itemSize={getItemSize()}
        itemData={filteredMessages}
        overscanCount={5}
        className="scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100"
      >
        {MessageItem}
      </List>
    </div>
  );
};
