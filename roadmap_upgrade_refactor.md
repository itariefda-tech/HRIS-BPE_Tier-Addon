# Roadmap Upgrade & Refactor
## Presensi -> HRIS-BPE (Basic / Pro / Enterprise + Add-ons)

---

## Tujuan Upgrade

- [x] upgrade aplikasi presensi lama menjadi single core HRIS untuk outsourcing security/satpam
- [x] jadikan tier `BASIC`, `PRO`, `ENTERPRISE` berbasis `product_tiers` + `feature_modules`
- [x] siapkan core platform modular tanpa database terpisah per tier
- [x] arahkan fondasi ke mobile-first guard dan supervisor
- [x] standarkan backend baru ke API `/api/v1`, RBAC, dan scope-based access
- [ ] bawa fondasi `HRIS Basic` sampai siap dipakai untuk pilot operasional phase 1

---

## Prinsip Upgrade

- [x] tidak rewrite total tanpa arah
- [x] gunakan source lama hanya sebagai referensi bisnis dan bahan migrasi
- [x] refactor bertahap dengan dokumen HRIS-BPE sebagai sumber kebenaran
- [x] flow bisnis utama tidak boleh putus saat migrasi
- [x] `employee_deployments` menjadi pusat relasi operasional
- [x] `work_schedules` menjadi pusat aktivitas harian
- [x] payroll dan billing tidak boleh berdiri tanpa fondasi operasional
- [ ] jaga kontrak API dan naming tetap konsisten saat domain bertambah

---

## PHASE 0 - Audit Source Lama

- [x] audit source lama dari `C:\Users\Administrator\OneDrive\Documents\GitHub\Presensi`
- [x] inventarisasi struktur, tabel, dan flow utama aplikasi lama
- [x] mapping fitur existing: auth, role, client, site, shift, attendance, leave, patrol, audit
- [x] identifikasi area monolith yang harus dipecah dari pola `app.py` lama
- [x] gap analysis antara source lama dan target arsitektur HRIS-BPE
- [x] tandai kode yang masih layak dipakai sebagai referensi migrasi
- [x] tandai area yang harus dirombak total karena bertentangan dengan fondasi baru
- [x] buat dokumen audit hasil review source lama

---

## PHASE 1 - Bootstrap Repo Baru

- [x] siapkan package Python backend baru berbasis API-first
- [x] siapkan `pyproject.toml` dan dependency phase 1
- [x] siapkan `.env.example`
- [x] siapkan `src/hris_bpe/main.py`
- [x] siapkan app bootstrap, router registry, dan exception envelope standar
- [x] siapkan database session PostgreSQL-ready dengan fallback SQLite untuk dev lokal
- [x] siapkan migration runner baseline
- [x] siapkan seed runner baseline
- [x] siapkan README developer singkat untuk menjalankan project baru

---

## PHASE 1.5 - Hardening Foundation HRIS Basic

- [x] tambahkan `user_scope_access` untuk pembatasan branch/site
- [x] tampilkan scope user pada response login dan `/auth/me`
- [x] terapkan scope dasar pada akses site, deployment, schedule, attendance, dashboard, dan employee list
- [x] tambahkan `deployment_histories` sebagai jejak perubahan deployment awal
- [x] tambahkan bulk schedule generation berbasis deployment aktif
- [x] tambahkan manual attendance adjustment berbasis `attendance_records`
- [x] siapkan seed scoped user untuk supervisor site dan HR branch
- [x] tambahkan integration test untuk scope authorization phase 1.5
- [x] tambah enforcement `COMPANY` scope end-to-end
- [x] tambah publish / approve workflow untuk schedule
- [x] tambah attendance exception workflow terpisah dari manual adjustment

---

## PHASE 2 - Database Core

- [x] buat tabel `product_tiers`
- [x] buat tabel `feature_modules`
- [x] buat tabel `company_subscriptions`
- [x] buat tabel `company_feature_modules`
- [x] buat tabel `companies`
- [x] buat tabel `branches`
- [x] buat tabel `users`
- [x] buat tabel `roles`
- [x] buat tabel `permissions`
- [x] buat tabel `role_permissions`
- [x] buat tabel `user_roles`
- [x] buat tabel `departments`
- [x] buat tabel `positions`
- [x] buat tabel `employees`
- [x] buat tabel `guard_profiles`
- [x] buat tabel `employee_contracts`
- [x] buat tabel `clients`
- [x] buat tabel `client_contracts`
- [x] buat tabel `client_sites`
- [x] buat tabel `site_posts`
- [x] buat tabel `employee_deployments`
- [x] buat tabel `shift_types`
- [x] buat tabel `work_schedules`
- [x] buat tabel `attendance_records`
- [x] tambah indeks komposit untuk query operasional real
- [x] tambah audit columns `created_by`, `updated_by`, `version_no` pada tabel kritis
- [x] siapkan baseline migration strategy yang lebih aman untuk PostgreSQL production

