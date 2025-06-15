# Friday Web Application Guide

## Overview

The Friday Web Application is a modern Next.js-based frontend that provides a visual interface for all Friday testing features. It offers an intuitive way to manage test scenarios, execute browser tests, generate test cases, and monitor results in real-time.

## Technology Stack

- **Next.js 15.1.6**: App Router with React Server Components
- **React 19.0.0**: Latest React with concurrent features
- **TypeScript 5.8.3**: Full type safety with auto-generated API types
- **Tailwind CSS 4.0.0**: Utility-first CSS with custom design system
- **shadcn/ui + Radix UI**: Accessible component primitives
- **Framer Motion**: Smooth animations and transitions
- **Axios**: HTTP client with interceptors and retry logic
- **WebSocket**: Real-time log streaming with auto-reconnection

## Architecture

### Directory Structure

```
app/
├── app/                          # Next.js App Router
│   ├── api/health/              # API routes
│   ├── globals.css              # Global Tailwind CSS
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Main UI page
├── components/
│   ├── features/                # Feature components
│   │   ├── api-tester/         # API testing functionality
│   │   ├── test-generator/     # Test generation UI
│   │   ├── web-crawler/        # Web crawling interface
│   │   └── browser-tester/     # Browser testing UI
│   ├── shared/                  # Reusable components
│   │   ├── file-uploader.tsx   # File upload handling
│   │   ├── log-viewer.tsx      # Real-time log display
│   │   ├── output-viewer.tsx   # Result output formatting
│   │   ├── result-display.tsx  # Test result presentation
│   │   └── toast-provider.tsx  # Toast notifications
│   └── ui/                      # shadcn/ui components
├── hooks/                       # Custom React hooks
│   ├── use-api.ts              # API communication
│   ├── use-api-error.ts        # Error handling
│   ├── use-file-upload.ts      # File upload logic
│   └── use-websocket.ts        # WebSocket management
├── services/api.ts              # HTTP client with retry logic
├── types/                       # TypeScript definitions
│   ├── api.ts                  # Auto-generated from OpenAPI
│   └── index.ts                # Extended type definitions
├── config/constants.ts          # API endpoints and configuration
└── lib/utils.ts                 # Tailwind utility functions
```

## Quick Start

### Prerequisites

- Node.js 18+ (recommended: 22+)
- npm or yarn package manager
- Friday API server running on port 8080

### Installation and Development

```bash
# Navigate to the app directory
cd app

# Install dependencies
npm install

# Start development server
npm run dev

# The app will be available at http://localhost:3000
```

### Using Friday CLI (Recommended)

```bash
# Start both API and web app
friday webui

# Start only the frontend (API must be running separately)
friday webui --frontend-only

# Open existing web UI
friday open
```

## Features Overview

### 1. Browser Testing Interface

The browser testing interface allows you to:

- **Upload YAML scenarios**: Drag and drop or browse for YAML test files
- **Create scenarios visually**: Use the built-in scenario builder
- **Execute tests**: Run browser automation with real-time progress
- **Monitor results**: View test results with screenshots and detailed logs
- **Download templates**: Get sample YAML files to start testing

#### Key Components:
- **File Uploader**: `components/shared/file-uploader.tsx`
- **Browser Tester**: `components/features/browser-tester/browser-tester.tsx`
- **Log Viewer**: `components/shared/log-viewer.tsx`
- **Result Display**: `components/shared/result-display.tsx`

### 2. Test Generation Interface

Generate test cases from Jira/GitHub issues:

- **Issue Integration**: Connect to Jira or GitHub repositories
- **Context Enhancement**: Add Confluence documentation for richer context
- **Template Selection**: Choose from predefined test case templates
- **Output Management**: Preview and download generated test cases

#### Key Components:
- **Test Generator**: `components/features/test-generator/test-generator.tsx`
- **Output Viewer**: `components/shared/output-viewer.tsx`

### 3. Web Crawling Interface

Crawl websites to build context databases:

- **URL Input**: Specify starting URLs and crawling parameters
- **Provider Selection**: Choose embedding providers (OpenAI, Gemini, etc.)
- **Progress Monitoring**: Real-time crawling progress and statistics
- **Database Management**: View and manage ChromaDB collections

