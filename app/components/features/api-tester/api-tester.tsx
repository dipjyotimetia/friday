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
import { FileUploader, ResultDisplay } from '@/components/shared';
import { apiService } from '@/services/api';
import { useApiError } from '@/hooks/use-api-error';
import { AI_PROVIDERS, FILE_CONFIG, DEFAULT_VALUES } from '@/config/constants';
import type {
  BaseComponentProps,
  AIProvider,
  ExtendedAPITestResponse,
} from '@/types';
import { Upload, Zap, Globe, Settings } from 'lucide-react';

export function ApiTester({
  setOutputText,
  setIsGenerating,
}: BaseComponentProps) {
  const [baseUrl, setBaseUrl] = useState('');
  const [specFileObj, setSpecFileObj] = useState<File | null>(null);
  const [provider, setProvider] = useState<AIProvider>('openai');
  const [isTestingApi, setIsTestingApi] = useState(false);
  const [testResult, setTestResult] = useState<ExtendedAPITestResponse | null>(
    null
  );

  const { handleError, showSuccess, showWarning } = useApiError();

  const handleApiTest = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!specFileObj) {
      showWarning(
        'Missing specification file',
        'Please upload an OpenAPI/Swagger specification file'
      );
      return;
    }

    if (!baseUrl) {
      showWarning('Missing base URL', 'Please provide a base URL for testing');
      return;
    }

    if (!specFileObj.name.match(/\.(json|yaml|yml)$/i)) {
      showWarning('Invalid file type', 'Must be .yaml, .yml or .json file');
      return;
    }

    setIsTestingApi(true);
    setIsGenerating(true);
    setTestResult(null);
    setOutputText('Initializing API tests...');

    try {
      // Read the spec file content
      const specContent = await specFileObj.text();

      const result = await apiService.testApi({
        spec_content: specContent,
        base_url: baseUrl.trim(),
        auth_config: undefined, // TODO: Add auth config support
      });

      setTestResult(result);
      setOutputText('');

      if (result.success) {
        showSuccess(
          'API tests completed successfully',
          `${result.passed_tests}/${result.total_tests} tests passed`
        );
      } else {
        showWarning(
          'API tests completed with issues',
          `${result.failed_tests} tests failed`
        );
      }
    } catch (err) {
      handleError(err, 'API Testing');
      setOutputText(
        `Failed to run API tests. Please check your inputs and try again.`
      );
    } finally {
      setIsTestingApi(false);
      setIsGenerating(false);
    }
  };

  const handleFileChange = (file: File | null) => {
    setSpecFileObj(file);
    setTestResult(null);
    setOutputText('');
  };

  return (
    <div className="space-y-6">
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-blue-500">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle>API Testing</CardTitle>
              <CardDescription>
                Test your APIs automatically using OpenAPI/Swagger
                specifications
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleApiTest} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  API Specification
                </label>
                <FileUploader
                  accept={FILE_CONFIG.ACCEPTED_SPEC_FORMATS}
                  onChange={handleFileChange}
                  placeholder="Upload OpenAPI/Swagger Spec"
                  disabled={isTestingApi}
                />
                {specFileObj && (
                  <Badge variant="secondary" className="text-xs">
                    {specFileObj.name}
                  </Badge>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  Base URL
                </label>
                <Input
                  type="url"
                  placeholder="https://api.example.com"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  disabled={isTestingApi}
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  AI Provider
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as AIProvider)}
                  disabled={isTestingApi}
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 glass-card"
                >
                  {AI_PROVIDERS.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <Button
              type="submit"
              disabled={isTestingApi || !specFileObj || !baseUrl}
              variant="gradient"
              size="lg"
              className="w-full"
            >
              {isTestingApi ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Running Tests...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Run API Tests
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Results Display */}
      {testResult && (
        <ResultDisplay
          result={testResult}
          type="api-test"
          isLoading={isTestingApi}
        />
      )}
    </div>
  );
}
