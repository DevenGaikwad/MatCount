"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { apiRequest } from "@/lib/api";
import type { Actor, SessionPayload } from "@/types/api";

const STORAGE_KEY = "sems.session.v1";

interface AuthState {
  actor: Actor | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<string | undefined>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [actor, setActor] = useState<Actor | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const clear = useCallback(() => {
    sessionStorage.removeItem(STORAGE_KEY);
    setActor(null);
    setToken(null);
  }, []);

  useEffect(() => {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      queueMicrotask(() => setLoading(false));
      return;
    }
    try {
      const saved = JSON.parse(raw) as { token: string };
      apiRequest<Actor>("/auth/me", {}, saved.token)
        .then(({ data }) => {
          setActor(data);
          setToken(saved.token);
        })
        .catch(clear)
        .finally(() => setLoading(false));
    } catch {
      queueMicrotask(() => {
        clear();
        setLoading(false);
      });
    }
  }, [clear]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiRequest<SessionPayload>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setActor(response.data.actor);
    setToken(response.data.access_token);
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ token: response.data.access_token }),
    );
    return response.message;
  }, []);

  const logout = useCallback(async () => {
    if (token) {
      await apiRequest<null>("/auth/logout", { method: "POST" }, token).catch(() => undefined);
    }
    clear();
  }, [clear, token]);

  const value = useMemo(
    () => ({ actor, token, loading, login, logout }),
    [actor, token, loading, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
