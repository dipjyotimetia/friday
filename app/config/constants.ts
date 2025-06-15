import type { ProviderOption } from '@/types';

// API Configuration
export const API_CONFIG = {
  BASE_URL:
    process.env.API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:8080',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  GENERATE: '/api/v1/generate',
  CRAWL: '/api/v1/crawl',
  TEST_API: '/api/v1/testapi',
  BROWSER_TEST_HEALTH: '/api/v1/browser-test/health',
} as const;

// AI Providers
export const AI_PROVIDERS: ProviderOption[] = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'ollama', label: 'Ollama' },
  { value: 'mistral', label: 'Mistral' },
] as const;

// File Upload Configuration
export const FILE_CONFIG = {
  ACCEPTED_SPEC_FORMATS: '.yaml,.yml,.json',
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_EXTENSIONS: ['yaml', 'yml', 'json'],
} as const;

// Default Values
export const DEFAULT_VALUES = {
  MAX_PAGES: 10,
  OUTPUT_FILENAME: 'test_cases.md',
  API_OUTPUT_FILENAME: 'api_test_report.md',
  BROWSER_TEST_OUTPUT_FILENAME: 'browser_test_report.md',
  CRAWL_PERSIST_DIR: './data/chroma',
} as const;
