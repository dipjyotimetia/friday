'use client'

import React, { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  Bug,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Copy,
  ExternalLink,
  Lightbulb
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { DetailedError } from '@/types'

interface EnhancedErrorDisplayProps {
  errors: (string | DetailedError)[]
  onRetry?: () => void
  retryDisabled?: boolean
  className?: string
}

function getSeverityIcon(severity?: string) {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return <AlertCircle className="h-4 w-4 text-red-500" />
    case 'high':
      return <AlertTriangle className="h-4 w-4 text-orange-500" />
    case 'medium':
      return <Info className="h-4 w-4 text-yellow-500" />
    case 'low':
      return <Info className="h-4 w-4 text-blue-500" />
    default:
      return <Bug className="h-4 w-4 text-gray-500" />
  }
}

function getSeverityColor(severity?: string) {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return 'border-red-200 bg-red-50'
    case 'high':
      return 'border-orange-200 bg-orange-50'
    case 'medium':
      return 'border-yellow-200 bg-yellow-50'
    case 'low':
      return 'border-blue-200 bg-blue-50'
    default:
      return 'border-gray-200 bg-gray-50'
  }
}

function getCategoryIcon(category?: string) {
  switch (category?.toLowerCase()) {
    case 'network_error':
      return '🌐'
    case 'timeout_error':
      return '⏱️'
    case 'element_not_found':
      return '🔍'
    case 'navigation_error':
      return '🧭'
    case 'javascript_error':
      return '⚡'
    case 'browser_error':
      return '🌍'
    case 'authentication_error':
      return '🔐'
    case 'permission_error':
      return '🚫'
    case 'validation_error':
      return '✅'
    case 'resource_error':
      return '📦'
    default:
      return '❓'
  }
}

function formatCategory(category?: string) {
  if (!category) return 'Unknown Error'
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function ErrorItem({ error, index }: { error: string | DetailedError; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)
  
  const isDetailedError = typeof error === 'object'
  const detailedError = isDetailedError ? error as DetailedError : null
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className={`p-4 ${detailedError ? getSeverityColor(detailedError.severity) : 'border-red-200 bg-red-50'}`}>
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            {detailedError ? getSeverityIcon(detailedError.severity) : <AlertCircle className="h-4 w-4 text-red-500" />}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              {detailedError && (
                <>
                  <span className="text-lg">{getCategoryIcon(detailedError.category)}</span>
                  <Badge variant="outline" className="text-xs">
                    {formatCategory(detailedError.category)}
                  </Badge>
                  {detailedError.severity && (
                    <Badge 
                      variant={detailedError.severity === 'critical' ? 'destructive' : 'secondary'}
                      className="text-xs"
                    >
                      {detailedError.severity.toUpperCase()}
                    </Badge>
                  )}
                  {detailedError.error_code && (
                    <Badge variant="outline" className="text-xs font-mono">
                      {detailedError.error_code}
                    </Badge>
                  )}
                </>
              )}
            </div>
            
            <p className="text-sm font-medium text-gray-900 mb-2">
              {detailedError ? detailedError.message : error as string}
            </p>
            
            {detailedError?.suggested_fix && (
              <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg mb-3">
                <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Suggested Fix:</p>
                  <p className="text-sm text-blue-800">{detailedError.suggested_fix}</p>
                </div>
              </div>
            )}
            
            <div className="flex items-center gap-2 mb-2">
              {detailedError?.retry_recommended && (
                <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                  ✓ Retry Recommended
                </Badge>
              )}
              
              {detailedError && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="h-6 px-2 text-xs"
                >
                  {isExpanded ? (
                    <>
                      <ChevronDown className="h-3 w-3 mr-1" />
                      Less Details
                    </>
                  ) : (
                    <>
                      <ChevronRight className="h-3 w-3 mr-1" />
                      More Details
                    </>
                  )}
                </Button>
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(detailedError ? detailedError.message : error as string)}
                className="h-6 px-2 text-xs"
              >
                {copied ? (
                  <>✓ Copied</>
                ) : (
                  <>
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </>
                )}
              </Button>
            </div>
            
            <AnimatePresence>
              {isExpanded && detailedError && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-3 space-y-3"
                >
                  {detailedError.context && Object.keys(detailedError.context).length > 0 && (
                    <div className="p-3 bg-white border rounded-lg">
                      <p className="text-sm font-medium mb-2">Context:</p>
                      <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(detailedError.context, null, 2)}
                      </pre>
                    </div>
                  )}
                  
                  {detailedError.stack_trace && (
                    <div className="p-3 bg-white border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium">Stack Trace:</p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(detailedError.stack_trace || '')}
                          className="h-6 px-2 text-xs"
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copy Stack
                        </Button>
                      </div>
                      <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto max-h-32 overflow-y-auto">
                        {detailedError.stack_trace}
                      </pre>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

export function EnhancedErrorDisplay({ 
  errors, 
  onRetry, 
  retryDisabled = false, 
  className = '' 
}: EnhancedErrorDisplayProps) {
  if (errors.length === 0) {
    return null
  }

  const hasRetryRecommendations = errors.some(error => 
    typeof error === 'object' && error.retry_recommended
  )

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-red-500" />
          <h3 className="text-lg font-medium text-red-700">
            {errors.length === 1 ? 'Error Detected' : `${errors.length} Errors Detected`}
          </h3>
        </div>
        
        {onRetry && hasRetryRecommendations && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            disabled={retryDisabled}
            className="border-green-200 text-green-700 hover:bg-green-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Tests
          </Button>
        )}
      </div>
      
      <div className="space-y-3">
        {errors.map((error, index) => (
          <ErrorItem key={index} error={error} index={index} />
        ))}
      </div>
      
      {hasRetryRecommendations && (
        <Card className="p-4 border-green-200 bg-green-50">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-green-900 mb-1">
                Some errors can be automatically resolved
              </p>
              <p className="text-sm text-green-800">
                The system has identified {errors.filter(e => typeof e === 'object' && e.retry_recommended).length} error(s) 
                that may be resolved by retrying the test. Consider using the retry button above.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}