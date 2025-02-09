const API_URL = 'http://localhost:8000';

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
  spec_file?: File; // For file upload
  spec_path?: string; // For file path
  base_url: string;
  output: string;
}

export interface PerfTestResponse {
  report: string;
}

export interface PerfTestRequest {
  spec_file?: File;
  curl_command?: string;
  base_url?: string;
  users: number;
  duration: number;
}

export const apiService = {
  async generateTests(data: GenerateRequest) {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async crawlWebsite(data: CrawlRequest) {
    const response = await fetch(`${API_URL}/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async testApi({
    spec_file,
    spec_path,
    base_url,
    output
  }: ApiTestRequest): Promise<{ message: string; total_tests: number; paths_tested: number }> {
    const formData = new FormData();

    // Handle either spec_file upload or spec_path
    if (spec_file) {
      formData.append('spec_upload', spec_file);
    } else if (spec_path) {
      formData.append('spec_file', spec_path);
    }

    formData.append('base_url', base_url);
    formData.append('output', output);

    const response = await fetch(`${API_URL}/testapi`, {
      method: 'POST', 
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API test request failed');
    }

    return response.json();
  },

  async runPerfTest({
    spec_file,
    curl_command,
    base_url,
    users,
    duration
  }: PerfTestRequest): Promise<{ report: string }> {
    const formData = new FormData();

    // Only append if values are provided
    if (spec_file) {
      formData.append('spec_file', spec_file);
    }

    if (curl_command) {
      formData.append('curl_command', curl_command);
    }

    if (base_url) {
      formData.append('base_url', base_url);
    }

    formData.append('users', users.toString());
    formData.append('duration', duration.toString());

    const response = await fetch(`${API_URL}/perftest`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to run performance test');
    }

    return response.json();
  }
};