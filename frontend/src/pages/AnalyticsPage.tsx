import { Activity, BarChart3, Link2, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAnalyticsSummary } from '../hooks/useAnalyticsSummary';
import { LinkHistoryRow } from '../components/LinkHistoryRow';
import { formatDate } from '../lib/formatDate';

export function AnalyticsPage() {
  const summaryQuery = useAnalyticsSummary();
  const summary = summaryQuery.data;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <div className="page-kicker"><span className="kicker-dot" /> Workspace analytics</div>
          <h1>Analytics</h1>
          <p>See how your short links are performing across their lifetime.</p>
        </div>
        <Link className="primary-button" to="/"><Link2 size={16} /> Create link</Link>
      </div>

      {summaryQuery.isLoading && <div className="analytics-message"><Activity className="spin" size={20} /> Loading analytics</div>}
      {summaryQuery.isError && (
        <div className="analytics-message analytics-error">
          <p>Unable to load analytics right now.</p>
          <button className="secondary-button" type="button" onClick={() => void summaryQuery.refetch()}><RefreshCw size={15} /> Try again</button>
        </div>
      )}
      {summary && summary.total_links === 0 && (
        <div className="empty-state analytics-empty">
          <span className="empty-icon"><BarChart3 size={20} /></span>
          <div><h2>No analytics yet</h2><p>Create your first short link to start building workspace activity.</p><Link className="secondary-button analytics-empty-action" to="/">Create your first link</Link></div>
        </div>
      )}
      {summary && summary.total_links > 0 && (
        <>
          <section className="analytics-kpi-grid" aria-label="Analytics summary">
            <article className="surface-card analytics-kpi"><span className="detail-label">Total links</span><strong>{summary.total_links.toLocaleString()}</strong></article>
            <article className="surface-card analytics-kpi"><span className="detail-label">Lifetime clicks</span><strong>{summary.total_clicks.toLocaleString()}</strong></article>
            <article className="surface-card analytics-kpi"><span className="detail-label">Last activity</span><strong className="analytics-kpi-date">{formatDate(summary.last_clicked_at)}</strong></article>
          </section>
          {summary.total_clicks === 0 && <div className="analytics-note">Your links are ready to share. Analytics will appear after the first visit.</div>}
          <div className="analytics-sections">
            <section className="surface-card links-card" aria-labelledby="top-links-heading">
              <div className="card-heading"><span className="card-icon"><BarChart3 size={18} /></span><div><h2 id="top-links-heading">Top-performing links</h2><p>Ranked by lifetime clicks</p></div></div>
              <div className="link-history-list analytics-list">{summary.top_links.map((link) => <LinkHistoryRow key={link.id} link={link} onCopied={() => undefined} />)}</div>
            </section>
            <section className="surface-card links-card" aria-labelledby="recent-links-heading">
              <div className="card-heading"><span className="card-icon"><Activity size={18} /></span><div><h2 id="recent-links-heading">Recently active links</h2><p>Links with the latest recorded activity</p></div></div>
              {summary.recently_active_links.length > 0 ? <div className="link-history-list analytics-list">{summary.recently_active_links.map((link) => <LinkHistoryRow key={link.id} link={link} onCopied={() => undefined} />)}</div> : <div className="muted-message">No clicks recorded yet.</div>}
            </section>
          </div>
        </>
      )}
    </div>
  );
}