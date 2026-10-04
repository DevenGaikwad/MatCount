"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "@/components/icon";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/fields";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface HealthData {
  api: string;
  database: { ok: boolean; name?: string; server_version?: string; message: string };
}

export default function LoginPage() {
  const { actor, loading, login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [health, setHealth] = useState<HealthData | null>(null);

  useEffect(() => {
    apiRequest<HealthData>("/health").then(({ data }) => setHealth(data)).catch(() => setHealth(null));
  }, []);
  useEffect(() => {
    if (!loading && actor) router.replace("/dashboard");
  }, [actor, loading, router]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Sign in could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-brand">
        <div className="circuit-motif" aria-hidden="true"><span /><span /><span /><span /><span /></div>
        <div className="login-brand-content">
          <div className="brand-lockup brand-lockup-light">
            <div className="brand-mark"><Icon name="component" size={26} /></div>
            <div><strong>SEMS</strong><span>Smart Electronics Management System</span></div>
          </div>
          <p className="eyebrow light">DES Pune University · Academic DBMS Platform</p>
          <h1>One trusted view of every component, request and laboratory movement.</h1>
          <p>Centralized electronic component and laboratory asset management for accountable, efficient college operations.</p>
          <div className="login-proof-grid">
            <div><Icon name="database" size={20} /><span><strong>One source of truth</strong>Authoritative shared data</span></div>
            <div><Icon name="transfer" size={20} /><span><strong>Workflow controlled</strong>Requests and transfers</span></div>
            <div><Icon name="reports" size={20} /><span><strong>Faculty ready</strong>Reports and evidence</span></div>
          </div>
        </div>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <div className="login-heading">
            <span className={`system-pill ${health?.database.ok ? "online" : "offline"}`}>
              <i /> {health?.database.ok ? "Service Available" : health ? "Service Unavailable" : "Checking Service"}
            </span>
            <h2>Welcome back</h2>
            <p>Sign in with your protected SEMS demonstration account.</p>
          </div>
          <form onSubmit={submit} className="login-form">
            <label htmlFor="email">Email address</label>
            <Input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@sems.local" required />
            <label htmlFor="password">Password</label>
            <div className="password-field">
              <Input id="password" type={showPassword ? "text" : "password"} autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required />
              <button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}><Icon name="eye" size={18} /></button>
            </div>
            {error ? <div className="inline-error" role="alert"><Icon name="alert" size={18} />{error}</div> : null}
            <Button type="submit" busy={busy} className="login-button">Sign In to SEMS</Button>
          </form>
          <p className="login-security">Your session is protected and every action is limited by your assigned role and laboratory scope.</p>
        </div>
        <p className="login-footer">Third-Year B.Tech DBMS Mini Project · School of Engineering &amp; Technology</p>
      </section>
    </main>
  );
}
