'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { OutputViewer } from '@/components/shared/output-viewer'
import { LogViewer } from '@/components/shared/log-viewer'
import { API_CONFIG } from '@/config/constants'
import { useWebSocket } from '@/hooks/use-websocket'
import { motion } from 'framer-motion'
import { 
  Monitor, 
  Eye, 
  EyeOff, 
  FileText, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  Upload,
  Download,
  Code,
  Play
} from 'lucide-react'

import type {
  BrowserTestResult
} from '@/types'

export function BrowserTester() {
  const [testResults, setTestResults] = useState<BrowserTestResult[]>([])
  const [testReport, setTestReport] = useState<string>('')
  const [testSummary, setTestSummary] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  
  // YAML-related state
  const [yamlContent, setYamlContent] = useState<string>('')
  const [yamlFile, setYamlFile] = useState<File | null>(null)
  const [yamlProvider, setYamlProvider] = useState('openai')
  const [yamlHeadless, setYamlHeadless] = useState(true)
  const [executeImmediately, setExecuteImmediately] = useState(false)

  const { logs, isConnected } = useWebSocket()


  const getStatusIcon = (result: BrowserTestResult) => {
    if (result.success) {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    } else {
      return <XCircle className="h-5 w-5 text-red-500" />
    }
  }

  const getStatusBadge = (result: BrowserTestResult) => {
    const variant = result.success ? 'default' : 'destructive'
    return (
      <Badge variant={variant}>
        {result.success ? 'PASSED' : 'FAILED'}
      </Badge>
    )
  }

  // YAML-related functions
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && (file.name.endsWith('.yaml') || file.name.endsWith('.yml'))) {
      setYamlFile(file)
      
      // Read file content
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setYamlContent(content)
      }
      reader.readAsText(file)
    } else {
      setError('Please select a valid YAML file (.yaml or .yml)')
    }
  }

  const handleYamlUploadAndExecute = async () => {
    if (!yamlFile) {
      setError('Please select a YAML file')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', yamlFile)
      formData.append('provider', yamlProvider)
      formData.append('headless', yamlHeadless.toString())
      formData.append('execute_immediately', executeImmediately.toString())

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/browser-test/yaml/upload`, {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (result.success) {
        if (result.execution_results) {
          setTestResults(result.execution_results)
          setTestReport(result.report || '')
          setTestSummary(result.summary || null)
        } else {
          // Just uploaded, show scenarios
          setError(null)
          console.log('YAML uploaded successfully:', result)
        }
      } else {
        setError(result.error || 'Failed to upload YAML file')
      }
    } catch (err: any) {
      console.error('YAML upload failed:', err)
      setError(err.message || 'Failed to upload YAML file')
    } finally {
      setLoading(false)
    }
  }

  const handleYamlExecute = async () => {
    if (!yamlContent.trim()) {
      setError('Please provide YAML content')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/browser-test/yaml/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          yaml_content: yamlContent,
          provider: yamlProvider,
          headless: yamlHeadless
        })
      })

      const result = await response.json()

      if (result.success) {
        setTestResults(result.results)
        setTestReport(result.report)
        setTestSummary(result.summary)
      } else {
        setError(result.error || 'Failed to execute YAML scenarios')
      }
    } catch (err: any) {
      console.error('YAML execution failed:', err)
      setError(err.message || 'Failed to execute YAML scenarios')
    } finally {
      setLoading(false)
    }
  }

  const downloadYamlTemplate = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/browser-test/yaml/template`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.template_content) {
        const blob = new Blob([result.template_content], { type: 'application/x-yaml' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'browser_test_template.yaml'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        console.log('Template downloaded successfully')
      } else {
        throw new Error('No template content received from server')
      }
    } catch (err: any) {
      console.error('Failed to download template:', err)
      setError(`Failed to download YAML template: ${err.message}`)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Monitor className="h-6 w-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Browser Testing Agent</h2>
          <p className="text-gray-600">AI-powered automated browser testing with YAML scenarios</p>
        </div>
      </div>


      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Code className="h-5 w-5" />
              YAML Test Scenarios
            </h3>
            <Button variant="outline" onClick={downloadYamlTemplate} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Download Template
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">LLM Provider</label>
              <select
                value={yamlProvider}
                onChange={(e) => setYamlProvider(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="openai">OpenAI</option>
                <option value="gemini">Google Gemini</option>
                <option value="ollama">Ollama</option>
                <option value="mistral">Mistral</option>
              </select>
            </div>

            <div className="flex items-center gap-4 pt-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={yamlHeadless}
                  onChange={(e) => setYamlHeadless(e.target.checked)}
                />
                <span className="text-sm">Headless Mode</span>
                {yamlHeadless ? 
                  <EyeOff className="h-4 w-4 text-gray-400" /> : 
                  <Eye className="h-4 w-4 text-blue-500" />
                }
              </label>
            </div>

            <div className="flex items-center gap-4 pt-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={executeImmediately}
                  onChange={(e) => setExecuteImmediately(e.target.checked)}
                />
                <span className="text-sm">Execute Immediately</span>
              </label>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium mb-3">Upload YAML File</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <input
                  type="file"
                  accept=".yaml,.yml"
                  onChange={handleFileUpload}
                  className="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {yamlFile && (
                  <span className="text-sm text-green-600">
                    ✓ {yamlFile.name}
                  </span>
                )}
              </div>
              
              <Button
                onClick={handleYamlUploadAndExecute}
                disabled={loading || !yamlFile}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {executeImmediately ? 'Uploading and Executing...' : 'Uploading...'}
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    {executeImmediately ? 'Upload and Execute' : 'Upload YAML'}
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium mb-3">Or Paste YAML Content</h4>
            <div className="space-y-3">
              <textarea
                placeholder="Paste your YAML content here..."
                value={yamlContent}
                onChange={(e) => setYamlContent(e.target.value)}
                className="w-full px-3 py-2 border rounded-md h-40 font-mono text-sm resize-none"
              />
              
              <Button
                onClick={handleYamlExecute}
                disabled={loading || !yamlContent.trim()}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Executing YAML Scenarios...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Execute YAML Scenarios
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">YAML Format</h4>
            <p className="text-sm text-blue-700 mb-2">
              Define test scenarios in YAML format with the following structure:
            </p>
            <div className="bg-white border rounded p-3 font-mono text-xs">
              <pre>{`name: "Test Suite Name"
scenarios:
  - name: "Test Name"
    requirement: "What to test"
    url: "https://example.com"
    test_type: "functional"
    context: "Additional context"
    take_screenshots: true`}</pre>
            </div>
          </div>
        </div>
      </Card>

      {/* Test Results */}
      {testResults.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Test Results
          </h3>

          {testSummary && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-600">{testSummary.total_tests}</div>
                  <div className="text-sm text-gray-600">Total Tests</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">{testSummary.passed_tests}</div>
                  <div className="text-sm text-gray-600">Passed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-red-600">{testSummary.failed_tests}</div>
                  <div className="text-sm text-gray-600">Failed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">{testSummary.success_rate?.toFixed(1)}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {testResults.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 border rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(result)}
                    <span className="font-medium">{result.requirement}</span>
                    {getStatusBadge(result)}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="h-4 w-4" />
                    {result.timestamp ? new Date(result.timestamp * 1000).toLocaleString() : 'N/A'}
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  <span className="font-medium">URL:</span> {result.url} | 
                  <span className="font-medium ml-2">Type:</span> {result.test_type}
                </div>

                {result.execution_result && (
                  <div className="mt-2">
                    <OutputViewer outputText={result.execution_result} />
                  </div>
                )}

                {result.errors.length > 0 && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                    <div className="flex items-center gap-2 text-red-700 font-medium mb-1">
                      <AlertCircle className="h-4 w-4" />
                      Errors
                    </div>
                    {result.errors.map((error, errorIndex) => (
                      <div key={errorIndex} className="text-sm text-red-600">
                        {error}
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Test Report */}
      {testReport && (
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">Test Report</h3>
          <OutputViewer outputText={testReport} />
        </Card>
      )}

      {/* Real-time Logs */}
      {isConnected && logs.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">Live Logs</h3>
          <LogViewer />
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-2">{error}</p>
        </Card>
      )}
    </div>
  )
}