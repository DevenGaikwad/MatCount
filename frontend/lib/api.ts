import type { ApiEnvelope, ApiFailure } from "@/types/api";

export const API_BASE =
  process.env.NEXT_PUBLIC_SEMS_API_URL ?? "http://127.0.0.1:8000/api";

export class ApiError extends Error {
  status: number;
  code: string;
  details: Array<{ field: string; message: string }>;

  constructor(
    message: string,
    status = 500,
    code = "API_ERROR",
    details: Array<{ field: string; message: string }> = [],
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<ApiEnvelope<T>> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "The SEMS service is unavailable. Confirm that the Python API is running.",
      0,
      "API_UNAVAILABLE",
    );
  }

  const payload = (await response.json().catch(() => ({}))) as
    | ApiEnvelope<T>
    | ApiFailure;
  if (!response.ok) {
    const failure = payload as ApiFailure;
    throw new ApiError(
      failure.error?.message ?? "The operation could not be completed.",
      response.status,
      failure.error?.code,
      failure.error?.details,
    );
  }
  return payload as ApiEnvelope<T>;
}

export async function downloadReport(
  viewName: string,
  token: string,
): Promise<void> {
  const response = await fetch(`${API_BASE}/reports/${viewName}/csv`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const failure = (await response.json().catch(() => ({}))) as ApiFailure;
    throw new ApiError(
      failure.error?.message ?? "CSV export could not be generated.",
      response.status,
      failure.error?.code,
    );
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${viewName}.csv`;
  anchor.click();
  URL.revokeObjectURL(url);
}
