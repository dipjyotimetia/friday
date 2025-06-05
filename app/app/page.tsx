'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TestGenerator } from '@/components/test-generator'
import { WebCrawler } from '@/components/web-crawler'
import { ApiTester } from '@/components/api-tester'
import { OutputViewer } from '@/components/output-viewer'
import { Bot, Globe, TestTube, Zap } from 'lucide-react'

export default function HomePage() {
  const [outputText, setOutputText] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-4"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="p-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
            >
              <Bot className="h-8 w-8 text-white" />
            </motion.div>
            <h1 className="text-5xl md:text-7xl font-bold gradient-text animate-float">
              FRIDAY
            </h1>
            <Badge variant="secondary" className="text-sm">
              AI Agent
            </Badge>
          </div>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Your AI-powered testing companion for generating test cases, crawling websites, and testing APIs with intelligent automation.
          </p>
        </motion.div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Tabs defaultValue="generator" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="generator" className="flex items-center gap-2">
                <TestTube className="h-4 w-4" />
                Test Generator
              </TabsTrigger>
              <TabsTrigger value="crawler" className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Web Crawler
              </TabsTrigger>
              <TabsTrigger value="api" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                API Tester
              </TabsTrigger>
            </TabsList>

            <TabsContent value="generator" className="space-y-6">
              <TestGenerator 
                setOutputText={setOutputText}
                setIsGenerating={setIsGenerating}
                isGenerating={isGenerating}
              />
            </TabsContent>

            <TabsContent value="crawler" className="space-y-6">
              <WebCrawler 
                setOutputText={setOutputText}
                setIsGenerating={setIsGenerating}
              />
            </TabsContent>

            <TabsContent value="api" className="space-y-6">
              <ApiTester 
                setOutputText={setOutputText}
                setIsGenerating={setIsGenerating}
              />
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Output Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <OutputViewer outputText={outputText} isGenerating={isGenerating} />
        </motion.div>
      </div>
    </div>
  )
}