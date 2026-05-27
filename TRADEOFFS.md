# Tradeoffs

Three things deliberately not built and why.

## 1. No User Authentication or RBAC

**What**: The app has no login, no user accounts, no role-based access control. Reviewer names are free-text.

**Why not**: Authentication adds significant complexity (token management, session handling, password resets, SSO integration) that is orthogonal to the core problem of data ingestion and review. In a 4-day prototype, spending time on auth means less time on the data model and ETL pipeline — which is what BreatheESG actually evaluates.

**What I would build with more time**: Django's built-in auth with two roles — `analyst` (can upload and review) and `auditor` (read-only access to approved records and audit trail). JWT tokens for the React frontend. SSO integration via django-allauth for enterprise deployment.

**Impact**: Anyone with the URL can upload data and approve records. This is acceptable for a prototype but would be the first thing to address before production.

## 2. No PDF Bill Parsing for Utility Data

**What**: The utility ingestion only handles structured CSV exports. No PDF bill parsing.

**Why not**: PDF utility bills have wildly inconsistent layouts across providers. Building a reliable PDF parser for even one provider takes days of layout analysis, OCR tuning, and edge case handling. For Indian utility providers (Tata Power, BSES, MSEDCL), there's no standard format.

**What I would build with more time**: Integration with a document extraction service (Textract, Google Document AI) with provider-specific templates. A "manual entry" fallback where facilities teams key in consumption from paper bills. Or direct API integration with utility portals that offer one (rare but growing).

**Impact**: Facilities teams that only have PDF bills can't use the current system. They'd need to transcribe data into CSV first.

## 3. No Async Processing or Background Jobs

**What**: File uploads are processed synchronously in the request-response cycle. No Celery, no background queues, no progress indicators.

**Why not**: The sample files have 10 rows each. Even a large enterprise client's monthly fuel data is typically under 1000 rows. Synchronous processing handles this in under a second. Adding Celery/Redis introduces operational complexity (another service to deploy and monitor) for a problem that doesn't exist at this scale.

**What I would build with more time**: Django-Q or Celery for files over 5000 rows, with a WebSocket-based progress indicator. This becomes necessary when processing utility data for a company with hundreds of meters across dozens of facilities — but that's a scale problem, not a correctness problem.

**Impact**: Very large files (10,000+ rows) may cause request timeouts. The fix is straightforward when needed.
