export type UserRole = "viewer" | "analyst" | "admin";
export type FinanceEntryType = "income" | "expense";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FinanceRecord {
  id: number;
  amount: string;
  entry_type: FinanceEntryType;
  category: string;
  entry_date: string;
  notes: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface CategoryTotal {
  category: string;
  total: string;
}

export interface TrendPoint {
  period: string;
  income: string;
  expense: string;
}

export interface RecentActivityItem {
  id: number;
  amount: string;
  entry_type: FinanceEntryType;
  category: string;
  entry_date: string;
}

export interface DashboardSummary {
  total_income: string;
  total_expenses: string;
  net_balance: string;
  category_totals: CategoryTotal[];
  trends: TrendPoint[];
  recent_activity: RecentActivityItem[];
}

export interface ScheduledReport {
  id: number;
  report_name: string;
  period_start: string;
  period_end: string;
  total_income: string;
  total_expenses: string;
  net_balance: string;
  record_count: number;
  payload?: {
    category_totals?: Array<{ category: string; total: string }>;
  };
  generated_at: string;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PageMeta;
}

export interface ApiErrorBody {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
}
