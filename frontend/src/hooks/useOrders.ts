import { useState, useEffect, useCallback } from 'react';
import { Order, OrderCreate, Plant, DistributionCenter } from '../types';

interface UseOrdersState {
  orders: Order[];
  plants: Plant[];
  centers: DistributionCenter[];
  loading: boolean;
  error: string | null;
  creating: boolean;
}

interface UseOrdersReturn extends UseOrdersState {
  fetchOrders: () => Promise<void>;
  createOrder: (order: OrderCreate) => Promise<boolean>;
  refreshOrders: () => void;
  refetch: () => Promise<void>;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const useOrders = (): UseOrdersReturn => {
  const [state, setState] = useState<UseOrdersState>({
    orders: [],
    plants: [],
    centers: [],
    loading: false,
    error: null,
    creating: false,
  });

  const fetchOrders = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const [ordersRes, plantsRes, centersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/orders`),
        fetch(`${API_BASE_URL}/plants`),
        fetch(`${API_BASE_URL}/centers`),
      ]);

      if (!ordersRes.ok) throw new Error(`Failed to fetch orders: ${ordersRes.status}`);
      if (!plantsRes.ok) throw new Error(`Failed to fetch plants: ${plantsRes.status}`);
      if (!centersRes.ok) throw new Error(`Failed to fetch centers: ${centersRes.status}`);

      const [orders, plants, centers] = await Promise.all([
        ordersRes.json() as Promise<Order[]>,
        plantsRes.json() as Promise<Plant[]>,
        centersRes.json() as Promise<DistributionCenter[]>,
      ]);

      setState(prev => ({ ...prev, orders, plants, centers, loading: false }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState(prev => ({ ...prev, error: errorMessage, loading: false }));
    }
  }, []);

  const createOrder = useCallback(async (orderData: OrderCreate): Promise<boolean> => {
    setState(prev => ({ ...prev, creating: true, error: null }));

    try {
      const response = await fetch(`${API_BASE_URL}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Failed to create order: ${response.status}`);
      }

      const newOrder: Order = await response.json();
      setState(prev => ({
        ...prev,
        orders: [...prev.orders, newOrder],
        creating: false,
      }));

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create order';
      setState(prev => ({ ...prev, error: errorMessage, creating: false }));
      return false;
    }
  }, []);

  const refreshOrders = useCallback(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return {
    ...state,
    fetchOrders,
    createOrder,
    refreshOrders,
    refetch: fetchOrders,
  };
};
