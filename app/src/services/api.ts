import { invoke } from '@tauri-apps/api/core';
import { TestGenerationParams, CrawlParams, ApiResponse } from '../types';

const API_URL = 'http://localhost:8080';

export async function generateTests(params: TestGenerationParams): Promise<ApiResponse> {
  try {
    const response = await invoke<ApiResponse>('generate_tests', {
      params: params
    });
    return response;
  } catch (error) {
    return { error: String(error) };
  }
}

export async function crawlWebsite(params: CrawlParams): Promise<ApiResponse> {
  try {
    const response = await invoke<ApiResponse>('crawl_website', {
      params: params
    });
    return response;
  } catch (error) {
    return { error: String(error) };
  }
}