---

## PHASE 3 - Migrasi Auth & Access Control

- [x] ganti auth session lama menjadi bearer token API
- [x] siapkan endpoint `/api/v1/auth/login`
- [x] siapkan endpoint `/api/v1/auth/me`
- [x] siapkan endpoint `/api/v1/auth/change-password`
- [x] normalisasi role ke tabel `roles`
- [x] normalisasi permission ke tabel `permissions`
- [x] normalisasi relasi `user_roles`
- [x] siapkan endpoint list `roles`
- [x] siapkan endpoint list `permissions`
- [x] siapkan endpoint create `users`
- [x] siapkan endpoint assign role ke user
- [x] siapkan endpoint kelola scope user
- [x] tambah refresh token
- [x] tambah revoke / logout token
- [x] tambah audit trail untuk perubahan role dan scope
- [x] tambahkan preferensi user untuk `preferred_language` (`id` / `en`)
- [x] tambahkan preferensi user untuk `preferred_theme` (`theme_1` / `theme_2` / `theme_3` / `theme_4` / `theme_5`)
- [x] tampilkan `preferred_language` dan `preferred_theme` pada response login
- [x] tampilkan `preferred_language` dan `preferred_theme` pada endpoint `/api/v1/auth/me`
- [x] siapkan endpoint update preferensi user (`preferred_language` + `preferred_theme`)

---

## PHASE 4 - Migrasi Organization & Master HR

- [x] siapkan endpoint list/create `companies`
- [x] siapkan endpoint list/create `branches`
- [x] siapkan endpoint list/create `departments`
- [x] siapkan endpoint list/create `positions`
- [x] siapkan endpoint list/create `employees`
- [x] siapkan endpoint list/create `guards`
- [x] siapkan endpoint create `employee_contracts`
- [x] pindahkan konsep `employee` terpisah dari user account
- [x] siapkan relasi `users.employee_id`
- [x] tambah validasi kode unik per company yang lebih ketat
- [x] tambah support multi-company owner
- [x] migrasikan emergency contact dan employee documents
- [x] tambahkan import batch employee
- [x] tambahkan lifecycle employee yang lebih lengkap
- [ ] tambahkan company setting untuk default language
- [ ] tambahkan company setting untuk default theme
- [ ] siapkan fallback: user preference > company default > system default

---

## PHASE 5 - Migrasi Site, Deployment, Schedule, Attendance

- [x] siapkan endpoint list/create `clients`
- [x] siapkan endpoint list/create `client_contracts`
- [x] siapkan endpoint list/create `client_sites`
- [x] siapkan endpoint list/create `site_posts`
- [x] siapkan endpoint list/create `employee_deployments`
- [x] siapkan endpoint list/create `shift_types`
- [x] siapkan endpoint list/create `work_schedules`
- [x] jadikan `employee_deployments` sebagai pusat relasi operasional
- [x] jadikan `work_schedules` sebagai pusat aktivitas harian
- [x] tambahkan history deployment dasar
- [x] tambahkan bulk schedule generation dasar
- [x] siapkan endpoint `/api/v1/attendance/check-in`
- [x] siapkan endpoint `/api/v1/attendance/check-out`
- [x] siapkan endpoint list attendance
- [x] tautkan attendance ke `work_schedules`
- [x] simpan geofence dan GPS validation flag
- [x] hitung `minutes_late`, `working_minutes`, dan `overtime_minutes`
- [x] tambahkan attendance manual adjustment
- [x] tambah schedule publish workflow
- [x] tambah attendance exception handling record
- [x] tambah selfie validation service
- [x] tambah QR attendance terpisah

---

## PHASE 6 - Dashboard & Reporting Basic

- [x] siapkan endpoint `/api/v1/dashboard/ops-summary`
- [x] hitung total employee
- [x] hitung total client
- [x] hitung total site
- [x] hitung active deployment
- [x] hitung work schedule hari ini
- [x] hitung attendance hari ini
- [x] tambah reporting employee
- [x] tambah reporting deployment
- [x] tambah reporting schedule
- [x] tambah reporting attendance
- [x] siapkan endpoint dashboard yang aman untuk scoped supervisor

---

## PHASE 7 - PRO Foundation

