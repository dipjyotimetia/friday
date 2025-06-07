"use client";

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useWebSocket } from '@/hooks/use-websocket';
import { LogEntry } from '@/types';
// ScrollArea component not available, using div with overflow

interface LogViewerProps {
  className?: string;
  maxHeight?: string;
  showConnectionStatus?: boolean;
  autoScroll?: boolean;
}

const levelColors = {
  DEBUG: 'bg-gray-100 text-gray-800',
  INFO: 'bg-blue-100 text-blue-800',
  WARNING: 'bg-yellow-100 text-yellow-800',
  ERROR: 'bg-red-100 text-red-800',
  CRITICAL: 'bg-red-200 text-red-900'
};

const connectionStatusColors = {
  connecting: 'bg-yellow-100 text-yellow-800',
  connected: 'bg-green-100 text-green-800',
  disconnected: 'bg-gray-100 text-gray-800',
  error: 'bg-red-100 text-red-800'
};

export function LogViewer({ 
  className = '', 
  maxHeight = '400px',
  showConnectionStatus = true,
  autoScroll = true
}: LogViewerProps) {
  const { logs, isConnected, connectionStatus, clearLogs, connect, disconnect, error } = useWebSocket();
  const [isExpanded, setIsExpanded] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const toggleExpanded = () => setIsExpanded(!isExpanded);

  if (!isExpanded) {
    return (
      <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
        <Button 
          onClick={toggleExpanded}
          variant="outline"
          className="shadow-lg"
          size="sm"
        >
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span>Logs ({logs.length})</span>
          </div>
        </Button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-4 right-4 z-50 w-96 ${className}`}>
      <Card className="shadow-xl">
        <div className="p-3 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-sm">Real-time Logs</h3>
              {showConnectionStatus && (
                <Badge 
                  variant="outline" 
                  className={connectionStatusColors[connectionStatus]}
                >
                  {connectionStatus}
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-1">
              <Button
                onClick={clearLogs}
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
              >
                Clear
              </Button>
              {!isConnected && (
                <Button
                  onClick={connect}
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                >
                  Reconnect
                </Button>
              )}
              <Button
                onClick={toggleExpanded}
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
              >
                ✕
              </Button>
            </div>
          </div>
          
          {error && (
            <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}
        </div>

        <div 
          ref={scrollAreaRef}
          className="h-96 overflow-y-auto"
          style={{ maxHeight }}
        >
          <div className="p-3 space-y-2">
            {logs.length === 0 ? (
              <div className="text-center text-gray-500 text-sm py-8">
                {isConnected ? 'Waiting for logs...' : 'Not connected to log stream'}
              </div>
            ) : (
              logs.map((log, index) => (
                <LogEntryComponent key={`${log.timestamp}-${index}`} log={log} />
              ))
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

interface LogEntryComponentProps {
  log: LogEntry;
}

function LogEntryComponent({ log }: LogEntryComponentProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div 
      className="border rounded p-2 text-xs hover:bg-gray-50 transition-colors cursor-pointer"
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start justify-between space-x-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <Badge 
              variant="outline" 
              className={`text-xs px-1 py-0 ${levelColors[log.level]}`}
            >
              {log.level}
            </Badge>
            <span className="text-gray-500 text-xs">
              {formatTimestamp(log.timestamp)}
            </span>
            {log.request_id && (
              <span className="text-gray-400 text-xs font-mono">
                {log.request_id.slice(-8)}
              </span>
            )}
          </div>
          <div className={`${isExpanded ? '' : 'truncate'} text-gray-900`}>
            {log.message}
          </div>
        </div>
      </div>
      
      {isExpanded && log.request_id && (
        <div className="mt-2 pt-2 border-t text-xs text-gray-500">
          <div><strong>Request ID:</strong> {log.request_id}</div>
          <div><strong>Source:</strong> {log.source}</div>
        </div>
      )}
    </div>
  );
}