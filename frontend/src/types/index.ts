export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Unknown';
export type ClauseStatus = 'Found' | 'Not Found' | 'Needs Review';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface UploadResponse {
  contract_id: string;
  filename: string;
  file_size_kb: number;
  page_count: number;
  chunk_count: number;
  message: string;
  uploaded_at: string;
}

export interface RiskClause {
  clause_type: string;
  status: ClauseStatus;
  risk_level: RiskLevel;
  confidence_score: number;
  summary: string;
  extracted_text?: string;
  suggested_improvement?: string;
  page_reference?: string;
}

export interface MissingClause {
  clause_type: string;
  importance: string;
  recommendation: string;
}

export interface AnalysisReport {
  contract_id: string;
  filename: string;
  overall_risk_level: RiskLevel;
  risk_score: number;
  executive_summary: string;
  clauses: RiskClause[];
  missing_clauses: MissingClause[];
  key_concerns: string[];
  key_obligations: string[];
  key_deadlines: string[];
  financial_commitments: string[];
  analyzed_at: string;
}

export interface ContractListItem {
  id: string;
  filename: string;
  file_size_kb: number;
  page_count: number;
  overall_risk_level: string;
  risk_score: number;
  uploaded_at: string;
  analyzed_at?: string;
}

export interface SourceDocument {
  content: string;
  page?: number;
  chunk_index?: number;
  relevance_score?: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  sources?: SourceDocument[];
  confidence?: number;
  timestamp: string;
}

export interface ChatResponse {
  contract_id: string;
  question: string;
  answer: string;
  confidence: number;
  sources: SourceDocument[];
  answered_at: string;
}

export interface AnalyticsData {
  total_contracts: number;
  average_risk_score: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  risk_distribution: Record<string, number>;
  clause_frequency: Record<string, number>;
  monthly_uploads: { month: string; count: number }[];
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  total_contracts: number;
  total_chunks: number;
  total_storage_mb: number;
  recent_logs: {
    id: string;
    user_id: string;
    action: string;
    details: string;
    timestamp: string;
  }[];
}
