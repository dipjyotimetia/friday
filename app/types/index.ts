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
export type YamlScenarioExecuteRequest = components['schemas']['YamlScenarioExecuteRequest'];
export type YamlScenarioExecuteResponse = components['schemas']['YamlScenarioExecuteResponse'];
export type YamlScenarioUploadResponse = components['schemas']['YamlScenarioUploadResponse'];
export type YamlTemplateSample = components['schemas']['YamlTemplateSample'];

// Enhanced Browser Testing Types (not in OpenAPI yet)
export interface EnhancedBrowserTestResult extends BrowserTestResult {
  test_id?: string;
  detailed_errors?: DetailedError[];
  browser_type?: string;
  session_id?: string;
}

export interface DetailedError {
  category: string;
  severity: string;
  message: string;
  error_code?: string;
  suggested_fix?: string;
  retry_recommended: boolean;
  stack_trace?: string;
  context?: Record<string, any>;
}

export interface ScreenshotInfo {
  filename: string;
  path: string;
  size: number;
  created_at: string;
  url: string;
}

export interface TestScreenshotsResponse {
  success: boolean;
  message: string;
  test_id: string;
  screenshots: ScreenshotInfo[];
  metadata?: Record<string, any>;
}

export interface BrowserSessionStats {
  total_sessions: number;
  active_sessions: number;
  max_sessions: number;
  total_tests_executed: number;
  browser_types: Record<string, number>;
  session_timeout: number;
}

export interface StorageStats {
  total_size_bytes: number;
  total_size_mb: number;
  total_files: number;
  test_count: number;
  base_path: string;
}

export interface TestMetrics {
  session_stats: BrowserSessionStats;
  storage_stats: StorageStats;
  timestamp: number;
}

export interface ValidationResponse {
  success: boolean;
  message: string;
  test_suite_name?: string;
  scenarios_count?: number;
  scenarios?: Array<{
    name: string;
    requirement: string;
    url: string;
    test_type: string;
  }>;
  errors?: string[];
}


// Advanced YAML Features
export interface YamlViewportConfig {
  width: number;
  height: number;
}

export interface YamlDataSource {
  type: string;
  source: string;
  format?: string;
}

export interface YamlGlobalConfig {
  max_parallel_tests?: number;
  default_timeout?: number;
  default_retry_count?: number;
  default_viewport?: YamlViewportConfig;
  setup_scripts?: string[];
  teardown_scripts?: string[];
  environment_variables?: Record<string, string>;
  reporting?: Record<string, any>;
}

export interface AdvancedYamlScenario {
  name: string;
  requirement: string;
  url: string;
  test_type?: string;
  context?: string;
  take_screenshots?: boolean;
  steps?: string[];
  expected_outcomes?: string[];
  tags?: string[];
  retry_count?: number;
  timeout?: number;
  prerequisites?: string[];
  parallel?: boolean;
  browsers?: string[];
  viewport?: YamlViewportConfig;
  environment_variables?: Record<string, string>;
  data_sources?: YamlDataSource[];
  wait_conditions?: string[];
  cleanup_actions?: string[];
}

export interface AdvancedYamlTestSuite {
  name: string;
  description?: string;
  version?: string;
  provider?: string;
  headless?: boolean;
  base_url?: string;
  global_context?: string;
  global_config?: YamlGlobalConfig;
  scenarios: AdvancedYamlScenario[];
}

// Tab Types
export type TabId = 'generator' | 'crawler' | 'api' | 'browser';

export interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}
