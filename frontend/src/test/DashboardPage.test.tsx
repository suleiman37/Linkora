import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from '../pages/DashboardPage';

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}><DashboardPage /></QueryClientProvider>
    </BrowserRouter>,
  );
}

describe('DashboardPage', () => {
  it('renders the shorten form and empty state', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: 'Welcome back' })).toBeInTheDocument();
    expect(screen.getByLabelText('Long URL')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /shorten url/i })).toBeDisabled();
    expect(screen.getByText('Your workspace is ready')).toBeInTheDocument();
  });

  it('shows a friendly API error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    renderPage();
    const input = screen.getByLabelText('Long URL');
    await import('@testing-library/user-event').then(async ({ default: userEvent }) => {
      const user = userEvent.setup();
      await user.type(input, 'https://example.com');
      await user.click(screen.getByRole('button', { name: /shorten url/i }));
    });
    expect(await screen.findByText(/unable to reach the api/i)).toBeInTheDocument();
    vi.unstubAllGlobals();
  });
});
