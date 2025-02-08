import styled from 'styled-components';

export const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

export const Title = styled.h1`
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
`;

export const Description = styled.p`
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
`;

export const TabsContainer = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
`;

export const TabButton = styled.button<{ isActive: boolean }>`
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--accent-primary);
  background: ${props => props.isActive ? 'var(--accent-primary)' : 'transparent'};
  color: ${props => props.isActive ? '#fff' : 'var(--text-primary)'};
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.3s ease, color 0.3s ease;

  &:hover {
    background: var(--accent-primary);
    color: #fff;
  }
`;

export const TabContent = styled.div<{ isActive: boolean }>`
  display: ${props => props.isActive ? 'block' : 'none'};
`;

export const FormSection = styled.div`
  background: var(--bg-secondary);
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
`;

export const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

export const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: 4px;
  transition: border 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--accent-primary);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: var(--input-bg-disabled, #1a1a1a);
  }
`;

export const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: 4px;
  transition: border 0.3s ease;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  &:hover {
    border-color: var(--accent-hover);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: var(--input-bg-disabled, #1a1a1a);
  }
`;

export const FlexRow = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
`;

export const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  cursor: pointer;

  input:disabled {
    cursor: not-allowed;
  }
  
  &:has(input:disabled) {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const SubmitButton = styled.button`
 background: var(--accent-primary);
  color: #fff;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s ease, opacity 0.3s ease;
  width: 100%;

  &:hover:not(:disabled) {
    background: var(--accent-hover);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const OutputSection = styled.div`
  background: var(--bg-secondary);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: var(--shadow);
  margin-bottom: 2rem;

  pre {
    background: var(--bg-primary);
    padding: 1rem;
    border-radius: 4px;
    color: var(--text-primary);
    overflow-x: auto;
  }

  /* Add styles for responsive design */
  @media (max-width: 768px) {
    padding: 1rem;
    border-radius: 8px;
  }

  /* Additional hover effect */
  &:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
`;

export const FileInput = styled.input`
  display: none;
`;

export const FileLabel = styled.label<{ $disabled: boolean }>`
  display: block;
  width: 100%;
  padding: 0.75rem;
  border: 2px dashed var(--border-color);
  background: ${({ $disabled }) => $disabled ? 'var(--input-bg-disabled, #1a1a1a)' : 'var(--input-bg)'};
  color: ${({ $disabled }) => $disabled ? 'lightgray' : 'var(--text-primary)'};
  border-radius: 4px;
  cursor: ${({ $disabled }) => $disabled ? 'not-allowed' : 'pointer'};
  text-align: center;
  transition: border-color 0.3s ease;

  &:hover {
    border-color: ${({ $disabled }) => $disabled ? 'var(--border-color)' : 'var(--accent-primary)'};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
    border-color: ${({ $disabled }) => $disabled ? 'var(--border-color)' : 'var(--accent-primary)'};
  }

  &:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }  
`;
  
