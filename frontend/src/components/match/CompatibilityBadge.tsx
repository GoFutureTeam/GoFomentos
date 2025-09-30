import React from 'react';
import { cn } from '@/lib/utils';

interface CompatibilityBadgeProps {
  percentage: number;
  className?: string;
}

export const CompatibilityBadge: React.FC<CompatibilityBadgeProps> = ({ 
  percentage, 
  className 
}) => {
  const getBackgroundColor = (percentage: number) => {
    if (percentage <= 69) return '#D33232';
    if (percentage <= 79) return '#FFFF00';
    return '#008000';
  };

  const getTextColor = (percentage: number) => {
    if (percentage <= 69) return 'text-white';
    if (percentage <= 79) return 'text-black';
    return 'text-white';
  };

  return (
    <div 
      className={cn(
        "flex flex-row items-center justify-center gap-1 px-3 py-2 rounded-xl text-sm font-bold",
        getTextColor(percentage),
        className
      )}
      style={{ backgroundColor: getBackgroundColor(percentage) }}
    >
      <span>{percentage}%</span>
      <span>compatível</span>
    </div>
  );
};