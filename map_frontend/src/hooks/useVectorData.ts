import { useState, useEffect, useCallback, useRef } from "react";

interface VectorDataState {
  loading: boolean;
  error: string | null;
  featureCount: number;
}

interface Viewport {
  longitude: number;
  latitude: number;
  zoom: number;
}

const API_BASE = (import.meta as { env?: Record<string, string> }).env?.VITE_API_URL ?? "";

/**
 * Custom hook that manages fetching and caching spatial vector tile metadata
 * as the user pans and zooms the map.
 *
 * @param viewport - Current map viewport.
 * @param selectedDate - ISO-8601 date string to scope the request.
 * @returns Loading state, error, and derived feature count for the viewport.
 */
export function useVectorData(viewport: Viewport, selectedDate: string): VectorDataState {
  const [state, setState] = useState<VectorDataState>({
    loading: false,
    error: null,
    featureCount: 0,
  });

  // Simple cache keyed by zoom + rounded coordinates + date.
  const cache = useRef<Map<string, number>>(new Map());
  const abortRef = useRef<AbortController | null>(null);

  const fetchStats = useCallback(async () => {
    const { longitude, latitude, zoom } = viewport;
    const cacheKey = `${Math.round(zoom)},${longitude.toFixed(2)},${latitude.toFixed(2)},${selectedDate}`;

    if (cache.current.has(cacheKey)) {
      setState({ loading: false, error: null, featureCount: cache.current.get(cacheKey)! });
      return;
    }

    // Cancel any in-flight request.
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const url = `${API_BASE}/temporal/history?lat=${latitude.toFixed(4)}&lon=${longitude.toFixed(4)}`;
      const resp = await fetch(url, { signal: abortRef.current.signal });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();
      const count: number = data?.events?.length ?? 0;

      cache.current.set(cacheKey, count);
      setState({ loading: false, error: null, featureCount: count });
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      setState({ loading: false, error: String(err), featureCount: 0 });
    }
  }, [viewport, selectedDate]);

  useEffect(() => {
    fetchStats();
    return () => abortRef.current?.abort();
  }, [fetchStats]);

  return state;
}
