import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  trend: 'up' | 'down' | 'neutral';
  color: 'blue' | 'green' | 'yellow' | 'purple';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, icon: Icon, trend, color }) => {
  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return {
          bg: 'bg-blue-50',
          icon: 'text-blue-600',
          border: 'border-blue-200'
        };
      case 'green':
        return {
          bg: 'bg-green-50',
          icon: 'text-green-600',
          border: 'border-green-200'
        };
      case 'yellow':
        return {
          bg: 'bg-yellow-50',
          icon: 'text-yellow-600',
          border: 'border-yellow-200'
        };
      case 'purple':
        return {
          bg: 'bg-purple-50',
          icon: 'text-purple-600',
          border: 'border-purple-200'
        };
      default:
        return {
          bg: 'bg-gray-50',
          icon: 'text-gray-600',
          border: 'border-gray-200'
        };
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'neutral':
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'neutral':
      default:
        return 'text-gray-500';
    }
  };

  const colorClasses = getColorClasses(color);

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${colorClasses.border} p-6 transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-2">{value}</p>
          <div className="flex items-center">
            {getTrendIcon()}
            <span className={`text-xs font-medium ml-1 ${getTrendColor()}`}>
              {trend === 'up' ? 'Good' : trend === 'down' ? 'Needs attention' : 'Stable'}
            </span>
          </div>
        </div>
        <div className={`${colorClasses.bg} p-3 rounded-lg`}>
          <Icon className={`w-6 h-6 ${colorClasses.icon}`} />
        </div>
      </div>
    </div>
  );
};

export default KPICard;