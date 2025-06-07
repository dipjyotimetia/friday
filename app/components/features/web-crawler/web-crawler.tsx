'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiService } from '@/services/api'
import { Globe, Settings, Hash, CheckSquare } from 'lucide-react'

interface WebCrawlerProps {
  setOutputText: (text: string) => void
  setIsGenerating: (isGenerating: boolean) => void
}

export function WebCrawler({ setOutputText, setIsGenerating }: WebCrawlerProps) {
  const [url, setUrl] = useState('')
  const [provider, setProvider] = useState('openai')
  const [maxPages, setMaxPages] = useState(10)
  const [sameDomain, setSameDomain] = useState(true)
  const [isCrawling, setIsCrawling] = useState(false)

  const handleCrawl = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsCrawling(true)
    setIsGenerating(true)
    setOutputText('Starting web crawl...')
    
    try {
      const result = await apiService.crawlWebsite({
        url,
        provider,
        max_pages: Number(maxPages),
        same_domain: sameDomain,
      })
      
      if (result.success) {
        const summary = `Web Crawling Complete!\n\n` +
          `Pages Crawled: ${result.pages_crawled}\n` +
          `Embeddings Created: ${result.embeddings_created || 0}\n\n` +
          `${result.content_summary || 'Crawl completed successfully.'}`;
        setOutputText(summary)
      } else {
        setOutputText(JSON.stringify(result, null, 2))
      }
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`)
    } finally {
      setIsCrawling(false)
      setIsGenerating(false)
    }
  }

  const providers = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'gemini', label: 'Gemini' },
    { value: 'ollama', label: 'Ollama' },
    { value: 'mistral', label: 'Mistral' },
  ]

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-teal-500">
            <Globe className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle>Web Crawler</CardTitle>
            <CardDescription>
              Crawl websites and extract content for AI-powered analysis and indexing
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleCrawl} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Website URL
              </label>
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isCrawling}
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
                  onChange={(e) => setProvider(e.target.value)}
                  disabled={isCrawling}
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 glass-card"
                >
                  {providers.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Hash className="h-4 w-4" />
                  Max Pages
                </label>
                <Input
                  type="number"
                  placeholder="10"
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  disabled={isCrawling}
                  min="1"
                  max="100"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                id="sameDomain"
                type="checkbox"
                checked={sameDomain}
                onChange={(e) => setSameDomain(e.target.checked)}
                disabled={isCrawling}
                className="peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <label
                htmlFor="sameDomain"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2"
              >
                <CheckSquare className="h-4 w-4" />
                Stay on same domain only
              </label>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-blue-50/10 border border-blue-200/20">
            <div className="flex items-start gap-3">
              <div className="p-1 rounded-full bg-blue-500/20">
                <Globe className="h-3 w-3 text-blue-400" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-blue-200">Crawling Options</p>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Content will be indexed using embeddings for semantic search</li>
                  <li>• Same domain restriction helps focus on relevant content</li>
                  <li>• Higher page limits may take longer to process</li>
                </ul>
              </div>
            </div>
          </div>

          <Button 
            type="submit" 
            disabled={isCrawling || !url}
            variant="gradient"
            size="lg"
            className="w-full"
          >
            {isCrawling ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Crawling Website...
              </>
            ) : (
              <>
                <Globe className="h-4 w-4 mr-2" />
                Start Crawling
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}