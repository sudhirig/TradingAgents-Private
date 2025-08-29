import { useCallback, useMemo, useRef } from 'react';

// Debounce hook for performance optimization
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => callback(...args), delay);
    }) as T,
    [callback, delay]
  );
}

// Throttle hook for performance optimization
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastRun = useRef(Date.now());

  return useCallback(
    ((...args: Parameters<T>) => {
      if (Date.now() - lastRun.current >= delay) {
        callback(...args);
        lastRun.current = Date.now();
      }
    }) as T,
    [callback, delay]
  );
}

// Virtual scrolling utilities
export interface VirtualScrollOptions {
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
}

export function useVirtualScroll<T>(
  items: T[],
  options: VirtualScrollOptions
) {
  const { itemHeight, containerHeight, overscan = 5 } = options;

  return useMemo(() => {
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const totalHeight = items.length * itemHeight;

    const getVisibleRange = (scrollTop: number) => {
      const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
      const end = Math.min(
        items.length - 1,
        start + visibleCount + overscan * 2
      );
      return { start, end };
    };

    const getVisibleItems = (scrollTop: number) => {
      const { start, end } = getVisibleRange(scrollTop);
      return items.slice(start, end + 1).map((item, index) => ({
        item,
        index: start + index,
        top: (start + index) * itemHeight,
      }));
    };

    return {
      totalHeight,
      getVisibleItems,
      getVisibleRange,
    };
  }, [items, itemHeight, containerHeight, overscan]);
}

// Message batching for WebSocket performance
export class MessageBatcher<T> {
  private batch: T[] = [];
  private timeoutId: NodeJS.Timeout | null = null;
  private readonly batchSize: number;
  private readonly flushInterval: number;
  private readonly onFlush: (batch: T[]) => void;

  constructor(
    onFlush: (batch: T[]) => void,
    batchSize = 10,
    flushInterval = 100
  ) {
    this.onFlush = onFlush;
    this.batchSize = batchSize;
    this.flushInterval = flushInterval;
  }

  add(item: T) {
    this.batch.push(item);

    if (this.batch.length >= this.batchSize) {
      this.flush();
    } else if (!this.timeoutId) {
      this.timeoutId = setTimeout(() => this.flush(), this.flushInterval);
    }
  }

  flush() {
    if (this.batch.length > 0) {
      this.onFlush([...this.batch]);
      this.batch = [];
    }

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }

  destroy() {
    this.flush();
  }
}

// Memory management utilities
export function createMemoryManager() {
  const cache = new Map<string, any>();
  const maxSize = 1000;

  return {
    get: (key: string) => cache.get(key),
    set: (key: string, value: any) => {
      if (cache.size >= maxSize) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      cache.set(key, value);
    },
    delete: (key: string) => cache.delete(key),
    clear: () => cache.clear(),
    size: () => cache.size,
  };
}

// Performance monitoring
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  startTiming(label: string): () => void {
    const start = performance.now();
    return () => {
      const duration = performance.now() - start;
      this.recordMetric(label, duration);
    };
  }

  recordMetric(label: string, value: number) {
    if (!this.metrics.has(label)) {
      this.metrics.set(label, []);
    }
    const values = this.metrics.get(label)!;
    values.push(value);
    
    // Keep only last 100 measurements
    if (values.length > 100) {
      values.shift();
    }
  }

  getMetrics(label: string) {
    const values = this.metrics.get(label) || [];
    if (values.length === 0) return null;

    const sum = values.reduce((a, b) => a + b, 0);
    const avg = sum / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    return { avg, min, max, count: values.length };
  }

  getAllMetrics() {
    const result: Record<string, any> = {};
    for (const [label] of this.metrics) {
      result[label] = this.getMetrics(label);
    }
    return result;
  }
}

export const performanceMonitor = new PerformanceMonitor();
