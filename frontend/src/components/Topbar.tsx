import { Link, Menu, X } from 'lucide-react';
import type { Dispatch, SetStateAction } from 'react';
import { NavLink } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

type TopbarProps = {
  menuOpen: boolean;
  onMenuToggle: () => void;
  theme: 'system' | 'light' | 'dark';
  setTheme: Dispatch<SetStateAction<'system' | 'light' | 'dark'>>;
};

export function Topbar({ menuOpen, onMenuToggle, theme, setTheme }: TopbarProps) {
  return (
    <header className="topbar">
      <NavLink className="brand" to="/" aria-label="Shorty dashboard">
        <span className="brand-mark"><Link size={18} strokeWidth={2.2} /></span>
        <span>Shorty</span>
      </NavLink>
      <nav className="top-nav" aria-label="Top navigation">
        <NavLink className={({ isActive }) => `top-nav-link${isActive ? ' top-nav-link-active' : ''}`} to="/">Dashboard</NavLink>
        <NavLink className={({ isActive }) => `top-nav-link${isActive ? ' top-nav-link-active' : ''}`} to="/links">Links</NavLink>
        <NavLink className={({ isActive }) => `top-nav-link${isActive ? ' top-nav-link-active' : ''}`} to="/analytics">Analytics</NavLink>
        <a className="top-nav-link" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API Docs</a>
      </nav>
      <div className="top-actions">
        <ThemeToggle theme={theme} setTheme={setTheme} />
        <button className="mobile-menu-button icon-button" type="button" aria-label={menuOpen ? 'Close navigation' : 'Open navigation'} onClick={onMenuToggle}>
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="avatar" aria-label="Workspace profile">S</div>
      </div>
    </header>
  );
}
