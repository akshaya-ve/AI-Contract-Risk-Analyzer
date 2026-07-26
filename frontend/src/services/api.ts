import axios from 'axios';
import {
  AdminStats,
  AnalysisReport,
  AnalyticsData,
  ChatResponse,
  ContractListItem,
  RiskClause,
  RisksResponse,
  SummaryResponse,
  UploadResponse,
  User,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Bearer JWT Token automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth Services
export const authApi = {
  register: async (email: string, password: string, fullName?: string) => {
    const res = await api.post<User>('/auth/register', { email, password, full_name: fullName });
    return res.data;
  },
  login: async (email: string, password: string) => {
    const res = await api.post<{ access_token: string; token_type: string; user: User }>('/auth/login', { email, password });
    return res.data;
  },
  getMe: async () => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

// Contract & Analysis Services
export const contractApi = {
  upload: async (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress?.(percent);
        }
      },
    });
    return res.data;
  },

  analyze: async (contractId: string) => {
    const res = await api.post<AnalysisReport>('/analyze', { contract_id: contractId });
    return res.data;
  },

  getSummary: async (contractId: string) => {
    const res = await api.get<SummaryResponse>(`/summary/${contractId}`);
    return res.data;
  },

  getRisks: async (contractId: string) => {
    const res = await api.get<RisksResponse>(`/risks/${contractId}`);
    return res.data;
  },

  listContracts: async () => {
    const res = await api.get<ContractListItem[]>('/contracts');
    return res.data;
  },

  deleteContract: async (contractId: string) => {
    const res = await api.delete<{ message: string }>(`/contracts/${contractId}`);
    return res.data;
  },

  getReportDownloadUrl: (contractId: string) => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/contracts/${contractId}/report${token ? `?token=${token}` : ''}`;
  },
};

// Chat Service
export const chatApi = {
  ask: async (contractId: string, question: string) => {
    const res = await api.post<ChatResponse>('/chat', { contract_id: contractId, question });
    return res.data;
  },
};

// Analytics & Admin Services
export const statsApi = {
  getAnalytics: async () => {
    const res = await api.get<AnalyticsData>('/analytics');
    return res.data;
  },
  getAdminStats: async () => {
    const res = await api.get<AdminStats>('/admin/stats');
    return res.data;
  },
};
