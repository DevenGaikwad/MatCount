"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { RoleBadge } from "@/components/ui/badge";
import { LoadingState } from "@/components/ui/states";
import { useAuth } from "@/lib/auth";
import { canOpen, navigationFor } from "@/lib/permissions";
import { humanize } from "@/lib/format";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { actor, loading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!loading && !actor) router.replace("/login");
  }, [actor, loading, router]);

  const groups = useMemo(() => (actor ? navigationFor(actor.role) : []), [actor]);
  const current = groups.flatMap((group) => group.items).find((item) => item.href === pathname);

  if (loading || !actor) {
    return <main className="full-state"><LoadingState label="Validating your SEMS session…" /></main>;
  }

  const permitted = canOpen(actor.role, pathname);
  return (
    <div className="app-frame">
      <button
        className={`sidebar-scrim ${mobileOpen ? "visible" : ""}`}
        type="button"
        aria-label="Close navigation"
        onClick={() => setMobileOpen(false)}
      />
      <aside className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true"><Icon name="component" size={24} /></div>
          <div><strong>SEMS</strong><span>Laboratory Operations</span></div>
        </div>
        <nav aria-label="Primary navigation">
          {groups.map((group) => (
            <div className="nav-group" key={group.label}>
              <p>{group.label}</p>
              {group.items.map((item) => (
                <Link key={item.href} href={item.href} className={pathname === item.href ? "active" : ""} aria-current={pathname === item.href ? "page" : undefined} onClick={() => setMobileOpen(false)}>
                  <Icon name={item.icon} size={19} /><span>{item.label}</span>
                </Link>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="avatar" aria-hidden="true">{actor.full_name.split(" ").map((part) => part[0]).slice(0, 2).join("")}</div>
          <div><strong>{actor.full_name}</strong><span>{humanize(actor.role)} · Lab {actor.lab_id}</span></div>
          <button type="button" onClick={() => logout().then(() => router.replace("/login"))} aria-label="Sign out">
            <Icon name="logout" size={18} />
          </button>
        </div>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <div>
            <button className="mobile-menu" type="button" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
              <Icon name="menu" size={21} />
            </button>
            <div className="breadcrumb"><span>SEMS</span><Icon name="chevron" size={14} /><strong>{current?.label ?? "Workspace"}</strong></div>
          </div>
          <div className="topbar-context">
            <span className="lab-context"><Icon name="lab" size={16} /> Laboratory {actor.lab_id}</span>
            <span className="system-online"><i /> Secure session</span>
            <div className="topbar-identity"><span>{actor.full_name}</span><RoleBadge value={actor.role} /></div>
          </div>
        </header>
        <main className="content-shell">
          {permitted ? children : (
            <section className="permission-panel" role="alert">
              <Icon name="alert" size={28} />
              <h1>Access restricted</h1>
              <p>Your {humanize(actor.role)} role is not permitted to open this SEMS module.</p>
              <Link href="/dashboard">Return to Dashboard</Link>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
