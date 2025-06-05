import React, { useState } from 'react';
import { apiService } from '../../services/api';

function Crawler() {
  const [url, setUrl] = useState('');
  const [provider, setProvider] = useState('openai');
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
        same_domain: sameDomain,
      });
      setOutputText(JSON.stringify(result, null, 2));
    } catch (err) {
      setOutputText(`Error: ${(err as Error).message}`);
    } finally {
      setIsCrawling(false);
    }
  };
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent">Web Crawler</h2>
      <form onSubmit={handleCrawl}>
        <div className="flex flex-col gap-5 mb-8 md:gap-4 md:mb-6">
          <input
            type="text"
            placeholder="Website URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isCrawling}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isCrawling}
            className="w-full p-4 border border-primary-600 bg-primary-700 text-primary-100 rounded-lg transition-all duration-300 cursor-pointer text-lg hover:border-accent-600 hover:shadow-glow focus:outline-none focus:border-accent-500 md:p-4 md:text-lg"
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama</option>
            <option value="mistral">Mistral</option>
          </select>
          <input
            type="number"
            placeholder="Max Pages"
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            disabled={isCrawling}
            className="input-field placeholder:text-white/50 md:p-4 md:text-lg"
          />
          <div className="flex gap-6 items-center flex-wrap justify-start md:gap-4">
            <label className={`flex items-center gap-3 text-primary-100 cursor-pointer transition-all duration-200 ${
              isCrawling ? 'opacity-60 cursor-not-allowed' : 'hover:text-accent-400 hover:scale-105'
            }`}>
              <input
                type="checkbox"
                checked={sameDomain}
                onChange={(e) => setSameDomain(e.target.checked)}
                disabled={isCrawling}
                className="w-4 h-4 accent-accent-500"
              />
              Stay on same domain
            </label>
          </div>
        </div>
        <button 
          type="submit" 
          disabled={isCrawling}
          className={`btn-primary w-full text-xl md:text-lg md:px-6 md:py-3 ${
            isCrawling ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          {isCrawling ? 'Crawling...' : 'Start Crawling'}
        </button>
      </form>
    </div>
  );
}

export default Crawler;
