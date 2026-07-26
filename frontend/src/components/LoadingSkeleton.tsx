import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => {
  return (
    <div className="space-y-4 w-full animate-pulse">
      <div className="h-8 bg-slate-800/80 rounded-lg w-1/3"></div>
      <div className="h-4 bg-slate-800/60 rounded-md w-3/4"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-32 bg-slate-800/40 rounded-xl border border-slate-800/60 p-4 space-y-3">
            <div className="h-4 bg-slate-700/60 rounded w-1/2"></div>
            <div className="h-3 bg-slate-800/80 rounded w-full"></div>
            <div className="h-3 bg-slate-800/80 rounded w-5/6"></div>
          </div>
        ))}
      </div>
    </div>
  );
};
