'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  TestGenerator,
  WebCrawler,
  ApiTester,
  OutputViewer,
  LogViewer,
} from '@/components';
import { Bot, Globe, TestTube, Zap } from 'lucide-react';

export default function HomePage() {
  const [outputText, setOutputText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="text-center space-y-6"
        >
          <div className="flex items-center justify-center gap-4 mb-6">
            <motion.div
              animate={{
                rotate: 360,
                scale: [1, 1.1, 1],
              }}
              transition={{
                rotate: { duration: 20, repeat: Infinity, ease: 'linear' },
                scale: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
              }}
              className="relative p-4 rounded-full bg-gradient-to-r from-blue-500 via-purple-600 to-pink-500 shadow-2xl"
            >
              <Bot className="h-10 w-10 text-white" />
              <motion.div
                className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-purple-600 to-pink-500 opacity-50"
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-6xl md:text-8xl font-bold gradient-text animate-float tracking-tight"
            >
              FRIDAY
            </motion.h1>
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 0.5,
                delay: 0.4,
                type: 'spring',
                stiffness: 200,
              }}
            >
              <Badge
                variant="secondary"
                className="text-sm px-3 py-1 bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30"
              >
                AI Agent
              </Badge>
            </motion.div>
          </div>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-xl text-muted-foreground max-w-4xl mx-auto leading-relaxed"
          >
            Your AI-powered testing companion for generating test cases,
            crawling websites, and testing APIs with intelligent automation.
          </motion.p>

          {/* Animated particles background */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {Array.from({ length: 3 }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full opacity-20"
                animate={{
                  x: [0, 100, 0],
                  y: [0, -100, 0],
                  opacity: [0.2, 0.8, 0.2],
                }}
                transition={{
                  duration: 10 + i * 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: i * 2,
                }}
                style={{
                  left: `${20 + i * 30}%`,
                  top: `${30 + i * 10}%`,
                }}
              />
            ))}
          </div>
        </motion.div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="relative"
        >
          <Tabs defaultValue="generator" className="w-full">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <TabsList className="grid w-full grid-cols-3 mb-8 max-w-2xl mx-auto">
                <TabsTrigger
                  value="generator"
                  className="flex items-center gap-3 relative overflow-hidden"
                >
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    <TestTube className="h-5 w-5" />
                  </motion.div>
                  <span className="font-medium">Test Generator</span>
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 opacity-0"
                    whileHover={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                </TabsTrigger>
                <TabsTrigger
                  value="crawler"
                  className="flex items-center gap-3 relative overflow-hidden"
                >
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Globe className="h-5 w-5" />
                  </motion.div>
                  <span className="font-medium">Web Crawler</span>
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-green-600/20 to-blue-600/20 opacity-0"
                    whileHover={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                </TabsTrigger>
                <TabsTrigger
                  value="api"
                  className="flex items-center gap-3 relative overflow-hidden"
                >
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Zap className="h-5 w-5" />
                  </motion.div>
                  <span className="font-medium">API Tester</span>
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-orange-600/20 to-red-600/20 opacity-0"
                    whileHover={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                </TabsTrigger>
              </TabsList>
            </motion.div>

            <TabsContent value="generator" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <TestGenerator
                  setOutputText={setOutputText}
                  setIsGenerating={setIsGenerating}
                  isGenerating={isGenerating}
                />
              </motion.div>
            </TabsContent>

            <TabsContent value="crawler" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <WebCrawler
                  setOutputText={setOutputText}
                  setIsGenerating={setIsGenerating}
                />
              </motion.div>
            </TabsContent>

            <TabsContent value="api" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <ApiTester
                  setOutputText={setOutputText}
                  setIsGenerating={setIsGenerating}
                />
              </motion.div>
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Output Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="relative"
        >
          <motion.div
            whileHover={{ scale: 1.01 }}
            transition={{ duration: 0.2 }}
          >
            <OutputViewer outputText={outputText} isGenerating={isGenerating} />
          </motion.div>
        </motion.div>

        {/* Real-time Log Viewer */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <LogViewer />
        </motion.div>
      </div>
    </div>
  );
}
