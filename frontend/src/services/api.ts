import { Plant, DistributionCenter, Order, DashboardSummary, OrderCreate } from '../types';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || '/api';
  }

  private async fetchWithErrorHandling<T>(url: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = Array.isArray(errorData.detail) 
              ? errorData.detail.map((err: any) => err.msg || err).join(', ')
              : errorData.detail;
          }
        } catch {
          // If we can't parse the error response, use the default message
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to the server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async getPlants(): Promise<Plant[]> {
    return this.fetchWithErrorHandling<Plant[]>('/plants');
  }

  async getDistributionCenters(): Promise<DistributionCenter[]> {
    return this.fetchWithErrorHandling<DistributionCenter[]>('/centers');
  }

  async getOrders(): Promise<Order[]> {
    return this.fetchWithErrorHandling<Order[]>('/orders');
  }

  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.fetchWithErrorHandling<DashboardSummary>('/dashboard/summary');
  }

  async createOrder(orderData: OrderCreate): Promise<Order> {
    return this.fetchWithErrorHandling<Order>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  // Health check method for testing connectivity
  async healthCheck(): Promise<{ status: string }> {
    try {
      return this.fetchWithErrorHandling<{ status: string }>('/health');
    } catch (error) {
      throw new Error('Backend health check failed');
    }
  }

  // Utility method to test all endpoints
  async testAllEndpoints(): Promise<{
    plants: boolean;
    centers: boolean;
    orders: boolean;
    dashboard: boolean;
  }> {
    const results = {
      plants: false,
      centers: false,
      orders: false,
      dashboard: false,
    };

    try {
      await this.getPlants();
      results.plants = true;
    } catch (error) {
      console.error('Plants endpoint failed:', error);
    }

    try {
      await this.getDistributionCenters();
      results.centers = true;
    } catch (error) {
      console.error('Distribution centers endpoint failed:', error);
    }

    try {
      await this.getOrders();
      results.orders = true;
    } catch (error) {
      console.error('Orders endpoint failed:', error);
    }

    try {
      await this.getDashboardSummary();
      results.dashboard = true;
    } catch (error) {
      console.error('Dashboard endpoint failed:', error);
    }

    return results;
  }
}

export const apiService = new ApiService();
export default apiService;