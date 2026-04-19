# Audit Source Lama Presensi

## Snapshot audit

- Source lama diambil dari `C:\Users\Administrator\OneDrive\Documents\GitHub\Presensi`
- Arsitektur lama adalah monolith Flask + SQLite dengan file utama [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py) sepanjang 11.272 baris
- Routing lama terbagi ke 90 route total:
  - 45 route `@app.route`
  - 45 route `@bp.route`
- Fokus bisnis lama: auth, user/role sederhana, client, site, assignment, shift, attendance, manual attendance, leave request, patrol, audit log

## Kondisi teknis lama

- Penyimpanan masih `sqlite3` langsung di [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L3806)
- Inisialisasi schema dilakukan lewat `_init_db()` di [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L6096)
- Role masih disimpan sebagai string tunggal pada tabel `users`
- Attendance lama berbasis event `checkin/checkout` per baris, belum berpusat pada `work_schedules`
- Assignment lama masih `assignments`, belum menjadi `employee_deployments` yang kaya konteks kontrak/site/post/position
- Banyak coupling antara API, session web, template render, flash message, dan query database mentah

## Kode yang masih layak dipakai sebagai referensi migrasi

- Logika validasi login dan password hashing:
  - [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L2491)
- Konsep assignment aktif dan policy attendance:
  - [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L3930)
  - [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L3994)
- Validasi attendance berbasis GPS/QR/selfie sebagai referensi aturan bisnis:
  - [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L1621)
- Alur penutupan assignment aktif saat ada assignment baru:
  - [`app.py`](C:/Users/Administrator/OneDrive/Documents/GitHub/Presensi/app.py#L5430)
- Audit log sebagai konsep governance minimal:
  - tabel `audit_logs` di source lama

## Kode yang harus dipindahkan lalu dipecah

- `users`, `role_permissions`, dan proses login
- `clients`, `sites`, `shifts`, `assignments`
- attendance check-in/check-out
- seed default role dan user

Semua area di atas berguna, tetapi hanya sebagai bahan ekstraksi logika bisnis. Implementasi teknisnya tidak boleh dipindah mentah.

## Kode yang harus dirombak total

- Struktur app tunggal Flask + template server-side
- Seluruh akses data `conn.execute(...)` tersebar
- Model user dengan `role` tunggal
- Attendance event table yang tidak terkait ke `work_schedules`
- Client/site schema yang masih bercampur data operasional dan data PIC
- Patrol yang langsung menempel ke assignment lama

## Kode yang sebaiknya dibuang

- Dependensi terhadap `flash`, `render_template`, dashboard HTML lama
- State session web lama untuk auth API
- File biner/tooling yang ikut tersimpan di repo lama:
  - `git-setup.exe`
  - `python-3.13.10-amd64.exe`
- `presensi.db` sebagai basis arsitektur akhir

## Gap analysis terhadap target HRIS-BPE

### Sudah ada di source lama

- Auth/login dasar
- Role access dasar
- Client dan site basic
- Shift basic
- Attendance basic
- Leave request basic
- Patrol basic
- Audit log dasar

### Belum memenuhi target HRIS-BPE

- Tidak ada `product_tiers`, `feature_modules`, `company_subscriptions`, `company_feature_modules`
- Tidak ada pemisahan domain `organization`, `master_hr`, `client_contract`, `site_operations`, `workforce_operations`
- Tidak ada API versioning `/api/v1`
- RBAC belum normalized ke `roles`, `permissions`, `role_permissions`, `user_roles`
- Scope access belum siap untuk branch/site/company scope
- Attendance belum menjadikan `work_schedules` sebagai pusat aktivitas harian
- Payroll dan billing belum punya fondasi operasional yang benar
- PostgreSQL readiness belum ada
- Testing dan migration masih lemah

## Kesimpulan refactor

- Source lama cocok diperlakukan sebagai bahan migrasi logika bisnis HRIS Basic
- Source lama tidak layak dijadikan final architecture
- Repo baru harus menerapkan:
  - single core platform
  - tier activation via subscription dan feature module
  - `employee_deployments` sebagai pusat relasi operasional
  - `work_schedules` sebagai pusat aktivitas harian
  - fondasi attendance yang siap dinaikkan ke patrol, incident, payroll, billing

## Struktur backend baru yang diadopsi

```text
src/hris_bpe
├── bootstrap
├── config
├── common
├── database
├── migrations
├── seeds
└── domains
    ├── product_control
    ├── auth
    ├── access_control
    ├── organization
    ├── master_hr
    ├── client_contract
    ├── site_operations
    ├── workforce_operations
    ├── attendance
    ├── dashboard
    ├── leave_replacement
    ├── patrol
    ├── incident
    ├── payroll
    ├── billing
    ├── audit
    ├── integration
    ├── notifications
    └── portal
```

