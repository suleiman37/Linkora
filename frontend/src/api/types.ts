export type CreateLinkResponse = {
  id: number;
  original_url: string;
  short_code: string;
  short_url: string;
  created_at: string;
};

export type LinkStatisticsResponse = {
  short_code: string;
  original_url: string;
  click_count: number;
  last_clicked_at: string | null;
  created_at: string;
};

export type LinkSort = 'created_desc' | 'created_asc' | 'clicks_desc';

export type LinkHistoryItem = {
  id: number;
  original_url: string;
  short_code: string;
  short_url: string;
  created_at: string;
  click_count: number;
  last_clicked_at: string | null;
};

export type LinkListResponse = {
  items: LinkHistoryItem[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
};

export type AnalyticsSummaryResponse = {
  total_links: number;
  total_clicks: number;
  last_clicked_at: string | null;
  top_links: LinkHistoryItem[];
  recently_active_links: LinkHistoryItem[];
};

export type BackendError = {
  error: {
    code: string;
    message: string;
    details: unknown;
    request_id: string;
  };
};

export type ApiFailure = Error & {
  status?: number;
  code?: string;
  requestId?: string;
  isNetworkError?: boolean;
};
