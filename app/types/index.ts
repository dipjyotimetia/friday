// Standardized API Response Types (matching backend)
export interface APIResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  request_id?: string;
  timestamp: string;
}

export interface ErrorDetail {
  error_code: string;
  message: string;
  field?: string;
  context?: Record<string, any>;
}

export interface ValidationErrorResponse {
  success: false;
  message: string;
  errors: ErrorDetail[];
  request_id?: string;
  timestamp: string;
}

// Test Generation Types (matching backend models)
export interface TestGenerationRequest {
  jira_key?: string;
  github_issue?: string;
  custom_requirements?: string;
  test_type?: string;
  provider?: string;
  include_confluence?: boolean;
}

export interface TestGenerationResponse {
  success: boolean;
  test_content?: string;
  metadata?: Record<string, any>;
  request_id?: string;
  timestamp: string;
}

// Web Crawling Types (matching backend models)
export interface CrawlRequest {
  url: string;
  max_pages?: number;
  provider?: string;
  include_external?: boolean;
}

export interface CrawlResponse {
  success: boolean;
  pages_crawled: number;
  content_summary?: string;
  embeddings_created?: number;
  request_id?: string;
  timestamp: string;
}

// API Testing Types (matching backend models)
export interface APITestRequest {
  spec_content: string;
  base_url?: string;
  auth_config?: Record<string, any>;
}

export interface APITestResponse {
  success: boolean;
  test_results?: Record<string, any>;
  total_tests?: number;
  passed_tests?: number;
  failed_tests?: number;
  request_id?: string;
  timestamp: string;
}

// WebSocket Log Entry Type
export interface LogEntry {
  timestamp: string;
  message: string;
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  request_id?: string;
  source: string;
}

// Component Props Types
export interface BaseComponentProps {
  setOutputText: (text: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
}

export interface TestGeneratorProps extends BaseComponentProps {
  isGenerating: boolean;
}

export interface FileUploaderProps {
  accept?: string;
  onChange: (file: File | null) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export interface OutputViewerProps {
  outputText: string;
  isGenerating?: boolean;
}

// AI Provider Types
export type AIProvider = 'openai' | 'gemini' | 'ollama' | 'mistral';

export interface ProviderOption {
  value: AIProvider;
  label: string;
}

// Tab Types
export type TabId = 'generator' | 'crawler' | 'api';

export interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}