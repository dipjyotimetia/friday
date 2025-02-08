import React, { useState } from 'react';
import { CheckboxLabel, FlexRow, FormSection, Input, InputGroup, Select, SubmitButton } from "../../css/friday";
import { apiService } from '../../services/api';

function Crawler() {
    const [url, setUrl] = useState('');
    const [provider, setProvider] = useState('vertex');
    const [maxPages, setMaxPages] = useState(10);
    const [sameDomain, setSameDomain] = useState(true);
    const [isCrawling, setIsCrawling] = useState(false);
    const [outputText, setOutputText] = useState('');


    const handleCrawl = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsCrawling(true);
        try {
            const result = await apiService.crawlWebsite({
                url,
                provider,
                persist_dir: './data/chroma',
                max_pages: Number(maxPages),
                same_domain: sameDomain
            });
            setOutputText(JSON.stringify(result, null, 2));
        } catch (err) {
            setOutputText(`Error: ${(err as Error).message}`);
        } finally {
            setIsCrawling(false);
        }
    };
    return (
        <>
            <FormSection>
                <h2>Web Crawler</h2>
                <form onSubmit={handleCrawl}>
                    <InputGroup>
                        <Input
                            type="text"
                            placeholder="Website URL"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={isCrawling}
                        />
                        <Select
                            value={provider}
                            onChange={(e) => setProvider(e.target.value)}
                            disabled={isCrawling}
                        >
                            <option value="vertex">Vertex</option>
                            <option value="openai">OpenAI</option>
                        </Select>
                        <Input
                            type="number"
                            placeholder="Max Pages"
                            value={maxPages}
                            onChange={(e) => setMaxPages(Number(e.target.value))}
                            disabled={isCrawling}
                        />
                        <FlexRow>
                            <CheckboxLabel>
                                <input
                                    type="checkbox"
                                    checked={sameDomain}
                                    onChange={(e) => setSameDomain(e.target.checked)}
                                    disabled={isCrawling}
                                />
                                Stay on same domain
                            </CheckboxLabel>
                        </FlexRow>
                    </InputGroup>
                    <SubmitButton type="submit" disabled={isCrawling}>
                        {isCrawling ? 'Crawling...' : 'Start Crawling'}
                    </SubmitButton>
                </form>
            </FormSection>
        </>
    );
}

export default Crawler;