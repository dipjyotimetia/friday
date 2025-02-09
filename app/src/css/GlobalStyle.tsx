import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  :root {
    /* Core colors */
    --bg-primary: #0a0a1f;
    --bg-secondary: rgba(18, 19, 35, 0.98);
    --text-primary: #ffffff;
    --text-secondary: #a8b2d1;
    
    /* Accent colors */
    --accent-primary: #9d5cff;
    --accent-secondary: #ff3d87;
    --accent-hover: #8a42ff;
    
    /* UI Elements */
    --border-color: rgba(255, 255, 255, 0.12);
    --input-bg: rgba(25, 26, 45, 0.98);
    --input-bg-disabled: rgba(20, 21, 35, 0.98);
    --glass-bg: rgba(18, 19, 35, 0.85);
    
    /* Effects */
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    --glow: 0 0 25px rgba(157, 92, 255, 0.35);
    --gradient-primary: linear-gradient(135deg, var(--accent-primary), #6d67ff);
    --gradient-secondary: linear-gradient(135deg, var(--accent-secondary), var(--accent-primary));
    
    /* Common transitions */
    --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Reset */
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    transition: all var(--transition-normal);
  }

  /* Base styles */
  body {
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    background: var(--bg-primary);
    background-image: 
      radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 0% 100%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
    background-attachment: fixed;
    color: var(--text-primary);
    line-height: 1.6;
    padding: clamp(16px, 5vw, 20px);
    -webkit-font-smoothing: antialiased;
  }

  /* Utility classes */
  .glass {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow);
  }

  .loading {
    background: linear-gradient(90deg, 
      var(--bg-secondary) 0%,
      var(--accent-primary) 50%, 
      var(--bg-secondary) 100%
    );
    background-size: 1000px 100%;
    animation: shimmer 2s infinite linear;
  }

  .float {
    animation: float 6s ease-in-out infinite;
  }

  /* Animations */
  @keyframes shimmer {
    from { background-position: -1000px 0; }
    to { background-position: 1000px 0; }
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  /* Interactive elements */
  a {
    color: var(--accent-primary);
    text-decoration: none;
    background: linear-gradient(to right, var(--accent-secondary), var(--accent-primary));
    background-size: 0% 2px;
    background-repeat: no-repeat;
    background-position: left bottom;
    transition: background-size var(--transition-normal);
    
    &:hover {
      background-size: 100% 2px;
    }
  }

  /* Mobile optimizations */
  @media (max-width: 768px) {
    * { touch-action: manipulation; }
    input, select, button { font-size: 16px; }
  }
`;