#### Key Components:
- **Web Crawler**: `components/features/web-crawler/web-crawler.tsx`

### 4. API Testing Interface

Test REST APIs using OpenAPI specifications:

- **Spec Upload**: Upload OpenAPI/Swagger specification files
- **Endpoint Testing**: Automated testing of API endpoints
- **Report Generation**: Detailed test reports with response validation
- **Real-time Execution**: Live progress monitoring

#### Key Components:
- **API Tester**: `components/features/api-tester/api-tester.tsx`

## Component Documentation

### Core Hooks

#### useApi Hook

Manages API communication with error handling and loading states.

```typescript
import { useApi } from '@/hooks/use-api';

const MyComponent = () => {
  const { data, loading, error, execute } = useApi();
  
  const handleSubmit = async (formData) => {
    await execute('/api/v1/generate', 'POST', formData);
  };
  
  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
};
```

#### useWebSocket Hook

Manages WebSocket connections for real-time logging.

```typescript
import { useWebSocket } from '@/hooks/use-websocket';

const LogViewer = () => {
  const { messages, isConnected, error } = useWebSocket('/api/v1/ws/logs');
  
  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      {messages.map((msg, idx) => (
        <div key={idx}>{msg.message}</div>
      ))}
    </div>
  );
};
```

#### useFileUpload Hook

Handles file upload operations with progress tracking.

```typescript
import { useFileUpload } from '@/hooks/use-file-upload';

const FileUploader = () => {
  const { upload, progress, uploading } = useFileUpload();
  
  const handleUpload = async (file: File) => {
    const result = await upload('/api/v1/browser-test/yaml/upload', file);
    console.log('Upload result:', result);
  };
  
  return (
    <div>
      <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
      {uploading && <div>Progress: {progress}%</div>}
    </div>
  );
};
```

### Shared Components

#### File Uploader Component

A drag-and-drop file uploader with validation and progress tracking.

```typescript
import { FileUploader } from '@/components/shared/file-uploader';

<FileUploader
  accept=".yaml,.yml"
  onUpload={(file) => handleFileUpload(file)}
  maxSize={5 * 1024 * 1024} // 5MB
  multiple={false}
/>
```

**Props**:
- `accept`: File types to accept
- `onUpload`: Callback when file is uploaded
- `maxSize`: Maximum file size in bytes
- `multiple`: Allow multiple file selection

#### Log Viewer Component

Real-time log display with filtering and search capabilities.

```typescript
import { LogViewer } from '@/components/shared/log-viewer';

<LogViewer
  endpoint="/api/v1/ws/logs"
  maxMessages={1000}
  showTimestamps={true}
  allowClear={true}
/>
```

**Props**:
- `endpoint`: WebSocket endpoint for logs
- `maxMessages`: Maximum number of messages to display
- `showTimestamps`: Show message timestamps
- `allowClear`: Allow clearing log history

#### Result Display Component

Formatted display of test results with expandable sections.

```typescript
import { ResultDisplay } from '@/components/shared/result-display';

<ResultDisplay
  results={testResults}
  showScreenshots={true}
  allowDownload={true}
  format="json" // or "markdown"
/>
```

**Props**:
- `results`: Test result data
- `showScreenshots`: Display screenshot thumbnails
- `allowDownload`: Enable result download
- `format`: Display format (json/markdown)

## Real-time Features

### WebSocket Integration

The web app maintains a persistent WebSocket connection to the API server for real-time updates:

```typescript
// WebSocket connection configuration
const WS_ENDPOINTS = {
  logs: '/api/v1/ws/logs',
  progress: '/api/v1/ws/progress',
  status: '/api/v1/ws/status'
};

// Auto-reconnection logic
const reconnectOptions = {
  maxAttempts: 5,
  delay: 1000,
  backoff: 1.5
};
```

### Live Log Streaming

Real-time log streaming provides instant feedback during:
- Browser test execution
- Test case generation
- Web crawling operations
- API testing

### Progress Monitoring

Live progress updates for long-running operations:
- File upload progress
- Test execution status
- Crawling progress
- Generation steps

## Styling and Theming

### Tailwind CSS Configuration

The app uses Tailwind CSS 4.0 with custom configuration:

