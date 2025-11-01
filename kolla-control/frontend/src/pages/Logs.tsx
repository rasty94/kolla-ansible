import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';
import { Search, Filter, Download, Play, Pause, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';

interface LogMessage {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  source?: string;
}

const LOG_LEVELS = ['all', 'debug', 'info', 'warning', 'error'] as const;
type LogLevel = typeof LOG_LEVELS[number];

const LOG_COLORS = {
  debug: 'text-gray-400',
  info: 'text-blue-400',
  warning: 'text-yellow-400',
  error: 'text-red-400'
};

const LOG_BG_COLORS = {
  debug: 'bg-gray-900',
  info: 'bg-blue-900',
  warning: 'bg-yellow-900',
  error: 'bg-red-900'
};

export const Logs: React.FC = () => {
  const { logs, isConnected } = useWebSocket();
  const [filteredLogs, setFilteredLogs] = useState<LogMessage[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLevel, setSelectedLevel] = useState<LogLevel>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // Filter logs based on search and level
  useEffect(() => {
    let filtered = logs;

    // Filter by level
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(log => log.level === selectedLevel);
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.source?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredLogs(filtered);
  }, [logs, searchTerm, selectedLevel]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && !isPaused && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, autoScroll, isPaused]);

  const handleScroll = () => {
    if (logsContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logsContainerRef.current;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
      setAutoScroll(isAtBottom);
    }
  };

  const clearLogs = () => {
    // This would typically call an API to clear logs on the server
    toast.success('Logs cleared');
  };

  const exportLogs = () => {
    const logText = filteredLogs.map(log =>
      `[${log.timestamp}] ${log.level.toUpperCase()}: ${log.message}${log.source ? ` (${log.source})` : ''}`
    ).join('\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kolla-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Logs exported');
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold">Real-time Logs</h1>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
            isConnected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-2 rounded-lg transition-colors ${
              isPaused ? 'bg-yellow-900 text-yellow-300' : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title={isPaused ? 'Resume logs' : 'Pause logs'}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </button>

          <button
            onClick={clearLogs}
            className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
            title="Clear logs"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={exportLogs}
            className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
            title="Export logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400"
            />
          </div>

          {/* Level Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value as LogLevel)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white"
            >
              {LOG_LEVELS.map(level => (
                <option key={level} value={level} className="bg-gray-700">
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <span>Total: {logs.length}</span>
          <span>Filtered: {filteredLogs.length}</span>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <span>Auto-scroll</span>
          </label>
        </div>
      </div>

      {/* Logs Container */}
      <div
        ref={logsContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-auto p-4 font-mono text-sm bg-gray-900"
      >
        {filteredLogs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="text-4xl mb-4">📋</div>
              <p>No logs to display</p>
              <p className="text-xs mt-2">
                {logs.length === 0 ? 'Waiting for log messages...' : 'Try adjusting your filters'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredLogs.map((log, index) => (
              <div
                key={index}
                className={`p-2 rounded border-l-4 ${
                  LOG_BG_COLORS[log.level] || 'bg-gray-800'
                } border-${log.level}-500 hover:bg-gray-800 transition-colors`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-xs text-gray-500 font-mono whitespace-nowrap">
                    {formatTimestamp(log.timestamp)}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    LOG_COLORS[log.level] || 'text-gray-400'
                  } bg-gray-800`}>
                    {log.level}
                  </span>
                  {log.source && (
                    <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                      {log.source}
                    </span>
                  )}
                  <span className="flex-1 text-gray-300 break-all">
                    {log.message}
                  </span>
                </div>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <span>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</span>
          <span>Auto-scroll: {autoScroll ? '✅ On' : '❌ Off'}</span>
          <span>Paused: {isPaused ? '⏸️ Yes' : '▶️ No'}</span>
        </div>
        <div>
          Showing {filteredLogs.length} of {logs.length} logs
        </div>
      </div>
    </div>
  );
};