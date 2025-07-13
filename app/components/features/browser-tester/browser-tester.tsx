"use client"

import React, { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { FileUploader } from "@/components/shared/file-uploader"
import { useWebSocket } from "@/hooks/use-websocket"
import { API_ENDPOINTS, API_CONFIG } from "@/config/constants"
import { BrowserTestReport, BrowserTestSuite, BrowserTestExecutionRequest } from "@/types"

interface BrowserTesterProps {
  className?: string
}

interface UploadedTestSuite {
  fileId: string
  filename: string
  content: string
  parsedSuite: BrowserTestSuite
}

interface TestExecution {
  executionId: string
  suiteId: string
  suiteName: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: BrowserTestReport
}

export function BrowserTester({ className }: BrowserTesterProps) {
  const [activeTab, setActiveTab] = useState("upload")
  const [uploadedSuites, setUploadedSuites] = useState<UploadedTestSuite[]>([])
  const [selectedSuites, setSelectedSuites] = useState<string[]>([])
  const [testExecutions, setTestExecutions] = useState<TestExecution[]>([])
  const [isExecuting, setIsExecuting] = useState(false)
  const [provider, setProvider] = useState("openai")
  const [headless, setHeadless] = useState(true)
  const [executionMode, setExecutionMode] = useState<'sequential' | 'parallel'>('sequential')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [uploadLoading, setUploadLoading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [executeLoading, setExecuteLoading] = useState(false)

  const [executionWebSocketUrl, setExecutionWebSocketUrl] = useState<string | null>(null)
  const { 
    logs, 
    isConnected, 
    connect: connectWebSocket, 
    disconnect: disconnectWebSocket 
  } = useWebSocket(executionWebSocketUrl ? {
    url: executionWebSocketUrl,
    autoReconnect: true,
    maxLogs: 200
  } : {})

  const handleFileUpload = async (file: File | null) => {
    if (!file) return

    if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
      setUploadError('Please upload a YAML file (.yaml or .yml)')
      return
    }

    const content = await file.text()

    // Upload to server
    setUploadLoading(true)
    setUploadError(null)
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.BROWSER_TEST.UPLOAD_YAML}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          content: content
        })
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const result = await response.json()
      
      // Add to uploaded suites
      const newSuite: UploadedTestSuite = {
        fileId: result.file_id,
        filename: file.name,
        content: content,
        parsedSuite: result.parsed_suite
      }
      
      setUploadedSuites(prev => [...prev, newSuite])
      setSelectedSuites(prev => [...prev, result.file_id])
      setActiveTab("preview")
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload YAML'
      setUploadError(errorMessage)
      console.error('Failed to upload YAML:', error)
    } finally {
      setUploadLoading(false)
    }
  }

  const handleMultipleFileUpload = async (files: FileList) => {
    const yamlFiles = Array.from(files).filter(file => 
      file.name.endsWith('.yaml') || file.name.endsWith('.yml')
    )

    if (yamlFiles.length === 0) {
      setUploadError('Please upload at least one YAML file (.yaml or .yml)')
      return
    }

    setUploadLoading(true)
    setUploadError(null)
    
    const uploadResults: UploadedTestSuite[] = []
    const newSelectedSuites: string[] = []

    try {
      for (const file of yamlFiles) {
        const content = await file.text()
        
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.BROWSER_TEST.UPLOAD_YAML}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            filename: file.name,
            content: content
          })
        })

        if (!response.ok) {
          throw new Error(`Upload failed for ${file.name}: ${response.statusText}`)
        }

        const result = await response.json()
        
        const newSuite: UploadedTestSuite = {
          fileId: result.file_id,
          filename: file.name,
          content: content,
          parsedSuite: result.parsed_suite
        }
        
        uploadResults.push(newSuite)
        newSelectedSuites.push(result.file_id)
      }
      
      setUploadedSuites(prev => [...prev, ...uploadResults])
      setSelectedSuites(prev => [...prev, ...newSelectedSuites])
      setActiveTab("preview")
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload YAML files'
      setUploadError(errorMessage)
      console.error('Failed to upload YAML files:', error)
    } finally {
      setUploadLoading(false)
    }
  }

  const handleExecuteTests = async () => {
    if (selectedSuites.length === 0) return

    setIsExecuting(true)
    setTestExecutions([])
    setExecuteLoading(true)

    try {
      setActiveTab("execution")

      if (executionMode === 'sequential') {
        await executeTestsSequentially()
      } else {
        await executeTestsInParallel()
      }
    } catch (error) {
      console.error('Failed to execute tests:', error)
    } finally {
      setIsExecuting(false)
      setExecuteLoading(false)
    }
  }

  const executeTestsSequentially = async () => {
    const executions: TestExecution[] = []

    for (const suiteId of selectedSuites) {
      const suite = uploadedSuites.find(s => s.fileId === suiteId)
      if (!suite) continue

      const execution: TestExecution = {
        executionId: '',
        suiteId: suiteId,
        suiteName: suite.parsedSuite.name,
        status: 'pending'
      }
      
      executions.push(execution)
      setTestExecutions([...executions])

      try {
        // Update status to running
        execution.status = 'running'
        setTestExecutions([...executions])

        const request: BrowserTestExecutionRequest = {
          file_id: suiteId,
          provider,
          headless,
          output_format: "json"
        }

        const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.BROWSER_TEST.EXECUTE_YAML}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request)
        })

        if (!response.ok) {
          throw new Error(`Execution failed: ${response.statusText}`)
        }

        const result = await response.json()
        execution.executionId = result.execution_id
        
        // Set up WebSocket for this execution
        const wsUrl = `${API_CONFIG.BASE_URL.replace('http', 'ws')}${API_ENDPOINTS.BROWSER_TEST.WS_BASE}/${result.execution_id}`
        setExecutionWebSocketUrl(wsUrl)
        connectWebSocket()
        
        // Poll for completion
        const finalResult = await pollExecutionStatus(result.execution_id)
        execution.status = 'completed'
        execution.result = finalResult
        setTestExecutions([...executions])
        
      } catch (error) {
        execution.status = 'failed'
        setTestExecutions([...executions])
        console.error(`Failed to execute suite ${suite.parsedSuite.name}:`, error)
      }
    }
    
    setActiveTab("results")
  }

  const executeTestsInParallel = async () => {
    const executionPromises = selectedSuites.map(async (suiteId) => {
      const suite = uploadedSuites.find(s => s.fileId === suiteId)
      if (!suite) return null

      const execution: TestExecution = {
        executionId: '',
        suiteId: suiteId,
        suiteName: suite.parsedSuite.name,
        status: 'running'
      }

      try {
        const request: BrowserTestExecutionRequest = {
          file_id: suiteId,
          provider,
          headless,
          output_format: "json"
        }

        const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.BROWSER_TEST.EXECUTE_YAML}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request)
        })

        if (!response.ok) {
          throw new Error(`Execution failed: ${response.statusText}`)
        }

        const result = await response.json()
        execution.executionId = result.execution_id
        
        // Set up WebSocket for this execution
        const wsUrl = `${API_CONFIG.BASE_URL.replace('http', 'ws')}${API_ENDPOINTS.BROWSER_TEST.WS_BASE}/${result.execution_id}`
        setExecutionWebSocketUrl(wsUrl)
        connectWebSocket()
        
        // Poll for completion
        const finalResult = await pollExecutionStatus(result.execution_id)
        execution.status = 'completed'
        execution.result = finalResult
        
        return execution
      } catch (error) {
        execution.status = 'failed'
        console.error(`Failed to execute suite ${suite.parsedSuite.name}:`, error)
        return execution
      }
    })

    // Initialize executions with pending status
    const initialExecutions: TestExecution[] = selectedSuites.map(suiteId => {
      const suite = uploadedSuites.find(s => s.fileId === suiteId)!
      return {
        executionId: '',
        suiteId: suiteId,
        suiteName: suite.parsedSuite.name,
        status: 'pending'
      }
    })
    setTestExecutions(initialExecutions)

    // Wait for all executions to complete
    const results = await Promise.all(executionPromises)
    const completedExecutions = results.filter(Boolean) as TestExecution[]
    setTestExecutions(completedExecutions)
    setActiveTab("results")
  }

  const pollExecutionStatus = async (execId: string): Promise<BrowserTestReport | null> => {
    const maxAttempts = 60 // 5 minutes max
    let attempts = 0

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.BROWSER_TEST.EXECUTION_STATUS}/${execId}`)
          
          if (!response.ok) {
            throw new Error(`Status check failed: ${response.statusText}`)
          }

          const result = await response.json()

          if (result.status === 'completed') {
            resolve(result.report)
          } else if (result.status === 'failed') {
            reject(new Error(result.error || 'Execution failed'))
          } else if (attempts < maxAttempts) {
            attempts++
            setTimeout(poll, 5000) // Poll every 5 seconds
          } else {
            reject(new Error('Execution timeout'))
          }
        } catch (error) {
          reject(error)
        }
      }

      setTimeout(poll, 2000) // Start polling after 2 seconds
    })
  }

  const handleReset = () => {
    setUploadedSuites([])
    setSelectedSuites([])
    setTestExecutions([])
    setIsExecuting(false)
    setActiveTab("upload")
    disconnectWebSocket()
    
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleSuiteSelection = (suiteId: string, selected: boolean) => {
    if (selected) {
      setSelectedSuites(prev => [...prev, suiteId])
    } else {
      setSelectedSuites(prev => prev.filter(id => id !== suiteId))
    }
  }

  const handleSelectAllSuites = () => {
    setSelectedSuites(uploadedSuites.map(suite => suite.fileId))
  }

  const handleDeselectAllSuites = () => {
    setSelectedSuites([])
  }

  const removeSuite = (suiteId: string) => {
    setUploadedSuites(prev => prev.filter(suite => suite.fileId !== suiteId))
    setSelectedSuites(prev => prev.filter(id => id !== suiteId))
  }

  const renderUploadTab = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Upload YAML Test Files</h3>
        <p className="text-sm text-gray-600 mb-4">
          Upload one or more YAML files containing your browser test scenarios
        </p>
      </div>

      <FileUploader
        accept=".yaml,.yml"
        onChange={handleFileUpload}
        disabled={uploadLoading}
        className="max-w-md mx-auto"
      />

      <div className="text-center">
        <p className="text-sm text-gray-500 mb-2">Or upload multiple files at once:</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".yaml,.yml"
          onChange={(e) => e.target.files && handleMultipleFileUpload(e.target.files)}
          disabled={uploadLoading}
          className="hidden"
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadLoading}
          variant="outline"
        >
          Select Multiple Files
        </Button>
      </div>
      
      {uploadLoading && (
        <div className="text-center text-sm text-gray-600">
          Uploading and parsing YAML files...
        </div>
      )}
      
      {uploadError && (
        <div className="text-center text-sm text-red-600 bg-red-50 p-2 rounded">
          {uploadError}
        </div>
      )}

      {uploadedSuites.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Test Suites ({uploadedSuites.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedSuites.map((suite) => (
                <div key={suite.fileId} className="flex items-center justify-between p-3 border rounded">
                  <div className="flex-1">
                    <h4 className="font-medium">{suite.parsedSuite.name}</h4>
                    <p className="text-sm text-gray-600">{suite.filename}</p>
                    <p className="text-xs text-gray-500">
                      {suite.parsedSuite.scenarios.length} scenarios
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeSuite(suite.fileId)}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )

  const renderPreviewTab = () => (
    <div className="space-y-6">
      {uploadedSuites.length > 0 && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Test Suite Selection</CardTitle>
              <CardDescription>
                Select which test suites to execute ({selectedSuites.length} of {uploadedSuites.length} selected)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={handleSelectAllSuites}>
                    Select All
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleDeselectAllSuites}>
                    Deselect All
                  </Button>
                </div>

                <div className="space-y-3">
                  {uploadedSuites.map((suite) => (
                    <div key={suite.fileId} className="flex items-start gap-3 p-3 border rounded">
                      <input
                        type="checkbox"
                        checked={selectedSuites.includes(suite.fileId)}
                        onChange={(e) => handleSuiteSelection(suite.fileId, e.target.checked)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-medium">{suite.parsedSuite.name}</h5>
                          <Badge variant="outline">
                            {suite.parsedSuite.scenarios.length} scenarios
                          </Badge>
                        </div>
                        {suite.parsedSuite.description && (
                          <p className="text-sm text-gray-600 mb-2">{suite.parsedSuite.description}</p>
                        )}
                        <p className="text-xs text-gray-500">{suite.filename}</p>
                        
                        <div className="mt-2 space-y-1">
                          {suite.parsedSuite.scenarios.map((scenario: any, index: number) => (
                            <div key={index} className="text-xs text-gray-600 pl-2 border-l-2 border-gray-200">
                              <span className="font-medium">{scenario.name}</span> - {scenario.test_type}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Execution Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">LLM Provider</label>
                    <select 
                      value={provider} 
                      onChange={(e) => setProvider(e.target.value)}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="openai">OpenAI</option>
                      <option value="gemini">Google Gemini</option>
                      <option value="ollama">Ollama</option>
                      <option value="mistral">Mistral</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Browser Mode</label>
                    <select 
                      value={headless ? "headless" : "visible"} 
                      onChange={(e) => setHeadless(e.target.value === "headless")}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="headless">Headless</option>
                      <option value="visible">Visible</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Execution Mode</label>
                  <select 
                    value={executionMode} 
                    onChange={(e) => setExecutionMode(e.target.value as 'sequential' | 'parallel')}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="sequential">Sequential (one after another)</option>
                    <option value="parallel">Parallel (all at once)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {executionMode === 'sequential' 
                      ? 'Tests will run one after another, safer for resource usage'
                      : 'Tests will run simultaneously, faster but uses more resources'
                    }
                  </p>
                </div>

                <div className="flex gap-2 pt-4">
                  <Button 
                    onClick={handleExecuteTests}
                    disabled={executeLoading || selectedSuites.length === 0}
                    className="flex-1"
                  >
                    {executeLoading 
                      ? "Starting..." 
                      : `Execute ${selectedSuites.length} Suite${selectedSuites.length !== 1 ? 's' : ''}`
                    }
                  </Button>
                  <Button variant="outline" onClick={handleReset}>
                    Reset All
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )

  const renderExecutionTab = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Execution Status
            {isExecuting && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"
              />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {testExecutions.length}
                </div>
                <div className="text-sm text-gray-600">Total Suites</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {testExecutions.filter(e => e.status === 'completed').length}
                </div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
            </div>

            <div className="flex justify-between">
              <span>Execution Mode:</span>
              <Badge variant="outline">{executionMode}</Badge>
            </div>
            <div className="flex justify-between">
              <span>WebSocket:</span>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {testExecutions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Suite Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {testExecutions.map((execution) => (
                <div key={execution.suiteId} className="flex items-center justify-between p-3 border rounded">
                  <div className="flex-1">
                    <h5 className="font-medium">{execution.suiteName}</h5>
                    {execution.executionId && (
                      <p className="text-xs text-gray-500">ID: {execution.executionId}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={
                      execution.status === 'completed' ? 'default' :
                      execution.status === 'failed' ? 'destructive' :
                      execution.status === 'running' ? 'secondary' : 'outline'
                    }>
                      {execution.status}
                    </Badge>
                    {execution.status === 'running' && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full"
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Real-time Execution Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="text-center text-gray-500 py-4">
                {isConnected ? 'Waiting for logs...' : 'Not connected to log stream'}
              </div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="text-sm p-2 bg-gray-50 rounded">
                  <span className="text-gray-500">{log.timestamp}</span>: {log.message}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderResultsTab = () => {
    const completedExecutions = testExecutions.filter(e => e.result)
    const totalTests = completedExecutions.reduce((sum, e) => sum + (e.result?.total_tests || 0), 0)
    const totalPassed = completedExecutions.reduce((sum, e) => sum + (e.result?.passed_tests || 0), 0)
    const totalFailed = completedExecutions.reduce((sum, e) => sum + (e.result?.failed_tests || 0), 0)
    const overallSuccessRate = totalTests > 0 ? (totalPassed / totalTests * 100) : 0

    return (
      <div className="space-y-6">
        {completedExecutions.length > 0 && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Overall Results Summary</CardTitle>
                <CardDescription>
                  Results from {completedExecutions.length} test suite{completedExecutions.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {totalTests}
                    </div>
                    <div className="text-sm text-gray-600">Total Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {totalPassed}
                    </div>
                    <div className="text-sm text-gray-600">Passed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {totalFailed}
                    </div>
                    <div className="text-sm text-gray-600">Failed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {overallSuccessRate.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {completedExecutions.map((execution) => (
              execution.result && (
                <Card key={execution.suiteId}>
                  <CardHeader>
                    <CardTitle>{execution.suiteName}</CardTitle>
                    <CardDescription>
                      Suite execution results
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600">
                          {execution.result.total_tests}
                        </div>
                        <div className="text-sm text-gray-600">Total Tests</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-green-600">
                          {execution.result.passed_tests}
                        </div>
                        <div className="text-sm text-gray-600">Passed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-red-600">
                          {execution.result.failed_tests}
                        </div>
                        <div className="text-sm text-gray-600">Failed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-purple-600">
                          {execution.result.success_rate.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">Success Rate</div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h5 className="font-medium">Scenario Results:</h5>
                      {execution.result.results.map((result, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded">
                          <div className="flex-1">
                            <h6 className="font-medium">{result.scenario_name}</h6>
                            <div className="text-sm text-gray-600 space-y-1">
                              <p>Execution time: {result.execution_time.toFixed(2)}s</p>
                              {result.error_message && (
                                <p className="text-red-600">Error: {result.error_message}</p>
                              )}
                              {result.screenshot_path && (
                                <p className="text-blue-600">Screenshot: {result.screenshot_path}</p>
                              )}
                            </div>
                          </div>
                          <Badge variant={result.success ? "default" : "destructive"}>
                            {result.success ? "PASSED" : "FAILED"}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )
            ))}
          </>
        )}

        {completedExecutions.length === 0 && (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-500">No test results available yet.</p>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle>Browser Testing Agent</CardTitle>
          <CardDescription>
            AI-powered browser testing using natural language scenarios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="upload">Upload</TabsTrigger>
              <TabsTrigger value="preview" disabled={uploadedSuites.length === 0}>
                Preview ({uploadedSuites.length})
              </TabsTrigger>
              <TabsTrigger value="execution" disabled={testExecutions.length === 0}>
                Execution
              </TabsTrigger>
              <TabsTrigger value="results" disabled={testExecutions.filter(e => e.result).length === 0}>
                Results
              </TabsTrigger>
            </TabsList>

            <div className="mt-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <TabsContent value="upload" className="mt-0">
                    {renderUploadTab()}
                  </TabsContent>
                  <TabsContent value="preview" className="mt-0">
                    {renderPreviewTab()}
                  </TabsContent>
                  <TabsContent value="execution" className="mt-0">
                    {renderExecutionTab()}
                  </TabsContent>
                  <TabsContent value="results" className="mt-0">
                    {renderResultsTab()}
                  </TabsContent>
                </motion.div>
              </AnimatePresence>
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

export default BrowserTester