import { BarChart3, LoaderCircle } from 'lucide-react';
import type { LinkStatisticsResponse } from '../api/types';
import { formatDate } from '../lib/formatDate';

type StatisticsCardProps = {
  stats: LinkStatisticsResponse | undefined;
  isLoading: boolean;
  isError: boolean;
};

export function StatisticsCard({ stats, isLoading, isError }: StatisticsCardProps) {
  return (
    <section className="surface-card statistics-card" aria-labelledby="stats-heading">
      <div className="card-heading"><span className="card-icon"><BarChart3 size={18} /></span><div><h2 id="stats-heading">Link reach</h2><p>Performance for your latest link</p></div></div>
      {isLoading && <div className="stats-loading"><LoaderCircle className="spin" size={20} /> Loading statistics</div>}
      {isError && !isLoading && <p className="muted-message">Statistics are temporarily unavailable.</p>}
      {stats && !isLoading && (
        <div className="stats-grid">
          <div className="stat-cell"><span className="detail-label">Clicks</span><strong className="stat-number">{stats.click_count.toLocaleString()}</strong></div>
          <div className="stat-cell"><span className="detail-label">Last clicked</span><strong className="stat-date">{formatDate(stats.last_clicked_at)}</strong></div>
        </div>
      )}
    </section>
  );
}
