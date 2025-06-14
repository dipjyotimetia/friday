'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ExtendedAPITestResponse,
  ExtendedCrawlResponse,
  ExtendedTestGenerationResponse,
} from '@/types';
import {
  CheckCircle,
  XCircle,
  Clock,
  Globe,
  FileText,
  AlertTriangle,
} from 'lucide-react';

interface ResultDisplayProps {
  result:
    | ExtendedAPITestResponse
    | ExtendedCrawlResponse
    | ExtendedTestGenerationResponse
    | string;
  type: 'api-test' | 'crawl' | 'test-generation';
  isLoading?: boolean;
}

export function ResultDisplay({ result, type, isLoading }: ResultDisplayProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <Clock className="h-5 w-5 animate-spin" />
            <span>Processing...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (typeof result === 'string') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Result</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
            {result}
          </pre>
        </CardContent>
      </Card>
    );
  }

  switch (type) {
    case 'api-test':
      return (
        <APITestResultDisplay result={result as ExtendedAPITestResponse} />
      );
    case 'crawl':
      return <CrawlResultDisplay result={result as ExtendedCrawlResponse} />;
    case 'test-generation':
      return (
        <TestGenerationResultDisplay
          result={result as ExtendedTestGenerationResponse}
        />
      );
    default:
      return <GenericResultDisplay result={result} />;
  }
}

function APITestResultDisplay({ result }: { result: ExtendedAPITestResponse }) {
  const successRate = result.total_tests
    ? (((result.passed_tests || 0) / result.total_tests) * 100).toFixed(1)
    : '0';

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span>API Test Results</span>
            <Badge variant={result.success ? 'default' : 'destructive'}>
              {result.success ? 'Success' : 'Failed'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.total_tests || 0}
              </div>
              <div className="text-sm text-gray-600">Total Tests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.passed_tests || 0}
              </div>
              <div className="text-sm text-gray-600">Passed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {result.failed_tests || 0}
              </div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {successRate}%
              </div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>

          {result.test_results && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Detailed Results:</h4>
              <pre className="text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(result.test_results, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function CrawlResultDisplay({ result }: { result: ExtendedCrawlResponse }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-blue-500" />
            <span>Web Crawl Results</span>
            <Badge variant={result.success ? 'default' : 'destructive'}>
              {result.success ? 'Success' : 'Failed'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.pages_crawled}
              </div>
              <div className="text-sm text-gray-600">Pages Crawled</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.embeddings_created || 0}
              </div>
              <div className="text-sm text-gray-600">Embeddings Created</div>
            </div>
          </div>

          {result.content_summary && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Content Summary:</h4>
              <div className="text-sm bg-gray-50 p-3 rounded-lg">
                {result.content_summary}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function TestGenerationResultDisplay({
  result,
}: {
  result: ExtendedTestGenerationResponse;
}) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-purple-500" />
            <span>Test Generation Results</span>
            <Badge variant={result.success ? 'default' : 'destructive'}>
              {result.success ? 'Success' : 'Failed'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {result.test_content && (
            <div className="mb-4">
              <h4 className="font-semibold mb-2">Generated Tests:</h4>
              <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96 whitespace-pre-wrap">
                {result.test_content}
              </pre>
            </div>
          )}

          {result.metadata && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Metadata:</h4>
              <pre className="text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-32">
                {JSON.stringify(result.metadata, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function GenericResultDisplay({ result }: { result: any }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-yellow-500" />
          <span>Result</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
          {JSON.stringify(result, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}
