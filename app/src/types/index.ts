export interface TestGenerationParams {
    jira_key?: string;
    gh_repo?: string;
    gh_issue?: string;
    confluence_id: string;
    output: string;
  }
  
  export interface CrawlParams {
    url: string;
    provider: string;
    persist_dir: string;
    max_pages: number;
    same_domain: boolean;
  }
  
  export interface ApiResponse<T = any> {
    message?: string;
    data?: T;
    error?: string;
  }