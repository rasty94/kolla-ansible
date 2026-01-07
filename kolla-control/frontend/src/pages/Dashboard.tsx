
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Server, 
  Activity, 
  AlertCircle, 
  CheckCircle,
  Rocket,
  Clock,
  TrendingUp
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface MetricsData {
  total_deployments: number;
  active_deployments: number;
  total_hosts: number;
  failed_deployments: number;
  avg_deployment_time: number;
  success_rate: number;
  recent_activity: Array<{
    timestamp: string;
    cpu: number;
    memory: number;
    deployments: number;
  }>;
}

const Dashboard: React.FC = () => {
  const { data: metrics, isLoading } = useQuery<MetricsData>({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/v1/metrics/dashboard`);
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Deployments',
      value: metrics?.total_deployments || 0,
      icon: Activity,
      color: 'blue',
      trend: '+12% from last month',
    },
    {
      name: 'Active Deployments',
      value: metrics?.active_deployments || 0,
      icon: Clock,
      color: 'yellow',
      trend: 'Currently running',
    },
    {
      name: 'Total Hosts',
      value: metrics?.total_hosts || 0,
      icon: Server,
      color: 'green',
      trend: '+5 new this week',
    },
    {
      name: 'Success Rate',
      value: `${metrics?.success_rate || 0}%`,
      icon: CheckCircle,
      color: 'emerald',
      trend: '+2.5% from last week',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
    emerald: 'bg-emerald-500',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your OpenStack deployments.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.name}
                  </p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-500 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    {stat.trend}
                  </p>
                </div>
                <div className={`p-3 rounded-full ${colorClasses[stat.color as keyof typeof colorClasses]}/10`}>
                  <Icon className={`w-6 h-6 ${colorClasses[stat.color as keyof typeof colorClasses].replace('bg-', 'text-')}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Activity Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              System Activity
            </h2>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Last 24 hours
            </p>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={metrics?.recent_activity || []}>
              <defs>
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
              <XAxis 
                dataKey="timestamp" 
                stroke="#6b7280"
                tick={{ fill: '#6b7280' }}
              />
              <YAxis stroke="#6b7280" tick={{ fill: '#6b7280' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                  color: '#fff'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="cpu" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorCpu)" 
                strokeWidth={2}
                name="CPU (%)"
              />
              <Area 
                type="monotone" 
                dataKey="memory" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#colorMemory)" 
                strokeWidth={2}
                name="Memory (%)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Deployments & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Deployments */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Deployments
          </h2>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      OpenStack deployment #{i}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      2 hours ago
                    </p>
                  </div>
                </div>
                <span className="px-2 py-1 text-xs font-medium text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30 rounded">
                  Success
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <button className="p-4 text-left bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors">
              <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400 mb-2" />
              <p className="text-sm font-medium text-gray-900 dark:text-white">New Deploy</p>
            </button>
            <button className="p-4 text-left bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 rounded-lg transition-colors">
              <Server className="w-6 h-6 text-green-600 dark:text-green-400 mb-2" />
              <p className="text-sm font-medium text-gray-900 dark:text-white">Add Host</p>
            </button>
            <button className="p-4 text-left bg-purple-50 dark:bg-purple-900/20 hover:bg-purple-100 dark:hover:bg-purple-900/30 rounded-lg transition-colors">
              <CheckCircle className="w-6 h-6 text-purple-600 dark:text-purple-400 mb-2" />
              <p className="text-sm font-medium text-gray-900 dark:text-white">Run Check</p>
            </button>
            <button className="p-4 text-left bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/30 rounded-lg transition-colors">
              <AlertCircle className="w-6 h-6 text-orange-600 dark:text-orange-400 mb-2" />
              <p className="text-sm font-medium text-gray-900 dark:text-white">View Alerts</p>
            </button>
          </div>
        </div>
      </div>
      {/* Floating Action Button (Mobile) */}
      <Link
        to="/deploy"
        className="lg:hidden fixed bottom-20 right-4 p-4 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors z-50"
      >
        <Rocket className="w-6 h-6" />
      </Link>
    </div>
  );
};

export default Dashboard;
