import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';

interface LogMessage {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  source?: string;
}

interface DeploymentProgress {
  deployment_id: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  progress: number;
  current_step: string;
  total_steps: number;
}

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  logs: LogMessage[];
  deploymentProgress: Record<string, DeploymentProgress>;
  subscribeToLogs: (callback: (log: LogMessage) => void) => () => void;
  subscribeToDeployment: (deploymentId: string, callback: (progress: DeploymentProgress) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [deploymentProgress, setDeploymentProgress] = useState<Record<string, DeploymentProgress>>({});

  useEffect(() => {
    const newSocket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      toast.success('Connected to server');
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      toast.error('Disconnected from server');
    });

    newSocket.on('log', (log: LogMessage) => {
      setLogs(prev => [...prev.slice(-99), log]); // Keep last 100 logs
    });

    newSocket.on('deployment:progress', (progress: DeploymentProgress) => {
      setDeploymentProgress(prev => ({
        ...prev,
        [progress.deployment_id]: progress
      }));
    });

    newSocket.on('error', (error: any) => {
      console.error('WebSocket error:', error);
      toast.error(`WebSocket error: ${error.message}`);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const subscribeToLogs = useCallback((callback: (log: LogMessage) => void) => {
    if (!socket) return () => {};
    
    socket.on('log', callback);
    
    return () => {
      socket.off('log', callback);
    };
  }, [socket]);

  const subscribeToDeployment = useCallback((deploymentId: string, callback: (progress: DeploymentProgress) => void) => {
    if (!socket) return () => {};
    
    socket.emit('subscribe:deployment', { deployment_id: deploymentId });
    
    const handler = (progress: DeploymentProgress) => {
      if (progress.deployment_id === deploymentId) {
        callback(progress);
      }
    };
    
    socket.on('deployment:progress', handler);
    
    return () => {
      socket.emit('unsubscribe:deployment', { deployment_id: deploymentId });
      socket.off('deployment:progress', handler);
    };
  }, [socket]);

  return (
    <WebSocketContext.Provider value={{
      socket,
      isConnected,
      logs,
      deploymentProgress,
      subscribeToLogs,
      subscribeToDeployment
    }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};
