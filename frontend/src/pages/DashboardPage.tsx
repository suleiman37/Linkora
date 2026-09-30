import { useState } from 'react';
import { Activity, BarChart3, RefreshCw, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { CreateLinkResponse } from '../api/types';
import { useAnalyticsSummary } from '../hooks/useAnalyticsSummary';
import { useAnalyticsVisibility } from '../hooks/useAnalyticsVisibility';
import { useLinkStats } from '../hooks/useLinkStats';
import { EmptyState } from '../components/EmptyState';
import { LinkResultCard } from '../components/LinkResultCard';
import { ShortenForm } from '../components/ShortenForm';
import { StatisticsCard } from '../components/StatisticsCard';
import { Toast } from '../components/Toast';
import { LinkHistoryRow } from '../components/LinkHistoryRow';
import { formatDate } from '../lib/formatDate';

export function DashboardPage() {
  const [createdLink, setCreatedLink] = useState<CreateLinkResponse | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const { isVisible, setIsVisible } = useAnalyticsVisibility();
  const statsQuery = useLinkStats(createdLink?.short_code ?? null);
  const analyticsQuery = useAnalyticsSummary(isVisible);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 3200);
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <div className="page-kicker"><span className="kicker-dot" /> Link workspace</div>
          <h1>Welcome back</h1>
          <p>Move ideas forward with links that are easy to share and understand.</p>
        </div>
        <div className="trust-note"><ShieldCheck size={16} /> Built for simple, reliable sharing</div>
      </div>
      <ShortenForm onCreated={(link) => { setCreatedLink(link); }} />
      {createdLink ? (
        <div className="content-stack">
          <LinkResultCard link={createdLink} onCopied={() => showToast('Link copied to clipboard')} />
          <StatisticsCard stats={statsQuery.data} isLoading={statsQuery.isLoading} isError={statsQuery.isError} />
        </div>
      ) : (
        <EmptyState />
      )}
      {isVisible ? (
        <section className="surface-card dashboard-analytics" aria-labelledby="dashboard-analytics-heading">
          <div className="dashboard-analytics-heading">
            <div className="card-heading">
              <span className="card-icon"><BarChart3 size={18} /></span>
              <div><h2 id="dashboard-analytics-heading">Workspace analytics</h2><p>Lifetime performance across your short links.</p></div>
            </div>
            <div className="dashboard-analytics-actions">
              <Link className="secondary-button" to="/analytics">See more</Link>
              <button className="secondary-button" type="button" onClick={() => setIsVisible(false)}>Hide</button>
            </div>
          </div>
          {analyticsQuery.isLoading && <div className="analytics-message"><Activity className="spin" size={18} /> Loading analytics</div>}
          {analyticsQuery.isError && <div className="analytics-preview-error"><span>Unable to load analytics right now.</span><button className="secondary-button" type="button" onClick={() => void analyticsQuery.refetch()}><RefreshCw size={14} /> Try again</button></div>}
          {analyticsQuery.data && analyticsQuery.data.total_links === 0 && <div className="analytics-preview-empty">No analytics yet. Create your first link to start building activity.</div>}
          {analyticsQuery.data && analyticsQuery.data.total_links > 0 && (
            <>
              <div className="dashboard-kpi-grid">
                <div><span className="detail-label">Total links</span><strong>{analyticsQuery.data.total_links.toLocaleString()}</strong></div>
                <div><span className="detail-label">Lifetime clicks</span><strong>{analyticsQuery.data.total_clicks.toLocaleString()}</strong></div>
                <div><span className="detail-label">Last activity</span><strong>{formatDate(analyticsQuery.data.last_clicked_at)}</strong></div>
              </div>
              {analyticsQuery.data.top_links.length > 0 && <div className="dashboard-top-links"><span className="detail-label">Top-performing links</span>{analyticsQuery.data.top_links.slice(0, 3).map((link) => <LinkHistoryRow key={link.id} link={link} onCopied={() => showToast('Link copied to clipboard')} />)}</div>}
            </>
          )}
        </section>
      ) : (
        <div className="analytics-hidden-note"><span>Analytics preview is hidden from your dashboard.</span><button className="secondary-button" type="button" onClick={() => setIsVisible(true)}>Show analytics</button></div>
      )}
      <Toast message={toast} />
    </div>
  );
}
