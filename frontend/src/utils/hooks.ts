'use client'; 

import { useCallback, useRef } from 'react';

export function useDebounce(callback: (...args: any[]) => void, delay: number) {
  const timeoutRef = useRef<NodeJS.Timeout>(null);

  const debouncedFunction = useCallback((...args: any[]) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    }, [callback, delay]);

    const cancel = useCallback(() => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    }, []);

  return [debouncedFunction, cancel] as const;
}

export function useThrottle(callback: (...args: any[]) => void, delay: number) {
  const lastCallRef = useRef<number>(0);

  const throttledFunction = useCallback((...args: any[]) => {
    const now = Date.now();

    if (now - lastCallRef.current >= delay) {
      lastCallRef.current = now;
      callback(...args);
    }
  }, [callback, delay]);

  return throttledFunction;
}
