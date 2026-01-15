import React from 'react';
import { CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'ACTIVE' | 'VOTED' | 'MOVED' | 'INACTIVE' | string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'ACTIVE':
        return {
          icon: CheckCircle,
          color: 'bg-green-100 text-green-800',
          label: 'Active'
        };
      case 'VOTED':
        return {
          icon: CheckCircle,
          color: 'bg-blue-100 text-blue-800',
          label: 'Voted'
        };
      case 'MOVED':
        return {
          icon: AlertCircle,
          color: 'bg-yellow-100 text-yellow-800',
          label: 'Moved'
        };
      case 'INACTIVE':
        return {
          icon: XCircle,
          color: 'bg-red-100 text-red-800',
          label: 'Inactive'
        };
      default:
        return {
          icon: Clock,
          color: 'bg-gray-100 text-gray-800',
          label: status
        };
    }
  };
  
  const config = getStatusConfig();
  const Icon = config.icon;
  
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      <Icon className="w-4 h-4 mr-1" />
      {config.label}
    </span>
  );
}