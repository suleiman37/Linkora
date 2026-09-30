import { useQuery } from '@tanstack/react-query';
import { getLinkStats } from '../api/links';

export function useLinkStats(shortCode: string | null) {
  return useQuery({
    queryKey: ['link-stats', shortCode],
    queryFn: () => getLinkStats(shortCode as string),
    enabled: Boolean(shortCode),
    staleTime: 15_000,
  });
}
