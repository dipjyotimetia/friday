import React, { useState } from 'react';
import { FormSection, Input, InputGroup, SubmitButton } from "../../css/friday";
import { apiService } from '../../services/api';
import { FileUploader } from '../FileUploader';

interface PerfTesterProps {
  setOutputText: (text: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
}

function PerfTester({ setOutputText, setIsGenerating }: PerfTesterProps) {
    const [baseUrl, setBaseUrl] = useState('');
    const [curlCommand, setCurlCommand] = useState('');
    const [users, setUsers] = useState(10);
    const [duration, setDuration] = useState(30);
    const [isTestingPerf, setIsTestingPerf] = useState(false);
    const [specFileObj, setSpecFileObj] = useState<File | null>(null);

    const handlePerfTest = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsTestingPerf(true);
        setIsGenerating(true);
        
        try {
            const formData = new FormData();
            if (specFileObj) {
                formData.append('spec_file', specFileObj);
            }
            if (curlCommand) {
                formData.append('curl_command', curlCommand);
            }
            if (baseUrl) {
                formData.append('base_url', baseUrl);
            }
            formData.append('users', users.toString());
            formData.append('duration', duration.toString());

            const result = await apiService.runPerfTest({
                spec_file: specFileObj || undefined,
                curl_command: curlCommand,
                base_url: baseUrl,
                users,
                duration
            });
            
            setOutputText(result.report);
        } catch (err) {
            setOutputText(`Error: ${(err as Error).message}`);
        } finally {
            setIsTestingPerf(false);
            setIsGenerating(false);
        }
    };

    return (
        <FormSection>
            <h2>Performance Testing</h2>
            <form onSubmit={handlePerfTest}>
                <InputGroup>
                    <FileUploader
                        accept=".yaml,.json"
                        onChange={(file) => setSpecFileObj(file)}
                        placeholder="Upload OpenAPI/Swagger Spec (Optional)"
                    />
                    <Input
                        type="text"
                        placeholder="Curl command (Optional)"
                        value={curlCommand}
                        onChange={(e) => setCurlCommand(e.target.value)}
                        disabled={isTestingPerf}
                    />
                    <Input
                        type="text"
                        placeholder="Base URL (Optional if using curl)"
                        value={baseUrl}
                        onChange={(e) => setBaseUrl(e.target.value)}
                        disabled={isTestingPerf}
                    />
                    <Input
                        type="number"
                        placeholder="Concurrent Users"
                        value={users}
                        onChange={(e) => setUsers(parseInt(e.target.value))}
                        disabled={isTestingPerf}
                    />
                    <Input
                        type="number"
                        placeholder="Duration (seconds)"
                        value={duration}
                        onChange={(e) => setDuration(parseInt(e.target.value))}
                        disabled={isTestingPerf}
                    />
                </InputGroup>
                <SubmitButton type="submit" disabled={isTestingPerf}>
                    {isTestingPerf ? 'Running Performance Tests...' : 'Run Performance Tests'}
                </SubmitButton>
            </form>
        </FormSection>
    );
}

export default PerfTester;