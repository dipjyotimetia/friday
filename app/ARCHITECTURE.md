# FRIDAY Frontend Architecture

## Project Structure Overview

```
/Users/dipjyotimetia/Documents/working/ccviews/friday/app/
├── app/                          # Next.js App Router
│   ├── globals.css              # Global styles with custom CSS
│   ├── layout.tsx               # Root layout component
│   └── page.tsx                 # Home page component
├── components/                   # Organized component structure
│   ├── features/                # Feature-specific components
│   │   ├── api-tester/         # API testing functionality
│   │   │   ├── api-tester.tsx
│   │   │   └── index.ts        # Barrel export
│   │   ├── test-generator/     # Test case generation
│   │   │   ├── test-generator.tsx
│   │   │   └── index.ts
│   │   └── web-crawler/        # Web crawling functionality
│   │       ├── web-crawler.tsx
│   │       └── index.ts
│   ├── shared/                 # Reusable components
│   │   ├── file-uploader.tsx   # File upload component
│   │   ├── output-viewer.tsx   # Output display component
│   │   └── index.ts            # Barrel export
│   ├── ui/                     # shadcn/ui components
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── tabs.tsx
│   └── index.ts                # Main barrel export
├── config/                     # Configuration and constants
│   └── constants.ts            # API endpoints, providers, defaults
├── hooks/                      # Custom React hooks
│   ├── use-api.ts             # API interaction hooks
│   ├── use-file-upload.ts     # File upload logic
│   └── index.ts               # Barrel export
├── lib/                       # Utility functions
│   └── utils.ts               # Common utilities (cn, etc.)
├── services/                  # External service integrations
│   └── api.ts                 # API service layer
├── types/                     # TypeScript definitions
│   └── index.ts              # All type definitions
└── Configuration Files
    ├── .gitignore            # Git ignore patterns
    ├── next.config.mjs       # Next.js configuration
    ├── package.json          # Dependencies and scripts
    ├── postcss.config.mjs    # PostCSS configuration
    ├── tailwind.config.mjs   # Tailwind CSS configuration
    └── tsconfig.json         # TypeScript configuration
```

## Architecture Principles

### 1. Feature-Based Organization

- Components are organized by feature rather than type
- Each feature has its own directory with related components
- Promotes colocation of related functionality

### 2. Separation of Concerns

- **Types**: Centralized TypeScript definitions
- **Hooks**: Custom logic extracted from components
- **Services**: External API interactions
- **Config**: Constants and configuration
- **Components**: Pure UI components

### 3. Barrel Exports

- Each directory has an `index.ts` file for clean imports
- Reduces import complexity and improves maintainability
- Example: `import { TestGenerator, ApiTester } from '@/components'`

### 4. Type Safety

- Comprehensive TypeScript coverage
- Proper interface definitions for all props
- Type-safe API interactions

## Component Architecture

### Feature Components

```typescript
// Located in components/features/{feature-name}/
export function FeatureComponent({
  setOutputText,
  setIsGenerating,
}: BaseComponentProps) {
  const { apiCall, loading } = useCustomHook();

  // Component logic
  return JSX;
}
```

### Shared Components

```typescript
// Located in components/shared/
export function SharedComponent({ ...props }: ComponentProps) {
  // Reusable logic
  return JSX;
}
```

### UI Components

```typescript
// Located in components/ui/
// Based on shadcn/ui patterns with custom styling
export function UIComponent({ className, ...props }: UIProps) {
  return <div className={cn("base-styles", className)} {...props} />
}
```

## Custom Hooks Pattern

### API Hooks

```typescript
// hooks/use-api.ts
export function useFeatureAPI() {
  const [state, setState] = useState<UseApiState>({
    data: null,
    loading: false,
    error: null,
  });

  const performAction = useCallback(async (request) => {
    // API logic with error handling
  }, []);

  return { ...state, performAction };
}
```

### File Upload Hook

```typescript
// hooks/use-file-upload.ts
export function useFileUpload(options) {
  // File upload logic with validation
  return {
    file,
    isDragOver,
    handleFileSelect,
    clearFile,
    // ... other handlers
  };
}
```

## Configuration Management

### Constants

```typescript
// config/constants.ts
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8080',
  TIMEOUT: 10000,
  // ...
} as const;

export const AI_PROVIDERS: ProviderOption[] = [
  { value: 'openai', label: 'OpenAI' },
  // ...
] as const;
```

### Environment-Specific Config

- Development: `http://localhost:8080`
- Production: Environment variables
- Cross-origin support for team development

## Service Layer

### API Service

```typescript
// services/api.ts
export const apiService = {
  async generateTests(data: GenerateRequest) {
    const response = await axiosWithRetry(API_ENDPOINTS.GENERATE, {
      method: 'POST',
      data,
    });
    return response.data;
  },
  // ... other methods
};
```

### Error Handling

- Centralized error handling in services
- Retry logic with exponential backoff
- Type-safe error responses

## Styling Architecture

### CSS Organization

1. **Global Styles**: `app/globals.css`

   - Tailwind directives
   - Custom CSS variables
   - Global animations
   - Original beautiful styling preserved

2. **Component Styles**:

   - Tailwind classes for layout
   - Custom CSS classes for effects
   - shadcn/ui component overrides

3. **Design System**:
   - Glass morphism effects
   - Gradient backgrounds
   - Consistent color palette
   - Responsive design

## Development Workflow

### Adding New Features

1. Create feature directory in `components/features/`
2. Add types to `types/index.ts`
3. Create custom hook if needed in `hooks/`
4. Add constants to `config/constants.ts`
5. Export through barrel files

### Import Patterns

```typescript
// Preferred imports
import { TestGenerator, ApiTester } from '@/components';
import { useTestGenerator } from '@/hooks';
import { API_PROVIDERS } from '@/config/constants';
import type { BaseComponentProps } from '@/types';
```

## Benefits of This Structure

1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new features
3. **Reusability**: Shared components and hooks
4. **Type Safety**: Comprehensive TypeScript coverage
5. **Performance**: Tree-shaking friendly exports
6. **Developer Experience**: Clean imports and organization

## Migration Benefits

- **From Vite to Next.js**: Better performance, SEO, and deployment
- **Feature Organization**: Better code organization and maintenance
- **Type Safety**: Reduced runtime errors
- **Hook Extraction**: Reusable business logic
- **Configuration Management**: Centralized constants and config
- **Better Imports**: Barrel exports reduce import complexity
