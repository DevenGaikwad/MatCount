import { describe, expect, it } from "vitest";
import { formatValue, humanize } from "./format";

describe("SEMS display formatting", () => {
  it("humanizes database identifiers without exposing view prefixes", () => {
    expect(humanize("v_low_stock_components")).toBe("Low Stock Components");
  });

  it("renders missing nullable coordinates consistently", () => {
    expect(formatValue("shelf_no", null)).toBe("—");
    expect(formatValue("drawer_no", "")).toBe("—");
  });

  it("formats valuation numbers as INR", () => {
    expect(formatValue("inventory_valuation", 1250)).toContain("1,250");
  });
});
