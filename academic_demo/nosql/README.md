# Optional SEMS NoSQL Academic Extension

This folder supports ETCS302 Unit V only. MongoDB is **not** a SEMS runtime dependency, MySQL remains authoritative, and no production record is migrated.

## Why production SEMS remains relational

SEMS depends on strict referential integrity among laboratories, users, components, inventory positions, requests, transfers and disposal history. Multi-row stock workflows require ACID transactions, guarded quantities, stable keys, foreign keys and explainable joins. The 13-relation MySQL design therefore fits the core problem better than a document-only design.

## Where a document store could help

A document database could hold a highly variable, read-heavy manufacturer catalogue where different component categories have different optional specifications. That is only a theoretical extension; the current `COMPONENT.specification` field is sufficient for the academic MVP.

## CAP and database categories

- **Key-value store:** retrieves an opaque value by key; useful for caches/sessions.
- **Document store:** stores self-describing JSON/BSON-like documents; flexible catalogue metadata is a possible fit.
- **Column-family store:** groups sparse wide columns for distributed, high-volume workloads; unnecessary for departmental SEMS.
- **Graph database:** optimizes relationship traversal; useful for dense compatibility/dependency graphs, which are outside the MVP.
- **CAP theorem:** under a network partition, a distributed system must choose between always-consistent responses and always-available responses. CAP does not mean a database permanently chooses only two properties in every normal operating state.

## Optional execution

1. Install/run MongoDB separately only if the faculty requires practical Unit V evidence.
2. Open `mongosh`.
3. Run `load("mongodb_demo.js")` from this directory.
4. Inspect the printed CRUD results.

The script touches only `sems_academic_demo.component_catalogue_demo` and removes only rows marked `academic_demo: true`.

