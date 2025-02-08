import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  :root {
    --bg-primary: #121212;
    --bg-secondary: #1f1f1f;
    --text-primary: #e0e0e0;
    --text-secondary: #b0b0b0;
    --accent-primary: #4285f4;
    --accent-hover: #3367d6;
    --border-color: #333;
    --input-bg: #2c2c2c;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    padding: 20px;
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: background 0.3s ease, color 0.3s ease;
  }
`;