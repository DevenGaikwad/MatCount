"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { StatusBadge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/states";
import { formatValue, humanize } from "@/lib/format";
import type { DataRow } from "@/types/api";

export interface Column {
  key: string;
  label?: string;
  numeric?: boolean;
  hidden?: boolean;
}

interface DataTableProps {
  rows: DataRow[];
  columns?: Column[];
  searchPlaceholder?: string;
  pageSize?: number;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (row: DataRow) => void;
  selectedId?: unknown;
  idKey?: string;
}

const statusKeys = /status|priority|role/i;

export function DataTable({
  rows,
  columns,
  searchPlaceholder = "Search displayed records",
  pageSize = 10,
  emptyTitle = "No records found",
  emptyDescription = "No data matches the current scope or filters.",
  onRowClick,
  selectedId,
  idKey = "id",
}: DataTableProps) {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<{ key: string; direction: "asc" | "desc" } | null>(null);
  const [page, setPage] = useState(1);
  const [hiddenColumns, setHiddenColumns] = useState<Set<string>>(new Set());
  const [density, setDensity] = useState<"comfortable" | "compact">("comfortable");

  const availableColumns = useMemo<Column[]>(() => {
    if (columns) return columns.filter((column) => !column.hidden);
    const first = rows[0];
    return first
      ? Object.keys(first).slice(0, 10).map((key): Column => ({ key, label: humanize(key) }))
      : [];
  }, [columns, rows]);

  const visibleColumns = useMemo(
    () => availableColumns.filter((column) => !hiddenColumns.has(column.key)),
    [availableColumns, hiddenColumns],
  );

  const filtered = useMemo(() => {
    const needle = search.trim().toLowerCase();
    const result = needle
      ? rows.filter((row) => Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(needle)))
      : [...rows];
    if (!sort) return result;
    return result.sort((left, right) => {
      const a = left[sort.key];
      const b = right[sort.key];
      const numeric = typeof a === "number" && typeof b === "number";
      const comparison = numeric
        ? Number(a) - Number(b)
        : String(a ?? "").localeCompare(String(b ?? ""), undefined, { numeric: true });
      return sort.direction === "asc" ? comparison : -comparison;
    });
  }, [rows, search, sort]);

  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, pages);
  const displayed = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);
  const firstRecord = filtered.length ? (safePage - 1) * pageSize + 1 : 0;
  const lastRecord = Math.min(safePage * pageSize, filtered.length);

  function toggleSort(key: string) {
    setSort((current) =>
      current?.key === key
        ? { key, direction: current.direction === "asc" ? "desc" : "asc" }
        : { key, direction: "asc" },
    );
  }

  function toggleColumn(key: string) {
    setHiddenColumns((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key);
      else if (availableColumns.length - next.size > 1) next.add(key);
      return next;
    });
  }

  if (!rows.length) return <EmptyState title={emptyTitle} description={emptyDescription} />;
  return (
    <div className={`data-grid density-${density}`}>
      <div className="table-toolbar">
        <label className="search-box">
          <Icon name="search" size={18} />
          <span className="sr-only">Search records</span>
          <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder={searchPlaceholder} />
        </label>
        <div className="table-toolbar-actions">
          <span>{filtered.length} record{filtered.length === 1 ? "" : "s"}</span>
          <details className="table-options">
            <summary aria-label="Table display options"><Icon name="columns" size={17} />Display</summary>
            <div className="table-options-menu">
              <fieldset>
                <legend>Visible columns</legend>
                {availableColumns.map((column) => (
                  <label key={column.key}>
                    <input
                      type="checkbox"
                      checked={!hiddenColumns.has(column.key)}
                      onChange={() => toggleColumn(column.key)}
                    />
                    {column.label ?? humanize(column.key)}
                  </label>
                ))}
              </fieldset>
              <fieldset>
                <legend>Row density</legend>
                <label><input type="radio" name="density" checked={density === "comfortable"} onChange={() => setDensity("comfortable")} />Comfortable</label>
                <label><input type="radio" name="density" checked={density === "compact"} onChange={() => setDensity("compact")} />Compact</label>
              </fieldset>
            </div>
          </details>
        </div>
      </div>
      <div className="table-scroll">
        <table>
          <caption className="sr-only">Searchable, sortable SEMS records</caption>
          <thead>
            <tr>
              {visibleColumns.map((column) => (
                <th
                  key={column.key}
                  className={column.numeric ? "numeric" : ""}
                  aria-sort={sort?.key === column.key ? (sort.direction === "asc" ? "ascending" : "descending") : "none"}
                >
                  <button
                    type="button"
                    onClick={() => toggleSort(column.key)}
                    aria-label={`Sort by ${column.label ?? humanize(column.key)}`}
                  >
                    {column.label ?? humanize(column.key)}
                    <span aria-hidden="true">{sort?.key === column.key ? (sort.direction === "asc" ? "↑" : "↓") : ""}</span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayed.map((row, index) => (
              <tr
                key={`${String(row[idKey] ?? "row")}-${index}`}
                className={`${onRowClick ? "clickable" : ""} ${selectedId === row[idKey] ? "selected" : ""}`}
                onClick={() => onRowClick?.(row)}
                tabIndex={onRowClick ? 0 : undefined}
                onKeyDown={(event) => {
                  if (onRowClick && (event.key === "Enter" || event.key === " ")) {
                    event.preventDefault();
                    onRowClick(row);
                  }
                }}
              >
                {visibleColumns.map((column) => {
                  const value = row[column.key];
                  return (
                    <td key={column.key} className={column.numeric ? "numeric" : ""}>
                      {statusKeys.test(column.key) && typeof value === "string" ? (
                        <StatusBadge value={value} />
                      ) : (
                        formatValue(column.key, value)
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pagination" aria-label="Table pagination">
        <span>Showing {firstRecord}–{lastRecord} of {filtered.length} · Page {safePage} of {pages}</span>
        <div>
          <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={safePage === 1}>Previous</button>
          <button type="button" onClick={() => setPage((value) => Math.min(pages, value + 1))} disabled={safePage === pages}>Next</button>
        </div>
      </div>
    </div>
  );
}
