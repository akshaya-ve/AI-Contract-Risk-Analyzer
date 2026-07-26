import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileText,
  Download,
  MessageSquare,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileCheck,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from 'lucide-react';
import { contractApi } from '../services/api';
import { AnalysisReport, RiskClause } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const ContractDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filterRisk, setFilterRisk] = useState<string>('All');
  const [expandedClause, setExpandedClause] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadReport(id);
    }
  }, [id]);

  const loadReport = async (contractId: string) => {
    setIsLoading(true);
    try {
      const data = await contractApi.analyze(contractId);
      setReport(data);
    } catch (err) {
      console.error('Failed to load contract report:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSkeleton rows={4} />;
  }

  if (!report) {
    return (
      <div className="text-center py-16">
        <h3 className="text-lg font-semibold text-slate-300">Contract report not found</h3>
        <Link to="/app/dashboard" className="text-brand-400 text-sm hover:underline mt-2 inline-block">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const filteredClauses = report.clauses.filter((c) => {
    if (filterRisk === 'All') return true;
    return c.risk_level.toLowerCase() === filterRisk.toLowerCase();
  });

  return (
    <div className="space-y-8 pb-12">
      {/* Header & Quick Action CTAs */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-brand-400 shrink-0" />
            <h1 className="text-xl font-bold text-white tracking-tight">{report.filename}</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Contract ID: <span className="font-mono text-slate-300">{report.contract_id}</span> • Analyzed: {new Date(report.analyzed_at).toLocaleString()}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to={`/app/chat/${report.contract_id}`}
            className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 hover:text-white font-medium text-xs flex items-center gap-2"
          >
            <MessageSquare className="h-4 w-4 text-brand-400" /> Chat with Document
          </Link>
          <a
            href={contractApi.getReportDownloadUrl(report.contract_id)}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition-all shadow-md shadow-brand-600/20 flex items-center gap-2"
          >
            <Download className="h-4 w-4" /> Download PDF Report
          </a>
        </div>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score Meter */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Aggregate Contract Risk</h3>
            <div className="mt-4 flex items-baseline gap-3">
              <span className="text-5xl font-extrabold text-white tracking-tight">{report.risk_score}</span>
              <span className="text-sm font-semibold text-slate-400">/ 100 Risk Score</span>
            </div>
            <div className="mt-4">
              <RiskBadge level={report.overall_risk_level} size="lg" />
            </div>
          </div>
          <div className="mt-6 pt-4 border-t border-slate-800 text-xs text-slate-400">
            Higher scores indicate increased legal exposure, liability risks, or unbalanced clauses.
          </div>
        </div>

        {/* Executive Summary */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 lg:col-span-2 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-brand-400" /> Executive Legal Summary
            </h3>
            <p className="text-sm text-slate-200 mt-3 leading-relaxed font-normal">
              {report.executive_summary}
            </p>
          </div>

          {report.key_concerns.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-800">
              <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2">Key Critical Concerns</h4>
              <ul className="space-y-1 text-xs text-slate-300">
                {report.key_concerns.map((kc, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-rose-400 font-bold">•</span> {kc}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Missing Clauses Section */}
      {report.missing_clauses.length > 0 && (
        <div className="glass-panel p-6 rounded-2xl border border-amber-500/30 bg-amber-500/5">
          <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2 mb-4">
            <AlertTriangle className="h-4 w-4" /> Recommended Missing Clauses ({report.missing_clauses.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {report.missing_clauses.map((mc, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <h4 className="font-semibold text-white text-sm">{mc.clause_type}</h4>
                <p className="text-xs text-slate-400 mt-1">{mc.importance}</p>
                <p className="text-xs text-brand-400 mt-2 font-medium">Proposed: {mc.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clause Analysis Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h2 className="text-lg font-bold text-white tracking-tight">12 Clause Category Assessments</h2>

          {/* Filter Pills */}
          <div className="flex items-center gap-2">
            {['All', 'High', 'Medium', 'Low'].map((level) => (
              <button
                key={level}
                onClick={() => setFilterRisk(level)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  filterRisk === level
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Clause Cards Grid */}
        <div className="space-y-4">
          {filteredClauses.map((clause) => {
            const isExpanded = expandedClause === clause.clause_type;
            return (
              <div
                key={clause.clause_type}
                className="glass-card rounded-2xl border border-slate-800/80 p-5 hover:border-slate-700 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-white text-base">{clause.clause_type}</h3>
                      <RiskBadge level={clause.risk_level} size="sm" />
                      <span className="text-[11px] text-slate-500 font-mono">
                        {Math.round(clause.confidence_score * 100)}% confidence
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 pt-2 leading-relaxed">{clause.summary}</p>
                  </div>

                  <button
                    onClick={() => setExpandedClause(isExpanded ? null : clause.clause_type)}
                    className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800 shrink-0"
                  >
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>

                {/* Extracted Text & Improvement Callout */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-4 text-xs">
                    {clause.extracted_text && (
                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80">
                        <span className="font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                          Verbatim Extracted Contract Text {clause.page_reference ? `(${clause.page_reference})` : ''}
                        </span>
                        <blockquote className="text-slate-300 italic font-mono text-[11px]">
                          "{clause.extracted_text}"
                        </blockquote>
                      </div>
                    )}

                    {clause.suggested_improvement && (
                      <div className="p-3.5 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-300">
                        <span className="font-semibold text-brand-400 uppercase tracking-wider block mb-1">
                          Actionable Risk Mitigation Recommendation
                        </span>
                        {clause.suggested_improvement}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
