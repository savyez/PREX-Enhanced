import { useCallback, useEffect, useRef, useState } from 'react';
import { chart_data } from '../utils/api.js';

const fetchWithTimeout = async (coinName, days, timeoutMs = 8000) => {
  return Promise.race([
    chart_data(coinName, days),
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Trend request timed out.')), timeoutMs);
    }),
  ]);
};

const normalizePoints = (points) =>
  (points || [])
    .map((point) => ({
      ...point,
      price: Number(point.price),
    }))
    .filter((point) => Number.isFinite(point.price));

export function useSparklineCache(items, keyField = 'coin_name') {
  const [cache, setCache] = useState({});
  const cacheRef = useRef({});
  const getKey = useCallback((item) => {
    const value = item?.[keyField];
    if (value === null || value === undefined) {
      return '';
    }

    return String(value).trim();
  }, [keyField]);

  useEffect(() => {
    let isActive = true;

    const load = async () => {
      if (!items.length) {
        return;
      }

      const missingItems = items.filter((item) => {
        const key = getKey(item);
        return key && !cacheRef.current[key];
      });
      if (!missingItems.length) {
        return;
      }

      setCache((current) => {
        const next = { ...current };
        missingItems.forEach((item) => {
          const key = getKey(item);
          if (!key) {
            return;
          }
          next[key] = {
            data: next[key]?.data || [],
            loading: true,
            error: null,
          };
        });
        cacheRef.current = next;
        return next;
      });

      const results = await Promise.allSettled(
        missingItems.map(async (item) => {
          const key = getKey(item);
          if (!key) {
            throw new Error('Trend unavailable');
          }
          const response = await fetchWithTimeout(key, 7);
          return { key, data: normalizePoints(response.chart_data) };
        })
      );

      if (!isActive) {
        return;
      }

      setCache((current) => {
        const next = { ...current };

        results.forEach((result, index) => {
          const item = missingItems[index];
          const key = getKey(item);
          if (!key) {
            return;
          }

          if (result.status === 'fulfilled') {
            next[key] = {
              data: result.value.data,
              loading: false,
              error: null,
            };
          } else {
            next[key] = {
              data: [],
              loading: false,
              error: result.reason?.message || 'Trend unavailable',
            };
          }
        });

        cacheRef.current = next;
        return next;
      });
    };

    load();

    return () => {
      isActive = false;
    };
  }, [items, getKey]);

  useEffect(() => {
    cacheRef.current = cache;
  }, [cache]);

  const resetCache = () => {
    cacheRef.current = {};
    setCache({});
  };

  return { cache, resetCache };
}
