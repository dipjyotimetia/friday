# FRIDAY Test Agent - Next.js Frontend

A stunning, modern React frontend built with Next.js 15, featuring AI-powered testing capabilities with a beautiful glassmorphism design.

## ✨ Features Completed

✅ **Next.js 15 Migration**: Fully migrated from Vite to Next.js with App Router  
✅ **Beautiful UI**: Glass morphism effects, gradient backgrounds, floating animations  
✅ **Original Styling Preserved**: All custom CSS classes and effects maintained  
✅ **Cross-Origin Support**: Configured for network access (192.168.1.40:3000)  
✅ **Component Library**: Modern shadcn/ui components with Radix UI primitives  
✅ **Responsive Design**: Mobile-first approach with adaptive layouts  
✅ **Performance Optimized**: Static generation and code splitting enabled  

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
npm install

# Start development server (localhost:3000 or 192.168.1.40:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Docker Development
```bash
# Build and run with Docker Compose
npm run docker:dev

# Or build Docker image manually
npm run docker:build
npm run docker:run

# View logs
npm run docker:logs

# Stop containers
npm run docker:stop
```

## 🎯 Migration Highlights

- **Preserved Original Design**: All beautiful styling from src/index.css maintained
- **Enhanced Components**: File uploaders, progress indicators, and animations
- **Cross-Origin Ready**: Network access configured for development team
- **Type Safety**: Full TypeScript support with strict mode
- **Modern Patterns**: Client/Server components separation

## 📁 Project Structure (Optimized for Maintainability)

```
app/
├── components/
│   ├── features/           # Feature-specific components
│   │   ├── api-tester/    # API testing functionality
│   │   ├── test-generator/ # Test case generation
│   │   └── web-crawler/   # Web crawling functionality
│   ├── shared/            # Reusable components
│   └── ui/                # shadcn/ui components
├── hooks/                 # Custom React hooks
├── types/                 # TypeScript definitions
├── config/                # Constants and configuration
├── services/              # API service layer
└── lib/                   # Utility functions
```

## 🔧 Architecture Benefits

- **Feature-Based Organization**: Components grouped by functionality
- **Type Safety**: Comprehensive TypeScript coverage
- **Custom Hooks**: Reusable business logic extraction
- **Barrel Exports**: Clean import statements
- **Configuration Management**: Centralized constants
- **Error Handling**: Robust API error management
- **Docker Ready**: Multi-stage builds with health monitoring
- **Production Optimized**: Standalone output for containers

## 🎨 UI Components

The app features three main sections:

### 1. Test Generator
- Generate comprehensive test cases from Jira tickets, GitHub issues, or Confluence pages
- Modern form design with validation and loading states
- Supports multiple data sources simultaneously

### 2. Web Crawler
- Crawl websites and extract content for AI analysis
- Configurable crawling options (max pages, domain restrictions)
- Real-time progress feedback with beautiful animations

### 3. API Tester
- Test APIs using OpenAPI/Swagger specifications
- Drag-and-drop file upload with visual feedback
- Support for multiple AI providers (OpenAI, Gemini, Ollama, Mistral)

## 🛠 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Radix UI primitives
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Type Safety**: TypeScript with strict mode

## 🎯 Design Principles

- **Glass Morphism**: Semi-transparent cards with backdrop blur
- **Gradient Accents**: Beautiful color transitions for visual appeal
- **Micro-interactions**: Hover effects and smooth transitions
- **Dark Theme**: Professional dark color scheme
- **Accessibility**: ARIA-compliant components with keyboard navigation

## 📱 Responsive Design

The interface adapts seamlessly across:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🔧 Development

The codebase follows modern React patterns:
- Server and Client Components separation
- Custom hooks for state management
- TypeScript for type safety
- ESLint and Prettier for code quality

## 🌟 New UI Features

- **Animated Loading States**: Pulse effects and spinner animations
- **File Upload**: Drag-and-drop with visual feedback
- **Progress Indicators**: Real-time operation status
- **Floating Elements**: Subtle animations for engaging UX
- **Copy/Download**: Easy output management with one-click actions