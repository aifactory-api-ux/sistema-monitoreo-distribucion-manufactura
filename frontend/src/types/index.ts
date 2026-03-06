// TypeScript interfaces matching Pydantic models for DistroViz v3

// Enums
export enum OrderStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled'
}

// Base interfaces
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at?: string | null;
}

// Plant interfaces
export interface PlantBase {
  name: string;
  location: string;
  capacity: number;
  is_active: boolean;
}

export interface PlantCreate extends PlantBase {}

export interface PlantUpdate {
  name?: string;
  location?: string;
  capacity?: number;
  is_active?: boolean;
}

export interface Plant extends PlantBase, BaseEntity {}

// Distribution Center interfaces
export interface DistributionCenterBase {
  name: string;
  region: string;
  storage_capacity: number;
  is_active: boolean;
}

export interface DistributionCenterCreate extends DistributionCenterBase {}

export interface DistributionCenterUpdate {
  name?: string;
  region?: string;
  storage_capacity?: number;
  is_active?: boolean;
}

export interface DistributionCenter extends DistributionCenterBase, BaseEntity {}

// Order interfaces
export interface OrderBase {
  plant_id: number;
  center_id: number;
  quantity: number;
  status: OrderStatus;
  order_date: string; // ISO date string
  expected_delivery_date?: string | null; // ISO date string
  actual_delivery_date?: string | null; // ISO date string
  notes?: string | null;
}

export interface OrderCreate extends OrderBase {}

export interface OrderUpdate {
  plant_id?: number;
  center_id?: number;
  quantity?: number;
  status?: OrderStatus;
  order_date?: string;
  expected_delivery_date?: string | null;
  actual_delivery_date?: string | null;
  notes?: string | null;
}

export interface Order extends OrderBase, BaseEntity {
  plant?: Plant | null;
  distribution_center?: DistributionCenter | null;
}

// Dashboard interfaces
export interface OrderTrend {
  date: string;
  orders: number;
  delivered?: number;
  fulfillment_rate?: number;
}

export interface StatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface DashboardSummary {
  total_orders: number;
  fulfillment_rate: number;
  avg_delivery_days: number;
  active_plants: number;
  active_centers?: number;
  recent_orders?: number;
  orders_by_status: Record<string, number>;
  status_distribution?: Record<string, number>;
  orders_trend: OrderTrend[];
}

// Health check interface
export interface HealthCheck {
  status: string;
  version: string;
  database_connected: boolean;
  timestamp: string;
}

// Error response interface
export interface ErrorResponse {
  detail: string;
  error_code?: string | null;
  timestamp: string;
}

// API response wrappers
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Form interfaces for UI components
export interface OrderFormData {
  plant_id: string; // String for form handling, converted to number
  center_id: string; // String for form handling, converted to number
  quantity: string; // String for form handling, converted to number
  order_date: string;
  expected_delivery_date?: string;
  notes?: string;
}

export interface FilterOptions {
  status?: OrderStatus[];
  plant_ids?: number[];
  center_ids?: number[];
  date_from?: string;
  date_to?: string;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

// Chart data interfaces
export interface ChartDataPoint {
  name: string;
  value: number;
  label?: string;
  color?: string;
}

export interface LineChartDataPoint {
  date: string;
  orders: number;
  delivered?: number;
  pending?: number;
  processing?: number;
  shipped?: number;
  cancelled?: number;
}

export interface PieChartDataPoint {
  name: string;
  value: number;
  percentage: number;
  color?: string;
}

// UI State interfaces
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface TableState {
  page: number;
  pageSize: number;
  sortField?: string;
  sortDirection?: 'asc' | 'desc';
  filters?: FilterOptions;
}

export interface ModalState {
  isOpen: boolean;
  mode: 'create' | 'edit' | 'view';
  data?: any;
}

// Navigation interfaces
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  active?: boolean;
}

// Theme interfaces
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  background: string;
  surface: string;
  text: string;
}

// Responsive breakpoints
export interface Breakpoints {
  xs: number; // 0px
  sm: number; // 640px
  md: number; // 768px
  lg: number; // 1024px
  xl: number; // 1280px
  '2xl': number; // 1536px
}

// Utility types
export type OrderStatusColor = {
  [K in OrderStatus]: string;
};

export type OrderStatusIcon = {
  [K in OrderStatus]: string;
};

// Constants
export const ORDER_STATUS_COLORS: OrderStatusColor = {
  [OrderStatus.PENDING]: '#f59e0b', // amber-500
  [OrderStatus.PROCESSING]: '#3b82f6', // blue-500
  [OrderStatus.SHIPPED]: '#8b5cf6', // violet-500
  [OrderStatus.DELIVERED]: '#10b981', // emerald-500
  [OrderStatus.CANCELLED]: '#ef4444', // red-500
};

export const ORDER_STATUS_ICONS: OrderStatusIcon = {
  [OrderStatus.PENDING]: 'clock',
  [OrderStatus.PROCESSING]: 'settings',
  [OrderStatus.SHIPPED]: 'truck',
  [OrderStatus.DELIVERED]: 'check-circle',
  [OrderStatus.CANCELLED]: 'x-circle',
};

export const BREAKPOINTS: Breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

// Type guards
export function isOrder(obj: any): obj is Order {
  return (
    obj &&
    typeof obj.id === 'number' &&
    typeof obj.plant_id === 'number' &&
    typeof obj.center_id === 'number' &&
    typeof obj.quantity === 'number' &&
    Object.values(OrderStatus).includes(obj.status) &&
    typeof obj.order_date === 'string'
  );
}

export function isPlant(obj: any): obj is Plant {
  return (
    obj &&
    typeof obj.id === 'number' &&
    typeof obj.name === 'string' &&
    typeof obj.location === 'string' &&
    typeof obj.capacity === 'number' &&
    typeof obj.is_active === 'boolean'
  );
}

export function isDistributionCenter(obj: any): obj is DistributionCenter {
  return (
    obj &&
    typeof obj.id === 'number' &&
    typeof obj.name === 'string' &&
    typeof obj.region === 'string' &&
    typeof obj.storage_capacity === 'number' &&
    typeof obj.is_active === 'boolean'
  );
}

export function isDashboardSummary(obj: any): obj is DashboardSummary {
  return (
    obj &&
    typeof obj.total_orders === 'number' &&
    typeof obj.fulfillment_rate === 'number' &&
    typeof obj.avg_delivery_days === 'number' &&
    typeof obj.active_plants === 'number' &&
    typeof obj.orders_by_status === 'object' &&
    Array.isArray(obj.orders_trend)
  );
}

