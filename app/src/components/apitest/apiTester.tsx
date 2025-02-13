import React, { useState } from 'react';
import { FormSection, Input, InputGroup, Select, SubmitButton } from '../../css/friday';
import { apiService } from '../../services/api';
import { FileUploader } from '../FileUploader';

interface ApiTesterProps {
  setOutputText: (text: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
}

function ApiTester({ setOutputText, setIsGenerating }: ApiTesterProps) {
  const [baseUrl, setBaseUrl] = useState('');
  const [isTestingApi, setIsTestingApi] = useState(false);
  const [apiOutput, setApiOutput] = useState('api_test_report.md');
  const [specFileObj, setSpecFileObj] = useState<File | null>(null);
  const [provider, setProvider] = useState('openai');

  const handleApiTest = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate inputs
    if (!specFileObj) {
      setOutputText('Error: Please upload an OpenAPI/Swagger specification file');
      return;
    }

    if (!baseUrl) {
      setOutputText('Error: Please provide a base URL');
      return;
    }

    // Validate file extension
    if (!specFileObj.name.match(/\.(json|yaml|yml)$/i)) {
      setOutputText('Error: Invalid file type. Must be .yaml, .yml or .json');
      return;
    }

    // Update loading states
    setIsTestingApi(true);
    setIsGenerating(true);
    setOutputText('Running API tests...');

    try {
      const result = await apiService.testApi({
        base_url: baseUrl.trim(),
        output: apiOutput,
        spec_upload: specFileObj,
        provider: provider,
      });

      setOutputText(
        `Test Results:\n` +
        `- Total Tests: ${result.total_tests}\n` +
        `- Paths Tested: ${result.paths_tested}\n` +
        `- Message: ${result.message}`
      );
    } catch (err) {
      setOutputText(`Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`);
    } finally {
      setIsTestingApi(false);
      setIsGenerating(false);
    }
  };

  const handleFileChange = (file: File | null) => {
    setSpecFileObj(file);
    setOutputText('');
  };

  return (
    <FormSection>
      <h2>API Testing</h2>
      <form onSubmit={handleApiTest}>
        <InputGroup>
          <FileUploader
            accept=".yaml,.yml,.json"
            onChange={handleFileChange}
            placeholder="Upload OpenAPI/Swagger Spec"
            disabled={isTestingApi}
          />
          <Input
            type="url"
            placeholder="Base URL (e.g. https://api.example.com)"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            disabled={isTestingApi}
            required
          />
          <Select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isTestingApi}
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama</option>
            <option value="mistral">Mistral</option>
          </Select>
          <Input
            type="text"
            placeholder="Output filename (e.g. api_test_report.md)"
            value={apiOutput}
            onChange={(e) => setApiOutput(e.target.value.trim() || 'api_test_report.md')}
            disabled={isTestingApi}
            pattern="^[\w-]+\.md$"
            title="Filename must end with .md extension"
          />
        </InputGroup>
        <SubmitButton type="submit" disabled={isTestingApi || !specFileObj || !baseUrl}>
          {isTestingApi ? 'Running Tests...' : 'Run API Tests'}
        </SubmitButton>
      </form>
    </FormSection>
  );
}

export default ApiTester;