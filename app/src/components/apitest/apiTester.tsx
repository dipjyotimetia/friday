import React, { useState } from 'react';
import { FormSection, Input, InputGroup, SubmitButton } from "../../css/friday";
import { apiService } from '../../services/api';
import { FileUploader } from '../FileUploader';

interface ApiTesterProps {
  setOutputText: (text: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
}

function ApiTester({ setOutputText, setIsGenerating }: ApiTesterProps) {
    const [baseUrl, setBaseUrl] = useState('');
    const [isTestingApi, setIsTestingApi] = useState(false);
    const [apiOutput, setApiOutput] = useState('test_report.md');
    const [specFileObj, setSpecFileObj] = useState<File | null>(null);

   const handleApiTest = async (e: React.FormEvent) => {
      e.preventDefault();
      setIsTestingApi(true);
      try {
        const formData = new FormData();
        if (specFileObj) {
          formData.append('spec_file', specFileObj);
        }
        formData.append('base_url', baseUrl);
        formData.append('output', apiOutput);
  
        const result = await apiService.testApi(formData);
        setOutputText(JSON.stringify(result, null, 2));
      } catch (err) {
        setOutputText(`Error: ${(err as Error).message}`);
      } finally {
        setIsGenerating(false);
      }
    };

  return (
    <>
        <FormSection>
            <h2>API Testing</h2>
            <form onSubmit={handleApiTest}>
              <InputGroup>
                <FileUploader
                  accept=".yaml,.json"
                  onChange={(file) => setSpecFileObj(file)}
                  placeholder="Upload OpenAPI/Swagger Spec"
                />
                <Input
                  type="text"
                  placeholder="Base URL (e.g. https://api.example.com)"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  disabled={isTestingApi}
                />
                <Input
                  type="text"
                  placeholder="Output filename"
                  value={apiOutput}
                  onChange={(e) => setApiOutput(e.target.value)}
                  disabled={isTestingApi}
                />
              </InputGroup>
              <SubmitButton type="submit" disabled={isTestingApi}>
                {isTestingApi ? 'Running Tests...' : 'Run API Tests'}
              </SubmitButton>
            </form>
          </FormSection>
    </>
  );
}

export default ApiTester;