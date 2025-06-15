// Export generated API types
export * from './api';
export type { paths, components, operations } from './api';

// Import components type for use in aliases
import type { components } from './api';

// Type aliases for OpenAPI types (for easier usage)
export type TestGenerationRequest = components['schemas']['GenerateRequest'];
export type TestGenerationResponse = components['schemas']['GenerateResponse'];
export type CrawlRequest = components['schemas']['CrawlRequest'];
export type APITestRequest =
  components['schemas']['Body_test_api_api_v1_testapi_post'];
export type APITestResponse = components['schemas']['ApiTestResponse'];

// Extended types for better UX (these add fields not in the OpenAPI spec)
export interface ExtendedTestGenerationRequest
  extends Omit<TestGenerationRequest, 'template' | 'output'> {
  github_issue?: string;
  custom_requirements?: string;
  test_type?: string;
  provider?: string;
  include_confluence?: boolean;
  template?: string;
  output?: string;
}

export interface ExtendedTestGenerationResponse {
  success: boolean;
  test_content?: string;
  metadata?: Record<string, any>;
  request_id?: string;
  timestamp: string;
}

export type ExtendedCrawlRequest = CrawlRequest;

export interface ExtendedCrawlResponse {
  success: boolean;
  pages_crawled: number;
  content_summary?: string;
  embeddings_created?: number;
  request_id?: string;
  timestamp: string;
}

export interface ExtendedAPITestRequest {
  spec_content: string;
  base_url?: string;
  auth_config?: Record<string, any>;
}

export interface ExtendedAPITestResponse extends APITestResponse {
  success: boolean;
  test_results?: Record<string, any>;
  request_id?: string;
  timestamp: string;
}

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

// Browser Testing Types (from OpenAPI schema)
export type BrowserTestResult = components['schemas']['BrowserTestResult'];

// Tab Types
export type TabId = 'generator' | 'crawler' | 'api' | 'browser';

export interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}
