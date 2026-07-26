import React, { useEffect, useState } from 'react';
import { Shield, Users, HardDrive, Database, Activity, FileText } from 'lucide-react';
import { statsApi } from '../services/api';
import { AdminStats } from '../types';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    statsApi
      .getAdminStats()
      .then(setStats)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <LoadingSkeleton rows={4} />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          <Shield className="h-6 w-6 text-brand-400" /> Admin System Monitoring
        </h1>
        <p className="text-sm text-slate-400 mt-1">System stats, vector store indexes, disk usage, and audit trail logs.</p>
      </div>

      {/* Admin Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Users</p>
            <h3 className="text-2xl font-bold text-white mt-2">{stats?.total_users || 0}</h3>
          </div>
          <div className="h-10 w-10 rounded-xl bg-brand-600/15 text-brand-400 flex items-center justify-center border border-brand-500/20">
            <Users className="h-5 w-5" />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Documents</p>
            <h3 className="text-2xl font-bold text-white mt-2">{stats?.total_contracts || 0}</h3>
          </div>
          <div className="h-10 w-10 rounded-xl bg-cyan-600/15 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
            <FileText className="h-5 w-5" />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vector Chunks (ChromaDB)</p>
            <h3 className="text-2xl font-bold text-purple-400 mt-2">{stats?.total_chunks || 0}</h3>
          </div>
          <div className="h-10 w-10 rounded-xl bg-purple-600/15 text-purple-400 flex items-center justify-center border border-purple-500/20">
            <Database className="h-5 w-5" />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Storage Used</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-2">{stats?.total_storage_mb || 0} MB</h3>
          </div>
          <div className="h-10 w-10 rounded-xl bg-emerald-600/15 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
            <HardDrive className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-semibold text-white text-base flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand-400" /> Recent System Audit Logs
          </h3>
          <span className="text-xs text-slate-400">{stats?.recent_logs.length || 0} entries recorded</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Action</th>
                <th className="px-6 py-3.5">User ID</th>
                <th className="px-6 py-3.5">Details</th>
                <th className="px-6 py-3.5 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {(stats?.recent_logs || []).map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40">
                  <td className="px-6 py-3.5">
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20 font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-slate-400">{log.user_id}</td>
                  <td className="px-6 py-3.5 text-slate-200">{log.details}</td>
                  <td className="px-6 py-3.5 text-right text-slate-400">{log.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
