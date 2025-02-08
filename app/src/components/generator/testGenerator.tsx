import React, { useState } from 'react';
import { FormSection, Input, InputGroup, SubmitButton } from "../../css/friday";
import { apiService } from '../../services/api';

interface TestGeneratorProps {
    setOutputText: (text: string) => void;
    isGenerating: boolean;
    setIsGenerating: (isGenerating: boolean) => void;
}

function TestGenerator({ setOutputText, isGenerating, setIsGenerating }: TestGeneratorProps) {

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
                output: outputFilename
            });
            setOutputText(JSON.stringify(result, null, 2));
        } catch (err) {
            setOutputText(`Error: ${(err as Error).message}`);
        } finally {
            setIsGenerating(false);
        }
    };


    return (
        <>
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
        </>
    )
}

export default TestGenerator;