```javascript
// tailwind.config.mjs
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        // Custom color palette
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      }
    }
  }
};
```

### Design System

The app follows a consistent design system:

- **Colors**: Semantic color tokens for consistent theming
- **Typography**: Consistent font sizing and line heights
- **Spacing**: Standardized spacing scale
- **Components**: Reusable UI components with variants
- **Animations**: Smooth transitions and micro-interactions

### Dark Mode Support

The app includes built-in dark mode support:

```typescript
// Theme switching
import { useTheme } from 'next-themes';

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle theme
    </button>
  );
};
```

## API Integration

### Type-Safe API Client

The app uses auto-generated TypeScript types from the OpenAPI specification:

```typescript
// Auto-generated types
import type { 
  GenerateRequest, 
  GenerateResponse,
  BrowserTestResult 
} from '@/types/api';

// Type-safe API calls
const generateTests = async (request: GenerateRequest): Promise<GenerateResponse> => {
  return apiClient.post('/api/v1/generate', request);
};
```

### Error Handling

Comprehensive error handling with user-friendly messages:

```typescript
import { useApiError } from '@/hooks/use-api-error';

const MyComponent = () => {
  const { handleError, clearError, error } = useApiError();
  
  const handleSubmit = async () => {
    try {
      await apiCall();
    } catch (err) {
      handleError(err, 'Failed to submit form');
    }
  };
  
  return (
    <div>
      {error && <ErrorBanner error={error} onDismiss={clearError} />}
      {/* Component content */}
    </div>
  );
};
```

### Retry Logic

Automatic retry for failed requests with exponential backoff:

```typescript
// API service configuration
const apiConfig = {
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error) => error.code !== 'ABORT_ERR'
};
```

## State Management

### React State Patterns

The app uses modern React patterns for state management:

```typescript
// Context for global state
const AppContext = createContext();

// Custom hooks for feature state
const useBrowserTesting = () => {
  const [tests, setTests] = useState([]);
  const [executing, setExecuting] = useState(false);
  
  const executeTests = useCallback(async (scenarios) => {
    setExecuting(true);
    try {
      const results = await api.executeTests(scenarios);
      setTests(prev => [...prev, results]);
    } finally {
      setExecuting(false);
    }
  }, []);
  
  return { tests, executing, executeTests };
};
```

### Form State Management

Robust form handling with validation:

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const formSchema = z.object({
  jiraKey: z.string().min(1, 'Jira key is required'),
  output: z.string().min(1, 'Output path is required')
});

const TestGenerationForm = () => {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      jiraKey: '',
      output: 'test_cases.md'
    }
  });
  
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
};
```

## Performance Optimization

### Code Splitting

The app uses dynamic imports for feature components:

```typescript
// Lazy loading feature components
const BrowserTester = dynamic(() => import('@/components/features/browser-tester'), {
  loading: () => <Skeleton />,
  ssr: false
});

const TestGenerator = dynamic(() => import('@/components/features/test-generator'), {
  loading: () => <Skeleton />
});
```

### Memoization

Strategic use of React.memo and useMemo for performance:

```typescript
// Memoized components
const MemoizedResultList = memo(({ results }) => (
  <div>
    {results.map(result => <ResultItem key={result.id} result={result} />)}
  </div>
));

// Memoized values
const processedData = useMemo(() => {
  return expensiveDataProcessing(rawData);
}, [rawData]);
```

### Virtual Scrolling

For large datasets like log messages:

```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualLogList = ({ logs }) => (
  <List
    height={400}
    itemCount={logs.length}
    itemSize={25}
    itemData={logs}
  >
    {({ index, style, data }) => (
      <div style={style}>
        {data[index].message}
      </div>
    )}
  </List>
);
```

## Testing

### Unit Testing

```bash
# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Integration Testing

```typescript
// Example test for browser testing component
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserTester } from '@/components/features/browser-tester';

describe('BrowserTester', () => {
  it('should upload and execute YAML scenarios', async () => {
    render(<BrowserTester />);
    
    const fileInput = screen.getByLabelText(/upload yaml/i);
    const file = new File(['test content'], 'test.yaml', { type: 'text/yaml' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    const executeButton = screen.getByRole('button', { name: /execute/i });
    fireEvent.click(executeButton);
    
    expect(screen.getByText(/executing tests/i)).toBeInTheDocument();
  });
});
```

