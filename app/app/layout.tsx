import type { Metadata } from 'next'
import './globals.css'
import { ToastProvider } from '@/components/shared/toast-provider'

export const metadata: Metadata = {
  title: 'FRIDAY Test Agent',
  description: 'AI-powered testing agent for test generation, web crawling, and API testing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 antialiased">
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  )
}