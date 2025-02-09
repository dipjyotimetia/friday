import { useState, JSX } from 'react';
import { LogViewer } from './LogViewer';
import {
  Container, Description,
  OutputSection, TabButton, TabContent, TabsContainer, Title
} from "../css/friday"
import { GlobalStyle } from '../css/GlobalStyle';
import TestGenerator from './generator/testGenerator';
import Crawler from './crawler/webCrawler';
import ApiTester from './apitest/apiTester';
import PerfTester from './apitest/perfTester';

// Define tab types to ensure type safety
type TabId = 'generator' | 'crawler' | 'apitest' | 'perftest';

interface Tab {
  id: TabId;
  label: string;
  component: (props: { setOutputText: (text: string) => void; setIsGenerating: (isGenerating: boolean) => void }) => JSX.Element;
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
      component: () => <TestGenerator setOutputText={setOutputText} isGenerating={isGenerating} setIsGenerating={setIsGenerating} />
    },
    {
      id: 'crawler',
      label: 'Web Crawler',
      component: Crawler
    },
    {
      id: 'apitest',
      label: 'API Testing',
      component: (props) => <ApiTester {...props} />
    },
    {
      id: 'perftest',
      label: 'Performance Testing',
      component: (props) => <PerfTester {...props} />
    }
  ];
  
  const handleTabClick = (tabId: TabId) => {
    setActiveTab(tabId);
    setOutputText('');
  };

  return (
    <>
      <GlobalStyle />
      <Container>
        <Title>FRIDAY Test Agent</Title>
        <Description>
          FRIDAY is a test agent that can generate test cases, crawl websites, and test APIs. Select
          the tab below to get started.
        </Description>

        <TabsContainer>
          {tabs.map(tab => (
            <TabButton
              key={tab.id}
              isActive={activeTab === tab.id}
              onClick={() => handleTabClick(tab.id)}
            >
              {tab.label}
            </TabButton>
          ))}
        </TabsContainer>

        {tabs.map(tab => (
          <TabContent key={tab.id} isActive={activeTab === tab.id}>
            <tab.component key={tab.id} setOutputText={setOutputText} setIsGenerating={setIsGenerating} />
          </TabContent>
        ))}

        <OutputSection>
          <h2>Output</h2>
          <pre>{outputText}</pre>
        </OutputSection>
        <LogViewer />
      </Container>
    </>
  );
}

export default FridayApp;