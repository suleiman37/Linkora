import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useTheme } from '../hooks/useTheme';

export function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  return (
    <div className="app-shell">
      <Topbar menuOpen={menuOpen} onMenuToggle={() => setMenuOpen((open) => !open)} theme={theme} setTheme={setTheme} />
      <div className={`shell-body${menuOpen ? ' shell-body-menu-open' : ''}`}>
        <Sidebar />
        <main className="main-content"><Outlet /></main>
      </div>
    </div>
  );
}
