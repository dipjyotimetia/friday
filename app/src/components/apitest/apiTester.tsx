import React, { useState } from 'react';
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
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent">API Testing</h2>
      <form onSubmit={handleApiTest}>
        <div className="flex flex-col gap-5 mb-8 md:gap-4 md:mb-6">
          <FileUploader
            accept=".yaml,.yml,.json"
            onChange={handleFileChange}
            placeholder="Upload OpenAPI/Swagger Spec"
            disabled={isTestingApi}
          />
          <input
            type="url"
            placeholder="Base URL (e.g. https://api.example.com)"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            disabled={isTestingApi}
            required
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isTestingApi}
            className="w-full p-4 border border-primary-600 bg-primary-700 text-primary-100 rounded-lg transition-all duration-300 cursor-pointer text-lg hover:border-accent-600 hover:shadow-glow focus:outline-none focus:border-accent-500 md:p-4 md:text-lg"
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama</option>
            <option value="mistral">Mistral</option>
          </select>
          <input
            type="text"
            placeholder="Output filename (e.g. api_test_report.md)"
            value={apiOutput}
            onChange={(e) => setApiOutput(e.target.value.trim() || 'api_test_report.md')}
            disabled={isTestingApi}
            pattern="^[\w-]+\.md$"
            title="Filename must end with .md extension"
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
        </div>
        <button 
          type="submit" 
          disabled={isTestingApi || !specFileObj || !baseUrl}
          className={`btn-primary w-full text-xl md:text-lg md:px-6 md:py-3 ${
            (isTestingApi || !specFileObj || !baseUrl) ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          {isTestingApi ? 'Running Tests...' : 'Run API Tests'}
        </button>
      </form>
    </div>
  );
}

export default ApiTester;