import React, { useState } from 'react';
import { apiService } from '../services/api';
import './styles.css'; // Import [app/styles.css](app/styles.css)

function FridayApp() {
  const [activeTab, setActiveTab] = useState('generator');
  const [jiraKey, setJiraKey] = useState('');
  const [ghIssue, setGhIssue] = useState('');
  const [ghRepo, setGhRepo] = useState('');
  const [confluenceId, setConfluenceId] = useState('');
  const [outputFilename, setOutputFilename] = useState('test_cases.md');
  const [url, setUrl] = useState('');
  const [provider, setProvider] = useState('vertex');
  const [maxPages, setMaxPages] = useState(10);
  const [sameDomain, setSameDomain] = useState(true);
  const [outputText, setOutputText] = useState('');

  const handleTabClick = (tabId: any) => {
    setActiveTab(tabId);
    setOutputText('');
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await apiService.generateTests({
        jira_key: jiraKey,
        gh_issue: ghIssue,
        gh_repo: ghRepo,
        confluence_id: confluenceId,
        output: outputFilename
      });
      setOutputText(JSON.stringify(result, null, 2));
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    }
  };

  
  const handleCrawl = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await apiService.crawlWebsite({
        url,
        provider,
        persist_dir: './data/chroma',
        max_pages: Number(maxPages),
        same_domain: sameDomain
      });
      setOutputText(JSON.stringify(result, null, 2));
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    }
  };

  return (
    <div className="container">
      <h1>FRIDAY Test Case Generator</h1>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'generator' ? 'active' : ''}`}
          onClick={() => handleTabClick('generator')}
          data-tab="generator"
        >
          Test Case Generator
        </button>
        <button
          className={`tab-btn ${activeTab === 'crawler' ? 'active' : ''}`}
          onClick={() => handleTabClick('crawler')}
          data-tab="crawler"
        >
          Web Crawler
        </button>
      </div>

      {/* Generator Tab */}
      <div className={`tab-content ${activeTab === 'generator' ? 'active' : ''}`} id="generator">
        <div className="form-section">
          <h2>Generate Test Cases</h2>
          <form onSubmit={handleGenerate}>
            <div className="input-group">
              <input
                type="text"
                placeholder="Jira Key (e.g. PROJ-123)"
                value={jiraKey}
                onChange={(e) => setJiraKey(e.target.value)}
              />
              <input
                type="text"
                placeholder="GitHub Issue Number"
                value={ghIssue}
                onChange={(e) => setGhIssue(e.target.value)}
              />
              <input
                type="text"
                placeholder="GitHub Repo (owner/repo)"
                value={ghRepo}
                onChange={(e) => setGhRepo(e.target.value)}
              />
              <input
                type="text"
                placeholder="Confluence Page ID"
                value={confluenceId}
                onChange={(e) => setConfluenceId(e.target.value)}
              />
              <input
                type="text"
                placeholder="Output filename"
                value={outputFilename}
                onChange={(e) => setOutputFilename(e.target.value)}
              />
            </div>
            <button type="submit">Generate Test Cases</button>
          </form>
        </div>
      </div>

      {/* Crawler Tab */}
      <div className={`tab-content ${activeTab === 'crawler' ? 'active' : ''}`} id="crawler">
        <div className="form-section">
          <h2>Web Crawler</h2>
          <form onSubmit={handleCrawl}>
            <div className="input-group">
              <input
                type="text"
                placeholder="URL to crawl"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <select value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="vertex">Vertex AI</option>
                <option value="openai">OpenAI</option>
              </select>
              <div className="flex-row">
                <input
                  type="number"
                  placeholder="Max pages"
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                />
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={sameDomain}
                    onChange={(e) => setSameDomain(e.target.checked)}
                  />
                  <span>Same domain only</span>
                </label>
              </div>
            </div>
            <button type="submit">Start Crawling</button>
          </form>
        </div>
      </div>

      <div className="output-section">
        <h2>Output</h2>
        <pre>{outputText}</pre>
      </div>
    </div>
  );
}

export default FridayApp;