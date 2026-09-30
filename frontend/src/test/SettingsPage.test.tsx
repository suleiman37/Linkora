import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import userEvent from '@testing-library/user-event';
import { SettingsPage } from '../pages/SettingsPage';

afterEach(() => {
  window.localStorage.clear();
});

describe('SettingsPage', () => {
  it('shows analytics by default and persists hiding it', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    const toggle = screen.getByRole('checkbox', { name: 'Show analytics on dashboard' });

    expect(toggle).toBeChecked();
    await user.click(toggle);

    expect(toggle).not.toBeChecked();
    expect(window.localStorage.getItem('shorty.analytics.dashboard-visible')).toBe('false');
    expect(screen.getByRole('status')).toHaveTextContent('hidden from the dashboard');
  });

  it('reads the saved visibility preference', () => {
    window.localStorage.setItem('shorty.analytics.dashboard-visible', 'false');
    render(<SettingsPage />);

    expect(screen.getByRole('checkbox', { name: 'Show analytics on dashboard' })).not.toBeChecked();
  });
});