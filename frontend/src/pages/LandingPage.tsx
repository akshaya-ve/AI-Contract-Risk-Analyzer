import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Zap,
  FileCheck,
  Bot,
  ArrowRight,
  CheckCircle2,
  Lock,
  Sparkles,
  HelpCircle,
  FileText,
} from 'lucide-react';
import { Navbar } from '../components/Navbar';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden border-b border-slate-800/60">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-900/30 via-slate-950 to-slate-950 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold uppercase tracking-wider mb-8">
            <Sparkles className="h-3.5 w-3.5" /> Next-Gen AI Legal Contract Risk Assessment
          </div>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight max-w-4xl mx-auto">
            Detect Legal Risks in Contracts Before You Sign
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal">
            Automate contract review using Large Language Models and RAG. Detect risky clauses, get plain-English summaries, and chat directly with your legal documents.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 text-white font-semibold text-base hover:from-brand-500 hover:to-brand-400 transition-all duration-200 shadow-lg shadow-brand-600/30 flex items-center justify-center gap-2"
            >
              Analyze Your First Contract Free <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/app/dashboard"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-semibold text-base hover:bg-slate-800 hover:text-white transition-colors"
            >
              View Live Demo Dashboard
            </Link>
          </div>

          {/* Hero Preview Card */}
          <div className="mt-16 max-w-5xl mx-auto glass-panel rounded-2xl p-4 sm:p-6 shadow-2xl border border-slate-800">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-rose-500" />
                <div className="h-3 w-3 rounded-full bg-amber-500" />
                <div className="h-3 w-3 rounded-full bg-emerald-500" />
                <span className="text-xs text-slate-400 font-mono ml-2">Master_Service_Agreement_v4.pdf</span>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                High Risk Score: 78/100
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider">Unlimited Liability</div>
                <p className="text-xs text-slate-300 mt-1">Found in Section 14.2 — No financial liability cap specified for indemnification claims.</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Auto Renewal</div>
                <p className="text-xs text-slate-300 mt-1">Found in Section 4.1 — Automatically renews for 12 months unless cancelled 60 days prior.</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Confidentiality</div>
                <p className="text-xs text-slate-300 mt-1">Found in Section 8.0 — Standard 3-year confidentiality term with mutual protection.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section className="py-20 bg-slate-950 border-b border-slate-800/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-white tracking-tight">Enterprise Features Built for Modern Legal Teams</h2>
            <p className="text-slate-400 mt-4 text-base">
              Everything you need to parse, audit, and negotiate complex business contracts with complete confidence.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-brand-500/40 transition-all">
              <div className="h-12 w-12 rounded-xl bg-brand-600/10 text-brand-400 flex items-center justify-center mb-6">
                <ShieldAlert className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white">12-Clause Risk Detection</h3>
              <p className="text-slate-400 text-sm mt-2 leading-relaxed">
                Automatically identifies liability caps, auto-renewals, non-competes, indemnification, and governing laws with risk severity scoring.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-brand-500/40 transition-all">
              <div className="h-12 w-12 rounded-xl bg-cyan-600/10 text-cyan-400 flex items-center justify-center mb-6">
                <Bot className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white">Interactive RAG Chatbot</h3>
              <p className="text-slate-400 text-sm mt-2 leading-relaxed">
                Ask natural language questions about payment schedules or termination windows and receive exact source paragraph citations.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-brand-500/40 transition-all">
              <div className="h-12 w-12 rounded-xl bg-purple-600/10 text-purple-400 flex items-center justify-center mb-6">
                <FileCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white">PDF Executive Reports</h3>
              <p className="text-slate-400 text-sm mt-2 leading-relaxed">
                Generate board-ready risk assessment PDF documents containing clause breakdowns, missing clauses, and negotiation recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-slate-900/40 border-b border-slate-800/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-white">How ContractAI Works in 3 Simple Steps</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="p-6">
              <div className="w-10 h-10 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center mx-auto mb-4">1</div>
              <h4 className="font-semibold text-white text-lg">Upload Contract</h4>
              <p className="text-slate-400 text-sm mt-2">Upload any standard PDF or DOCX legal contract securely.</p>
            </div>
            <div className="p-6">
              <div className="w-10 h-10 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center mx-auto mb-4">2</div>
              <h4 className="font-semibold text-white text-lg">AI RAG Analysis</h4>
              <p className="text-slate-400 text-sm mt-2">Gemini & ChromaDB chunk, embed, and analyze all 12 key clause categories.</p>
            </div>
            <div className="p-6">
              <div className="w-10 h-10 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center mx-auto mb-4">3</div>
              <h4 className="font-semibold text-white text-lg">Export & Negotiate</h4>
              <p className="text-slate-400 text-sm mt-2">Download the risk report and ask clarifying questions via AI chat.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-slate-950 border-b border-slate-800/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-white">Transparent Plans for Every Team</h2>
            <p className="text-slate-400 mt-2">Choose the plan that fits your legal audit volume.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="glass-card p-8 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="font-semibold text-lg text-white">Developer / Free</h3>
                <p className="text-3xl font-extrabold text-white mt-4">$0 <span className="text-sm font-normal text-slate-400">/mo</span></p>
                <ul className="mt-6 space-y-3 text-sm text-slate-300">
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> 5 Contracts / month</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> 12-Clause Risk Detection</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Basic RAG Chatbot</li>
                </ul>
              </div>
              <Link to="/register" className="mt-8 block text-center py-2.5 rounded-xl bg-slate-800 text-white font-medium text-sm hover:bg-slate-700">Get Started</Link>
            </div>

            <div className="glass-card p-8 rounded-2xl border border-brand-500/50 bg-brand-950/20 relative flex flex-col justify-between">
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-brand-600 text-white text-[11px] font-bold uppercase tracking-wider">Most Popular</span>
              <div>
                <h3 className="font-semibold text-lg text-white">Pro SaaS</h3>
                <p className="text-3xl font-extrabold text-white mt-4">$49 <span className="text-sm font-normal text-slate-400">/mo</span></p>
                <ul className="mt-6 space-y-3 text-sm text-slate-300">
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Unlimited Contracts</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> PDF Executive Report Export</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Advanced Q&A Source Citations</li>
                </ul>
              </div>
              <Link to="/register" className="mt-8 block text-center py-2.5 rounded-xl bg-brand-600 text-white font-medium text-sm hover:bg-brand-500">Start 14-Day Trial</Link>
            </div>

            <div className="glass-card p-8 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="font-semibold text-lg text-white">Enterprise</h3>
                <p className="text-3xl font-extrabold text-white mt-4">$199 <span className="text-sm font-normal text-slate-400">/mo</span></p>
                <ul className="mt-6 space-y-3 text-sm text-slate-300">
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Custom LLM / On-Premise Vector DB</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Team RBAC & Audit Logging</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Dedicated API SLA</li>
                </ul>
              </div>
              <Link to="/register" className="mt-8 block text-center py-2.5 rounded-xl bg-slate-800 text-white font-medium text-sm hover:bg-slate-700">Contact Sales</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-950 border-t border-slate-900 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 AI Contract Risk Analyzer SaaS. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-slate-300 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-slate-300 cursor-pointer">Terms of Service</span>
            <span className="hover:text-slate-300 cursor-pointer">Security</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
