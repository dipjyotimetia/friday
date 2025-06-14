'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Terminal, Copy, Download } from 'lucide-react';
import { motion } from 'framer-motion';

interface OutputViewerProps {
  outputText: string;
  isGenerating?: boolean;
}

export function OutputViewer({
  outputText,
  isGenerating = false,
}: OutputViewerProps) {
  const copyToClipboard = async () => {
    if (outputText) {
      await navigator.clipboard.writeText(outputText);
    }
  };

  const downloadOutput = () => {
    if (outputText) {
      const blob = new Blob([outputText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'friday-output.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Terminal className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle>Output</CardTitle>
              <CardDescription>
                Results and logs from your operations
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isGenerating && (
              <Badge variant="secondary" className="animate-pulse">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current mr-2" />
                Processing...
              </Badge>
            )}
            {outputText && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyToClipboard}
                  className="flex items-center gap-1"
                >
                  <Copy className="h-3 w-3" />
                  Copy
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadOutput}
                  className="flex items-center gap-1"
                >
                  <Download className="h-3 w-3" />
                  Download
                </Button>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative">
          <motion.pre
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`
              bg-slate-900 text-slate-100 p-6 rounded-lg overflow-auto font-mono text-sm leading-relaxed min-h-[200px] max-h-[500px] border
              ${isGenerating ? 'animate-pulse-glow' : ''}
            `}
          >
            {outputText || (
              <span className="text-slate-400 italic">
                {isGenerating
                  ? 'Processing your request...'
                  : 'Output will appear here after running an operation'}
              </span>
            )}
          </motion.pre>

          {isGenerating && (
            <div className="absolute top-4 right-4">
              <div className="flex items-center gap-2 bg-blue-500/20 backdrop-blur-sm rounded-full px-3 py-1 border border-blue-500/30">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-400" />
                <span className="text-xs text-blue-200">Working...</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
