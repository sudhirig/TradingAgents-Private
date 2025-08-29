import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import { WSMessage, WSAgentStatusMessage, WSAnalysisMessage, WSToolCallMessage, WSReportMessage, WSErrorMessage } from '../types';

const WS_URL = 'ws://localhost:8003/ws';
const RECONNECT_INTERVAL = 3000;
const MAX_RECONNECT_ATTEMPTS = 10;

export const useWebSocket = (sessionId?: string) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false);

  const {
    setWSConnected,
    setWSReconnecting,
    updateAgentStatus,
    addMessage,
    addToolCall,
    addReport,
    setError,
  } = useAppStore();

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WSMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'agent_status':
          const agentStatusMsg = message as WSAgentStatusMessage;
          updateAgentStatus(agentStatusMsg.data.agent_name, agentStatusMsg.data);
          break;
          
        case 'message':
          const analysisMsg = message as WSAnalysisMessage;
          addMessage(analysisMsg.data);
          break;
          
        case 'tool_call':
          const toolCallMsg = message as WSToolCallMessage;
          addToolCall(toolCallMsg.data);
          break;
          
        case 'report':
          const reportMsg = message as WSReportMessage;
          addReport(reportMsg.data);
          break;
          
        case 'error':
          const errorMsg = message as WSErrorMessage;
          setError(errorMsg.data.error);
          console.error('WebSocket error:', errorMsg.data);
          break;
          
        case 'heartbeat':
          // Handle heartbeat - just acknowledge
          break;
          
        default:
          console.warn('Unknown WebSocket message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, [updateAgentStatus, addMessage, addToolCall, addReport, setError]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const url = sessionId ? `${WS_URL}/${sessionId}` : WS_URL;
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setWSConnected(true);
        setWSReconnecting(false);
        reconnectAttemptsRef.current = 0;
        setError(null);
      };

      wsRef.current.onmessage = handleMessage;

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setWSConnected(false);

        if (!isManualCloseRef.current && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          setWSReconnecting(true);
          reconnectAttemptsRef.current++;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
            connect();
          }, RECONNECT_INTERVAL);
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          setError('Failed to reconnect to WebSocket after maximum attempts');
          setWSReconnecting(false);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setError('Failed to establish WebSocket connection');
    }
  }, [sessionId, handleMessage, setWSConnected, setWSReconnecting, setError]);

  const disconnect = useCallback(() => {
    isManualCloseRef.current = true;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setWSConnected(false);
    setWSReconnecting(false);
  }, [setWSConnected, setWSReconnecting]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  // Auto-connect on mount and when sessionId changes
  useEffect(() => {
    isManualCloseRef.current = false;
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};
