import styled from 'styled-components';

export const LogViewerContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 400px; // Add fixed height
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  backdrop-filter: blur(20px);

  @media (max-width: 768px) {
    border-radius: 12px;
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
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

export const Status = styled.span<{ isConnected: boolean }>`
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  background: ${props => props.isConnected ? 
    'linear-gradient(135deg, #43a047, #2e7d32)' : 
    'linear-gradient(135deg, #d32f2f, #b71c1c)'};
  color: var(--text-primary);
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
`;

export const LogContainer = styled.div`
  flex: 1;
  height: calc(100% - 60px); // Subtract header height
  overflow-y: auto;
  padding: 1.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;

  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-secondary);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--gradient-primary);
    border-radius: 3px;
  }

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

export const LogEntry = styled.div<{ level?: 'info' | 'error' | 'warn' }>`
  padding: 0.5rem 0;
  line-height: 1.6;
  color: ${props => {
    switch (props.level) {
      case 'error': return 'var(--accent-secondary)';
      case 'warn': return '#ffd700';
      default: return 'var(--text-primary)';
    }
  }};
  transition: all 0.2s ease;

  &:hover {
    background: var(--input-bg);
    border-radius: 8px;
    padding: 0.5rem;
    transform: translateX(4px);
  }
`;

export const Timestamp = styled.span`
  color: var(--text-secondary);
  margin-right: 1rem;
  font-size: 0.8rem;
  opacity: 0.8;
`;