import { useState } from 'react';

const STORAGE_KEY = 'shorty.analytics.dashboard-visible';

function readVisibility(): boolean {
  if (typeof window === 'undefined') return true;
  return window.localStorage.getItem(STORAGE_KEY) !== 'false';
}

export function useAnalyticsVisibility() {
  const [isVisible, setIsVisible] = useState(readVisibility);

  function updateVisibility(nextValue: boolean) {
    setIsVisible(nextValue);
    window.localStorage.setItem(STORAGE_KEY, String(nextValue));
  }

  return {
    isVisible,
    setIsVisible: updateVisibility,
  };
}