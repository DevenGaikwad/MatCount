export function humanize(value: string): string {
  return value
    .replace(/^v_/, "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatValue(key: string, value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") {
    if (/cost|value|valuation|amount/i.test(key)) {
      return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
      }).format(value);
    }
    return new Intl.NumberFormat("en-IN").format(value);
  }
  if (/date|created_at|updated_at/i.test(key) && typeof value === "string") {
    const date = new Date(value);
    if (!Number.isNaN(date.valueOf())) {
      return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(date);
    }
  }
  return humanize(String(value));
}

export function today(): string {
  return new Date().toISOString().slice(0, 10);
}