- [x] siapkan placeholder `leave_replacement`
- [x] siapkan placeholder `patrol`
- [x] siapkan placeholder `incident`
- [x] siapkan placeholder `payroll`
- [ ] buat migration batch berikutnya untuk tabel Pro
- [ ] pindahkan logika leave lama ke domain baru
- [ ] pindahkan logika patrol lama ke domain baru
- [ ] refactor patrol agar bergantung ke `work_schedules`, bukan assignment lama
- [ ] siapkan incident foundation berbasis `work_schedule_id`
- [ ] siapkan payroll foundation yang menarik data dari deployment + schedule + attendance

---

## PHASE 8 - ENTERPRISE Foundation

- [x] siapkan placeholder `billing`
- [x] siapkan placeholder `audit`
- [x] siapkan placeholder `integration`
- [x] siapkan placeholder `notifications`
- [x] siapkan placeholder `portal`
- [ ] siapkan `billing_rules` setelah kontrak, deployment, dan attendance stabil
- [ ] siapkan `audit_logs` generik lintas domain
- [ ] siapkan webhook dan integration log
- [ ] siapkan portal client read-only basic
- [ ] siapkan analytics summary setelah query operasional stabil

---

## PHASE 9 - Add-on Ecosystem

- [ ] siapkan kerangka add-on `recruitment`
- [ ] siapkan kerangka add-on `employee_loan`
- [ ] siapkan kerangka add-on `training`
- [ ] siapkan kerangka add-on `asset`
- [ ] siapkan kerangka add-on `performance`
- [ ] definisikan aturan aktivasi add-on per subscription
- [ ] siapkan dokumentasi contract add-on terhadap core platform

---

## PHASE 10 - Quality, Security, DevOps

- [x] siapkan standar response envelope `success`, `message`, `data`, `meta`, `errors`
- [x] siapkan prefix `/api/v1`
- [x] siapkan integration test bootstrap phase 1
- [x] siapkan integration test scope authorization phase 1.5
- [x] siapkan dev runner auto-reload ala `npm run dev`
- [ ] tambahkan unit test per domain service
- [ ] tambahkan CI untuk compile check dan test
- [ ] tambahkan Dockerfile backend baru
- [ ] tambahkan structured logging
- [ ] tambahkan rate limiting untuk auth endpoint
- [ ] tambahkan secret management yang lebih aman untuk production
- [ ] tambahkan rollback strategy untuk migration

---

## PHASE 11 - Release Readiness Phase 1

- [x] siapkan seed `BASIC`, `PRO`, `ENTERPRISE`
- [x] siapkan seed feature modules inti
- [x] siapkan seed role minimum
- [x] siapkan demo admin dan demo guard
- [x] siapkan scoped demo user untuk phase 1.5
- [x] siapkan dokumen audit source lama
- [ ] validasi endpoint phase 1 terhadap kontrak frontend/mobile
- [ ] review naming final seluruh endpoint dan payload
- [ ] freeze scope phase 1 agar tidak lompat ke Enterprise penuh
- [ ] siapkan baseline tag `v0.1.0-phase1-foundation`
- [ ] siapkan demo flow end-to-end untuk pilot operasional

---

# 🎨 PHASE 11.5 — UI-1 BASIC (DEMO & INTERNAL TEST READY)

## 🎯 Tujuan
Menjadikan HRIS Basic:
> Sudah bisa dilihat, didemokan, dan diuji secara nyata oleh user internal (admin & guard)

Fokus:
- bukan UI sempurna
- tapi UI yang cukup untuk validasi flow bisnis end-to-end
- wajib baca dulu tech_stack.md
---

## 🧩 SCOPE UI YANG WAJIB ADA

### 1. AUTH & BASE LAYOUT
- [ ] halaman login (web admin)
- [ ] simpan token & session
- [ ] proteksi route (auth guard)
- [ ] layout sidebar + header basic
- [ ] tampilkan user profile sederhana

## 🌐 CATATAN UI FOUNDATION
- [ ] siapkan struktur i18n dasar agar UI Basic tidak hardcode text (`id` / `en`)
- [ ] siapkan theme token dasar agar warna/layout tidak hardcode (`theme_1` / `theme_2` / `theme_3` / `theme_4` / `theme_5`)
- [ ] belum wajib aktif 2 bahasa penuh pada phase ini
- [ ] belum wajib aktif 5 tema penuh pada phase ini
- [ ] target phase ini hanya menyiapkan pondasi agar tidak refactor besar saat masuk UI/UX phase berikutnya

---

