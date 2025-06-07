import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '@/config/constants';
import type { 
  TestGenerationRequest,
  TestGenerationResponse,
  CrawlRequest, 
  CrawlResponse,
  APITestRequest, 
  APITestResponse,
  APIResponse,
  ValidationErrorResponse
} from '@/types';

// Custom error class for API errors
export class APIError extends Error {
  public statusCode: number;
  public errorCode?: string;
  public requestId?: string;
  public details?: any;

  constructor(message: string, statusCode: number, errorCode?: string, requestId?: string, details?: any) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.requestId = requestId;
    this.details = details;
  }
}

// Validation error class
export class ValidationError extends APIError {
  public errors: any[];

  constructor(message: string, errors: any[], requestId?: string) {
    super(message, 422, 'VALIDATION_ERROR', requestId);
    this.errors = errors;
  }
}

interface RetryOptions {
  retries?: number;
  retryDelay?: number;
}

const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
});

// Add request/response interceptors for standardized error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      
      // Handle standardized error responses
      if (data && typeof data === 'object') {
        if (status === 422 && data.errors) {
          // Validation error
          throw new ValidationError(
            data.message || 'Validation failed',
            data.errors,
            data.request_id
          );
        } else if (data.success === false) {
          // Standardized API error response
          throw new APIError(
            data.message || 'Request failed',
            status,
            data.data?.error_code,
            data.request_id,
            data.data
          );
        }
      }
      
      // Fallback for non-standardized errors
      throw new APIError(
        data?.detail || data?.message || `HTTP ${status} Error`,
        status
      );
    }
    
    // Network or other errors
    throw new APIError(
      error.message || 'Network error',
      0
    );
  }
);

async function axiosWithRetry<T = any>(
  url: string,
  options: AxiosRequestConfig = {},
  retryOptions: RetryOptions = { 
    retries: API_CONFIG.RETRY_ATTEMPTS, 
    retryDelay: API_CONFIG.RETRY_DELAY 
  }
): Promise<AxiosResponse<APIResponse<T>>> {
  const { retries = API_CONFIG.RETRY_ATTEMPTS, retryDelay = API_CONFIG.RETRY_DELAY } = retryOptions;

  let attempt = 0;

  while (attempt <= retries) {
    try {
      const response = await axiosInstance(url, options);
      return response;
    } catch (error: any) {
      // Don't retry on client errors (4xx) except 429 (rate limit)
      if (
        attempt === retries || 
        (error instanceof APIError && error.statusCode >= 400 && error.statusCode < 500 && error.statusCode !== 429)
      ) {
        throw error;
      }

      attempt++;
      const delay = retryDelay * Math.pow(2, attempt - 1); // Exponential backoff
      console.log(`Retrying ${url}, attempt ${attempt}/${retries} in ${delay}ms`);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw new APIError(`Failed to fetch ${url} after ${retries} retries`, 0);
}

export const apiService = {
  async generateTests(data: TestGenerationRequest): Promise<TestGenerationResponse> {
    const response = await axiosWithRetry<TestGenerationResponse>(API_ENDPOINTS.GENERATE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    
    // Handle both standardized and legacy response formats
    const responseData = response.data as any;
    if (responseData.success !== undefined && responseData.timestamp !== undefined) {
      return responseData as TestGenerationResponse;
    } else {
      // Legacy format - convert to standardized format
      return {
        success: true,
        test_content: typeof responseData === 'string' ? responseData : JSON.stringify(responseData),
        timestamp: new Date().toISOString()
      };
    }
  },

  async crawlWebsite(data: CrawlRequest): Promise<CrawlResponse> {
    const response = await axiosWithRetry<CrawlResponse>(API_ENDPOINTS.CRAWL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    
    // Handle both standardized and legacy response formats
    const responseData = response.data as any;
    if (responseData.success !== undefined && responseData.pages_crawled !== undefined) {
      return responseData as CrawlResponse;
    } else {
      // Legacy format - convert to standardized format  
      return {
        success: true,
        pages_crawled: responseData.pages_processed || 0,
        content_summary: typeof responseData === 'string' ? responseData : JSON.stringify(responseData),
        embeddings_created: responseData.total_documents || 0,
        timestamp: new Date().toISOString()
      };
    }
  },

  async testApi(request: APITestRequest): Promise<APITestResponse> {
    const formData = new FormData();
    
    // Handle both file upload and direct spec content
    if (request.spec_content) {
      formData.append('spec_content', request.spec_content);
    }
    
    if (request.base_url) {
      formData.append('base_url', request.base_url);
    }
    
    if (request.auth_config) {
      formData.append('auth_config', JSON.stringify(request.auth_config));
    }

    const response = await axiosWithRetry<APITestResponse>(API_ENDPOINTS.TEST_API, {
      method: 'POST',
      headers: { 'Content-Type': 'multipart/form-data' },
      data: formData,
    });
    
    // Handle both standardized and legacy response formats
    const responseData = response.data as any;
    if (responseData.success !== undefined && responseData.timestamp !== undefined) {
      return responseData as APITestResponse;
    } else {
      // Legacy format - convert to standardized format
      return {
        success: true,
        test_results: responseData,
        total_tests: responseData.total_tests || 0,
        passed_tests: responseData.passed_tests || 0,
        failed_tests: responseData.failed_tests || 0,
        timestamp: new Date().toISOString()
      };
    }
  },

  // Health check endpoint
  async getHealth(): Promise<APIResponse<any>> {
    const response = await axiosWithRetry<any>('/health', {
      method: 'GET',
    });
    return response.data;
  },

  // Get application version
  async getVersion(): Promise<APIResponse<{ version: string }>> {
    const response = await axiosWithRetry<{ version: string }>('/version', {
      method: 'GET',
    });
    return response.data;
  }
};