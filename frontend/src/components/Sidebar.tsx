import { BarChart3, FileText, LayoutDashboard, Settings2 } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const items: Array<{ label: string; icon: typeof LayoutDashboard; to: string; disabled?: boolean }> = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { label: 'Links', icon: FileText, to: '/links' },
  { label: 'Analytics', icon: BarChart3, to: '/analytics' },
  { label: 'Settings', icon: Settings2, to: '/settings' },
];

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <nav>
        {items.map(({ label, icon: Icon, to, disabled }) =>
          disabled ? (
            <span className="nav-item nav-item-disabled" key={label} title="Coming soon">
              <Icon size={18} strokeWidth={1.8} />
              {label}
              <span className="nav-soon">Soon</span>
            </span>
          ) : (
            <NavLink className={({ isActive }) => `nav-item${isActive ? ' nav-item-active' : ''}`} to={to} key={label}>
              <Icon size={18} strokeWidth={1.8} />
              {label}
            </NavLink>
          ),
        )}
      </nav>
      <div className="sidebar-footer">
        <span className="sidebar-kicker">SHORTY WORKSPACE</span>
        <p>Simple links. Clear reach.</p>
      </div>
    </aside>
  );
}
