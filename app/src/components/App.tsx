import { useState, JSX } from 'react';
import { LogViewer } from './LogViewer';
import TestGenerator from './generator/testGenerator';
import Crawler from './crawler/webCrawler';
import ApiTester from './apitest/apiTester';

// Define tab types to ensure type safety
type TabId = 'generator' | 'crawler' | 'apitest';

interface Tab {
  id: TabId;
  label: string;
  component: (props: {
    setOutputText: (text: string) => void;
    setIsGenerating: (isGenerating: boolean) => void;
  }) => JSX.Element;
}

function FridayApp() {
  const [activeTab, setActiveTab] = useState<TabId>('generator');
  const [outputText, setOutputText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  // Define tabs configuration
  const tabs: Tab[] = [
    {
      id: 'generator',
      label: 'Test Case Generator',
      component: () => (
        <TestGenerator
          setOutputText={setOutputText}
          isGenerating={isGenerating}
          setIsGenerating={setIsGenerating}
        />
      ),
    },
    {
      id: 'crawler',
      label: 'Web Crawler',
      component: Crawler,
    },
    {
      id: 'apitest',
      label: 'API Testing',
      component: (props) => <ApiTester {...props} />,
    },
  ];

  const handleTabClick = (tabId: TabId) => {
    setActiveTab(tabId);
    setOutputText('');
  };

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-12 animate-fade-in bg-primary-800/60 backdrop-blur-lg rounded-3xl border border-white/10 shadow-2xl transition-all duration-300 hover:shadow-glow hover:-translate-y-1">
      <h1 className="text-center mb-12 text-6xl md:text-7xl font-extrabold tracking-tight bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent animate-float transition-all duration-300 hover:scale-105">
        FRIDAY Test Agent
      </h1>
      <p className="text-center text-primary-200 mb-10 text-xl leading-relaxed max-w-4xl mx-auto transition-colors duration-300 hover:text-primary-100">
        FRIDAY is a test agent that can generate test cases, crawl websites,
        and test APIs. Select the tab below to get started.
      </p>

      <div className="flex gap-5 justify-center mb-14 relative p-2 rounded-xl bg-primary-700/30 backdrop-blur-md transition-all duration-300 hover:shadow-glow">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => handleTabClick(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {tabs.map((tab) => (
        <div key={tab.id} className={`${activeTab === tab.id ? 'block animate-fade-in' : 'hidden'}`}>
          <tab.component
            key={tab.id}
            setOutputText={setOutputText}
            setIsGenerating={setIsGenerating}
          />
        </div>
      ))}

      <div className="card mt-12">
        <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-accent-500 to-secondary-500 bg-clip-text text-transparent">Output</h2>
        <pre className="bg-primary-900 p-7 rounded-lg text-primary-100 overflow-x-auto font-mono leading-relaxed border border-primary-600 text-base">
          {outputText}
        </pre>
      </div>
      <LogViewer />
    </div>
  );
}

export default FridayApp;
