import { BarChart3, Check, Settings2 } from 'lucide-react';
import { useAnalyticsVisibility } from '../hooks/useAnalyticsVisibility';

export function SettingsPage() {
  const { isVisible, setIsVisible } = useAnalyticsVisibility();

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <div className="page-kicker"><span className="kicker-dot" /> Workspace settings</div>
          <h1>Settings</h1>
          <p>Choose which workspace information appears on your dashboard.</p>
        </div>
      </div>

      <section className="surface-card settings-card" aria-labelledby="analytics-setting-heading">
        <div className="card-heading">
          <span className="card-icon"><BarChart3 size={18} /></span>
          <div>
            <h2 id="analytics-setting-heading">Analytics display</h2>
            <p>Control the analytics preview on your dashboard.</p>
          </div>
        </div>
        <label className="settings-toggle-row">
          <span className="settings-toggle-copy">
            <strong>Show analytics on dashboard</strong>
            <span>{isVisible ? 'The analytics preview is currently visible.' : 'The analytics preview is currently hidden.'}</span>
          </span>
          <input
            className="settings-toggle"
            type="checkbox"
            checked={isVisible}
            onChange={(event) => setIsVisible(event.target.checked)}
            aria-label="Show analytics on dashboard"
          />
        </label>
        <div className={`settings-status${isVisible ? ' settings-status-visible' : ''}`} role="status">
          {isVisible ? <><Check size={15} /> Analytics preview is visible on the dashboard.</> : <><Settings2 size={15} /> Analytics preview is hidden from the dashboard.</>}
        </div>
      </section>
    </div>
  );
}