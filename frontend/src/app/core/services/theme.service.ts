import { Injectable, computed, signal } from '@angular/core';

export type ThemeMode = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'iiis-theme';

  readonly theme = signal<ThemeMode>(this.initialTheme());
  readonly isDark = computed(() => this.theme() === 'dark');

  constructor() {
    this.applyTheme(this.theme());
  }

  setTheme(theme: ThemeMode): void {
    this.theme.set(theme);
    this.applyTheme(theme);

    try {
      window.localStorage.setItem(this.storageKey, theme);
    } catch {
      // Ignore storage failures; the current page can still switch theme.
    }
  }

  toggle(): void {
    this.setTheme(this.isDark() ? 'light' : 'dark');
  }

  private initialTheme(): ThemeMode {
    try {
      const stored = window.localStorage.getItem(this.storageKey);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }

      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  }

  private applyTheme(theme: ThemeMode): void {
    const root = document.documentElement;
    root.dataset['theme'] = theme;
    root.classList.toggle('dark-theme', theme === 'dark');
    root.classList.toggle('light-theme', theme === 'light');
    root.style.colorScheme = theme;
    window.dispatchEvent(new CustomEvent<ThemeMode>('iiis-theme-change', { detail: theme }));
  }
}
