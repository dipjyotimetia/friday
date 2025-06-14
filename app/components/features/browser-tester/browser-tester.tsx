'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { OutputViewer } from '@/components/shared/output-viewer'
import { LogViewer } from '@/components/shared/log-viewer'
import { apiService } from '@/services/api'
import { BROWSER_TEST_CONFIG } from '@/config/constants'
import { useWebSocket } from '@/hooks/use-websocket'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Globe, 
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
  Code
} from 'lucide-react'

import type {
  BrowserTestRequest,
  BrowserTestResult,
  MultipleBrowserTestRequest
} from '@/types'

export function BrowserTester() {
  const [activeTab, setActiveTab] = useState('single')
  const [singleTest, setSingleTest] = useState<BrowserTestRequest>({
    requirement: '',
    url: '',
    test_type: BROWSER_TEST_CONFIG.DEFAULT_TEST_TYPE,
    context: '',
    headless: BROWSER_TEST_CONFIG.DEFAULT_HEADLESS,
    take_screenshots: BROWSER_TEST_CONFIG.DEFAULT_SCREENSHOTS
  })
  
  const [multipleTests, setMultipleTests] = useState<MultipleBrowserTestRequest>({
    test_cases: [{
      requirement: '',
      url: '',
      test_type: BROWSER_TEST_CONFIG.DEFAULT_TEST_TYPE,
      context: '',
      take_screenshots: BROWSER_TEST_CONFIG.DEFAULT_SCREENSHOTS
    }],
    headless: BROWSER_TEST_CONFIG.DEFAULT_HEADLESS
  })

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

  const testTypes = BROWSER_TEST_CONFIG.TEST_TYPES.map(type => ({
    ...type,
    icon: type.value === 'functional' ? '⚙️' :
          type.value === 'ui' ? '🎨' :
          type.value === 'integration' ? '🔗' :
          type.value === 'accessibility' ? '♿' :
          type.value === 'performance' ? '⚡' : '🔧'
  }))

  const handleSingleTest = async () => {
    if (!singleTest.requirement || !singleTest.url) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiService.runSingleBrowserTest(singleTest)

      if (response.success && response.data) {
        setTestResults([response.data])
        setTestReport('')
        setTestSummary(null)
      }
    } catch (err: any) {
      console.error('Browser test failed:', err)
      setError(err.message || 'Failed to run browser test')
    } finally {
      setLoading(false)
    }
  }

  const handleMultipleTests = async () => {
    const validTestCases = multipleTests.test_cases.filter(
      tc => tc.requirement.trim() && tc.url.trim()
    )

    if (validTestCases.length === 0) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiService.runMultipleBrowserTests({
        ...multipleTests,
        test_cases: validTestCases
      })

      if (response.success && response.data) {
        setTestResults(response.data)
        setTestReport(response.report || '')
        setTestSummary(response.summary || null)
      }
    } catch (err: any) {
      console.error('Multiple browser tests failed:', err)
      setError(err.message || 'Failed to run multiple browser tests')
    } finally {
      setLoading(false)
    }
  }

  const addTestCase = () => {
    setMultipleTests(prev => ({
      ...prev,
      test_cases: [
        ...prev.test_cases,
        {
          requirement: '',
          url: '',
          test_type: BROWSER_TEST_CONFIG.DEFAULT_TEST_TYPE,
          context: '',
          take_screenshots: BROWSER_TEST_CONFIG.DEFAULT_SCREENSHOTS
        }
      ]
    }))
  }

  const removeTestCase = (index: number) => {
    setMultipleTests(prev => ({
      ...prev,
      test_cases: prev.test_cases.filter((_, i) => i !== index)
    }))
  }

  const updateTestCase = (index: number, field: string, value: any) => {
    setMultipleTests(prev => ({
      ...prev,
      test_cases: prev.test_cases.map((tc, i) => 
        i === index ? { ...tc, [field]: value } : tc
      )
    }))
  }

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

      const response = await fetch('/api/v1/browser-test/yaml/upload', {
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
      const response = await fetch('/api/v1/browser-test/yaml/execute', {
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
      const response = await fetch('/api/v1/browser-test/yaml/template')
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
      }
    } catch (err: any) {
      console.error('Failed to download template:', err)
      setError('Failed to download YAML template')
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
          <p className="text-gray-600">AI-powered automated browser testing</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="single" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Single Test
          </TabsTrigger>
          <TabsTrigger value="multiple" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Multiple Tests
          </TabsTrigger>
          <TabsTrigger value="yaml" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            YAML Scenarios
          </TabsTrigger>
        </TabsList>

        <TabsContent value="single" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Test Requirement *
                </label>
                <Input
                  placeholder="Describe what you want to test (e.g., 'Test user login functionality')"
                  value={singleTest.requirement}
                  onChange={(e) => setSingleTest(prev => ({ ...prev, requirement: e.target.value }))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Target URL *
                </label>
                <Input
                  placeholder="https://example.com"
                  value={singleTest.url}
                  onChange={(e) => setSingleTest(prev => ({ ...prev, url: e.target.value }))}
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Test Type
                  </label>
                  <select
                    value={singleTest.test_type}
                    onChange={(e) => setSingleTest(prev => ({ ...prev, test_type: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    {testTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-4 pt-6">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={singleTest.headless}
                      onChange={(e) => setSingleTest(prev => ({ ...prev, headless: e.target.checked }))}
                    />
                    <span className="text-sm">Headless Mode</span>
                    {singleTest.headless ? 
                      <EyeOff className="h-4 w-4 text-gray-400" /> : 
                      <Eye className="h-4 w-4 text-blue-500" />
                    }
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={singleTest.take_screenshots}
                      onChange={(e) => setSingleTest(prev => ({ ...prev, take_screenshots: e.target.checked }))}
                    />
                    <span className="text-sm">Screenshots</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Additional Context (Optional)
                </label>
                <textarea
                  placeholder="Any additional instructions or context for the test..."
                  value={singleTest.context || ''}
                  onChange={(e) => setSingleTest(prev => ({ ...prev, context: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md h-20 resize-none"
                />
              </div>

              <Button
                onClick={handleSingleTest}
                disabled={loading || !singleTest.requirement || !singleTest.url}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Running Browser Test...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Run Browser Test
                  </>
                )}
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="multiple" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Test Cases</h3>
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={multipleTests.headless}
                      onChange={(e) => setMultipleTests(prev => ({ ...prev, headless: e.target.checked }))}
                    />
                    Headless Mode
                    {multipleTests.headless ? 
                      <EyeOff className="h-4 w-4 text-gray-400" /> : 
                      <Eye className="h-4 w-4 text-blue-500" />
                    }
                  </label>
                </div>
              </div>

              <AnimatePresence>
                {multipleTests.test_cases.map((testCase, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="p-4 border rounded-lg space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">Test Case {index + 1}</h4>
                      {multipleTests.test_cases.length > 1 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeTestCase(index)}
                        >
                          Remove
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <Input
                        placeholder="Test requirement"
                        value={testCase.requirement}
                        onChange={(e) => updateTestCase(index, 'requirement', e.target.value)}
                      />
                      <Input
                        placeholder="Target URL"
                        value={testCase.url}
                        onChange={(e) => updateTestCase(index, 'url', e.target.value)}
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <select
                        value={testCase.test_type}
                        onChange={(e) => updateTestCase(index, 'test_type', e.target.value)}
                        className="px-3 py-2 border rounded-md"
                      >
                        {testTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.icon} {type.label}
                          </option>
                        ))}
                      </select>

                      <Input
                        placeholder="Context (optional)"
                        value={testCase.context || ''}
                        onChange={(e) => updateTestCase(index, 'context', e.target.value)}
                      />

                      <label className="flex items-center gap-2 px-3">
                        <input
                          type="checkbox"
                          checked={testCase.take_screenshots}
                          onChange={(e) => updateTestCase(index, 'take_screenshots', e.target.checked)}
                        />
                        <span className="text-sm">Screenshots</span>
                      </label>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              <div className="flex gap-2">
                <Button variant="outline" onClick={addTestCase}>
                  Add Test Case
                </Button>
                <Button
                  onClick={handleMultipleTests}
                  disabled={loading || multipleTests.test_cases.every(tc => !tc.requirement || !tc.url)}
                  className="flex-1"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Running Tests...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run All Tests
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="yaml" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">YAML Test Scenarios</h3>
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
        </TabsContent>
      </Tabs>

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
              <div key={index} className="p-4 border rounded-lg">
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
              </div>
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