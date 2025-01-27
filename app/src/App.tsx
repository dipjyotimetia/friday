import { useState } from 'react';
import { TestGenerationParams, CrawlParams, ApiResponse } from './types';
import { generateTests, crawlWebsite } from './services/api';
import './App.css';

function App() {
  const [issueSource, setIssueSource] = useState<'jira' | 'github'>('jira');
  const [activeTab, setActiveTab] = useState<'tests' | 'crawler'>('tests');
  const [result, setResult] = useState<ApiResponse | null>(null);

  async function handleGenerateTests(e: React.FormEvent) {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    
    const params: TestGenerationParams = {
      confluence_id: formData.get('confluenceId') as string,
      output: 'test_cases.md'
    };

    if (issueSource === 'jira') {
      params.jira_key = formData.get('jiraKey') as string;
    } else {
      params.gh_repo = formData.get('ghRepo') as string;
      params.gh_issue = formData.get('ghIssue') as string;
    }

    const response = await generateTests(params);
    setResult(response);
  }

  async function handleCrawlWebsite(e: React.FormEvent) {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    
    const params: CrawlParams = {
      url: formData.get('url') as string,
      provider: 'vertex',
      persist_dir: './data/chroma',
      max_pages: Number(formData.get('maxPages')),
      same_domain: true
    };

    const response = await crawlWebsite(params);
    setResult(response);
  }


  return (
    <div className="container">
      <h1>Friday Test Generator</h1>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('tests')}
        >
          Test Generator
        </button>
        <button 
          className={`tab ${activeTab === 'crawler' ? 'active' : ''}`}
          onClick={() => setActiveTab('crawler')}
        >
          Web Crawler
        </button>
      </div>

      <div className="card">
        {activeTab === 'tests' ? (
          <>
            <h2>Generate Test Cases</h2>
            <form onSubmit={handleGenerateTests}>
            <div className="form-group">
            <label>Issue Source</label>
            <select 
              value={issueSource}
              onChange={(e) => setIssueSource(e.target.value as 'jira' | 'github')}>
              <option value="jira">Jira</option>
              <option value="github">GitHub</option>
            </select>

            {issueSource === 'jira' ? (
              <div>
                <label>Jira Key</label>
                <input name="jiraKey" placeholder="PROJ-123" />
              </div>
            ) : (
              <div>
                <label>GitHub Repository</label>
                <input name="ghRepo" placeholder="owner/repo" />
                <label>Issue Number</label>
                <input name="ghIssue" placeholder="456" />
              </div>
            )}

            <label>Confluence ID</label>
            <input name="confluenceId" placeholder="12345" />

            <button type="submit">Generate Tests</button>
          </div>
            </form>
          </>
        ) : (
          <>
            <h2>Web Crawler</h2>
            <form onSubmit={handleCrawlWebsite}>
            <div className="form-group">
            <label>URL</label>
            <input name="url" placeholder="https://example.com" />
            
            <label>Max Pages</label>
            <input name="maxPages" type="number" defaultValue={5} />

            <button type="submit">Start Crawling</button>
          </div>
            </form>
          </>
        )}

        {result && (
          <div className="result">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}


export default App;