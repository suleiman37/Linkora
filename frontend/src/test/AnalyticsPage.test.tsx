import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AnalyticsPage } from '../pages/AnalyticsPage';

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}><AnalyticsPage /></QueryClientProvider>
    </BrowserRouter>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('AnalyticsPage', () => {
  it('shows the empty workspace state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ total_links: 0, total_clicks: 0, last_clicked_at: null, top_links: [], recently_active_links: [] }),
    }));

    renderPage();

    expect(await screen.findByRole('heading', { name: 'No analytics yet' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /create your first link/i })).toBeInTheDocument();
  });

  it('renders lifetime totals and top links', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        total_links: 2,
        total_clicks: 12,
        last_clicked_at: '2026-09-14T10:30:00Z',
        top_links: [{
          id: 1,
          original_url: 'https://example.com/one',
          short_code: 'one0001',
          short_url: 'http://localhost:8000/one0001',
          created_at: '2026-09-13T10:30:00Z',
          click_count: 12,
          last_clicked_at: '2026-09-14T10:30:00Z',
        }],
        recently_active_links: [],
      }),
    }));

    renderPage();

    expect(await screen.findByText('Lifetime clicks')).toBeInTheDocument();
    expect(within(screen.getByRole('region', { name: 'Analytics summary' })).getByText('12')).toBeInTheDocument();
    expect(screen.getByText('http://localhost:8000/one0001')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Top-performing links' })).toBeInTheDocument();
  });
});