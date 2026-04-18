# API_DESIGN.md

## Ringkasan
Dokumen ini menjabarkan rancangan **API backend** untuk HRIS khusus perusahaan outsourcing security/satpam dengan pendekatan produk bertingkat:

- **HRIS Basic**
- **HRIS Pro**
- **HRIS Enterprise**
- **Add-on Module**

Tujuan dokumen ini:
- menjadi kontrak awal antara backend, frontend web, dan mobile
- menjaga konsistensi endpoint, payload, dan alur otorisasi
- mempermudah implementasi bertahap sesuai roadmap tier produk
- memisahkan dengan jelas endpoint core, endpoint pro, endpoint enterprise, dan endpoint add-on

Pendekatan yang dipakai:
- **REST API**
- **JSON request/response**
- versioning via prefix `/api/v1`
- auth berbasis **access token**
- **RBAC + scope-based access**
- siap dikembangkan ke model multi-branch dan multi-company

---

# 1. PRINSIP DESAIN API

Prinsip utama:
- endpoint mengikuti domain bisnis
- response konsisten untuk web admin, mobile guard, dan portal client
- endpoint disusun agar selaras dengan paket produk
- flow operasional harus tetap utuh dari deployment sampai attendance, payroll, dan billing
- aman untuk data sensitif seperti payroll, incident, dan invoice
- siap dikembangkan menjadi enterprise scale

### Base URL
```text
/api/v1
```

### Format response umum
```json
{
  "success": true,
  "message": "OK",
  "data": {},
  "meta": {}
}
```

