'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { FileUploader } from '@/components/shared'
import { apiService } from '@/services/api'
import { AI_PROVIDERS, FILE_CONFIG, DEFAULT_VALUES } from '@/config/constants'
import { useApiTester } from '@/hooks'
import type { BaseComponentProps, AIProvider } from '@/types'
import { Upload, Zap, Globe, Settings } from 'lucide-react'

export function ApiTester({ setOutputText, setIsGenerating }: BaseComponentProps) {
  const [baseUrl, setBaseUrl] = useState('')
  const [apiOutput, setApiOutput] = useState<string>(DEFAULT_VALUES.API_OUTPUT_FILENAME)
  const [specFileObj, setSpecFileObj] = useState<File | null>(null)
  const [provider, setProvider] = useState<AIProvider>('openai')
  
  const { testApi, loading: isTestingApi } = useApiTester()

  const handleApiTest = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!specFileObj) {
      setOutputText('Error: Please upload an OpenAPI/Swagger specification file')
      return
    }

    if (!baseUrl) {
      setOutputText('Error: Please provide a base URL')
      return
    }

    if (!specFileObj.name.match(/\.(json|yaml|yml)$/i)) {
      setOutputText('Error: Invalid file type. Must be .yaml, .yml or .json')
      return
    }

    setIsGenerating(true)
    setOutputText('Running API tests...')

    try {
      const result = await testApi({
        base_url: baseUrl.trim(),
        output: apiOutput,
        spec_upload: specFileObj,
        provider: provider,
      })

      setOutputText(
        `🎯 API Test Results:\n\n` +
        `📊 **Test Statistics:**\n` +
        `• Total Tests: ${result.total_tests}\n` +
        `• Paths Tested: ${result.paths_tested}\n` +
        `• Success Rate: ${result.success_rate}%\n\n` +
        `✅ Passed: ${result.passed_tests}\n` +
        `❌ Failed: ${result.failed_tests}\n` +
        `⚠️  Errors: ${result.error_tests}\n\n` +
        `📄 ${result.message}\n\n` +
        `The detailed test report has been generated with comprehensive results for each endpoint and method tested.`
      )
    } catch (err) {
      setOutputText(`Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleFileChange = (file: File | null) => {
    setSpecFileObj(file)
    setOutputText('')
  }


  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-blue-500">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle>API Testing</CardTitle>
            <CardDescription>
              Test your APIs automatically using OpenAPI/Swagger specifications
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

            <div className="grid grid-cols-2 gap-4">
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

              <div className="space-y-2">
                <label className="text-sm font-medium">Output Filename</label>
                <Input
                  type="text"
                  placeholder="api_test_report.md"
                  value={apiOutput}
                  onChange={(e) => setApiOutput(e.target.value.trim() || DEFAULT_VALUES.API_OUTPUT_FILENAME)}
                  disabled={isTestingApi}
                  pattern="^[\w-]+\.md$"
                />
              </div>
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
  )
}