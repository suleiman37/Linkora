import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { getLinks } from '../api/links';
import type { LinkSort } from '../api/types';

export function useLinks(params: {
  page: number;
  pageSize: number;
  search: string;
  sort: LinkSort;
}) {
  return useQuery({
    queryKey: ['links', params],
    queryFn: () => getLinks(params),
    placeholderData: keepPreviousData,
    staleTime: 15_000,
  });
}
