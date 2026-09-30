import { apiRequest } from './client';
import type { AnalyticsSummaryResponse, CreateLinkResponse, LinkListResponse, LinkSort, LinkStatisticsResponse } from './types';

export function createLink(url: string): Promise<CreateLinkResponse> {
  return apiRequest<CreateLinkResponse>('/api/v1/links', {
    method: 'POST',
    body: JSON.stringify({ url }),
  });
}

export function getLinkStats(shortCode: string): Promise<LinkStatisticsResponse> {
  return apiRequest<LinkStatisticsResponse>(`/api/v1/links/${encodeURIComponent(shortCode)}/stats`);
}

export function getAnalyticsSummary(): Promise<AnalyticsSummaryResponse> {
  return apiRequest<AnalyticsSummaryResponse>('/api/v1/analytics/summary');
}

export function getLinks(params: {
  page: number;
  pageSize: number;
  search: string;
  sort: LinkSort;
}): Promise<LinkListResponse> {
  const query = new URLSearchParams({
    page: String(params.page),
    page_size: String(params.pageSize),
    sort: params.sort,
  });
  if (params.search) query.set('search', params.search);
  return apiRequest<LinkListResponse>(`/api/v1/links?${query.toString()}`);
}

export function checkHealth(): Promise<{ status: string }> {
  return apiRequest<{ status: string }>('/health');
}
