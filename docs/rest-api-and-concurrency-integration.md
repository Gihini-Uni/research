# Feedora Research Backend: REST API Seam & Concurrency Architecture

This document outlines the lightweight, zero-dependency REST API seam and SQLite concurrency enhancements added to `gihini-research`.

These additions empower external clients (such as the Feedora React Native mobile and web application) to authenticate, fetch research survey metadata, submit responses with gamified points, and inspect user/organization history **without scraping HTML pages and without changing any existing Django views or templates**.

---

## 1. Summary of Changes

| Component | Status | Details |
| :--- | :--- | :--- |
| **Dependencies** | **0 New Dependencies** | Uses standard Django `JsonResponse`, `django.contrib.auth`, and built-in Python libraries (`json`, `time`, `random`). `requirements.txt` is completely unchanged. |
| **Existing Views** | **100% Preserved** | All template-rendered views (`/surveys/`, `/surveys/new/`, `/accounts/login/`, etc.) continue functioning exactly as before. |
| **Database Models** | **No Migrations Required** | Operates on existing `Survey`, `Question`, `Option`, `Response`, and `Answer` models. |
| **Database Concurrency** | **WAL Mode Enabled** | SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) enabled in `settings.py` to support high-throughput concurrent survey submissions. |
| **Self-Documentation** | **Built-in Swagger & OpenAPI** | Interactive Swagger UI live at `/api/v1/docs/` and OpenAPI 3.0 specification at `/api/v1/openapi.json`. |

---

## 2. API Endpoints Catalog (`/api/v1/`)

All endpoints are registered under `feedora_project/api_urls.py` and handled by `feedora_project/api_views.py`.

### A. Authentication & Session Management

| Method | Path | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login/` | Authenticate using `username` / `password`. Sets standard Django session cookie. | No |
| `POST` | `/api/v1/auth/register/` | Register new researcher or respondent account. | No |
| `GET` | `/api/v1/auth/me/` | Inspect current session profile, roles, and aggregate points. | Optional |
| `POST` | `/api/v1/auth/logout/` | Terminate session and flush session cookie. | Yes |

### B. Respondent History & Analytics

| Method | Path | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/respondent/history/` | Returns historical survey submissions, points earned per survey, level progress, and organizational point aggregations. | Yes |

### C. Survey Metadata & Distribution

| Method | Path | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/surveys/` | List active public surveys available for response. | No |
| `GET` | `/api/v1/surveys/mine/` | List all surveys owned by the authenticated researcher (including drafts). | Yes (Creator/Staff) |
| `POST` | `/api/v1/surveys/create/` | Create a new research survey with ordered questions and choice options. | Yes (Creator/Staff) |
| `GET` | `/api/v1/surveys/<uuid>/meta/` | Fetch complete survey schema, HMSAM constructs, and question items by UUID. | No |
| `GET` | `/api/v1/surveys/code/<access_code>/meta/` | Fetch complete survey schema by 6-character access code (e.g., `HMSAM1`, `YG0Z3D`). | No |

### D. Response Submission & Gamification

| Method | Path | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/surveys/<uuid>/submit/` | Submit answers via JSON. Automatically calculates points based on question type, creates atomic `Response` and `Answer` records, and updates gamification standings. | No (supports anonymous & authenticated) |

---

## 3. SQLite Concurrency & High-Throughput Protection

### The Problem
Under default SQLite configuration, any concurrent write (e.g., multiple participants submitting survey responses simultaneously during a classroom trial) locks the entire database file (`sqlite3.OperationalError: database is locked`).

### The Solution
We hardened SQLite concurrency in `feedora_project/settings.py` using two connection hooks:
1. **Write-Ahead Logging (WAL)**:
   ```sql
   PRAGMA journal_mode=WAL;
   ```
   Allows simultaneous readers and writers without blocking each other.
2. **Busy Timeout & Synchronous Setting**:
   ```sql
   PRAGMA busy_timeout=5000;
   PRAGMA synchronous=NORMAL;
   ```
   Instructs SQLite to wait up to 5,000ms for locks to clear before raising an error.
3. **Application-Level Exponential Backoff**:
   In `api_survey_submit`, database transactions employ randomized exponential backoff (up to 10 retry attempts) in the rare event of transient SQLite lock contention.

### Concurrency Test Suite
A dedicated stress test [`feedora_project/test_hostile_concurrency.py`](file:///c:/projects/gihini-research/feedora_project/test_hostile_concurrency.py) validates that 50 simultaneous threads submitting answers concurrently achieve a 100% success rate with 0 database locked errors.

---

## 4. Interactive Documentation

Start the Django development server:
```powershell
python manage.py runserver 0.0.0.0:8000
```

Visit the interactive Swagger UI in your browser:
- **Swagger Documentation**: `http://127.0.0.1:8000/api/v1/docs/`
- **Raw OpenAPI 3.0 Specification**: `http://127.0.0.1:8000/api/v1/openapi.json`
