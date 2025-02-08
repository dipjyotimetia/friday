import React, { useEffect, useState, useRef, useCallback } from 'react';
import styled from 'styled-components';

interface LogEntry {
  id: string;
  message: string;
  timestamp: string;
  level?: 'info' | 'error' | 'warn';
}

const LogViewerContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;

  h3 {
    margin: 0;
    color: #fff;
  }
`;

const Status = styled.span<{ isConnected: boolean }>`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  background: ${props => props.isConnected ? '#1b5e20' : '#b71c1c'};
  color: #fff;
`;

const LogContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9rem;
`;

const LogEntry = styled.div<{ level?: 'info' | 'error' | 'warn' }>`
  padding: 4px 0;
  line-height: 1.4;
  color: ${props => {
    switch (props.level) {
      case 'error': return '#f44336';
      case 'warn': return '#ffd700';
      default: return '#d4d4d4';
    }
  }};
`;

const Timestamp = styled.span`
  color: #888;
  margin-right: 8px;
  font-size: 0.8rem;
`;

export function LogViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  const appendLog = useCallback((newLog: LogEntry) => {
    setLogs(prev => {
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
          id: crypto.randomUUID()
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
      <LogContainer ref={logContainerRef}>
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