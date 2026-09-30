import { Monitor, Moon, Sun } from 'lucide-react';
import type { Dispatch, SetStateAction } from 'react';

type Theme = 'system' | 'light' | 'dark';

type ThemeToggleProps = {
  theme: Theme;
  setTheme: Dispatch<SetStateAction<Theme>>;
};

export function ThemeToggle({ theme, setTheme }: ThemeToggleProps) {
  const nextTheme: Theme = theme === 'system' ? 'light' : theme === 'light' ? 'dark' : 'system';
  const Icon = theme === 'system' ? Monitor : theme === 'light' ? Sun : Moon;

  return (
    <button
      className="icon-button"
      type="button"
      aria-label={`Theme: ${theme}. Switch to ${nextTheme}`}
      title={`Theme: ${theme}`}
      onClick={() => setTheme(nextTheme)}
    >
      <Icon size={18} strokeWidth={1.8} />
    </button>
  );
}
