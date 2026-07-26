import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CheckCircle, AlertCircle, Sparkles, ArrowRight } from 'lucide-react';
import { contractApi } from '../services/api';

export const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'done' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      validateAndSetFile(selected);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const validateAndSetFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setErrorMessage('Unsupported file format. Please upload a PDF or DOCX file.');
      return;
    }
    if (f.size > 25 * 1024 * 1024) {
      setErrorMessage('File size exceeds 25 MB limit.');
      return;
    }
    setErrorMessage(null);
    setFile(f);
  };

  const startUploadAndAnalyze = async () => {
    if (!file) return;
    setStatus('uploading');
    setUploadProgress(0);
    setErrorMessage(null);

    try {
      // 1. Upload & Index
      const uploadRes = await contractApi.upload(file, (percent) => {
        setUploadProgress(percent);
      });

      // 2. Trigger AI Analysis
      setStatus('analyzing');
      await contractApi.analyze(uploadRes.contract_id);

      setStatus('done');
      setTimeout(() => {
        navigate(`/app/contract/${uploadRes.contract_id}`);
      }, 1000);
    } catch (err: any) {
      console.error(err);
      setStatus('error');
      setErrorMessage(err.response?.data?.error || 'Failed to process contract.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-4">
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">Upload Legal Contract</h1>
        <p className="text-sm text-slate-400 mt-1">Upload PDF or DOCX contracts for automated 12-clause risk assessment.</p>
      </div>

      <div className="glass-panel p-8 rounded-2xl border border-slate-800 space-y-6">
        {/* Dropzone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 cursor-pointer ${
            isDragOver
              ? 'border-brand-500 bg-brand-500/10'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40'
          }`}
        >
          <input
            type="file"
            accept=".pdf,.docx"
            id="file-input"
            className="hidden"
            onChange={handleFileChange}
          />
          <label htmlFor="file-input" className="cursor-pointer block">
            <div className="h-16 w-16 rounded-2xl bg-brand-600/10 text-brand-400 border border-brand-500/20 flex items-center justify-center mx-auto mb-4">
              <Upload className="h-8 w-8" />
            </div>
            <p className="text-base font-semibold text-white">
              {file ? file.name : 'Click to upload or drag & drop file'}
            </p>
            <p className="text-xs text-slate-400 mt-1">PDF or DOCX (Max 25 MB)</p>
          </label>
        </div>

        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {errorMessage}
          </div>
        )}

        {/* Selected File Details */}
        {file && status === 'idle' && (
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-brand-400" />
              <div>
                <p className="text-sm font-medium text-white">{file.name}</p>
                <p className="text-xs text-slate-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
            </div>
            <button
              onClick={startUploadAndAnalyze}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 text-white font-semibold text-sm hover:from-brand-500 hover:to-brand-400 transition-all shadow-md shadow-brand-600/20 flex items-center gap-2"
            >
              Start AI Analysis <Sparkles className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Upload & Progress Status Bar */}
        {status !== 'idle' && (
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center gap-2">
                {status === 'uploading' && 'Uploading document...'}
                {status === 'analyzing' && 'RAG Pipeline & LLM Analyzing 12 Clause Categories...'}
                {status === 'done' && 'Analysis Complete! Redirecting...'}
                {status === 'error' && 'Analysis Error'}
              </span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
              <div
                className="bg-gradient-to-r from-brand-600 to-cyan-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${status === 'analyzing' ? 90 : uploadProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
