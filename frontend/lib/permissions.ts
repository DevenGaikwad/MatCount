import type { Role } from "@/types/api";

export interface NavigationItem {
  label: string;
  href: string;
  icon: string;
  roles: Role[];
}

export interface NavigationGroup {
  label: string;
  items: NavigationItem[];
}

const ALL: Role[] = ["STUDENT", "FACULTY", "LAB_ASSISTANT", "ADMINISTRATOR"];

export type Capability =
  | "VIEW_FINANCIAL_FIELDS"
  | "VIEW_INVENTORY_COORDINATES"
  | "MANAGE_INVENTORY"
  | "MANAGE_USERS"
  | "REVIEW_REQUESTS"
  | "PLAN_TRANSFERS"
  | "APPROVE_TRANSFERS"
  | "EXECUTE_TRANSFERS"
  | "DISPOSE_STOCK"
  | "VIEW_GLOBAL_REPORTS";

const CAPABILITY_ROLES: Record<Capability, Role[]> = {
  VIEW_FINANCIAL_FIELDS: ["LAB_ASSISTANT", "ADMINISTRATOR"],
  VIEW_INVENTORY_COORDINATES: ["FACULTY", "LAB_ASSISTANT", "ADMINISTRATOR"],
  MANAGE_INVENTORY: ["LAB_ASSISTANT", "ADMINISTRATOR"],
  MANAGE_USERS: ["ADMINISTRATOR"],
  REVIEW_REQUESTS: ["FACULTY", "ADMINISTRATOR"],
  PLAN_TRANSFERS: ["LAB_ASSISTANT", "ADMINISTRATOR"],
  APPROVE_TRANSFERS: ["ADMINISTRATOR"],
  EXECUTE_TRANSFERS: ["LAB_ASSISTANT", "ADMINISTRATOR"],
  DISPOSE_STOCK: ["ADMINISTRATOR"],
  VIEW_GLOBAL_REPORTS: ["ADMINISTRATOR"],
};

export const NAVIGATION: NavigationGroup[] = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", href: "/dashboard", icon: "dashboard", roles: ALL }],
  },
  {
    label: "Master Data",
    items: [
      { label: "Laboratories", href: "/laboratories", icon: "lab", roles: ["ADMINISTRATOR"] },
      { label: "Users", href: "/users", icon: "users", roles: ["ADMINISTRATOR"] },
      { label: "Component Catalogue", href: "/components", icon: "component", roles: ALL },
      {
        label: "Storage Locations",
        href: "/storage-locations",
        icon: "storage",
        roles: ["LAB_ASSISTANT", "ADMINISTRATOR"],
      },
    ],
  },
  {
    label: "Operations",
    items: [
      { label: "Inventory", href: "/inventory", icon: "inventory", roles: ALL },
      { label: "Component Requests", href: "/requests", icon: "request", roles: ALL },
      {
        label: "Inter-Lab Transfers",
        href: "/transfers",
        icon: "transfer",
        roles: ["FACULTY", "LAB_ASSISTANT", "ADMINISTRATOR"],
      },
      { label: "Disposal", href: "/disposal", icon: "disposal", roles: ["ADMINISTRATOR"] },
    ],
  },
  {
    label: "Analytics",
    items: [{ label: "Reports", href: "/reports", icon: "reports", roles: ALL }],
  },
];

export function navigationFor(role: Role): NavigationGroup[] {
  return NAVIGATION.map((group) => ({
    ...group,
    items: group.items.filter((item) => item.roles.includes(role)),
  })).filter((group) => group.items.length > 0);
}

export function canOpen(role: Role, pathname: string): boolean {
  return NAVIGATION.flatMap((group) => group.items).some(
    (item) => item.href === pathname && item.roles.includes(role),
  );
}

export function can(role: Role, capability: Capability): boolean {
  return CAPABILITY_ROLES[capability].includes(role);
}