### E2E Testing

```typescript
// Playwright E2E tests
import { test, expect } from '@playwright/test';

test('browser testing workflow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Navigate to browser testing tab
  await page.click('[data-testid="browser-tab"]');
  
  // Upload YAML file
  await page.setInputFiles('[data-testid="file-upload"]', 'test-scenarios.yaml');
  
  // Execute tests
  await page.click('[data-testid="execute-button"]');
  
  // Wait for results
  await expect(page.locator('[data-testid="test-results"]')).toBeVisible();
});
```

## Deployment

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start

# Static export (if needed)
npm run export
```

### Docker Deployment

```dockerfile
# Dockerfile for web app
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

### Environment Configuration

```bash
# Production environment variables
NEXT_PUBLIC_API_URL=https://api.friday.example.com
NEXT_PUBLIC_WS_URL=wss://api.friday.example.com
NEXT_PUBLIC_ENVIRONMENT=production
```

## Accessibility

### WCAG Compliance

The app follows WCAG 2.1 AA guidelines:

- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and roles
- **Color Contrast**: Meets AA contrast requirements
- **Focus Management**: Clear focus indicators

### Accessibility Features

```typescript
// Example accessible component
const AccessibleButton = ({ children, ...props }) => (
  <button
    {...props}
    aria-label={props['aria-label'] || children}
    role="button"
    tabIndex={0}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        props.onClick?.(e);
      }
    }}
  >
    {children}
  </button>
);
```

## Security

### Content Security Policy

```javascript
// next.config.mjs
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
  }
];

export default {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### Input Validation

All user inputs are validated both client-side and server-side:

```typescript
// Example validation schema
const uploadSchema = z.object({
  file: z.instanceof(File)
    .refine(file => file.size <= 5 * 1024 * 1024, 'File too large')
    .refine(file => file.name.endsWith('.yaml') || file.name.endsWith('.yml'), 'Invalid file type'),
  provider: z.enum(['openai', 'gemini', 'ollama', 'mistral'])
});
```

## Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failures

**Problem**: Real-time logs not working

**Solution**:
```bash
# Check API server is running
curl http://localhost:8080/health

# Verify WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:8080/api/v1/ws/logs
```

#### 2. API Connection Errors

**Problem**: Frontend can't connect to API

**Solution**:
```bash
# Check CORS configuration
echo $ALLOWED_ORIGINS

# Verify API is accessible
curl http://localhost:8080/health

# Check frontend environment
echo $NEXT_PUBLIC_API_URL
```

#### 3. File Upload Issues

**Problem**: YAML file uploads failing

**Solution**:
- Check file size (max 5MB)
- Verify file extension (.yaml or .yml)
- Validate YAML syntax
- Check API server logs

#### 4. Build Errors

**Problem**: Production build failing

**Solution**:
```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install

# Check TypeScript errors
npx tsc --noEmit

# Verify all dependencies
npm audit
```

### Debug Mode

Enable debug logging in development:

```javascript
// next.config.mjs
export default {
  env: {
    DEBUG: process.env.NODE_ENV === 'development' ? 'true' : 'false'
  }
};
```

## Development Guidelines

### Code Style

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

### Component Development

1. **Component Structure**:
   ```typescript
   // MyComponent.tsx
   interface Props {
     // Define props
   }
   
   export const MyComponent: FC<Props> = ({ ...props }) => {
     // Component logic
     return (
       <div>
         {/* JSX */}
       </div>
     );
   };
   ```

2. **Hook Development**:
   ```typescript
   // useMyHook.ts
   export const useMyHook = () => {
     // Hook logic
     return {
       // Return values
     };
   };
   ```

3. **Type Definitions**:
   ```typescript
   // types/index.ts
   export interface MyInterface {
     // Interface definition
   }
   ```

### Performance Best Practices

1. **Use React.memo for expensive components**
2. **Implement proper key props for lists**
3. **Debounce user inputs**
4. **Lazy load heavy components**
5. **Optimize bundle size with tree shaking**

---

**Last Updated**: December 2024  
**Version**: 0.1.47

For the latest updates and documentation, visit the [GitHub repository](https://github.com/dipjyotimetia/friday).