### 2. DASHBOARD BASIC (WAJIB ADA)
- [ ] total employee
- [ ] total client
- [ ] total site
- [ ] active deployment
- [ ] attendance hari ini
- [ ] present / late / absent

Endpoint:
- `/api/v1/dashboard/ops-summary`

---

### 3. EMPLOYEE MANAGEMENT UI
- [ ] halaman list employee
- [ ] create employee
- [ ] edit employee
- [ ] detail employee
- [ ] filter by branch / status / position

---

### 4. CLIENT, SITE & POST UI
- [ ] list client
- [ ] create/edit client
- [ ] list contract
- [ ] list site
- [ ] create/edit site
- [ ] site posts management

---

### 5. DEPLOYMENT UI (KRITIS)
- [ ] list deployment
- [ ] assign guard ke site
- [ ] end deployment
- [ ] filter by site/client/status

---

### 6. SCHEDULE UI (KRITIS)
- [ ] list schedule (table)
- [ ] generate schedule
- [ ] publish schedule
- [ ] filter by site/post/date
- [ ] optional: calendar sederhana

---

### 7. ATTENDANCE MONITORING UI
- [ ] list attendance
- [ ] filter by date/site/status
- [ ] detail attendance
- [ ] tandai late / absent
- [ ] tampilkan GPS flag sederhana

---

## 📱 MOBILE GUARD (MINIMAL VIABLE UI)

### WAJIB ADA:
- [ ] login
- [ ] lihat jadwal (my schedules)
- [ ] check-in
- [ ] check-out
- [ ] status hadir hari ini

Endpoint:
- `/my/schedules`
- `/attendance/check-in`
- `/attendance/check-out`

---

## 🔗 FLOW YANG HARUS BISA DIUJI

- [ ] create employee
- [ ] create client
- [ ] create site & post
- [ ] assign deployment
- [ ] generate schedule
- [ ] publish schedule
- [ ] guard login mobile
- [ ] guard check-in
- [ ] guard check-out
- [ ] admin lihat attendance di dashboard

---

## 🧪 QA MINIMAL

- [ ] test login admin
- [ ] test login guard
- [ ] test create employee
- [ ] test deployment muncul di schedule
- [ ] test schedule muncul di mobile
- [ ] test check-in masuk ke dashboard
- [ ] test data konsisten

---

## 🚫 BELUM MASUK (PHASE PRO)

- [ ] payroll UI
- [ ] patrol UI
- [ ] incident UI
- [ ] billing UI
- [ ] analytics

---

## 🧭 DEFINISI DONE — UI-1

- [ ] semua modul Basic punya UI minimal
- [ ] flow end-to-end berjalan tanpa error
- [ ] mobile guard bisa check-in real
- [ ] dashboard tampil data real
- [ ] bisa simulasi 1 site operasional

---

# 🎨 PHASE 11.6 — UI FOUNDATION: I18N & THEME READINESS

## 🎯 Tujuan
Menyiapkan pondasi frontend agar dual bahasa dan multi tema bisa ditambahkan tanpa bongkar ulang struktur UI.

## Scope
- [ ] tentukan standar i18n frontend
- [ ] pisahkan text UI ke translation files
- [ ] siapkan struktur `id.json` dan `en.json`
- [ ] siapkan naming key translation yang konsisten
- [ ] siapkan theme tokens / CSS variables / design tokens
- [ ] implementasikan theme system dasar (`theme_1` / `theme_2` / `theme_3` / `theme_4` / `theme_5`)
- [ ] siapkan mekanisme persist preference theme dan language di frontend
- [ ] sinkronkan preferensi user dari backend (`/api/v1/auth/login` dan `/api/v1/auth/me`) ke frontend session
- [ ] implementasikan language switcher basic
- [ ] implementasikan theme switcher basic

## Definisi done
- [ ] text utama UI tidak hardcode
- [ ] bahasa bisa diganti minimal ID / EN
- [ ] tema bisa diganti minimal via switcher
- [ ] preference tersimpan dan terbaca saat login ulang

---

## 🔥 STRATEGI

Basic Backend → Stabil  
→ UI-1 (Demo & Test)  
→ lanjut ke HRIS Pro


## Next

- [ ] lanjutkan phase 1 ke validasi kontrak frontend/mobile, reporting basic, dan hardening auth/access control
- [ ] stabilkan phase 1 sampai layak untuk pilot customer
- [ ] lanjut ke phase PRO setelah fondasi operasional phase 1 benar-benar stabil
- [ ] lanjut ke phase ENTERPRISE setelah kontrak, deployment, schedule, attendance, dan dashboard sudah matang
- [ ] buka add-on ecosystem setelah kontrak domain core sudah final
