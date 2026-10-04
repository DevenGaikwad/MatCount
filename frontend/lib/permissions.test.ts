import { describe, expect, it } from "vitest";
import { can, canOpen, navigationFor } from "./permissions";

describe("role-aware navigation", () => {
  it("keeps transfer and disposal out of Student navigation", () => {
    const links = navigationFor("STUDENT").flatMap((group) => group.items.map((item) => item.href));
    expect(links).not.toContain("/transfers");
    expect(links).not.toContain("/disposal");
    expect(links).toContain("/requests");
  });

  it("permits only Administrator access to disposal", () => {
    expect(canOpen("ADMINISTRATOR", "/disposal")).toBe(true);
    expect(canOpen("FACULTY", "/disposal")).toBe(false);
    expect(canOpen("LAB_ASSISTANT", "/disposal")).toBe(false);
  });

  it("keeps Faculty transfer monitoring while withholding storage administration", () => {
    expect(canOpen("FACULTY", "/transfers")).toBe(true);
    expect(canOpen("FACULTY", "/storage-locations")).toBe(false);
  });

  it("allows Lab Assistant operational inventory and storage routes", () => {
    expect(canOpen("LAB_ASSISTANT", "/inventory")).toBe(true);
    expect(canOpen("LAB_ASSISTANT", "/storage-locations")).toBe(true);
    expect(canOpen("LAB_ASSISTANT", "/users")).toBe(false);
  });

  it("denies unknown paths for every role", () => {
    expect(canOpen("ADMINISTRATOR", "/future-procurement")).toBe(false);
    expect(canOpen("STUDENT", "/future-procurement")).toBe(false);
  });

  it("models financial visibility without granting it to Student or Faculty", () => {
    expect(can("STUDENT", "VIEW_FINANCIAL_FIELDS")).toBe(false);
    expect(can("FACULTY", "VIEW_FINANCIAL_FIELDS")).toBe(false);
    expect(can("LAB_ASSISTANT", "VIEW_FINANCIAL_FIELDS")).toBe(true);
    expect(can("ADMINISTRATOR", "VIEW_FINANCIAL_FIELDS")).toBe(true);
  });

  it("keeps approval, execution and disposal capabilities distinct", () => {
    expect(can("FACULTY", "REVIEW_REQUESTS")).toBe(true);
    expect(can("FACULTY", "APPROVE_TRANSFERS")).toBe(false);
    expect(can("LAB_ASSISTANT", "EXECUTE_TRANSFERS")).toBe(true);
    expect(can("LAB_ASSISTANT", "APPROVE_TRANSFERS")).toBe(false);
    expect(can("ADMINISTRATOR", "DISPOSE_STOCK")).toBe(true);
  });
});
