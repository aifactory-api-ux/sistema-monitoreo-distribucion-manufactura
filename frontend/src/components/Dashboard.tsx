import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Package, Clock, MapPin } from 'lucide-react';
import KPICard from './KPICard';
import LoadingSpinner from './LoadingSpinner';
import { useDashboard } from '../hooks/useDashboard';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Dashboard: React.FC = () => {
  const { data, loading, error } = useDashboard();
  
  console.log('[Dashboard] RENDER - loading:', loading, 'data exists:', !!data, 'error:', !!error);

  if (loading) {
    console.log('[Dashboard] CONDITION TRUE - Rendering spinner');
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  console.log('[Dashboard] loading is false, passed spinner check');

  if (error) {
    console.log('[Dashboard] CONDITION TRUE - Rendering error');
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!data) {
    console.log('[Dashboard] CONDITION TRUE - No data');
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">No dashboard data available</p>
      </div>
    );
  }

  console.log('[Dashboard] All conditions false - Rendering content');

  const kpiData = [
    {
      title: 'Total Orders',
      value: data.total_orders.toString(),
      icon: Package,
      trend: data.total_orders > 0 ? 'up' : 'neutral',
      color: 'blue'
    },
    {
      title: 'Fulfillment Rate',
      value: `${data.fulfillment_rate.toFixed(1)}%`,
      icon: TrendingUp,
      trend: data.fulfillment_rate >= 80 ? 'up' : data.fulfillment_rate >= 60 ? 'neutral' : 'down',
      color: 'green'
    },
    {
      title: 'Avg Delivery Days',
      value: data.avg_delivery_days.toFixed(1),
      icon: Clock,
      trend: data.avg_delivery_days <= 3 ? 'up' : data.avg_delivery_days <= 5 ? 'neutral' : 'down',
      color: 'yellow'
    },
    {
      title: 'Active Plants',
      value: data.active_plants.toString(),
      icon: MapPin,
      trend: data.active_plants > 0 ? 'up' : 'neutral',
      color: 'purple'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiData.map((kpi, index) => (
          <KPICard
            key={index}
            title={kpi.title}
            value={kpi.value}
            icon={kpi.icon}
            trend={kpi.trend as 'up' | 'down' | 'neutral'}
            color={kpi.color as 'blue' | 'green' | 'yellow' | 'purple'}
          />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Order Trends Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Trends</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.orders_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6b7280"
                  fontSize={12}
                  tickLine={false}
                />
                <YAxis 
                  stroke="#6b7280"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar 
                  dataKey="orders" 
                  fill="#3b82f6" 
                  radius={[4, 4, 0, 0]}
                  name="Orders"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Order Status Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status Distribution</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={Object.entries(data.status_distribution ?? data.orders_by_status ?? {}).map(([name, count]) => ({ name, count }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {Object.keys(data.status_distribution ?? data.orders_by_status ?? {}).map((_key, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;