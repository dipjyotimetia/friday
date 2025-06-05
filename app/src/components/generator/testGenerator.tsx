import React, { useState } from 'react';
import { apiService } from '../../services/api';

interface TestGeneratorProps {
  setOutputText: (text: string) => void;
  isGenerating: boolean;
  setIsGenerating: (isGenerating: boolean) => void;
}

function TestGenerator({
  setOutputText,
  isGenerating,
  setIsGenerating,
}: TestGeneratorProps) {
  const [jiraKey, setJiraKey] = useState('');
  const [ghIssue, setGhIssue] = useState('');
  const [ghRepo, setGhRepo] = useState('');
  const [confluenceId, setConfluenceId] = useState('');
  const [outputFilename, setOutputFilename] = useState('test_cases.md');

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    try {
      const result = await apiService.generateTests({
        jira_key: jiraKey,
        gh_issue: ghIssue,
        gh_repo: ghRepo,
        confluence_id: confluenceId,
        output: outputFilename,
      });
      setOutputText(JSON.stringify(result, null, 2));
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent">Generate Test Cases</h2>
      <form onSubmit={handleGenerate}>
        <div className="flex flex-col gap-5 mb-8 md:gap-4 md:mb-6">
          <input
            type="text"
            placeholder="Jira Key (e.g. PROJ-123)"
            value={jiraKey}
            onChange={(e) => setJiraKey(e.target.value)}
            disabled={isGenerating}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <input
            type="text"
            placeholder="GitHub Issue Number"
            value={ghIssue}
            onChange={(e) => setGhIssue(e.target.value)}
            disabled={isGenerating}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <input
            type="text"
            placeholder="GitHub Repo (owner/repo)"
            value={ghRepo}
            onChange={(e) => setGhRepo(e.target.value)}
            disabled={isGenerating}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <input
            type="text"
            placeholder="Confluence Page ID"
            value={confluenceId}
            onChange={(e) => setConfluenceId(e.target.value)}
            disabled={isGenerating}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <input
            type="text"
            placeholder="Output filename"
            value={outputFilename}
            onChange={(e) => setOutputFilename(e.target.value)}
            disabled={isGenerating}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
        </div>
        <button 
          type="submit" 
          disabled={isGenerating}
          className={`btn-primary w-full text-xl md:text-lg md:px-6 md:py-3 ${
            isGenerating ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          {isGenerating ? 'Generating...' : 'Generate Test Cases'}
        </button>
      </form>
    </div>
  );
}

export default TestGenerator;
