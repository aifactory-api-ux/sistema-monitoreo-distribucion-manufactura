import { useState, useEffect, useMemo } from 'react';
import { DashboardSummary } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const useDashboard = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('[useDashboard] Hook mounted, starting fetch');
    const fetchDashboard = async () => {
      try {
        console.log('[useDashboard] Fetching from:', `${API_BASE_URL}/dashboard/summary`);
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/dashboard/summary`);
        console.log('[useDashboard] Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[useDashboard] Data received:', result);
        setData(result);
        setError(null);
        console.log('[useDashboard] State updated, loading should be false now');
      } catch (err) {
        console.error('[useDashboard] Error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setData(null);
      } finally {
        console.log('[useDashboard] Setting loading to false');
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  const result = useMemo(() => ({ data, loading, error }), [data, loading, error]);
  console.log('[useDashboard] Returning from hook:', result);
  return result;
};