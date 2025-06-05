import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = 'http://localhost:8080';

interface RetryOptions {
  retries?: number;
  retryDelay?: number;
}

const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000, // Adjust as needed
});

async function axiosWithRetry<T = any>(
  url: string,
  options: AxiosRequestConfig = {},
  retryOptions: RetryOptions = { retries: 3, retryDelay: 1000 }
): Promise<AxiosResponse<T>> {
  const { retries = 3, retryDelay = 1000 } = retryOptions;

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

  throw new Error(`Failed to fetch ${url} after ${retries} retries`); // Should not reach here
}

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
  persist_dir: string;
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

export const apiService = {
  async generateTests(data: GenerateRequest) {
    const response = await axiosWithRetry<any>(`/api/v1/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    return response.data;
  },

  async crawlWebsite(data: CrawlRequest) {
    const response = await axiosWithRetry<any>(`/api/v1/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data,
    });
    return response.data;
  },

  async testApi(request: ApiTestRequest): Promise<{
    message: string;
    total_tests: number;
    paths_tested: number;
  }> {
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
      const response = await axiosWithRetry<any>(`/api/v1/testapi`, {
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