'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { LogEntry } from '@/types';

interface UseWebSocketOptions {
  url?: string;
  maxLogs?: number;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  logs: LogEntry[];
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  clearLogs: () => void;
  connect: () => void;
  disconnect: () => void;
  error: string | null;
}

export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const defaultUrl = typeof window !== 'undefined' 
    ? (process.env.NODE_ENV === 'production'
        ? `wss://${window.location.host}/api/v1/ws/logs`
        : 'ws://localhost:8080/api/v1/ws/logs')
    : 'ws://localhost:8080/api/v1/ws/logs';

  const {
    url = defaultUrl,
    maxLogs = 100,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  console.log('WebSocket hook initialized with URL:', url, 'NODE_ENV:', process.env.NODE_ENV);

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    'connecting' | 'connected' | 'disconnected' | 'error'
  >('disconnected');
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    // Close any existing connection first
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    try {
      setConnectionStatus('connecting');
      setError(null);
      
      console.log('Attempting WebSocket connection to:', url);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;
        console.log('WebSocket connected for real-time logs');
      };

      ws.onmessage = (event) => {
        try {
          const logEntry: LogEntry = JSON.parse(event.data);

          // Validate log entry structure
          if (logEntry.timestamp && logEntry.message && logEntry.level) {
            // Filter out debug heartbeat messages from displaying
            if (
              logEntry.level === 'DEBUG' &&
              logEntry.source === 'websocket_heartbeat'
            ) {
              return; // Don't display heartbeat messages
            }

            setLogs((prevLogs) => {
              const newLogs = [...prevLogs, logEntry];
              // Keep only the last maxLogs entries
              return newLogs.slice(-maxLogs);
            });
          } else {
            console.warn('Invalid log entry received:', logEntry);
          }
        } catch (parseError) {
          console.error('Failed to parse WebSocket message:', parseError);
          console.error('Raw message:', event.data);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        wsRef.current = null;

        if (
          !event.wasClean &&
          autoReconnect &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current += 1;
          const delay =
            reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1); // Exponential backoff

          console.log(
            `WebSocket disconnected. Attempting reconnect ${reconnectAttemptsRef.current}/${maxReconnectAttempts} in ${delay}ms`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Failed to reconnect after maximum attempts');
          setConnectionStatus('error');
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        console.error('WebSocket URL was:', url);
        setError(`WebSocket connection error: ${event.type}`);
        setConnectionStatus('error');
      };
    } catch (connectError) {
      console.error('Failed to create WebSocket connection:', connectError);
      setError('Failed to create WebSocket connection');
      setConnectionStatus('error');
    }
  }, [url, autoReconnect, reconnectInterval, maxLogs]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('disconnected');
    setError(null);
    reconnectAttemptsRef.current = 0;
  }, []);

  // Auto-connect on mount and cleanup on unmount
  useEffect(() => {
    // Small delay to ensure component is fully mounted
    const connectTimer = setTimeout(() => {
      connect();
    }, 100);

    return () => {
      clearTimeout(connectTimer);
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    logs,
    isConnected,
    connectionStatus,
    clearLogs,
    connect,
    disconnect,
    error,
  };
}
