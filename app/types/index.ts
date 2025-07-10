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

// Browser Testing Types
export interface BrowserTestScenario {
  name: string;
  requirement: string;
  url: string;
  test_type: 'functional' | 'ui' | 'integration' | 'accessibility' | 'performance';
  context?: string;
  expected_outcome?: string;
  timeout?: number;
}

export interface BrowserTestSuite {
  name: string;
  description?: string;
  scenarios: BrowserTestScenario[];
  global_timeout?: number;
}

export interface BrowserTestResult {
  scenario_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  execution_time: number;
  success: boolean;
  error_message?: string;
  screenshot_path?: string;
  logs: string[];
  actions_taken: string[];
  started_at: string;
  completed_at?: string;
}

export interface BrowserTestReport {
  suite_name: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  skipped_tests: number;
  execution_time: number;
  success_rate: number;
  results: BrowserTestResult[];
  started_at: string;
  completed_at: string;
  browser_info: Record<string, any>;
}

export interface BrowserTestExecutionRequest {
  file_id?: string;
  test_suite?: BrowserTestSuite;
  provider: string;
  headless: boolean;
  output_format: string;
}

export interface BrowserTestExecutionResponse {
  message: string;
  execution_id: string;
  status: string;
  report?: BrowserTestReport;
}

export interface YamlUploadRequest {
  filename: string;
  content: string;
}

export interface YamlUploadResponse {
  message: string;
  file_id: string;
  parsed_suite: BrowserTestSuite;
}

// Tab Types
export type TabId = 'generator' | 'crawler' | 'api' | 'browser';

export interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}
