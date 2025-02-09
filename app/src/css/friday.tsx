import styled, { keyframes } from 'styled-components';

const fadeIn = keyframes`
  from { 
    opacity: 0; 
    transform: translateY(20px) scale(0.98);
    filter: blur(8px);
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
`;

export const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem;
  animation: ${fadeIn} 0.8s ease-out;
  background: rgba(15, 16, 22, 0.6);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);

  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 16px;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
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
  margin-bottom: 2.5rem;
  font-size: 3.5rem;
  font-weight: 800;
  letter-spacing: -1px;
  background: linear-gradient(
    135deg,
    var(--accent-primary),
    var(--accent-secondary)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);
  animation: float 6s ease-in-out infinite;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
  
  @media (max-width: 480px) {
    font-size: 2rem;
  }
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
  background: rgba(15, 16, 22, 0.8);
  padding: 3rem;
  border-radius: 24px;
  margin-bottom: 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(139, 92, 246, 0.3);
  }
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 16px;
  }  
`;

export const Input = styled.input`
  width: 100%;
  padding: 1.2rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 16, 22, 0.6);
  color: var(--text-primary);
  border-radius: 12px;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);

  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
    transform: translateY(-2px);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
  
  @media (max-width: 768px) {
    padding: 0.8rem;
    font-size: 1rem;
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
  background: linear-gradient(
    45deg,
    var(--accent-primary),
    var(--accent-secondary),
    var(--accent-primary)
  );
  background-size: 200% auto;
  color: #fff;
  padding: 1.2rem 2.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.4s ease;
  width: 100%;
  position: relative;
  overflow: hidden;
  box-shadow: 0 6px 15px rgba(139, 92, 246, 0.3);

  &:hover:not(:disabled) {
    background-position: right center;
    transform: translateY(-3px);
    box-shadow: 0 12px 25px rgba(139, 92, 246, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(-1px);
  }
  
  @media (max-width: 768px) {
    padding: 1rem 2rem;
    font-size: 1rem;
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