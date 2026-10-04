"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export function useApiData<T>(path: string, enabled = true) {
  const { token } = useAuth();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    if (!token || !enabled) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await apiRequest<T>(path, {}, token);
      setData(response.data);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "SEMS data could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [enabled, path, token]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void refresh(); }, 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);
  return { data, loading, error, refresh, setData };
}
