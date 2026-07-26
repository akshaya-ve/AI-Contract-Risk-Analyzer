import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Send,
  Bot,
  User,
  Sparkles,
  FileText,
  HelpCircle,
  BookOpen,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { chatApi } from '../services/api';
import { ChatMessage, SourceDocument } from '../types';

export const ChatPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      content:
        'Hello! I am your AI Contract Assistant. Ask me any question about this contract, such as payment terms, termination notices, or liability limits.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  const sampleQuestions = [
    'What are my payment obligations?',
    'When does this contract expire?',
    'What are the termination conditions?',
    'Are there any liability caps?',
  ];

  const handleSend = async (questionText?: string) => {
    const q = questionText || input;
    if (!q.trim() || !id || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatApi.ask(id, q);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: res.answer,
        confidence: res.confidence,
        sources: res.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: 'Sorry, I encountered an error searching the document for your answer.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSources = (msgId: string) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-7rem)] flex flex-col glass-panel rounded-2xl border border-slate-800 overflow-hidden">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            to={`/app/contract/${id}`}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="h-9 w-9 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-semibold text-white text-sm">Contract RAG Q&A Assistant</h2>
            <p className="text-[11px] text-slate-400">Scoped to Contract ID: {id}</p>
          </div>
        </div>
      </div>

      {/* Message List Area */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-6">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const hasSources = msg.sources && msg.sources.length > 0;
          const showSources = expandedSources[msg.id];

          return (
            <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="h-8 w-8 rounded-full bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-400 shrink-0">
                  <Sparkles className="h-4 w-4" />
                </div>
              )}

              <div className={`max-w-2xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    isUser
                      ? 'bg-brand-600 text-white rounded-tr-none shadow-md shadow-brand-600/20'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {!isUser && msg.confidence && (
                    <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                      <span>RAG Confidence: {Math.round(msg.confidence * 100)}%</span>
                      <span>{msg.timestamp}</span>
                    </div>
                  )}
                </div>

                {/* Source Citations Box */}
                {!isUser && hasSources && (
                  <div className="mt-2">
                    <button
                      onClick={() => toggleSources(msg.id)}
                      className="inline-flex items-center gap-1.5 text-xs text-brand-400 hover:underline font-medium"
                    >
                      <BookOpen className="h-3.5 w-3.5" />
                      {msg.sources!.length} Source Citation Excerpts
                      {showSources ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    </button>

                    {showSources && (
                      <div className="mt-2 space-y-2">
                        {msg.sources!.map((src, i) => (
                          <div key={i} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
                            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1">
                              <span>Page {src.page || 'N/A'}</span>
                              <span>Relevance: {Math.round((src.relevance_score || 0.8) * 100)}%</span>
                            </div>
                            <p className="text-slate-300 italic">"{src.content}"</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-400">
              <Sparkles className="h-4 w-4 animate-spin" />
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-slate-400 animate-pulse">
              Retrieving context & generating answer...
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="px-4 py-2 border-t border-slate-800/80 bg-slate-950/40 flex items-center gap-2 overflow-x-auto">
        <span className="text-[11px] font-semibold text-slate-500 uppercase shrink-0">Suggested:</span>
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs whitespace-nowrap transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this contract..."
          className="flex-1 px-4 py-2.5 rounded-xl glass-input text-white text-sm focus:outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium transition-all shadow-md shadow-brand-600/20 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};
