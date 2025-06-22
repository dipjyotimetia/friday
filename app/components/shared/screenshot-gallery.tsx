'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiService } from '@/services/api'
import { 
  Image as ImageIcon, 
  Download, 
  Trash2, 
  ZoomIn, 
  Clock,
  FileText,
  X,
  ChevronLeft,
  ChevronRight,
  Maximize2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ScreenshotInfo, TestScreenshotsResponse } from '@/types'

interface ScreenshotGalleryProps {
  testId?: string
  screenshots?: string[]
  onScreenshotClick?: (screenshot: string) => void
}

interface LightboxProps {
  screenshots: ScreenshotInfo[]
  currentIndex: number
  onClose: () => void
  onPrevious: () => void
  onNext: () => void
}

function Lightbox({ screenshots, currentIndex, onClose, onPrevious, onNext }: LightboxProps) {
  const currentScreenshot = screenshots[currentIndex]
  
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft') onPrevious()
      if (e.key === 'ArrowRight') onNext()
    }
    
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [onClose, onPrevious, onNext])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="relative max-w-7xl max-h-full w-full h-full flex items-center justify-center">
        {/* Close Button */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-4 right-4 z-10 text-white hover:bg-white/20"
          onClick={onClose}
        >
          <X className="h-6 w-6" />
        </Button>

        {/* Navigation */}
        {screenshots.length > 1 && (
          <>
            <Button
              variant="ghost"
              size="sm"
              className="absolute left-4 z-10 text-white hover:bg-white/20"
              onClick={onPrevious}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="h-8 w-8" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-4 z-10 text-white hover:bg-white/20"
              onClick={onNext}
              disabled={currentIndex === screenshots.length - 1}
            >
              <ChevronRight className="h-8 w-8" />
            </Button>
          </>
        )}

        {/* Image */}
        <div className="flex flex-col items-center max-h-full" onClick={(e) => e.stopPropagation()}>
          <img
            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}${currentScreenshot.url}`}
            alt={currentScreenshot.filename}
            className="max-w-full max-h-[80vh] object-contain"
          />
          
          {/* Image Info */}
          <div className="mt-4 text-white text-center">
            <p className="text-lg font-medium">{currentScreenshot.filename}</p>
            <p className="text-sm opacity-75">
              {(currentScreenshot.size / 1024).toFixed(1)} KB • {new Date(currentScreenshot.created_at).toLocaleString()}
            </p>
            {screenshots.length > 1 && (
              <p className="text-sm opacity-75 mt-2">
                {currentIndex + 1} of {screenshots.length}
              </p>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export function ScreenshotGallery({ testId, screenshots = [], onScreenshotClick }: ScreenshotGalleryProps) {
  const [screenshotData, setScreenshotData] = useState<ScreenshotInfo[]>([])
  const [metadata, setMetadata] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null)

  useEffect(() => {
    if (testId) {
      loadTestScreenshots()
    } else if (screenshots.length > 0) {
      // Convert simple screenshot paths to ScreenshotInfo format
      const convertedScreenshots: ScreenshotInfo[] = screenshots.map((path, index) => ({
        filename: path.split('/').pop() || `screenshot_${index + 1}`,
        path: path,
        size: 0,
        created_at: new Date().toISOString(),
        url: `/api/v1/browser-test/screenshots/${path}`
      }))
      setScreenshotData(convertedScreenshots)
    }
  }, [testId, screenshots])

  const loadTestScreenshots = async () => {
    if (!testId) return

    setLoading(true)
    setError(null)

    try {
      const response = await apiService.getTestScreenshots(testId)
      setScreenshotData(response.screenshots)
      setMetadata(response.metadata)
    } catch (err: any) {
      setError(err.message || 'Failed to load screenshots')
    } finally {
      setLoading(false)
    }
  }

  const downloadScreenshot = async (screenshot: ScreenshotInfo) => {
    if (!testId) return

    try {
      const blob = await apiService.getScreenshotFile(testId, screenshot.filename)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = screenshot.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      console.error('Failed to download screenshot:', err)
    }
  }

  const cleanupScreenshots = async () => {
    if (!testId) return

    try {
      await apiService.cleanupTestScreenshots(testId)
      setScreenshotData([])
      setMetadata(null)
    } catch (err: any) {
      setError(err.message || 'Failed to cleanup screenshots')
    }
  }

  const openLightbox = (index: number) => {
    setLightboxIndex(index)
    if (onScreenshotClick && screenshotData[index]) {
      onScreenshotClick(screenshotData[index].path)
    }
  }

  const closeLightbox = () => {
    setLightboxIndex(null)
  }

  const previousImage = () => {
    if (lightboxIndex !== null && lightboxIndex > 0) {
      setLightboxIndex(lightboxIndex - 1)
    }
  }

  const nextImage = () => {
    if (lightboxIndex !== null && lightboxIndex < screenshotData.length - 1) {
      setLightboxIndex(lightboxIndex + 1)
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3">Loading screenshots...</span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex items-center gap-2 text-red-700">
          <ImageIcon className="h-5 w-5" />
          <span className="font-medium">Error loading screenshots</span>
        </div>
        <p className="text-red-600 mt-2">{error}</p>
        {testId && (
          <Button
            variant="outline"
            size="sm"
            className="mt-3"
            onClick={loadTestScreenshots}
          >
            Retry
          </Button>
        )}
      </Card>
    )
  }

  if (screenshotData.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <ImageIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No screenshots available</p>
          <p className="text-sm">Screenshots will appear here after test execution</p>
        </div>
      </Card>
    )
  }

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5" />
            <h3 className="text-lg font-medium">Screenshots</h3>
            <Badge variant="secondary">{screenshotData.length}</Badge>
          </div>
          
          {testId && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loadTestScreenshots}
              >
                Refresh
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={cleanupScreenshots}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Cleanup
              </Button>
            </div>
          )}
        </div>

        {metadata && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-4 w-4" />
              <span className="font-medium">Test Information</span>
            </div>
            <div className="text-sm space-y-1">
              <p><span className="font-medium">Test ID:</span> {metadata.test_id}</p>
              <p><span className="font-medium">URL:</span> {metadata.url}</p>
              <p><span className="font-medium">Requirement:</span> {metadata.requirement}</p>
              {metadata.started_at && (
                <p><span className="font-medium">Started:</span> {new Date(metadata.started_at * 1000).toLocaleString()}</p>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {screenshotData.map((screenshot, index) => (
            <motion.div
              key={screenshot.filename}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="group relative"
            >
              <Card className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-gray-100 relative">
                  <img
                    src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}${screenshot.url}`}
                    alt={screenshot.filename}
                    className="w-full h-full object-cover"
                    onClick={() => openLightbox(index)}
                  />
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation()
                          openLightbox(index)
                        }}
                      >
                        <ZoomIn className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation()
                          downloadScreenshot(screenshot)
                        }}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                
                <div className="p-3">
                  <p className="text-sm font-medium truncate" title={screenshot.filename}>
                    {screenshot.filename}
                  </p>
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                    <span>{(screenshot.size / 1024).toFixed(1)} KB</span>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(screenshot.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Lightbox */}
      <AnimatePresence>
        {lightboxIndex !== null && (
          <Lightbox
            screenshots={screenshotData}
            currentIndex={lightboxIndex}
            onClose={closeLightbox}
            onPrevious={previousImage}
            onNext={nextImage}
          />
        )}
      </AnimatePresence>
    </>
  )
}