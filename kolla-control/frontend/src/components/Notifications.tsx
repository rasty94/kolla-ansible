import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';

interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
}

const Notifications: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { logs } = useWebSocket();

  useEffect(() => {
    if (logs.length > 0) {
      const lastLog = logs[logs.length - 1];
      const newNotification: Notification = {
        id: Math.random().toString(36).substr(2, 9),
        message: lastLog.message,
        type: lastLog.level === 'error' ? 'error' : lastLog.level === 'warning' ? 'warning' : 'info',
        timestamp: new Date(),
      };
      
      setNotifications((prev) => {
        // Avoid duplicates based on message and timestamp proximity if needed
        // For now just add it
        return [newNotification, ...prev].slice(0, 50);
      });
      
      if (!isOpen) {
        setUnreadCount((prev) => prev + 1);
      }
    }
  }, [logs, isOpen]);

  const handleOpen = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setUnreadCount(0);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={handleOpen}
        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 relative"
      >
        <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Notifications
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No notifications
                </div>
              ) : (
                notifications.map((notification) => (
                  <div key={notification.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <p className="text-sm text-gray-900 dark:text-white">
                      {notification.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {notification.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Notifications;
