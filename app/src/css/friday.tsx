import styled, { keyframes } from 'styled-components';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  animation: ${fadeIn} 0.6s ease-out;

  @media (max-width: 768px) {
    padding: 1rem;
    max-width: 100%;
  }
`;

export const FlexRow = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    gap: 0.5rem;
  }
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

export const TabContent = styled.div<{ isActive: boolean }>`
  display: ${props => props.isActive ? 'block' : 'none'};
`;

export const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;

  @media (max-width: 768px) {
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
`;

export const Title = styled.h1`
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 2rem;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(120deg, var(--accent-primary), #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

export const Description = styled.p`
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.6;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: 768px) {
    font-size: 1rem;
    margin-bottom: 1.5rem;
  }
`;

export const TabsContainer = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
  }
`;

export const TabButton = styled.button<{ isActive: boolean }>`
  padding: 1rem 2rem;
  border: none;
  background: ${props => props.isActive ? 
    'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))' : 
    'transparent'};
  color: ${props => props.isActive ? '#fff' : 'var(--text-primary)'};
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: ${props => props.isActive ? 
    '0 4px 15px rgba(66, 133, 244, 0.3)' : 'none'};

  &:hover {
    transform: translateY(-2px);
    background: ${props => props.isActive ? 
      'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))' : 
      'rgba(66, 133, 244, 0.1)'};
  }
  
  @media (max-width: 768px) {
    width: 100%;
    padding: 0.75rem 1rem;
  }    
`;

export const FormSection = styled.div`
  background: var(--bg-secondary);
  padding: 2.5rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
  
  @media (max-width: 768px) {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }  
`;

export const Input = styled.input`
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: var(--input-bg-disabled);
  }
`;

export const FileInput = styled.input`
  display: none;
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
  
  &:hover:not(:disabled) {
    border-color: var(--accent-hover);
  }
`;

export const SubmitButton = styled.button`
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-hover));
  color: #fff;
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  width: 100%;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      120deg,
      transparent,
      rgba(255, 255, 255, 0.2),
      transparent
    );
    transition: 0.5s;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(66, 133, 244, 0.3);

    &::before {
      left: 100%;
    }
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const FileLabel = styled.label<{ $disabled: boolean }>`
  display: block;
  width: 100%;
  padding: 2rem;
  border: 2px dashed ${props => props.$disabled ? 
    'var(--border-color)' : 
    'var(--accent-primary)'};
  background: ${props => props.$disabled ? 
    'var(--input-bg-disabled)' : 
    'var(--input-bg)'};
  color: ${props => props.$disabled ? 
    'var(--text-secondary)' : 
    'var(--text-primary)'};
  border-radius: 12px;
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  text-align: center;
  transition: all 0.3s ease;

  &:hover:not([disabled]) {
    background: rgba(66, 133, 244, 0.05);
    transform: translateY(-2px);
  }

  &:active:not([disabled]) {
    transform: scale(0.98);
  }
`;

export const OutputSection = styled.div`
  background: var(--bg-secondary);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);

  pre {
    background: var(--bg-primary);
    padding: 1.5rem;
    border-radius: 8px;
    color: var(--text-primary);
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.5;
    border: 1px solid var(--border-color);
  }

  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;