import React, { useEffect, useState } from 'react';
import { BarChart3, PieChart, TrendingUp, AlertTriangle, FileText } from 'lucide-react';
import { statsApi } from '../services/api';
import { AnalyticsData } from '../types';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    statsApi
      .getAnalytics()
      .then(setData)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <LoadingSkeleton rows={3} />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">Contract Risk Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">Aggregated statistics, risk distribution, and high-frequency clause exposure.</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Audited Contracts</span>
          <h3 className="text-3xl font-extrabold text-white mt-2">{data?.total_contracts || 0}</h3>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Portfolio Risk</span>
          <h3 className="text-3xl font-extrabold text-amber-400 mt-2">{data?.average_risk_score || 0} <span className="text-xs font-normal text-slate-400">/ 100</span></h3>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Critical Exposure (High)</span>
          <h3 className="text-3xl font-extrabold text-rose-400 mt-2">{data?.high_risk_count || 0}</h3>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Compliant Contracts (Low)</span>
          <h3 className="text-3xl font-extrabold text-emerald-400 mt-2">{data?.low_risk_count || 0}</h3>
        </div>
      </div>

      {/* Visual Distribution Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Distribution Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-base flex items-center gap-2">
              <PieChart className="h-4 w-4 text-brand-400" /> Risk Rating Breakdown
            </h3>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>High Risk ({data?.high_risk_count || 0})</span>
                <span>{data?.total_contracts ? Math.round(((data?.high_risk_count || 0) / data.total_contracts) * 100) : 0}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                <div className="bg-rose-500 h-full rounded-full" style={{ width: `${data?.total_contracts ? ((data?.high_risk_count || 0) / data.total_contracts) * 100 : 0}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>Medium Risk ({data?.medium_risk_count || 0})</span>
                <span>{data?.total_contracts ? Math.round(((data?.medium_risk_count || 0) / data.total_contracts) * 100) : 0}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: `${data?.total_contracts ? ((data?.medium_risk_count || 0) / data.total_contracts) * 100 : 0}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>Low Risk ({data?.low_risk_count || 0})</span>
                <span>{data?.total_contracts ? Math.round(((data?.low_risk_count || 0) / data.total_contracts) * 100) : 0}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${data?.total_contracts ? ((data?.low_risk_count || 0) / data.total_contracts) * 100 : 0}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Top Flagged Clause Frequencies */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="font-semibold text-white text-base flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" /> Most Frequent High-Risk Clauses
          </h3>
          <div className="space-y-3 pt-2">
            {Object.entries(data?.clause_frequency || { 'Unlimited Liability': 3, 'Auto Renewal': 2, 'Indemnification': 2 }).map(([clause, count]) => (
              <div key={clause} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between text-xs">
                <span className="font-medium text-slate-200">{clause}</span>
                <span className="px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20">
                  {count} Flagged
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
