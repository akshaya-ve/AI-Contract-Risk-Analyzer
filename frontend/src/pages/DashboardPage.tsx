import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Upload,
  ShieldAlert,
  BarChart2,
  ArrowUpRight,
  Trash2,
  MessageSquare,
  FileCheck,
  RefreshCw,
} from 'lucide-react';
import { contractApi, statsApi } from '../services/api';
import { AnalyticsData, ContractListItem } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const DashboardPage: React.FC = () => {
  const [contracts, setContracts] = useState<ContractListItem[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [contractsData, analyticsData] = await Promise.all([
        contractApi.listContracts(),
        statsApi.getAnalytics(),
      ]);
      setContracts(contractsData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this contract?')) {
      try {
        await contractApi.deleteContract(id);
        loadData();
      } catch (err) {
        alert('Failed to delete contract.');
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Contract Audit Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Overview of risk scores, clause breakdown, and analyzed contracts.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <Link
            to="/app/upload"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm transition-all shadow-md shadow-brand-600/20 flex items-center gap-2"
          >
            <Upload className="h-4 w-4" /> Upload Contract
          </Link>
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={3} />
      ) : (
        <>
          {/* Analytics Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Contracts</p>
                <h3 className="text-2xl font-bold text-white mt-2">{analytics?.total_contracts || 0}</h3>
              </div>
              <div className="h-11 w-11 rounded-xl bg-brand-600/15 text-brand-400 flex items-center justify-center border border-brand-500/20">
                <FileText className="h-5 w-5" />
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Risk Score</p>
                <h3 className="text-2xl font-bold text-white mt-2">
                  {analytics?.average_risk_score || 0}<span className="text-xs font-normal text-slate-400">/100</span>
                </h3>
              </div>
              <div className="h-11 w-11 rounded-xl bg-amber-600/15 text-amber-400 flex items-center justify-center border border-amber-500/20">
                <BarChart2 className="h-5 w-5" />
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">High Risk Contracts</p>
                <h3 className="text-2xl font-bold text-rose-400 mt-2">{analytics?.high_risk_count || 0}</h3>
              </div>
              <div className="h-11 w-11 rounded-xl bg-rose-600/15 text-rose-400 flex items-center justify-center border border-rose-500/20">
                <ShieldAlert className="h-5 w-5" />
              </div>
            </div>

            <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Low Risk Contracts</p>
                <h3 className="text-2xl font-bold text-emerald-400 mt-2">{analytics?.low_risk_count || 0}</h3>
              </div>
              <div className="h-11 w-11 rounded-xl bg-emerald-600/15 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                <FileCheck className="h-5 w-5" />
              </div>
            </div>
          </div>

          {/* Contracts Table */}
          <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="font-semibold text-white text-base">Recent Analyzed Contracts</h3>
              <span className="text-xs text-slate-400">{contracts.length} documents stored</span>
            </div>

            {contracts.length === 0 ? (
              <div className="p-12 text-center">
                <FileText className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                <h4 className="text-base font-semibold text-slate-300">No contracts uploaded yet</h4>
                <p className="text-xs text-slate-500 mt-1 mb-6">Upload a PDF or DOCX file to run AI risk analysis.</p>
                <Link
                  to="/app/upload"
                  className="px-4 py-2 rounded-xl bg-brand-600 text-white font-medium text-xs hover:bg-brand-500 transition-colors inline-flex items-center gap-1.5"
                >
                  <Upload className="h-3.5 w-3.5" /> Upload Contract
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-900/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3.5">Contract Name</th>
                      <th className="px-6 py-3.5">Pages</th>
                      <th className="px-6 py-3.5">Risk Rating</th>
                      <th className="px-6 py-3.5">Uploaded</th>
                      <th className="px-6 py-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {contracts.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-900/40 transition-colors group">
                        <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                          <FileText className="h-4 w-4 text-brand-400 shrink-0" />
                          <span className="truncate max-w-xs">{c.filename}</span>
                        </td>
                        <td className="px-6 py-4 text-xs text-slate-400">{c.page_count} pages ({c.file_size_kb} KB)</td>
                        <td className="px-6 py-4">
                          <RiskBadge level={c.overall_risk_level} score={c.risk_score} size="sm" />
                        </td>
                        <td className="px-6 py-4 text-xs text-slate-400">
                          {new Date(c.uploaded_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              to={`/app/contract/${c.id}`}
                              className="px-3 py-1.5 rounded-lg bg-brand-600/15 text-brand-400 hover:bg-brand-600/30 text-xs font-semibold flex items-center gap-1 border border-brand-500/20"
                            >
                              Report <ArrowUpRight className="h-3.5 w-3.5" />
                            </Link>
                            <Link
                              to={`/app/chat/${c.id}`}
                              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
                              title="Chat with Contract"
                            >
                              <MessageSquare className="h-4 w-4" />
                            </Link>
                            <button
                              onClick={(e) => handleDelete(c.id, e)}
                              className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                              title="Delete Contract"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
