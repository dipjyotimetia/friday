// API Request/Response Types
export interface GenerateRequest {
  jira_key: string;
  gh_issue: string;
  gh_repo: string;
  confluence_id: string;
  output: string;
}

export interface CrawlRequest {
  url: string;
  provider: string;
  max_pages: number;
  same_domain: boolean;
}

export interface ApiTestRequest {
  base_url: string;
  output: string;
  spec_file?: string;
  spec_upload?: File;
  provider: string;
}

export interface ApiTestResponse {
  message: string;
  total_tests: number;
  paths_tested: number;
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