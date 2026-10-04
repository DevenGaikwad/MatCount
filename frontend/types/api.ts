export type Role = "STUDENT" | "FACULTY" | "LAB_ASSISTANT" | "ADMINISTRATOR";

export interface Actor {
  user_id: number;
  email: string;
  full_name: string;
  role: Role;
  lab_id: number;
  account_status: string;
}

export type DataRow = Record<string, unknown>;

export interface ApiEnvelope<T> {
  data: T;
  message?: string;
}

export interface ApiFailure {
  error?: {
    code?: string;
    message?: string;
    details?: Array<{ field: string; message: string }>;
  };
}

export interface SessionPayload {
  access_token: string;
  token_type: string;
  expires_at: string;
  actor: Actor;
}

export interface DashboardData {
  kpis: Record<string, number>;
  stock_by_lab: DataRow[];
  request_status: DataRow[];
}

export interface DetailPayload {
  request?: DataRow;
  transfer?: DataRow;
  items: DataRow[];
}
