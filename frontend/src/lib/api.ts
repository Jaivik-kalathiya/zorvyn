import { API_BASE_URL } from "@/lib/config";
import type {
  DashboardSummary,
  FinanceEntryType,
  FinanceRecord,
  PaginatedResponse,
  ScheduledReport,
  TokenResponse,
  User,
  UserRole,
  ApiErrorBody,
} from "@/lib/types";

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  token?: string;
  body?: unknown;
  params?: Record<string, string | number | undefined | null>;
}

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: unknown;

  constructor(
    message: string,
    status: number,
    code?: string,
    details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);

  if (options.params) {
    for (const [key, value] of Object.entries(options.params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const response = await fetch(url.toString(), {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    let payload: ApiErrorBody | null = null;
    try {
      payload = (await response.json()) as ApiErrorBody;
    } catch {
      payload = null;
    }

    throw new ApiError(
      payload?.error?.message ?? "Request failed",
      response.status,
      payload?.error?.code,
      payload?.error?.details,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return undefined as T;
}

function extractFilename(
  contentDisposition: string | null,
  fallback: string,
): string {
  const match = /filename="?([^";]+)"?/i.exec(contentDisposition ?? "");
  return match?.[1] ?? fallback;
}

async function requestBlob(
  path: string,
  options: RequestOptions,
  fallbackFilename: string,
): Promise<{ blob: Blob; filename: string }> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (options.params) {
    for (const [key, value] of Object.entries(options.params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const response = await fetch(url.toString(), {
    method: options.method ?? "GET",
    headers: {
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let payload: ApiErrorBody | null = null;
    try {
      payload = (await response.json()) as ApiErrorBody;
    } catch {
      payload = null;
    }

    throw new ApiError(
      payload?.error?.message ?? "Request failed",
      response.status,
      payload?.error?.code,
      payload?.error?.details,
    );
  }

  return {
    blob: await response.blob(),
    filename: extractFilename(
      response.headers.get("content-disposition"),
      fallbackFilename,
    ),
  };
}

export function bootstrapAdmin(input: {
  email: string;
  full_name: string;
  password: string;
}): Promise<User> {
  return request<User>("/auth/bootstrap-admin", {
    method: "POST",
    body: input,
  });
}

export function login(input: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", { method: "POST", body: input });
}

export function logout(
  token: string,
  payload: { refresh_token?: string },
): Promise<void> {
  return request<void>("/auth/logout", {
    method: "POST",
    token,
    body: payload,
  });
}

export function getMe(token: string): Promise<User> {
  return request<User>("/auth/me", { token });
}

export function getDashboardSummary(
  token: string,
  filters?: {
    fromDate?: string;
    toDate?: string;
  },
): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary", {
    token,
    params: {
      from_date: filters?.fromDate,
      to_date: filters?.toDate,
    },
  });
}

export function listRecords(
  token: string,
  params: {
    page: number;
    pageSize: number;
    entryType?: FinanceEntryType;
    category?: string;
    fromDate?: string;
    toDate?: string;
    search?: string;
  },
): Promise<PaginatedResponse<FinanceRecord>> {
  return request<PaginatedResponse<FinanceRecord>>("/records", {
    token,
    params: {
      page: params.page,
      page_size: params.pageSize,
      entry_type: params.entryType,
      category: params.category,
      from_date: params.fromDate,
      to_date: params.toDate,
      search: params.search,
    },
  });
}

export function exportRecordsCsv(
  token: string,
  params: {
    entryType?: FinanceEntryType;
    category?: string;
    fromDate?: string;
    toDate?: string;
    search?: string;
  },
): Promise<{ blob: Blob; filename: string }> {
  return requestBlob(
    "/records/export/csv",
    {
      token,
      params: {
        entry_type: params.entryType,
        category: params.category,
        from_date: params.fromDate,
        to_date: params.toDate,
        search: params.search,
      },
    },
    "finance-records.csv",
  );
}

export function createRecord(
  token: string,
  payload: {
    amount: number;
    entry_type: FinanceEntryType;
    category: string;
    entry_date: string;
    notes?: string;
  },
): Promise<FinanceRecord> {
  return request<FinanceRecord>("/records", {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteRecord(
  token: string,
  recordId: number,
): Promise<FinanceRecord> {
  return request<FinanceRecord>(`/records/${recordId}`, {
    method: "DELETE",
    token,
  });
}

export function listUsers(
  token: string,
  params: { page: number; pageSize: number; search?: string },
): Promise<PaginatedResponse<User>> {
  return request<PaginatedResponse<User>>("/users", {
    token,
    params: {
      page: params.page,
      page_size: params.pageSize,
      search: params.search,
    },
  });
}

export function createUser(
  token: string,
  payload: {
    email: string;
    full_name: string;
    password: string;
    role: UserRole;
  },
): Promise<User> {
  return request<User>("/users", {
    method: "POST",
    token,
    body: payload,
  });
}

export function listReports(
  token: string,
  params: { page: number; pageSize: number },
): Promise<PaginatedResponse<ScheduledReport>> {
  return request<PaginatedResponse<ScheduledReport>>("/reports", {
    token,
    params: {
      page: params.page,
      page_size: params.pageSize,
    },
  });
}

export function runReportNow(
  token: string,
  payload: { report_name: string; lookback_days: number },
): Promise<ScheduledReport> {
  return request<ScheduledReport>("/reports/run", {
    method: "POST",
    token,
    body: payload,
  });
}

export function exportReportCsv(
  token: string,
  reportId: number,
): Promise<{ blob: Blob; filename: string }> {
  return requestBlob(
    `/reports/${reportId}/csv`,
    { token },
    `report-${reportId}.csv`,
  );
}
