import React, { createContext, useContext, useEffect, useState } from 'react';
import { Theme, ThemeConfig } from '../types';
import { getStorageItem, setStorageItem, removeStorageItem } from '../utils';

const ThemeContext = createContext<ThemeConfig | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
}

function getStoredTheme(): Theme | null {
  const stored = getStorageItem('ridemeta-theme');
  return stored === 'light' || stored === 'dark' ? stored : null;
}

function resolveInitialTheme(defaultTheme: Theme): Theme {
  if (typeof window === 'undefined') {
    return defaultTheme;
  }

  const stored = getStoredTheme();
  if (stored) return stored;

  const mediaQuery = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-color-scheme: dark)')
    : null;

  const prefersDark = mediaQuery ? mediaQuery.matches : defaultTheme === 'dark';
  return prefersDark ? 'dark' : defaultTheme;
}

export function ThemeProvider({ children, defaultTheme = 'dark' }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => resolveInitialTheme(defaultTheme));
  const [hasUserPreference, setHasUserPreference] = useState<boolean>(() => getStoredTheme() !== null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement;
      const nextTheme = theme === 'dark' ? 'dark' : 'light';

      root.classList.remove('light', 'dark');
      root.classList.add(nextTheme);
      root.dataset.theme = nextTheme;
      root.style.colorScheme = nextTheme;

      if (hasUserPreference) {
        setStorageItem('ridemeta-theme', nextTheme);
      } else {
        removeStorageItem('ridemeta-theme');
      }
    }
  }, [theme, hasUserPreference]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const media = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (event: MediaQueryListEvent) => {
        if (!hasUserPreference) {
          setThemeState(event.matches ? 'dark' : 'light');
        }
      };

      media.addEventListener('change', handleChange);
      return () => media.removeEventListener('change', handleChange);
    }
    return undefined;
  }, [hasUserPreference]);

  const setTheme = (newTheme: Theme) => {
    setHasUserPreference(true);
    setThemeState(newTheme === 'dark' ? 'dark' : 'light');
  };

  const toggleTheme = () => {
    setHasUserPreference(true);
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const value = {
    theme,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
