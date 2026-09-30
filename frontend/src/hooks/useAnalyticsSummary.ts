import { useQuery } from '@tanstack/react-query';
import { getAnalyticsSummary } from '../api/links';

export function useAnalyticsSummary(enabled = true) {
  return useQuery({
    queryKey: ['analytics-summary'],
    queryFn: getAnalyticsSummary,
    enabled,
    staleTime: 15_000,
  });
}