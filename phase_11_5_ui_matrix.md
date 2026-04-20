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
| `/dashboard` | lihat ringkasan Basic | `GET /api/v1/dashboard/ops-summary`, `GET /api/v1/dashboard/reports/attendance` | total inti + `present / late / absent` siap | `absent` diturunkan dari schedule `PUBLISHED` atau `APPROVED` tanpa attendance record; tabel status masih menggabungkan status record aktual dengan baris `ABSENT` sintetis |
| `/employees` | list, create, detail, dan update employee | `GET /api/v1/master-hr/employees`, `POST /api/v1/master-hr/employees`, `GET /api/v1/master-hr/employees/{employee_id}`, `PUT /api/v1/master-hr/employees/{employee_id}`, `GET /api/v1/organization/companies`, `GET /api/v1/organization/branches`, `GET /api/v1/organization/departments`, `GET /api/v1/organization/positions` | list + create + detail + update siap | perubahan `company_id` belum ada di kontrak update employee; filter server-side by branch/status/position belum ada |
| `/clients` | list/create/detail/update client, list/create contract | `GET /api/v1/client-contract/clients`, `POST /api/v1/client-contract/clients`, `GET /api/v1/client-contract/clients/{client_id}`, `PUT /api/v1/client-contract/clients/{client_id}`, `GET /api/v1/client-contract/contracts`, `POST /api/v1/client-contract/contracts`, `GET /api/v1/organization/companies` | client list + create + detail + update siap; contract list + create siap | endpoint update contract dan filter server-side belum ada |
| `/sites` | list/create/detail/update site, list/create/detail/update post | `GET /api/v1/site-operations/sites`, `POST /api/v1/site-operations/sites`, `GET /api/v1/site-operations/sites/{site_id}`, `PUT /api/v1/site-operations/sites/{site_id}`, `GET /api/v1/site-operations/posts`, `POST /api/v1/site-operations/posts`, `GET /api/v1/site-operations/posts/{post_id}`, `PUT /api/v1/site-operations/posts/{post_id}`, `GET /api/v1/client-contract/clients` | site dan post list + create + detail + update siap | filter server-side belum ada |
| `/deployments` | assign guard ke site, list/detail/update deployment, end deployment | `GET /api/v1/workforce-operations/deployments`, `POST /api/v1/workforce-operations/deployments`, `GET /api/v1/workforce-operations/deployments/{deployment_id}`, `PUT /api/v1/workforce-operations/deployments/{deployment_id}`, `POST /api/v1/workforce-operations/deployments/{deployment_id}/end`, referensi employee/client/contract/site/post/position | create + detail + update + end deployment siap | filter server-side by site/client/status belum ada |
| `/schedules` | list/generate/detail/update/publish schedule | `GET /api/v1/workforce-operations/work-schedules`, `GET /api/v1/workforce-operations/work-schedules/{schedule_id}`, `PUT /api/v1/workforce-operations/work-schedules/{schedule_id}`, `POST /api/v1/workforce-operations/work-schedules/generate`, `POST /api/v1/workforce-operations/work-schedules/{schedule_id}/publish`, `GET /api/v1/workforce-operations/shift-types`, `POST /api/v1/workforce-operations/shift-types` | list + generate + detail + update + publish siap | belum ada calendar view dan filter server-side by site/post/date |
| `/attendance` | monitoring attendance, filter, lihat detail, manual adjustment, dan exception | `GET /api/v1/attendance/records`, `GET /api/v1/attendance/records/{attendance_record_id}`, `GET /api/v1/attendance/manual-adjustments`, `POST /api/v1/attendance/manual-adjustments`, `GET /api/v1/attendance/exceptions`, `POST /api/v1/attendance/exceptions`, `POST /api/v1/attendance/exceptions/{exception_id}/resolve`, `GET /api/v1/site-operations/sites`, `GET /api/v1/site-operations/posts`, `GET /api/v1/master-hr/employees` | list + detail + action attendance dasar siap | `absent` sekarang dihitung dari schedule tanpa attendance record, sehingga belum muncul sebagai baris record attendance tersendiri; filter masih client-side |
| `mobile guard` | login, lihat jadwal sendiri, status hadir hari ini, check-in, check-out | `POST /api/v1/auth/login`, `GET /api/v1/my/schedules`, `GET /api/v1/attendance/records`, `POST /api/v1/attendance/check-in`, `POST /api/v1/attendance/check-out` | source Flutter minimal siap; kontrak backend guard flow sudah tervalidasi via integration test | build/runtime mobile belum diverifikasi di environment ini karena Flutter SDK, `dart`, `adb`, dan emulator runner belum siap; folder platform perlu dibootstrap dengan `flutter create .` bila belum ada |

## Gap Prioritas Sebelum Pilot

### P0 - Harus jelas sebelum demo pilot

- review naming final payload sebelum UI dan mobile melebar

### P1 - Bisa jalan dulu dengan fallback UI

- filter masih client-side pada list Basic
- validasi runtime mobile guard setelah Flutter SDK tersedia di environment kerja
- update contract, calendar schedule, dan action attendance lanjutan selain adjustment/exception masih ditunda sesuai kontrak backend/UI

## Implementasi Web Admin Iterasi 1

| Screen | Scope UI Saat Ini |
| --- | --- |
| Login | form login, simpan token, auth guard, user profile, logout |
| Dashboard | total employee, client, site, deployment aktif, schedule hari ini, attendance hari ini, present, late, absent |
| Employees | create employee, list employee, detail employee, update employee, filter client-side |
| Clients | create client, update client, detail client, create contract, list client, list contract |
| Sites | create site, update site, detail site, create post, update post, detail post, list site, list post |
| Deployments | assign guard, detail deployment, update deployment, end deployment, list deployment, filter client-side |
| Schedules | create shift type, generate schedule, detail schedule, update schedule, publish draft, list schedule, filter client-side |
| Attendance | list attendance, filter client-side, detail via endpoint khusus, flag GPS/geofence/face, manual adjustment, create/resolve exception |

## Implementasi Mobile Guard Iterasi 1

| Screen | Scope UI Saat Ini |
| --- | --- |
| Mobile guard | login, persist session, list `my schedules`, status hadir hari ini, check-in GPS, check-out GPS |

## Keterkaitan dengan Roadmap

- Mendukung `PHASE 11.5 UI-1 BASIC`
- Menjadi dasar untuk menutup `PHASE 11` pada poin validasi kontrak frontend/mobile
- Menjaga alur inti tetap sesuai roadmap:

```text
Employee -> Deployment -> Schedule -> Attendance
```
