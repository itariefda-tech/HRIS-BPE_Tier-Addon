# Phase 11.5 UI Matrix

## Ringkasan

Matrix ini memetakan layar UI Basic ke kontrak API yang sudah ada di backend `FastAPI /api/v1`, sekaligus menandai gap yang masih menghalangi status `demo ready` dan `pilot operasional phase 1`.

Fokus iterasi awal:

1. auth
2. dashboard
3. employee
4. client, contract, site, post
5. deployment
6. schedule
7. attendance

## Freeze Scope Basic

- Web admin: login, dashboard, employee, client, site, deployment, schedule, attendance
- Mobile guard: login, my schedules, check-in, check-out
- Di luar scope iterasi ini: payroll, patrol, incident, billing, analytics lanjutan

## Matrix UI -> Endpoint -> Gap

| Screen | User Goal | Endpoint | Status Backend Saat Ini | Gap / Warning |
| --- | --- | --- | --- | --- |
| `/login` | admin login dan simpan session | `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout` | siap dipakai | refresh token flow belum dipakai di UI web awal |
| `/dashboard` | lihat ringkasan Basic | `GET /api/v1/dashboard/ops-summary`, `GET /api/v1/dashboard/reports/attendance` | siap dipakai untuk total inti | `ops-summary` belum memberi `present / late / absent`; `present` dan `late` diambil dari reporting attendance, `absent` belum punya kontrak final |
| `/employees` | list dan create employee | `GET /api/v1/master-hr/employees`, `POST /api/v1/master-hr/employees`, `GET /api/v1/organization/companies`, `GET /api/v1/organization/branches`, `GET /api/v1/organization/departments`, `GET /api/v1/organization/positions` | list + create siap | belum ada endpoint detail employee khusus, update employee, dan filter server-side by branch/status/position |
| `/clients` | list client, create client, list/create contract | `GET /api/v1/client-contract/clients`, `POST /api/v1/client-contract/clients`, `GET /api/v1/client-contract/contracts`, `POST /api/v1/client-contract/contracts`, `GET /api/v1/organization/companies` | list + create siap | belum ada update client, detail client, dan filter server-side |
| `/sites` | list site, create site, list/create post | `GET /api/v1/site-operations/sites`, `POST /api/v1/site-operations/sites`, `GET /api/v1/site-operations/posts`, `POST /api/v1/site-operations/posts`, `GET /api/v1/client-contract/clients` | list + create siap | belum ada update site/post, detail site, dan filter server-side |
| `/deployments` | assign guard ke site, list deployment, end deployment | `GET /api/v1/workforce-operations/deployments`, `POST /api/v1/workforce-operations/deployments`, `POST /api/v1/workforce-operations/deployments/{deployment_id}/end`, referensi employee/client/contract/site/post/position | create dan end deployment siap | belum ada update deployment, detail deployment, dan filter server-side by site/client/status |
| `/schedules` | list schedule, generate schedule, publish schedule | `GET /api/v1/workforce-operations/work-schedules`, `POST /api/v1/workforce-operations/work-schedules/generate`, `POST /api/v1/workforce-operations/work-schedules/{schedule_id}/publish`, `GET /api/v1/workforce-operations/shift-types`, `POST /api/v1/workforce-operations/shift-types` | list + generate + publish siap | belum ada calendar view, detail schedule khusus, dan filter server-side by site/post/date |
| `/attendance` | monitoring attendance, filter, lihat detail sederhana | `GET /api/v1/attendance/records`, `GET /api/v1/site-operations/sites` | list siap | belum ada endpoint detail attendance khusus; `absent` belum punya kontrak final terpisah; filter masih client-side |
| `mobile guard` | lihat jadwal sendiri, check-in, check-out | roadmap: `/my/schedules`, `/attendance/check-in`, `/attendance/check-out` | `check-in` dan `check-out` ada | endpoint `/my/schedules` belum ditemukan di source backend saat ini |

## Gap Prioritas Sebelum Pilot

### P0 - Harus jelas sebelum demo pilot

- finalisasi kontrak `absent` untuk dashboard Basic
- pastikan endpoint guard `my schedules` ada atau revisi roadmap ke kontrak yang benar
- review naming final payload sebelum UI dan mobile melebar

### P1 - Bisa jalan dulu dengan fallback UI

- filter masih client-side pada list Basic
- detail entity memakai data list atau panel ringkas, karena belum ada endpoint detail khusus
- edit entity ditunda sampai endpoint update tersedia

## Implementasi Web Admin Iterasi 1

| Screen | Scope UI Saat Ini |
| --- | --- |
| Login | form login, simpan token, auth guard, user profile, logout |
| Dashboard | total employee, client, site, deployment aktif, schedule hari ini, attendance hari ini, present, late |
| Employees | create employee, list employee, filter client-side |
| Clients | create client, create contract, list client, list contract |
| Sites | create site, create post, list site, list post |
| Deployments | assign guard, end deployment, list deployment, filter client-side |
| Schedules | create shift type, generate schedule, publish draft, list schedule, filter client-side |
| Attendance | list attendance, filter client-side, detail sederhana, flag GPS/geofence/face |

## Keterkaitan dengan Roadmap

- Mendukung `PHASE 11.5 UI-1 BASIC`
- Menjadi dasar untuk menutup `PHASE 11` pada poin validasi kontrak frontend/mobile
- Menjaga alur inti tetap sesuai roadmap:

```text
Employee -> Deployment -> Schedule -> Attendance
```
