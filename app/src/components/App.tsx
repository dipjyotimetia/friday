import React, { useState } from 'react';
import { apiService } from '../services/api';
import { LogViewer } from './LogViewer';
import { FileUploader } from './FileUploader';
import {
  CheckboxLabel, Container, Description, FlexRow, FormSection, Input, InputGroup,
  OutputSection, Select, SubmitButton, TabButton, TabContent, TabsContainer, Title
} from "../css/friday"
import { GlobalStyle } from '../css/GlobalStyle';


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
  const [baseUrl, setBaseUrl] = useState('');
  const [apiOutput, setApiOutput] = useState('test_report.md');
  const [specFileObj, setSpecFileObj] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [isTestingApi, setIsTestingApi] = useState(false);

  const handleTabClick = (tabId: any) => {
    setActiveTab(tabId);
    setOutputText('');
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
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
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCrawl = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCrawling(true);
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
    } finally {
      setIsCrawling(false);
    }
  };

  const handleApiTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTestingApi(true);
    try {
      const formData = new FormData();
      if (specFileObj) {
        formData.append('spec_file', specFileObj);
      }
      formData.append('base_url', baseUrl);
      formData.append('output', apiOutput);

      const result = await apiService.testApi(formData);
      setOutputText(JSON.stringify(result, null, 2));
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    } finally {
      setIsGenerating(false);
    }
  };


  return (
    <>
      <GlobalStyle />
      <Container>
        <Title>FRIDAY Test Agent</Title>
        <Description>
          FRIDAY is a test agent that can generate test cases, crawl websites, and test APIs. Select
          the tab below to get started.
        </Description>

        <TabsContainer>
          <TabButton
            isActive={activeTab === 'generator'}
            onClick={() => handleTabClick('generator')}
          >
            Test Case Generator
          </TabButton>
          <TabButton
            isActive={activeTab === 'crawler'}
            onClick={() => handleTabClick('crawler')}
          >
            Web Crawler
          </TabButton>
          <TabButton
            isActive={activeTab === 'apitest'}
            onClick={() => handleTabClick('apitest')}
          >
            API Testing
          </TabButton>
        </TabsContainer>

        <TabContent isActive={activeTab === 'generator'}>
          <FormSection>
            <h2>Generate Test Cases</h2>
            <form onSubmit={handleGenerate}>
              <InputGroup>
                <Input
                  type="text"
                  placeholder="Jira Key (e.g. PROJ-123)"
                  value={jiraKey}
                  onChange={(e) => setJiraKey(e.target.value)}
                  disabled={isGenerating}
                />
                <Input
                  type="text"
                  placeholder="GitHub Issue Number"
                  value={ghIssue}
                  onChange={(e) => setGhIssue(e.target.value)}
                  disabled={isGenerating}
                />
                <Input
                  type="text"
                  placeholder="GitHub Repo (owner/repo)"
                  value={ghRepo}
                  onChange={(e) => setGhRepo(e.target.value)}
                  disabled={isGenerating}
                />
                <Input
                  type="text"
                  placeholder="Confluence Page ID"
                  value={confluenceId}
                  onChange={(e) => setConfluenceId(e.target.value)}
                  disabled={isGenerating}
                />
                <Input
                  type="text"
                  placeholder="Output filename"
                  value={outputFilename}
                  onChange={(e) => setOutputFilename(e.target.value)}
                  disabled={isGenerating}
                />
              </InputGroup>
              <SubmitButton type="submit" disabled={isGenerating}>{isGenerating ? 'Generating...' : 'Generate Test Cases'}</SubmitButton>
            </form>
          </FormSection>
        </TabContent>

        <TabContent isActive={activeTab === 'crawler'}>
          <FormSection>
            <h2>Web Crawler</h2>
            <form onSubmit={handleCrawl}>
              <InputGroup>
                <Input
                  type="text"
                  placeholder="Website URL"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={isCrawling}
                />
                <Select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  disabled={isCrawling}
                >
                  <option value="vertex">Vertex</option>
                  <option value="openai">OpenAI</option>
                </Select>
                <Input
                  type="number"
                  placeholder="Max Pages"
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  disabled={isCrawling}
                />
                <FlexRow>
                  <CheckboxLabel>
                    <input
                      type="checkbox"
                      checked={sameDomain}
                      onChange={(e) => setSameDomain(e.target.checked)}
                      disabled={isCrawling}
                    />
                    Stay on same domain
                  </CheckboxLabel>
                </FlexRow>
              </InputGroup>
              <SubmitButton type="submit" disabled={isCrawling}>
                {isCrawling ? 'Crawling...' : 'Start Crawling'}
              </SubmitButton>
            </form>
          </FormSection>
        </TabContent>

        <TabContent isActive={activeTab === 'apitest'}>
          <FormSection>
            <h2>API Testing</h2>
            <form onSubmit={handleApiTest}>
              <InputGroup>
                <FileUploader
                  accept=".yaml,.json"
                  onChange={(file) => setSpecFileObj(file)}
                  placeholder="Upload OpenAPI/Swagger Spec"
                />
                <Input
                  type="text"
                  placeholder="Base URL (e.g. https://api.example.com)"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  disabled={isTestingApi}
                />
                <Input
                  type="text"
                  placeholder="Output filename"
                  value={apiOutput}
                  onChange={(e) => setApiOutput(e.target.value)}
                  disabled={isTestingApi}
                />
              </InputGroup>
              <SubmitButton type="submit" disabled={isTestingApi}>
                {isTestingApi ? 'Running Tests...' : 'Run API Tests'}
              </SubmitButton>
            </form>
          </FormSection>
        </TabContent>

        <OutputSection>
          <h2>Output</h2>
          <pre>{outputText}</pre>
        </OutputSection>
        <LogViewer />
      </Container>
    </>
  );
}

export default FridayApp;