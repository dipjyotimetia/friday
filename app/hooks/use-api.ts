'use client';

import { useState, useCallback } from 'react';
import { apiService } from '@/services/api';
import type {
  ExtendedTestGenerationRequest,
  ExtendedCrawlRequest,
  ExtendedAPITestRequest,
  ExtendedAPITestResponse,
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

  const generateTests = useCallback(
    async (request: ExtendedTestGenerationRequest) => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await apiService.generateTests(request);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Unknown error occurred';
        setState({ data: null, loading: false, error: errorMessage });
        throw error;
      }
    },
    []
  );

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

  const crawlWebsite = useCallback(async (request: ExtendedCrawlRequest) => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await apiService.crawlWebsite(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error occurred';
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
  const [state, setState] = useState<UseApiState<ExtendedAPITestResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const testApi = useCallback(async (request: ExtendedAPITestRequest) => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await apiService.testApi(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    testApi,
  };
}

// Generic API hook for making custom requests
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const makeRequest = useCallback(async (url: string, options?: RequestInit) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      setLoading(false);
      throw err;
    }
  }, []);

  return {
    makeRequest,
    loading,
    error,
  };
}
