import type {
  ApiEnvelope,
  AttendanceRecord,
  AuthUser,
  Branch,
  Client,
  ClientContract,
  ClientSite,
  Company,
  DashboardAttendanceReport,
  DashboardOpsSummary,
  Department,
  Employee,
  EmployeeDeployment,
  LoginResponse,
  Position,
  ShiftType,
  SitePost,
  WorkSchedule,
} from "@/lib/types";

const apiBaseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1"
).replace(/\/$/, "");

type RequestOptions = {
  method?: "GET" | "POST" | "PUT";
  token?: string;
  body?: unknown;
};

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

function buildUrl(path: string) {
  return `${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

function extractErrorMessage(payload: unknown, fallback: string) {
  if (payload && typeof payload === "object") {
    if ("message" in payload && typeof payload.message === "string") {
      return payload.message;
    }
    if ("detail" in payload && typeof payload.detail === "string") {
      return payload.detail;
    }
  }
  return fallback;
}

async function request<T>(path: string, options: RequestOptions = {}) {
  const headers = new Headers({
    Accept: "application/json",
  });

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(buildUrl(path), {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  let payload: ApiEnvelope<T> | Record<string, unknown> | null = null;
  try {
    payload = (await response.json()) as ApiEnvelope<T>;
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new ApiError(
      extractErrorMessage(payload, `Request gagal dengan status ${response.status}.`),
      response.status,
      payload,
    );
  }

  if (!payload || typeof payload !== "object" || !("data" in payload)) {
    throw new ApiError("Response API tidak sesuai kontrak.", response.status, payload);
  }

  return payload.data as T;
}

export const api = {
  auth: {
    login: (payload: { identifier: string; password: string }) =>
      request<LoginResponse>("/auth/login", {
        method: "POST",
        body: payload,
      }),
    me: (token: string) => request<AuthUser>("/auth/me", { token }),
    logout: (token: string) =>
      request<unknown>("/auth/logout", {
        method: "POST",
        token,
      }),
  },
  organization: {
    listCompanies: (token: string) =>
      request<Company[]>("/organization/companies", { token }),
    listBranches: (token: string) =>
      request<Branch[]>("/organization/branches", { token }),
    listDepartments: (token: string) =>
      request<Department[]>("/organization/departments", { token }),
    listPositions: (token: string) =>
      request<Position[]>("/organization/positions", { token }),
  },
  masterHr: {
    listEmployees: (token: string) =>
      request<Employee[]>("/master-hr/employees", { token }),
    createEmployee: (token: string, payload: Record<string, unknown>) =>
      request<Employee>("/master-hr/employees", {
        method: "POST",
        token,
        body: payload,
      }),
  },
  clientContract: {
    listClients: (token: string) =>
      request<Client[]>("/client-contract/clients", { token }),
    createClient: (token: string, payload: Record<string, unknown>) =>
      request<Client>("/client-contract/clients", {
        method: "POST",
        token,
        body: payload,
      }),
    listContracts: (token: string) =>
      request<ClientContract[]>("/client-contract/contracts", { token }),
    createContract: (token: string, payload: Record<string, unknown>) =>
      request<ClientContract>("/client-contract/contracts", {
        method: "POST",
        token,
        body: payload,
      }),
  },
  siteOperations: {
    listSites: (token: string) =>
      request<ClientSite[]>("/site-operations/sites", { token }),
    createSite: (token: string, payload: Record<string, unknown>) =>
      request<ClientSite>("/site-operations/sites", {
        method: "POST",
        token,
        body: payload,
      }),
    listPosts: (token: string) =>
      request<SitePost[]>("/site-operations/posts", { token }),
    createPost: (token: string, payload: Record<string, unknown>) =>
      request<SitePost>("/site-operations/posts", {
        method: "POST",
        token,
        body: payload,
      }),
  },
  workforceOperations: {
    listDeployments: (token: string) =>
      request<EmployeeDeployment[]>("/workforce-operations/deployments", { token }),
    createDeployment: (token: string, payload: Record<string, unknown>) =>
      request<EmployeeDeployment>("/workforce-operations/deployments", {
        method: "POST",
        token,
        body: payload,
      }),
    endDeployment: (
      token: string,
      deploymentId: number,
      payload: Record<string, unknown>,
    ) =>
      request<EmployeeDeployment>(
        `/workforce-operations/deployments/${deploymentId}/end`,
        {
          method: "POST",
          token,
          body: payload,
        },
      ),
    listShiftTypes: (token: string) =>
      request<ShiftType[]>("/workforce-operations/shift-types", { token }),
    createShiftType: (token: string, payload: Record<string, unknown>) =>
      request<ShiftType>("/workforce-operations/shift-types", {
        method: "POST",
        token,
        body: payload,
      }),
    listWorkSchedules: (token: string) =>
      request<WorkSchedule[]>("/workforce-operations/work-schedules", { token }),
    generateWorkSchedules: (token: string, payload: Record<string, unknown>) =>
      request<WorkSchedule[]>("/workforce-operations/work-schedules/generate", {
        method: "POST",
        token,
        body: payload,
      }),
    publishWorkSchedule: (token: string, scheduleId: number) =>
      request<WorkSchedule>(
        `/workforce-operations/work-schedules/${scheduleId}/publish`,
        {
          method: "POST",
          token,
        },
      ),
  },
  attendance: {
    listRecords: (token: string) =>
      request<AttendanceRecord[]>("/attendance/records", { token }),
  },
  dashboard: {
    opsSummary: (token: string) =>
      request<DashboardOpsSummary>("/dashboard/ops-summary", { token }),
    attendanceReport: (token: string, payload: { dateFrom: string; dateTo: string }) =>
      request<DashboardAttendanceReport>(
        `/dashboard/reports/attendance?date_from=${payload.dateFrom}&date_to=${payload.dateTo}`,
        { token },
      ),
  },
};
