import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  :root {
    /* Core colors - Darker and more nuanced */
    --bg-primary: #0B0D1A;
    --bg-secondary: #161A2E; /* Slightly lighter for contrast */
    --text-primary: #E2E8F0; /* Lighter, softer white */
    --text-secondary: #A1AABF; /* Muted, for less important text */

    /* Accent colors - More vibrant and harmonious */
    --accent-primary: #7983FF; /* A softer, more inviting purple */
    --accent-secondary: #FF6B6B; /* A complementary red/pink */
    --accent-hover: #9CB4FF; /* Lighter version for hover states */

    /* UI Elements - Refined for better aesthetics */
    --border-color: rgba(255, 255, 255, 0.08); /* Even more subtle */
    --input-bg: #1E223A; /* Darker input background */
    --input-bg-disabled: #242946; /* Even darker for disabled */
    --glass-bg: rgba(22, 26, 47, 0.7); /* More transparent glass */

    /* Effects - Subtler and more sophisticated */
    --shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* Less intense shadow */
    --glow: 0 0 15px rgba(121, 131, 255, 0.2); /* Softer glow */
    --gradient-primary: linear-gradient(135deg, var(--accent-primary), #5C67FF);
    --gradient-secondary: linear-gradient(135deg, var(--accent-secondary), var(--accent-primary));

    /* Common transitions - Slightly faster for responsiveness */
    --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
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
    /* More subtle background texture */
    background-image:
      radial-gradient(circle at 100% 0%, rgba(121, 131, 255, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 0% 100%, rgba(255, 107, 107, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(92, 103, 255, 0.05) 0%, transparent 50%);
    background-attachment: fixed;
    color: var(--text-primary);
    line-height: 1.6;
    padding: clamp(16px, 5vw, 20px);
    -webkit-font-smoothing: antialiased;
  }

  /* Utility classes */
  .glass {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
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
    50% { transform: translateY(-8px); } /* Reduced float height */
  }

  /* Interactive elements */
  a {
    color: var(--accent-primary);
    text-decoration: none;
    background: linear-gradient(to right, var(--accent-secondary), var(--accent-primary));
    background-size: 0% 1.5px; /* Thinner underline */
    background-repeat: no-repeat;
    background-position: left bottom;
    transition: background-size var(--transition-normal);

    &:hover {
      background-size: 100% 1.5px;
    }
  }

  /* Mobile optimizations */
  @media (max-width: 768px) {
    * { touch-action: manipulation; }
    input, select, button { font-size: 16px; }
  }
`;
