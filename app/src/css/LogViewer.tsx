import styled from 'styled-components';

export const LogViewerContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 400px;
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  backdrop-filter: blur(20px);
  transition: all 0.3s ease; /* Added transition for smoother appearance */

  @media (max-width: 768px) {
    border-radius: 12px;
  }

  /* Subtle hover effect for the entire container */
  &:hover {
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    transform: translateY(-3px);
  }
`;

export const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem;
  background: var(--glass-bg);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(12px);

  h3 {
    margin: 0;
    color: var(--text-primary);
    /* Using a more vibrant gradient */
    background: linear-gradient(
      135deg,
      var(--accent-primary),
      var(--accent-secondary)
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; /* Slightly bolder font weight */
    letter-spacing: 0.5px; /* Slight letter spacing for better readability */
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

export const Status = styled.span<{ $isConnected: boolean }>`
  padding: 0.6rem 1.2rem; /* Adjusted padding */
  border-radius: 16px; /* More rounded corners */
  font-size: 0.9rem;
  background: ${(props) =>
    props.$isConnected
      ? 'linear-gradient(135deg, #43a047, #2e7d32)'
      : 'linear-gradient(135deg, #d32f2f, #b71c1c)'};
  color: var(--text-primary);
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  font-weight: 500; /* Slightly bolder font weight */
`;

export const LogContainer = styled.div`
  flex: 1;
  height: calc(100% - 60px);
  overflow-y: auto;
  padding: 1.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;

  /* Custom scrollbar styling */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--gradient-primary);
    border-radius: 4px;
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

export const LogEntry = styled.div<{ level?: 'info' | 'error' | 'warn' }>`
  padding: 0.6rem 0; /* Adjusted padding */
  line-height: 1.6;
  color: ${(props) => {
    switch (props.level) {
      case 'error':
        return 'var(--accent-secondary)';
      case 'warn':
        return '#ffd700';
      default:
        return 'var(--text-primary)';
    }
  }};
  transition: all 0.2s ease;
  border-radius: 8px; /* Added border-radius for a softer look */

  &:hover {
    background: var(--input-bg);
    padding: 0.6rem;
    transform: translateX(5px); /* Slightly more pronounced hover effect */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Added subtle shadow on hover */
  }
`;

export const Timestamp = styled.span`
  color: var(--text-secondary);
  margin-right: 1rem;
  font-size: 0.8rem;
  opacity: 0.8;
`;
