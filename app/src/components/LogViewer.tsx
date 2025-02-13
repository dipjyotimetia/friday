import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  Header,
  LogContainer,
  LogEntry,
  LogViewerContainer,
  Status,
  Timestamp,
} from '../css/LogViewer';

interface LogEntry {
  id: string;
  message: string;
  timestamp: string;
  level?: 'info' | 'error' | 'warn';
}

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
    const ws = new WebSocket('ws://localhost:8000/ws/logs');
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
          socketRef.current = new WebSocket('ws://localhost:8000/ws/logs');
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
    <LogViewerContainer>
      <Header>
        <h3>Agent Logs</h3>
        <Status isConnected={isConnected}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </Status>
      </Header>
      <LogContainer ref={logContainerRef} onScroll={handleScroll}>
        {logs.map(({ id, message, timestamp, level }) => (
          <LogEntry key={id} level={level}>
            <Timestamp>{timestamp}</Timestamp>
            <span>{message}</span>
          </LogEntry>
        ))}
      </LogContainer>
    </LogViewerContainer>
  );
}
