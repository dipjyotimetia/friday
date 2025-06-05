'use client'

import { useState, useCallback } from 'react';
import { apiService } from '@/services/api';
import type { 
  GenerateRequest, 
  CrawlRequest, 
  ApiTestRequest, 
  ApiTestResponse 
} from '@/types';

interface UseApiState<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useTestGenerator() {
  const [state, setState] = useState<UseApiState>({
    data: null,
    loading: false,
    error: null,
  });

  const generateTests = useCallback(async (request: GenerateRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await apiService.generateTests(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    generateTests,
  };
}

export function useWebCrawler() {
  const [state, setState] = useState<UseApiState>({
    data: null,
    loading: false,
    error: null,
  });

  const crawlWebsite = useCallback(async (request: CrawlRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await apiService.crawlWebsite(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    crawlWebsite,
  };
}

export function useApiTester() {
  const [state, setState] = useState<UseApiState<ApiTestResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const testApi = useCallback(async (request: ApiTestRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await apiService.testApi(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    testApi,
  };
}