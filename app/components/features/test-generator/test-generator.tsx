'use client';

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiService } from '@/services/api';
import { TestTube, Github, FileText, Building } from 'lucide-react';

interface TestGeneratorProps {
  setOutputText: (text: string) => void;
  isGenerating: boolean;
  setIsGenerating: (isGenerating: boolean) => void;
}

export function TestGenerator({
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
    setOutputText('Generating test cases...');

    try {
      const result = await apiService.generateTests({
        jira_key: jiraKey || undefined,
        github_issue: ghIssue || undefined,
        custom_requirements: ghRepo || undefined, // Using as custom requirements for now
        include_confluence: !!confluenceId,
        test_type: 'api',
        provider: 'openai',
      });

      if (result.success && result.test_content) {
        setOutputText(result.test_content);
      } else {
        setOutputText(JSON.stringify(result, null, 2));
      }
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const hasRequiredFields = jiraKey || (ghIssue && ghRepo) || confluenceId;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600">
            <TestTube className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle>Test Case Generator</CardTitle>
            <CardDescription>
              Generate comprehensive test cases from Jira tickets, GitHub
              issues, or Confluence pages
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleGenerate} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Building className="h-4 w-4" />
                Jira Integration
              </label>
              <Input
                type="text"
                placeholder="Jira Key (e.g. PROJ-123)"
                value={jiraKey}
                onChange={(e) => setJiraKey(e.target.value)}
                disabled={isGenerating}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Github className="h-4 w-4" />
                  GitHub Issue
                </label>
                <Input
                  type="text"
                  placeholder="Issue Number"
                  value={ghIssue}
                  onChange={(e) => setGhIssue(e.target.value)}
                  disabled={isGenerating}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">GitHub Repository</label>
                <Input
                  type="text"
                  placeholder="owner/repo"
                  value={ghRepo}
                  onChange={(e) => setGhRepo(e.target.value)}
                  disabled={isGenerating}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Confluence Page
              </label>
              <Input
                type="text"
                placeholder="Confluence Page ID"
                value={confluenceId}
                onChange={(e) => setConfluenceId(e.target.value)}
                disabled={isGenerating}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Output Filename</label>
              <Input
                type="text"
                placeholder="test_cases.md"
                value={outputFilename}
                onChange={(e) => setOutputFilename(e.target.value)}
                disabled={isGenerating}
              />
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>•</span>
            <span>
              At least one source is required (Jira, GitHub, or Confluence)
            </span>
          </div>

          <Button
            type="submit"
            disabled={isGenerating || !hasRequiredFields}
            variant="gradient"
            size="lg"
            className="w-full"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Generating Test Cases...
              </>
            ) : (
              <>
                <TestTube className="h-4 w-4 mr-2" />
                Generate Test Cases
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
