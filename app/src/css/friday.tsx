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
  transition: all 0.3s ease;

  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 16px;
  }

  @media (max-width: 480px) {
    padding: 1rem;
  }

  &:hover {
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
    transform: translateY(-3px);
  }
`;

export const FlexRow = styled.div`
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-start;

  @media (max-width: 768px) {
    gap: 1rem;
  }
`;

export const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  input:disabled {
    cursor: not-allowed;
  }

  &:has(input:disabled) {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:hover {
    color: var(--accent-hover);
    transform: scale(1.05);
  }
`;

export const TabContent = styled.div<{ $isActive: boolean }>`
  display: ${(props) => (props.$isActive ? 'block' : 'none')};
  animation: ${fadeIn} 0.4s ease-out;
`;

export const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
`;

export const Title = styled.h1`
  text-align: center;
  margin-bottom: 3rem;
  font-size: 4rem;
  font-weight: 800;
  letter-spacing: -1.5px;
  background: linear-gradient(
    135deg,
    var(--accent-primary),
    var(--accent-secondary)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
  animation: float 6s ease-in-out infinite;
  transition: all 0.3s ease;

  @media (max-width: 768px) {
    font-size: 3rem;
    margin-bottom: 2rem;
  }

  @media (max-width: 480px) {
    font-size: 2.5rem;
  }

  &:hover {
    text-shadow: 0 6px 18px rgba(139, 92, 246, 0.5);
  }
`;

export const Description = styled.p`
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
  font-size: 1.2rem;
  line-height: 1.7;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  transition: color 0.3s ease;

  @media (max-width: 768px) {
    font-size: 1.1rem;
    margin-bottom: 2rem;
  }

  &:hover {
    color: var(--text-primary);
  }
`;

export const TabsContainer = styled.div`
  display: flex;
  gap: 1.25rem;
  justify-content: center;
  margin-bottom: 3.5rem;
  position: relative;
  padding: 0.5rem;
  border-radius: 12px;
  background: rgba(22, 26, 47, 0.3);
  backdrop-filter: blur(15px);
  transition: all 0.3s ease;

  &::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: linear-gradient(
      90deg,
      transparent,
      var(--accent-primary),
      transparent
    );
    border-radius: 4px;
  }

  &:hover {
    box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
  }
`;

export const TabButton = styled.button<{ $isActive: boolean }>`
  padding: 1.1rem 2.2rem;
  border: none;
  background: ${(props) =>
    props.$isActive
      ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))'
      : 'transparent'};
  color: ${(props) => (props.$isActive ? '#fff' : 'var(--text-primary)')};
  cursor: pointer;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: ${(props) =>
    props.$isActive ? '0 6px 20px rgba(66, 133, 244, 0.4)' : 'none'};
  letter-spacing: 0.6px;

  &:hover {
    transform: translateY(-3px);
    background: ${(props) =>
      props.$isActive
        ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))'
        : 'rgba(66, 133, 244, 0.1)'};
    box-shadow: 0 8px 24px rgba(66, 133, 244, 0.3);
  }

  @media (max-width: 768px) {
    width: 100%;
    padding: 0.9rem 1.2rem;
  }
`;

export const FormSection = styled.div`
  background: rgba(15, 16, 22, 0.8);
  padding: 3.5rem;
  border-radius: 28px;
  margin-bottom: 3rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(139, 92, 246, 0.3);
  }

  @media (max-width: 768px) {
    padding: 2rem;
    border-radius: 20px;
  }
`;

export const Input = styled.input`
  width: 100%;
  padding: 1.4rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 16, 22, 0.6);
  color: var(--text-primary);
  border-radius: 14px;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);

  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 5px rgba(139, 92, 246, 0.2);
    transform: translateY(-3px);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  @media (max-width: 768px) {
    padding: 1rem;
    font-size: 1.1rem;
  }
`;

export const FileInput = styled.input`
  display: none;
`;

export const Select = styled.select`
  width: 100%;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: 6px;
  transition:
    border 0.3s ease,
    box-shadow 0.3s ease;
  cursor: pointer;
  font-size: 1.1rem;

  &:hover:not(:disabled) {
    border-color: var(--accent-hover);
    box-shadow: 0 0 0 3px rgba(121, 131, 255, 0.1);
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
  padding: 1.4rem 3rem;
  border: none;
  border-radius: 14px;
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: 0.7px;
  transition: all 0.4s ease;
  width: 100%;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);

  &:hover:not(:disabled) {
    background-position: right center;
    transform: translateY(-5px);
    box-shadow: 0 14px 30px rgba(139, 92, 246, 0.5);
  }

  &:active:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(139, 92, 246, 0.4);
  }

  @media (max-width: 768px) {
    padding: 1.2rem 2.5rem;
    font-size: 1.1rem;
  }
`;

export const FileLabel = styled.label<{ $disabled: boolean }>`
  display: block;
  width: 100%;
  padding: 2.2rem;
  border: 2px dashed
    ${(props) =>
      props.$disabled ? 'var(--border-color)' : 'var(--accent-primary)'};
  background: ${(props) =>
    props.$disabled ? 'var(--input-bg-disabled)' : 'var(--input-bg)'};
  color: ${(props) =>
    props.$disabled ? 'var(--text-secondary)' : 'var(--text-primary)'};
  border-radius: 14px;
  cursor: ${(props) => (props.$disabled ? 'not-allowed' : 'pointer')};
  text-align: center;
  transition: all 0.3s ease;
  font-size: 1.1rem;

  &:hover:not([disabled]) {
    background: rgba(66, 133, 244, 0.05);
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.2);
  }

  &:active:not([disabled]) {
    transform: scale(0.97);
  }
`;

export const OutputSection = styled.div`
  background: var(--bg-secondary);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  margin-bottom: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;

  pre {
    background: var(--bg-primary);
    padding: 1.75rem;
    border-radius: 10px;
    color: var(--text-primary);
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.6;
    border: 1px solid var(--border-color);
    font-size: 1rem;
  }

  @media (max-width: 768px) {
    padding: 2rem;
  }

  &:hover {
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  }
`;
