import React, { useEffect, useState, useRef, useCallback } from 'react';

interface LogEntry {
  id: string;
  message: string;
  timestamp: string;
  level?: 'info' | 'error' | 'warn';
}

const API_URL = 'localhost:8080';

export function LogViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const socketRef = useRef<WebSocket | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  const handleScroll = useCallback(() => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
      setAutoScroll(isAtBottom);
    }
  }, []);

  const appendLog = useCallback((newLog: LogEntry) => {
    setLogs((prev) => {
      // Keep only last 1000 logs to prevent memory issues
      const updatedLogs = [...prev, newLog];
      return updatedLogs.slice(-1000);
    });
  }, []);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  useEffect(() => {
    const ws = new WebSocket(`ws://${API_URL}/api/v1/ws/logs`);
    socketRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (socketRef.current?.readyState === WebSocket.CLOSED) {
          socketRef.current = new WebSocket(`ws://${API_URL}/api/v1/ws/logs`);
          console.log('Attempting to reconnect...');
        }
      }, 3000);
    };

    ws.onmessage = (event) => {
      try {
        const logEntry: LogEntry = JSON.parse(event.data);
        appendLog({
          ...logEntry,
          timestamp: new Date().toISOString(),
          id: crypto.randomUUID(),
        });
      } catch (error) {
        console.error('Failed to parse log message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [appendLog]);

  return (
    <div className="flex flex-col h-96 w-full bg-primary-800 rounded-2xl overflow-hidden border border-primary-600 shadow-xl backdrop-blur-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 md:rounded-xl">
      <div className="flex justify-between items-center p-5 glass border-b border-primary-600 backdrop-blur-md">
        <h3 className="m-0 text-primary-100 bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent font-bold tracking-wide">
          Agent Logs
        </h3>
        <span className={`px-5 py-2 rounded-2xl text-sm font-medium shadow-md transition-all duration-300 ${
          isConnected 
            ? 'bg-gradient-to-r from-green-600 to-green-700 text-white' 
            : 'bg-gradient-to-r from-red-600 to-red-700 text-white'
        }`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <div 
        ref={logContainerRef} 
        onScroll={handleScroll}
        className="flex-1 h-full overflow-y-auto p-6 font-mono text-sm scrollbar-thin scrollbar-thumb-accent-500 scrollbar-track-primary-800 md:p-4"
      >
        {logs.map(({ id, message, timestamp, level }) => (
          <div 
            key={id} 
            className={`py-2 leading-relaxed transition-all duration-200 rounded-lg hover:bg-primary-700 hover:px-2 hover:translate-x-1 hover:shadow-sm ${
              level === 'error' ? 'text-secondary-500' : 
              level === 'warn' ? 'text-yellow-400' : 'text-primary-100'
            }`}
          >
            <span className="text-primary-300 mr-4 text-xs opacity-80">{timestamp}</span>
            <span>{message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
