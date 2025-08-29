import { useState, useEffect, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  session_id: string;
  timestamp: string;
  data: any;
}

export const WebSocketTest = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [sessionId, setSessionId] = useState('test_session');
  const wsRef = useRef<WebSocket | null>(null);

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(`ws://localhost:8003/ws/${sessionId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('Received message:', message);
      setMessages(prev => [...prev.slice(-19), message]); // Keep last 20 messages
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    wsRef.current = ws;
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const sendMessage = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'test',
        message: 'Hello from frontend!',
        timestamp: new Date().toISOString()
      }));
    }
  };

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">🔌 Live WebSocket Test</h2>
      
      <div className="space-y-4">
        {/* Connection Controls */}
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="Session ID"
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          <button
            onClick={connect}
            disabled={connected}
            className={`px-4 py-2 rounded-md font-medium ${
              connected 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Connect
          </button>
          <button
            onClick={disconnect}
            disabled={!connected}
            className={`px-4 py-2 rounded-md font-medium ${
              !connected 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
          >
            Disconnect
          </button>
          <button
            onClick={sendMessage}
            disabled={!connected}
            className={`px-4 py-2 rounded-md font-medium ${
              !connected 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            Send Test Message
          </button>
        </div>

        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={`font-medium ${connected ? 'text-green-700' : 'text-red-700'}`}>
            {connected ? 'Connected' : 'Disconnected'}
          </span>
          {connected && (
            <span className="text-sm text-gray-500">
              ws://localhost:8003/ws/{sessionId}
            </span>
          )}
        </div>

        {/* Messages */}
        <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
          <h3 className="font-medium text-gray-700 mb-2">Live Messages ({messages.length})</h3>
          {messages.length === 0 ? (
            <p className="text-gray-500 text-sm">No messages yet. Connect to start receiving real-time updates.</p>
          ) : (
            <div className="space-y-2">
              {messages.map((message, index) => (
                <div key={index} className="bg-white p-3 rounded border text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-blue-600">{message.type}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(message.data, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
