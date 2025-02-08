import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  :root {
    --bg-primary: #121212;
    --bg-secondary: rgba(31, 31, 31, 0.95);
    --text-primary: #e0e0e0;
    --text-secondary: #b0b0b0;
    --accent-primary: #4285f4;
    --accent-hover: #3367d6;
    --border-color: #333;
    --input-bg: rgba(44, 44, 44, 0.95);
    --input-bg-disabled: rgba(26, 26, 26, 0.95);
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    --gradient-primary: linear-gradient(135deg, #4285f4, #34a853);
    --gradient-secondary: linear-gradient(135deg, #ea4335, #fbbc05);
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 20px;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }

  @media (max-width: 768px) {
    body {
      padding: 10px;
    }
  }

  @keyframes shimmer {
    0% {
      background-position: -1000px 0;
    }
    100% {
      background-position: 1000px 0;
    }
  }
`;