### Format error umum
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "field_name": ["field is required"]
  }
}
```

### Header umum
```text
Authorization: Bearer <token>
Content-Type: application/json
Accept: application/json
```

---

# 2. STRATEGI API BERDASARKAN TIER PRODUK

## 2.1 Tier mapping

### HRIS Basic
Endpoint minimum untuk menjalankan flow:
```text
Employee → Deployment → Schedule → Attendance → Dashboard
```

### HRIS Pro
Endpoint tambahan untuk menjalankan flow:
```text
Attendance → Replacement / Patrol / Incident → Payroll
```

### HRIS Enterprise
Endpoint tambahan untuk menjalankan flow:
```text
Payroll / Contract / Attendance → Billing → Analytics / Audit / Portal / Integration
```

### Add-on
Endpoint modular yang dapat diaktifkan terpisah tanpa merusak endpoint inti.

---

# 3. AUTHENTICATION & AUTHORIZATION

## 3.1 Auth endpoints

### POST /auth/login
Login user.

Request:
```json
{
  "username": "supervisor01",
  "password": "secret123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login success",
  "data": {
    "access_token": "jwt_or_token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 10,
      "name": "Budi Supervisor",
      "role": "site_supervisor"
    }
  }
}
```

### POST /auth/logout
### GET /auth/me
### POST /auth/refresh
### POST /auth/change-password

## 3.2 Role minimum
- super_admin
- hr_admin
- ops_admin
- site_supervisor
- finance_admin
- payroll_admin
- management
- guard
- client_user

## 3.3 Access model
Akses berbasis:
- role
- permission
- company scope
- branch scope
- site scope
- optional client scope untuk portal client

---

# 4. STANDAR QUERY API

## Pagination
```text
?page=1&per_page=20
```

## Sorting
```text
?sort_by=created_at&sort_order=desc
```

## Filtering
```text
?status=active&client_id=12&site_id=30
```

## Search
```text
?search=budi
```

## Include relation
```text
?include=branch,position,guard_profile
```

## Response list
```json
{
  "success": true,
  "message": "OK",
  "data": [],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 120,
    "last_page": 6
  }
}
```

---

# 5. DOMAIN API UTAMA

Domain endpoint utama:
- auth
- users & access
- organization
- employees
- guards
- clients
- contracts
- sites & posts
- manpower planning
- deployments
- shifts & schedules
- attendance
- leave & replacement
- patrol
- incidents
- payroll
- billing
- dashboard & reports
- audit
- notifications
- client portal
- integrations
- add-on modules

---

# 6. HRIS BASIC API

## 6.1 Organization & access basic

### GET /companies
### GET /branches
### POST /branches
### PUT /branches/{id}

### GET /users
### POST /users
### GET /users/{id}
### PUT /users/{id}
### PATCH /users/{id}/status

### GET /roles
### GET /permissions
### POST /users/{id}/roles

Request:
```json
{
  "role_ids": [1, 2]
}
```

---

## 6.2 Employee & guard master

### GET /employees
Filter umum:
- company_id
- branch_id
- position_id
- employee_status
- employment_status

### POST /employees
```json
{
  "employee_number": "EMP-0001",
  "full_name": "Budi Santoso",
  "branch_id": 1,
  "department_id": 2,
  "position_id": 5,
  "phone": "08123456789",
  "hire_date": "2026-04-18",
  "employment_status": "contract",
  "employee_status": "active"
}
```

### GET /employees/{id}
### PUT /employees/{id}
### PATCH /employees/{id}/status

### GET /employees/{id}/documents
### POST /employees/{id}/documents
### GET /employees/{id}/contracts
### POST /employees/{id}/contracts
### GET /employees/{id}/emergency-contacts
### POST /employees/{id}/emergency-contacts

### GET /guards
### POST /guards
```json
{
  "employee_id": 100,
  "guard_registration_number": "G-7788",
  "guard_level": "gada_pratama",
  "uniform_size": "L",
  "shoe_size": 42,
  "fitness_status": "fit"
}
```

### GET /guards/{employee_id}
### PUT /guards/{employee_id}
### GET /guards/{employee_id}/certifications
### POST /guards/{employee_id}/certifications

---

## 6.3 Client, contract, site, post

### GET /clients
### POST /clients
### GET /clients/{id}
### PUT /clients/{id}
### PATCH /clients/{id}/status

### GET /contracts
### POST /contracts
```json
{
  "client_id": 10,
  "contract_number": "CTR-2026-001",
  "contract_title": "Security Services 2026",
  "start_date": "2026-05-01",
  "end_date": "2027-04-30",
  "contract_type": "monthly",
  "currency": "IDR",
  "payment_term_days": 30,
  "status": "active"
}
```

### GET /contracts/{id}
### PUT /contracts/{id}
### POST /contracts/{id}/files

### GET /sites
### POST /sites
```json
{
  "client_id": 10,
  "client_contract_id": 20,
  "branch_id": 1,
  "code": "SITE-MALL-01",
  "name": "Mall Sentosa Jakarta",
  "address": "Jl. Sudirman No. 1",
  "city": "Jakarta",
  "province": "DKI Jakarta",
  "latitude": -6.2,
  "longitude": 106.8,
  "geofence_radius_meter": 150,
  "site_type": "mall",
  "operational_status": "active"
}
```

### GET /sites/{id}
### PUT /sites/{id}
### GET /sites/{id}/posts
### POST /sites/{id}/posts
### GET /sites/{id}/manpower-requirements
### POST /sites/{id}/manpower-requirements

---

## 6.4 Deployment, shift, schedule

### GET /deployments
### POST /deployments
```json
{
  "employee_id": 100,
  "client_id": 10,
  "client_contract_id": 20,
  "client_site_id": 30,
  "site_post_id": 40,
  "position_id": 5,
  "start_date": "2026-05-01",
  "deployment_status": "active",
  "source_type": "regular"
}
```

### GET /deployments/{id}
### PUT /deployments/{id}
### PATCH /deployments/{id}/end
### GET /deployments/{id}/history

### GET /shift-types
### POST /shift-types
### GET /shift-types/{id}
### PUT /shift-types/{id}

### GET /schedules
### POST /schedules
### POST /schedules/generate
```json
{
  "client_site_id": 30,
  "date_from": "2026-05-01",
  "date_to": "2026-05-31",
  "shift_pattern_id": 3,
  "employee_ids": [100, 101, 102]
}
```

### GET /schedules/{id}
### PUT /schedules/{id}
### PATCH /schedules/{id}/publish
### GET /my/schedules

---

## 6.5 Attendance basic

### POST /attendance/check-in
```json
{
  "work_schedule_id": 500,
  "check_in_datetime": "2026-05-05T07:01:00+07:00",
  "latitude": -6.2,
  "longitude": 106.8,
  "photo": "base64_or_file_token",
  "device_id": "device-001"
}
```

### POST /attendance/check-out
```json
{
  "attendance_id": 900,
  "check_out_datetime": "2026-05-05T19:02:00+07:00",
  "latitude": -6.2,
  "longitude": 106.8,
  "photo": "base64_or_file_token"
}
```

### GET /attendance
### GET /attendance/{id}
### GET /attendance/exceptions
### POST /attendance/{id}/adjustments
### GET /my/attendance

---

## 6.6 Dashboard & reporting basic

### GET /dashboard/ops-summary
### GET /reports/employees
### GET /reports/deployments
### GET /reports/schedules
### GET /reports/attendance

---

# 7. HRIS PRO API

Semua endpoint HRIS Basic termasuk, ditambah endpoint berikut.

## 7.1 Leave, permission, replacement

### GET /leave-types
### GET /leave-requests
### POST /leave-requests
### GET /leave-requests/{id}
### POST /leave-requests/{id}/approve
### POST /leave-requests/{id}/reject

### GET /replacement-requests
### POST /replacement-requests
```json
{
  "work_schedule_id": 500,
  "request_type": "absent_replacement",
  "reason": "Guard sakit mendadak",
  "replacement_employee_id": 120
}
```

### POST /replacement-requests/{id}/approve
### POST /replacement-requests/{id}/reject
### GET /standby-pools
### POST /standby-pools

---

## 7.2 Patrol / guard tour basic

### GET /patrol/routes
### POST /patrol/routes
### GET /patrol/routes/{id}
### PUT /patrol/routes/{id}
### GET /patrol/routes/{id}/checkpoints
### POST /patrol/routes/{id}/checkpoints

### POST /patrol/sessions/start
```json
{
  "work_schedule_id": 500,
  "patrol_route_id": 20,
  "start_datetime": "2026-05-05T22:00:00+07:00"
}
```

### POST /patrol/sessions/{id}/scan
```json
{
  "patrol_checkpoint_id": 90,
  "scanned_at": "2026-05-05T22:20:00+07:00",
  "latitude": -6.2,
  "longitude": 106.8,
  "scan_method": "qr",
  "photo": "file_token"
}
```

### POST /patrol/sessions/{id}/finish
### GET /patrol/sessions
### GET /patrol/sessions/{id}
### GET /reports/patrol

---

## 7.3 Incident control & report

### GET /incidents
### POST /incidents
```json
{
  "client_site_id": 30,
  "site_post_id": 40,
  "employee_id": 100,
  "work_schedule_id": 500,
  "incident_category_id": 3,
  "occurred_at": "2026-05-05T23:30:00+07:00",
  "severity_level": "high",
  "title": "Keributan di parkiran",
  "description": "Terjadi keributan antara pengunjung.",
  "action_taken": "Mengamankan lokasi awal"
}
```

### GET /incidents/{id}
### PUT /incidents/{id}
### POST /incidents/{id}/files
### POST /incidents/{id}/follow-ups
### PATCH /incidents/{id}/close
### GET /reports/incidents

---

## 7.4 Approval workflow basic

### POST /attendance/{id}/approve-adjustment
### POST /leave-requests/{id}/approve
### POST /replacement-requests/{id}/approve
### POST /incidents/{id}/approve-close
### GET /approvals/pending

---

## 7.5 Payroll basic

### GET /payroll/periods
### POST /payroll/periods
### GET /payroll/periods/{id}
### POST /payroll/periods/{id}/process
```json
{
  "recalculate": true
}
```

### GET /payroll/periods/{id}/employees
### GET /payroll/employees/{id}
### POST /payroll/employees/{id}/components
### POST /payroll/employees/{id}/approve
### POST /payroll/periods/{id}/approve
### GET /payslips
### GET /payslips/{id}
### POST /payslips/{id}/publish
### GET /my/payslips
### GET /reports/payroll

---

## 7.6 Notifications & dashboard pro

### GET /notifications
### POST /notifications/{id}/read
### POST /notifications/read-all
### GET /dashboard/supervisor-summary
### GET /dashboard/ops-alerts

---

# 8. HRIS ENTERPRISE API

Semua endpoint HRIS Pro termasuk, ditambah endpoint berikut.

## 8.1 Billing & invoice management

### GET /billing-rules
### POST /billing-rules
### GET /billing-rules/{id}
### PUT /billing-rules/{id}

### GET /invoices
### POST /invoices/generate
```json
{
  "client_id": 10,
  "client_contract_id": 20,
  "client_site_id": 30,
  "billing_period_start": "2026-05-01",
  "billing_period_end": "2026-05-31"
}
```

### GET /invoices/{id}
### PUT /invoices/{id}
### POST /invoices/{id}/issue
### POST /invoices/{id}/send
### POST /invoices/{id}/payments
```json
{
  "payment_date": "2026-06-20",
  "payment_amount": 15000000,
  "payment_method": "bank_transfer",
  "reference_number": "TRX-889977"
}
```

### GET /reports/invoices
### GET /reports/accounts-receivable

---

## 8.2 Advanced approval workflow

### GET /approval-matrices
### POST /approval-matrices
### PUT /approval-matrices/{id}
### GET /approval-logs
### POST /approvals/{id}/escalate
### POST /approvals/{id}/delegate

---

## 8.3 Audit & compliance

### GET /audit-logs
### GET /audit-logs/{id}
### GET /entity-history/{entity_name}/{entity_id}
### GET /compliance/site-sla
### GET /compliance/manpower

---

## 8.4 Analytics & management dashboard

### GET /dashboard/finance-summary
### GET /dashboard/management-summary
### GET /dashboard/site-performance
### GET /analytics/revenue-by-client
### GET /analytics/margin-by-site
### GET /analytics/attendance-trends
### GET /analytics/incident-trends
### GET /analytics/patrol-compliance
### GET /analytics/outstanding-invoices

---

## 8.5 Multi-company / multi-branch / scope

### GET /regions
### POST /regions
### GET /company-groups
### POST /company-groups
### GET /access-scopes
### POST /users/{id}/scopes

---

## 8.6 Client portal

### GET /portal/client/profile
### GET /portal/client/invoices
### GET /portal/client/attendance-summary
### GET /portal/client/incidents
### GET /portal/client/reports
### GET /portal/client/sla-summary

---

## 8.7 API & integration readiness

### GET /integrations
### POST /integrations/webhooks
### GET /integrations/webhooks/{id}
### PUT /integrations/webhooks/{id}
### POST /integrations/imports/{type}
### GET /integrations/exports/{type}

---

# 9. ADD-ON API MODULE

Add-on diaktifkan modular. Endpoint berikut sebaiknya dipisah ke service/module tersendiri.

## 9.1 Recruitment system

### GET /recruitment/requisitions
### POST /recruitment/requisitions
### GET /recruitment/candidates
### POST /recruitment/candidates
### GET /recruitment/candidates/{id}
### POST /recruitment/candidates/{id}/screenings
### POST /recruitment/candidates/{id}/interviews
### POST /recruitment/candidates/{id}/medical-checks
### POST /recruitment/candidates/{id}/background-checks
### POST /recruitment/candidates/{id}/convert-to-employee

---

## 9.2 Employee loan / dana talangan

### GET /employee-loans
### POST /employee-loans
### GET /employee-loans/{id}
### POST /employee-loans/{id}/approve
### POST /employee-loans/{id}/reject
### GET /employee-loans/{id}/installments
### POST /employee-loans/{id}/close

---

## 9.3 Reimbursement & claim

### GET /claims
### POST /claims
### GET /claims/{id}
### POST /claims/{id}/approve
### POST /claims/{id}/reject
### POST /claims/{id}/pay

---

## 9.4 Training & certification

### GET /trainings
### POST /trainings
### GET /training-sessions
### POST /training-sessions
### GET /employee-trainings
### POST /employee-trainings
### GET /certification-reminders

---

## 9.5 Asset & uniform management

### GET /assets
### POST /assets
### GET /assets/{id}
### POST /asset-assignments
### GET /asset-assignments
### POST /asset-returns
### GET /uniform-packages

---

## 9.6 Visitor / logbook digital

### GET /logbook/entries
### POST /logbook/entries
### GET /logbook/visitors
### POST /logbook/visitors
### GET /logbook/vehicle-entries
### POST /logbook/vehicle-entries
### POST /logbook/shift-handovers

---

## 9.7 Performance & discipline

### GET /performance/reviews
### POST /performance/reviews
### GET /discipline/cases
### POST /discipline/cases
### POST /discipline/cases/{id}/warning-letter
### GET /performance/rankings

---

## 9.8 Notification suite advanced

### POST /notifications/test
### GET /notification-templates
### POST /notification-templates
### POST /notifications/send-bulk
### GET /notification-channels

---

## 9.9 Payroll advanced

### GET /payroll/formulas
### POST /payroll/formulas
### POST /payroll/periods/{id}/simulate
### POST /payroll/periods/{id}/thr
### POST /payroll/periods/{id}/bonus
### GET /payroll/bank-export/{period_id}

---

## 9.10 Billing advanced

### GET /billing/formulas
### POST /billing/formulas
### POST /invoices/{id}/approve
### POST /invoices/{id}/split
### GET /invoice-templates
### POST /invoice-templates

---

## 9.11 Patrol advanced

### GET /patrol/live-monitoring
### GET /patrol/compliance-score
### POST /patrol/dynamic-schedules
### GET /reports/patrol-missed-analysis

---

## 9.12 Incident command center

### GET /incident-war-room/boards
### GET /incident-sla/timers
### POST /incidents/{id}/escalate
### POST /incidents/{id}/root-cause
### POST /incidents/{id}/corrective-actions

---

## 9.13 SLA & compliance monitoring

### GET /sla/rules
### POST /sla/rules
### GET /sla/reports
### GET /sla/site-scores
### GET /sla/manpower-compliance

---

## 9.14 Client portal advanced

### GET /portal/client/complaints
### POST /portal/client/complaints
### GET /portal/client/patrol-summary
### GET /portal/client/payment-status

---

## 9.15 API & integration pack

### GET /open-api/keys
### POST /open-api/keys
### DELETE /open-api/keys/{id}
### GET /webhooks/events
### POST /connectors/accounting/sync
### POST /connectors/attendance-device/sync

---

# 10. ENDPOINT PRIORITAS PER PHASE

## Phase 1 — HRIS Basic
- /auth/login
- /auth/me
- /users
- /employees
- /guards
- /clients
- /contracts
- /sites
- /sites/{id}/posts
- /sites/{id}/manpower-requirements
- /deployments
- /shift-types
- /schedules
- /schedules/generate
- /attendance/check-in
- /attendance/check-out
- /attendance
- /dashboard/ops-summary

## Phase 2 — HRIS Pro
- /leave-requests
- /replacement-requests
- /standby-pools
- /patrol/routes
- /patrol/sessions/start
- /patrol/sessions/{id}/scan
- /incidents
- /attendance/{id}/approve-adjustment
- /payroll/periods
- /payroll/periods/{id}/process
- /payslips
- /notifications

## Phase 3 — HRIS Enterprise
- /billing-rules
- /invoices/generate
- /invoices
- /invoices/{id}/payments
- /audit-logs
- /dashboard/management-summary
- /analytics/revenue-by-client
- /portal/client/invoices
- /integrations/webhooks

## Phase 4 — Add-on prioritas
- /recruitment/*
- /employee-loans/*
- /assets/*
- /trainings/*
- /claims/*

## Phase 5 — Advanced add-on
- /payroll/formulas
- /billing/formulas
- /patrol/live-monitoring
- /incident-war-room/boards
- /sla/reports
- /open-api/keys

---

# 11. VALIDASI KRITIS

## Deployment
- guard aktif
- kontrak client aktif
- site aktif
- tidak ada bentrok deployment aktif

## Schedule
- guard tidak punya shift bentrok
- shift valid
- deployment valid untuk tanggal itu

## Attendance
- hanya bisa check-in untuk schedule valid
- geofence wajib valid atau masuk exception
- check-out tidak boleh sebelum check-in
- device dan photo validation bisa diperketat per tier

## Patrol
- checkpoint harus milik route yang sama
- sesi patroli harus aktif
- scan timestamp tidak boleh tidak masuk akal

## Incident
- incident wajib terkait site valid
- incident close harus menyimpan resolution note

## Payroll
- periode payroll tidak boleh diproses dua kali tanpa recalculate
- komponen loan/claim/add-on payroll harus tervalidasi

## Invoice
- periode invoice tidak boleh overlap untuk rule yang sama tanpa override
- payment tidak boleh melebihi sisa tagihan tanpa override

---

# 12. STATUS CODE YANG DIREKOMENDASIKAN

- `200 OK` untuk GET/PUT/PATCH sukses
- `201 Created` untuk POST create
- `400 Bad Request` untuk payload salah
- `401 Unauthorized` jika belum login
- `403 Forbidden` jika tidak punya akses
- `404 Not Found` jika resource tidak ditemukan
- `409 Conflict` untuk bentrok data
- `422 Unprocessable Entity` untuk validasi gagal
- `500 Internal Server Error` untuk error server

---

# 13. SARAN STRUKTUR SERVICE BACKEND

```text
/modules
  /auth
  /access
  /organization
  /employees
  /guards
  /clients
  /contracts
  /sites
  /manpower
  /deployments
  /shifts
  /attendance
  /leave
  /replacement
  /patrol
  /incidents
  /payroll
  /billing
  /dashboard
  /reports
  /audit
  /notifications
  /portal
  /integrations
  /recruitment
  /employee_loans
  /claims
  /training
  /assets
  /logbook
  /performance
  /sla
```

Tiap module minimal punya:
- controller
- service
- repository/data access
- validator
- policy/authorization
- dto/request schema
- tests

---

# 14. REKOMENDASI KONTRAK API FRONTEND

## Web admin
Butuh endpoint domain lengkap untuk:
- HR admin
- ops admin
- finance
- payroll
- management

## Mobile guard
Butuh endpoint ringan untuk:
- auth
- my schedules
- attendance check-in/out
- patrol start/scan/finish
- incident create
- my payslips
- notification inbox

## Client portal
Butuh endpoint terbatas untuk:
- invoice
- attendance summary
- incident summary
- SLA summary
- laporan periodik

---

# 15. KESIMPULAN

Rancangan API ini dibuat agar:
- developer backend punya kontrak implementasi jelas
- frontend web punya pembagian endpoint per tier produk
- mobile guard punya endpoint lapangan yang ringan
- client portal punya endpoint terbatas yang aman
- sistem bisa dibangun bertahap sesuai roadmap Basic → Pro → Enterprise → Add-on

Ringkasnya:

```text
REST API
+ RBAC & Scope Access
+ Tier-based Product Design
+ Modular Domain Service
= Fondasi backend HRIS security outsourcing yang siap dijual dan dikembangkan
```
