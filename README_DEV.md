# README Developer

Backend baru HRIS-BPE phase 1 berada di `src/hris_bpe` dan bersifat API-first. Arsitektur ini menggantikan monolith lama Flask + SQLite menjadi domain-based backend yang PostgreSQL-ready, tetapi tetap bisa dijalankan lokal memakai SQLite untuk bootstrap awal.

## Stack

- FastAPI
- SQLAlchemy 2.x
- Bearer token auth
- Custom migration runner phase 1
- Seed reference data untuk tier, feature module, role, demo admin, dan demo guard
- Seed data phase 1.5 untuk user scoped branch/site/company, deployment history, schedule workflow, dan multi-company demo

## Jalankan lokal

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .[dev]
Copy-Item .env.example .env
python -m hris_bpe.dev
```

Command di atas setara gaya `npm run dev` untuk backend ini:

- otomatis menjalankan bootstrap migration + seed saat start
- otomatis menjalankan auto-reload saat file di `src` berubah
- default host/port mengikuti `.env`

Alternatif command setelah editable install:

```powershell
hris-bpe-dev
```

Jika hanya ingin bootstrap database tanpa start server:

```powershell
python -m hris_bpe.database.cli bootstrap
```

## Endpoint penting

- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/product-control/tiers`
- `GET /api/v1/dashboard/ops-summary`
- `PUT /api/v1/access-control/users/{user_id}/scopes`
- `GET /api/v1/access-control/audit-logs`
- `GET /api/v1/workforce-operations/deployment-histories`
- `POST /api/v1/workforce-operations/work-schedules/generate`
- `POST /api/v1/workforce-operations/work-schedules/{schedule_id}/publish`
- `POST /api/v1/workforce-operations/work-schedules/{schedule_id}/approve`
- `GET /api/v1/attendance/exceptions`
- `POST /api/v1/attendance/exceptions`
- `POST /api/v1/attendance/manual-adjustments`

## Akun seed

- Owner: `owner@bpe.co.id` / `Admin123!`
- Guard: `guard@bpe.co.id` / `Guard123!`
- Ops Supervisor scoped site: `supervisor@bpe.co.id` / `Supervisor123!`
- HR Branch scoped branch: `hr.branch@bpe.co.id` / `HrBranch123!`
- Company scoped multi-company owner: `company.scope@bpe.co.id` / `CompanyScope123!`

## Catatan phase 1

- Fokus masih HRIS Basic foundation
- `employee_deployments` menjadi pusat relasi operasional
- `work_schedules` menjadi pusat aktivitas harian
- `attendance_records` sudah terkait ke schedule
- dev runner `python -m hris_bpe.dev` sekarang menjadi entrypoint lokal yang direkomendasikan
- migration runner sekarang memakai revision sequence terurut + PostgreSQL advisory lock untuk baseline production safety
- schema phase 2 sekarang menyiapkan composite indexes operasional dan audit columns `created_by`, `updated_by`, `version_no` pada tabel kritis
- phase 3 sekarang menambahkan refresh session, token revocation, endpoint logout, dan audit log perubahan role/scope
- phase 1.5 menambahkan `user_scope_access` untuk company/branch/site scope
- phase 1.5 menambahkan `deployment_histories`, bulk schedule generation, dan workflow `DRAFT -> PUBLISHED -> APPROVED`
- phase 1.5 menambahkan `attendance_exceptions` terpisah dari `attendance_manual_adjustments`
- Domain Pro dan Enterprise baru disiapkan sebagai placeholder, belum diimplementasikan penuh
