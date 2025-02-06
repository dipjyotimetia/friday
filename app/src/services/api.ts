const API_URL = process.env.API_URL || 'http://localhost:8080';

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

export const apiService = {
  async generateTests(data: GenerateRequest) {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async crawlWebsite(data: CrawlRequest) {
    const response = await fetch(`${API_URL}/crawl`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    return response.json();
  }
};