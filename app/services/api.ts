import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '@/config/constants';
import type { 
  GenerateRequest, 
  CrawlRequest, 
  ApiTestRequest, 
  ApiTestResponse 
} from '@/types';

interface RetryOptions {
  retries?: number;
  retryDelay?: number;
}

const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
});

async function axiosWithRetry<T = any>(
  url: string,
  options: AxiosRequestConfig = {},
  retryOptions: RetryOptions = { 
    retries: API_CONFIG.RETRY_ATTEMPTS, 
    retryDelay: API_CONFIG.RETRY_DELAY 
  }
): Promise<AxiosResponse<T>> {
  const { retries = API_CONFIG.RETRY_ATTEMPTS, retryDelay = API_CONFIG.RETRY_DELAY } = retryOptions;

  let attempt = 0;

  while (attempt <= retries) {
    try {
      const response = await axiosInstance(url, options);
      return response;
    } catch (error: any) {
      if (attempt === retries || !error.response || error.response.status >= 500) {
        throw error;
      }

      attempt++;
      console.log(`Retrying ${url}, attempt ${attempt}/${retries}`);
      await new Promise((resolve) => setTimeout(resolve, retryDelay));
    }
  }

  throw new Error(`Failed to fetch ${url} after ${retries} retries`);
}

export const apiService = {
  async generateTests(data: GenerateRequest) {
    const response = await axiosWithRetry<any>(API_ENDPOINTS.GENERATE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    return response.data;
  },

  async crawlWebsite(data: CrawlRequest) {
    const response = await axiosWithRetry<any>(API_ENDPOINTS.CRAWL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    return response.data;
  },

  async testApi(request: ApiTestRequest): Promise<ApiTestResponse> {
    const formData = new FormData();
    formData.append('base_url', request.base_url);
    formData.append('output', request.output);
    formData.append('provider', request.provider);

    if (request.spec_upload) {
      formData.append('spec_upload', request.spec_upload);
    } else if (request.spec_file) {
      formData.append('spec_file', request.spec_file);
    }

    try {
      const response = await axiosWithRetry<ApiTestResponse>(API_ENDPOINTS.TEST_API, {
        method: 'POST',
        headers: { 'Content-Type': 'multipart/form-data' },
        data: formData,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'API test request failed');
    }
  },
};