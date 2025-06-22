'use client'

import React, { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiService } from '@/services/api'
import { 
  Globe, 
  RefreshCw, 
  Activity,
  Clock,
  BarChart3,
  Monitor,
  HardDrive,
  Users
} from 'lucide-react'
import { motion } from 'framer-motion'
import type { BrowserSessionStats, StorageStats, TestMetrics } from '@/types'

interface SessionManagementProps {
  refreshInterval?: number
  showStorageStats?: boolean
  className?: string
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

export function SessionManagement({ 
  refreshInterval = 10000, 
  showStorageStats = true,
  className = ''
}: SessionManagementProps) {
  const [metrics, setMetrics] = useState<TestMetrics | null>(null)
  const [sessionData, setSessionData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const loadMetrics = async () => {
    setLoading(true)
    setError(null)

    try {
      const [metricsResponse, sessionsResponse] = await Promise.all([
        apiService.getBrowserTestMetrics(),
        apiService.getBrowserSessions()
      ])
      
      setMetrics(metricsResponse)
      setSessionData(sessionsResponse)
      setLastRefresh(new Date())
    } catch (err: any) {
      setError(err.message || 'Failed to load session metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMetrics()
    
    const interval = setInterval(loadMetrics, refreshInterval)
    return () => clearInterval(interval)
  }, [refreshInterval])

  const sessionStats = metrics?.session_stats
  const storageStats = metrics?.storage_stats

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-medium">Browser Session Management</h3>
        </div>
        
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-sm text-gray-500">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={loadMetrics}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-700">
            <Activity className="h-5 w-5" />
            <span className="font-medium">Error loading session data</span>
          </div>
          <p className="text-red-600 mt-2">{error}</p>
        </Card>
      )}

      {/* Session Statistics */}
      {sessionStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Active Sessions</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {sessionStats.active_sessions}
                  </p>
                  <p className="text-xs text-gray-500">
                    of {sessionStats.max_sessions} max
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Globe className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Sessions</p>
                  <p className="text-2xl font-bold text-green-600">
                    {sessionStats.total_sessions}
                  </p>
                  <p className="text-xs text-gray-500">
                    {sessionStats.total_tests_executed} tests run
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Clock className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Session Timeout</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {formatDuration(sessionStats.session_timeout)}
                  </p>
                  <p className="text-xs text-gray-500">idle timeout</p>
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tests Executed</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {sessionStats.total_tests_executed}
                  </p>
                  <p className="text-xs text-gray-500">total completed</p>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      )}

      {/* Browser Types */}
      {sessionStats?.browser_types && Object.keys(sessionStats.browser_types).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Monitor className="h-5 w-5" />
              <h4 className="font-medium">Browser Distribution</h4>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {Object.entries(sessionStats.browser_types).map(([browser, count]) => (
                <Badge key={browser} variant="outline" className="flex items-center gap-2">
                  <span className="capitalize">{browser}</span>
                  <span className="font-bold">{count}</span>
                </Badge>
              ))}
            </div>
          </Card>
        </motion.div>
      )}

      {/* Storage Statistics */}
      {showStorageStats && storageStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <HardDrive className="h-5 w-5" />
              <h4 className="font-medium">Storage Statistics</h4>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {formatBytes(storageStats.total_size_bytes)}
                </p>
                <p className="text-sm text-gray-600">Total Storage</p>
              </div>
              
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {storageStats.total_files}
                </p>
                <p className="text-sm text-gray-600">Total Files</p>
              </div>
              
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  {storageStats.test_count}
                </p>
                <p className="text-sm text-gray-600">Test Directories</p>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Storage Path:</span> {storageStats.base_path}
              </p>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Session Details */}
      {sessionData?.stats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-5 w-5" />
              <h4 className="font-medium">Session Details</h4>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Current Load:</span>
                <span className="font-medium">
                  {sessionStats?.active_sessions || 0} / {sessionStats?.max_sessions || 0} sessions
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Capacity Usage:</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${Math.min(100, ((sessionStats?.active_sessions || 0) / (sessionStats?.max_sessions || 1)) * 100)}%` 
                      }}
                    />
                  </div>
                  <span className="font-medium">
                    {Math.round(((sessionStats?.active_sessions || 0) / (sessionStats?.max_sessions || 1)) * 100)}%
                  </span>
                </div>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Average Tests per Session:</span>
                <span className="font-medium">
                  {(sessionStats?.total_sessions || 0) > 0 
                    ? Math.round((sessionStats?.total_tests_executed || 0) / (sessionStats?.total_sessions || 1))
                    : 0
                  }
                </span>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  )
}