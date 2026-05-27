# Data Model

## Overview

The data model is designed around one core fact: ESG ingestion is fundamentally a data quality problem, not a computation problem. Every design decision prioritizes traceability — knowing exactly which file produced which row, who reviewed it, and what happened at every step.

## Schema

### Company
Multi-tenant root entity. Every emission record and upload belongs to a company.

| Field | Type | Purpose |
|---|---|---|
| id | BigAutoField | Primary key |
| name | CharField(255) | Unique company name |
| industry | CharField(100) | Sector classification |
| created_at | DateTimeField | Record creation timestamp |
| updated_at | DateTimeField | Last modification timestamp |

### Upload (Source-of-Truth Tracking)
Every CSV file upload creates one Upload record. This is the lineage anchor — you can always trace any emission record back to the exact file that produced it.

| Field | Type | Purpose |
|---|---|---|
| id | BigAutoField | Primary key |
| company | FK → Company | Tenant isolation |
| source_type | CharField(20) | sap_fuel / utility / travel |
| file_name | CharField(255) | Original filename |
| file_hash | CharField(64) | SHA-256 hash for deduplication |
| row_count | PositiveIntegerField | Total rows processed |
| suspicious_count | PositiveIntegerField | Flagged rows count |
| status | CharField(20) | processing / completed / failed |
| created_at | DateTimeField | Upload timestamp |

### EmissionRecord (Core Fact Table)
One row per ingested data point. Stores both raw and normalized values so auditors can see exactly what came in and what the system did to it.

| Field | Type | Purpose |
|---|---|---|
| id | BigAutoField | Primary key |
| company | FK → Company | Tenant isolation |
| upload | FK → Upload | Source lineage — which file produced this row |
| row_number | PositiveIntegerField | Row position in source file |
| source_type | CharField(20) | sap_fuel / utility / travel |
| scope | PositiveSmallIntegerField | GHG Protocol scope (1, 2, or 3) |
| category | CharField(200) | Human-readable description |
| raw_value | FloatField | Original value from source |
| normalized_value | FloatField | Converted to standard unit |
| raw_unit | CharField(50) | Original unit from source |
| normalized_unit | CharField(50) | Standardized unit (L, kWh, km) |
| emission_factor | FloatField | kgCO₂ per unit applied |
| co2_kg | FloatField | Computed carbon footprint |
| reporting_date | DateField | When this activity occurred |
| is_suspicious | BooleanField | Flagged by parser |
| suspicious_reason | TextField | Why it was flagged |
| status | CharField(20) | pending / approved / rejected |
| created_at | DateTimeField | Ingestion timestamp |
| updated_at | DateTimeField | Last modification |

### ReviewDecision
Analyst decisions on individual records. Multiple reviews per record are allowed — the latest wins.

| Field | Type | Purpose |
|---|---|---|
| id | BigAutoField | Primary key |
| emission_record | FK → EmissionRecord | Which record was reviewed |
| decision | CharField(10) | approved / rejected |
| reviewer_name | CharField(100) | Who made the decision |
| notes | TextField | Justification |
| created_at | DateTimeField | Decision timestamp |

### AuditLog
Append-only log. Every upload and every review decision creates an entry. Never edited, never deleted.

| Field | Type | Purpose |
|---|---|---|
| id | BigAutoField | Primary key |
| action | CharField(30) | upload / review_approved / review_rejected |
| target_type | CharField(50) | What was acted on (upload, emission_record) |
| target_id | PositiveIntegerField | ID of the target |
| details | JSONField | Structured metadata |
| performed_by | CharField(100) | Who did it |
| created_at | DateTimeField | When it happened |

## Design Rationale

**Scope classification**: SAP fuel data is Scope 1 (direct combustion), utility electricity is Scope 2 (purchased energy), travel is Scope 3 (business travel). This is auto-assigned during ingestion based on source type, following GHG Protocol boundaries.

**Dual value storage** (raw_value + normalized_value): Auditors need to see the original data exactly as it came in. The normalized value is what the system uses for calculations. This prevents "which number is right?" arguments.

**Emission factors stored per-record**: Different fuel types have different factors. Storing the applied factor alongside the result means any CO₂ calculation is fully reproducible and auditable.

**Upload as lineage anchor**: The Upload model with file_hash enables deduplication and complete traceability. Every EmissionRecord points back to its Upload, so you can always answer "where did this number come from?"

**Status workflow**: Records start as `pending`, move to `approved` or `rejected` through analyst review. Approved records are audit-ready. This is a deliberate three-state machine — no intermediate states to complicate the workflow.

**Multi-tenancy via Company FK**: Every data-bearing table has a Company foreign key. In a production system, this would be enforced at the middleware level. For this prototype, it's enforced at the API level via query parameters.
