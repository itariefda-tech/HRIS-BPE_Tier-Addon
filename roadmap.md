# roadmap.md

## Ringkasan
Dokumen ini adalah **roadmap development coding** untuk aplikasi HRIS khusus perusahaan outsourcing security/satpam.

Roadmap ini disusun agar:
- mudah dipakai tim developer
- jelas urutan implementasinya
- sinkron dengan model produk **HRIS Basic**, **HRIS Pro**, **HRIS Enterprise**, dan **Add-on**
- mudah dijadikan checklist kerja harian/mingguan/sprint

Prinsip utama roadmap ini:

```text
Build by product tier
+ keep business flow intact
+ prepare monetization from early stage
```

Flow inti yang harus tetap terjaga:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Patrol / Incident
→ Payroll
→ Billing
→ Dashboard / Audit
```

---

# 1. ATURAN PENGGUNAAN ROADMAP

Checklist menggunakan format:
- `[ ]` belum dikerjakan
- `[x]` sudah selesai

Disarankan dipakai per:
- sprint mingguan
- milestone per phase
- pembagian backend / frontend / mobile / QA

---

# 2. PHASE 0 — FOUNDATION & PROJECT SETUP

## 2.1 Product foundation
- [ ] finalisasi scope produk HRIS Basic
- [ ] finalisasi scope produk HRIS Pro
- [ ] finalisasi scope produk HRIS Enterprise
- [ ] finalisasi daftar add-on prioritas
- [ ] tetapkan aturan mana yang core module vs add-on
- [ ] tetapkan flow bisnis utama yang tidak boleh terputus

## 2.2 Technical foundation
- [ ] pilih stack backend
- [ ] pilih stack frontend web admin
- [ ] pilih stack mobile app guard/supervisor
- [ ] pilih database utama (PostgreSQL)
- [ ] pilih object storage untuk file/dokumen/foto
- [ ] tentukan struktur monorepo atau multirepo
- [ ] buat standard branching git
- [ ] buat standard environment dev / staging / production
- [ ] buat standard coding style dan linting
- [ ] buat standard API response format
- [ ] buat standard error handling format
- [ ] buat standard logging format

## 2.3 Initial engineering setup
- [ ] inisialisasi repository backend
- [ ] inisialisasi repository frontend web
- [ ] inisialisasi repository mobile
- [ ] setup CI/CD basic
- [ ] setup environment variables management
- [ ] setup migration system
- [ ] setup seed system
- [ ] setup API versioning `/api/v1`
- [ ] setup auth middleware
- [ ] setup RBAC base structure
- [ ] setup audit logging base
- [ ] setup file upload service
- [ ] setup notification abstraction layer

## 2.4 Documentation foundation
- [ ] rapikan README.md
- [ ] rapikan FLOW_system.md
- [ ] rapikan STRUCHTURE_DB-SCHEM.md
- [ ] rapikan API design sesuai phase build
- [ ] sinkronkan breakdown_modul.md dengan roadmap

---

# 3. PHASE 1 — HRIS BASIC (MVP SIAP JUAL)

## Target phase
Menyelesaikan produk **HRIS Basic** yang sudah layak dipakai harian dan sudah bisa dijual.

## 3.1 Core access & organization

### Backend
- [ ] buat migration tabel companies
- [ ] buat migration tabel branches
- [ ] buat migration tabel users
- [ ] buat migration tabel roles
- [ ] buat migration tabel permissions
- [ ] buat migration tabel user_roles
- [ ] buat migration tabel role_permissions
- [ ] buat seeder role default
- [ ] buat endpoint auth login
- [ ] buat endpoint auth logout
- [ ] buat endpoint auth refresh
- [ ] buat endpoint auth me
- [ ] buat endpoint users CRUD
- [ ] buat endpoint roles list
- [ ] buat endpoint permissions list
- [ ] buat policy/authorization per modul dasar

### Frontend Web
- [ ] buat halaman login
- [ ] buat halaman profile user
- [ ] buat halaman manajemen user
- [ ] buat halaman role & permission sederhana
- [ ] buat halaman company profile
- [ ] buat halaman branch management

### QA / Testing
- [ ] test login sukses/gagal
- [ ] test role access per menu
- [ ] test inactive user tidak bisa login

---

## 3.2 Employee & Guard Master

### Backend
- [ ] buat migration tabel departments
- [ ] buat migration tabel positions
- [ ] buat migration tabel employees
- [ ] buat migration tabel employee_emergency_contacts
- [ ] buat migration tabel employee_documents
- [ ] buat migration tabel employee_contracts
- [ ] buat migration tabel guard_profiles
- [ ] buat migration tabel guard_certifications
- [ ] buat endpoint departments CRUD basic
- [ ] buat endpoint positions CRUD basic
- [ ] buat endpoint employees CRUD
- [ ] buat endpoint employee documents upload/list
- [ ] buat endpoint employee contracts CRUD basic
- [ ] buat endpoint emergency contacts CRUD
- [ ] buat endpoint guards CRUD
- [ ] buat validation employee number unique
- [ ] buat validation status kerja dan status employee

### Frontend Web
- [ ] buat halaman list employee
- [ ] buat halaman create/edit employee
- [ ] buat halaman detail employee
- [ ] buat halaman dokumen employee
- [ ] buat halaman kontrak kerja employee
- [ ] buat halaman guard profile
- [ ] buat filter employee by branch/position/status

### Mobile
- [ ] tampilkan profil guard basic

### QA / Testing
- [ ] test create employee
- [ ] test upload dokumen
- [ ] test create guard profile
- [ ] test status employee aktif/nonaktif

---

## 3.3 Client, Contract, Site & Post

### Backend
- [ ] buat migration tabel clients
- [ ] buat migration tabel client_contracts
- [ ] buat migration tabel client_contract_files
- [ ] buat migration tabel client_sites
- [ ] buat migration tabel site_posts
- [ ] buat migration tabel site_manpower_requirements
- [ ] buat endpoint clients CRUD
- [ ] buat endpoint contracts CRUD
- [ ] buat endpoint upload file kontrak
- [ ] buat endpoint sites CRUD
- [ ] buat endpoint site posts CRUD
- [ ] buat endpoint manpower requirements CRUD basic
- [ ] buat validasi kontrak aktif
- [ ] buat validasi site harus terkait client & contract

### Frontend Web
- [ ] buat halaman list client
- [ ] buat halaman create/edit client
- [ ] buat halaman list contract
- [ ] buat halaman detail contract
- [ ] buat halaman upload file kontrak
- [ ] buat halaman list site
- [ ] buat halaman create/edit site
- [ ] buat halaman site posts
- [ ] buat halaman manpower planning basic

### QA / Testing
- [ ] test create client
- [ ] test create contract
- [ ] test create site dan post
- [ ] test manpower planning basic

---

## 3.4 Deployment Management

### Backend
- [ ] buat migration tabel employee_deployments
- [ ] buat migration tabel deployment_histories
- [ ] buat endpoint deployments CRUD
- [ ] buat endpoint end deployment
- [ ] buat endpoint deployment history
- [ ] buat validasi employee aktif sebelum deployment
- [ ] buat validasi tidak ada deployment aktif yang bentrok
- [ ] buat validasi site/post/contract aktif

### Frontend Web
- [ ] buat halaman list deployment
- [ ] buat halaman assign deployment
- [ ] buat halaman end deployment
- [ ] buat halaman history deployment
- [ ] buat filter deployment by site/client/status

### QA / Testing
- [ ] test assign deployment normal
- [ ] test bentrok deployment ditolak
- [ ] test end deployment

---

## 3.5 Shift Type & Schedule Basic

### Backend
- [ ] buat migration tabel shift_types
- [ ] buat migration tabel shift_patterns
- [ ] buat migration tabel shift_pattern_details
- [ ] buat migration tabel work_schedules
- [ ] buat migration tabel shift_change_requests
- [ ] buat endpoint shift types CRUD
- [ ] buat endpoint schedules list/detail/create/update
- [ ] buat endpoint schedules generate basic
- [ ] buat endpoint schedules publish
- [ ] buat validasi shift time dan cross day
- [ ] buat validasi bentrok schedule per employee
- [ ] buat validasi deployment harus aktif pada tanggal schedule

### Frontend Web
- [ ] buat halaman shift type
- [ ] buat halaman list schedule
- [ ] buat halaman calendar/table schedule
- [ ] buat form generate schedule
- [ ] buat action publish schedule
- [ ] buat filter schedule by site/post/employee/date

### Mobile
- [ ] buat halaman lihat jadwal guard

### QA / Testing
- [ ] test create schedule manual
- [ ] test generate schedule
- [ ] test publish schedule
- [ ] test bentrok jadwal ditolak

---

## 3.6 Attendance Basic

### Backend
- [ ] buat migration tabel attendance_records
- [ ] buat migration tabel attendance_exceptions
- [ ] buat migration tabel attendance_manual_adjustments
- [ ] buat endpoint check-in
- [ ] buat endpoint check-out
- [ ] buat endpoint attendance list/detail
- [ ] buat endpoint attendance exceptions list
- [ ] buat endpoint attendance manual adjustment
- [ ] buat validasi hanya bisa check-in untuk jadwal valid
- [ ] buat validasi geofence basic
- [ ] buat validasi check-out tidak boleh sebelum check-in
- [ ] hitung minutes late
- [ ] hitung working minutes
- [ ] hitung overtime minutes basic
- [ ] simpan foto check-in/check-out

### Frontend Web
- [ ] buat halaman monitoring attendance
- [ ] buat halaman detail attendance
- [ ] buat halaman attendance exception
- [ ] buat halaman adjustment attendance basic
- [ ] buat filter attendance by date/site/status

### Mobile
- [ ] buat halaman check-in
- [ ] buat halaman check-out
- [ ] tampilkan status hadir hari ini
- [ ] tampilkan histori attendance sederhana
- [ ] tampilkan validasi GPS/geofence ke user

### QA / Testing
- [ ] test check-in normal
- [ ] test check-in di luar geofence
- [ ] test check-out normal
- [ ] test double check-in ditangani
- [ ] test adjustment attendance

---

## 3.7 Dashboard & Reporting Basic

### Backend
- [ ] buat endpoint dashboard ops summary
- [ ] buat endpoint laporan employee basic
- [ ] buat endpoint laporan deployment basic
- [ ] buat endpoint laporan schedule basic
- [ ] buat endpoint laporan attendance basic
- [ ] buat export CSV/Excel basic

### Frontend Web
- [ ] buat dashboard basic
- [ ] tampilkan active site
- [ ] tampilkan scheduled guard
- [ ] tampilkan present guard
- [ ] tampilkan late guard
- [ ] tampilkan absent guard
- [ ] buat halaman reporting basic

### QA / Testing
- [ ] test angka dashboard sesuai data
- [ ] test export laporan basic

---

## 3.8 Release readiness HRIS Basic
- [ ] audit seluruh flow Basic end-to-end
- [ ] test flow employee → deployment → schedule → attendance
- [ ] siapkan demo data Basic
- [ ] siapkan script seeding demo tenant
- [ ] siapkan panduan onboarding customer Basic
- [ ] siapkan bug fixing sprint
- [ ] siapkan release candidate HRIS Basic

---

# 4. PHASE 2 — HRIS PRO

## Target phase
Menyelesaikan **HRIS Pro** sebagai paket operasional paling kuat dan paling layak jadi best seller.

## 4.1 Leave, Permission & Replacement

### Backend
- [ ] buat migration tabel leave_types
- [ ] buat migration tabel leave_requests
- [ ] buat migration tabel replacement_requests
- [ ] buat migration tabel standby_pools
- [ ] buat endpoint leave types list
- [ ] buat endpoint leave requests CRUD dasar
- [ ] buat endpoint approve/reject leave
- [ ] buat endpoint replacement requests CRUD dasar
- [ ] buat endpoint approve/reject replacement
- [ ] buat endpoint standby pool list/manage
- [ ] buat validasi replacement terhadap jadwal aktif
- [ ] update schedule jika replacement disetujui

### Frontend Web
- [ ] buat halaman leave requests
- [ ] buat halaman replacement requests
- [ ] buat halaman standby pool
- [ ] buat halaman approval leave/replacement

### Mobile
- [ ] buat form pengajuan izin/cuti dasar
- [ ] tampilkan status pengajuan

### QA / Testing
- [ ] test approval leave
- [ ] test replacement update jadwal
- [ ] test standby guard bisa dipilih

---

## 4.2 Patrol / Guard Tour Basic

### Backend
- [ ] buat migration tabel patrol_routes
- [ ] buat migration tabel patrol_checkpoints
- [ ] buat migration tabel patrol_sessions
- [ ] buat migration tabel patrol_logs
- [ ] buat endpoint patrol routes CRUD
- [ ] buat endpoint patrol checkpoints CRUD
- [ ] buat endpoint patrol session start
- [ ] buat endpoint patrol session scan
- [ ] buat endpoint patrol session finish
- [ ] buat endpoint patrol sessions list/detail
- [ ] buat validasi checkpoint harus milik route yang sama
- [ ] buat validasi session harus aktif
- [ ] buat deteksi missed checkpoint basic

### Frontend Web
- [ ] buat halaman patrol routes
- [ ] buat halaman patrol checkpoints
- [ ] buat halaman monitoring patrol session
- [ ] buat halaman log patroli

### Mobile
- [ ] buat halaman mulai patroli
- [ ] buat halaman scan checkpoint
- [ ] buat halaman selesai patroli
- [ ] tampilkan daftar checkpoint dan progress

### QA / Testing
- [ ] test start patrol
- [ ] test scan checkpoint valid
- [ ] test checkpoint salah ditolak
- [ ] test missed checkpoint terdeteksi

---

## 4.3 Incident Control & Report

### Backend
- [ ] buat migration tabel incident_categories
- [ ] buat migration tabel incidents
- [ ] buat migration tabel incident_files
- [ ] buat migration tabel incident_follow_ups
- [ ] buat endpoint incident categories CRUD basic
- [ ] buat endpoint incidents CRUD
- [ ] buat endpoint upload incident file
- [ ] buat endpoint incident follow-up
- [ ] buat endpoint close incident
- [ ] buat validasi severity dan status incident
- [ ] buat notifikasi incident ke supervisor

### Frontend Web
- [ ] buat halaman list incident
- [ ] buat halaman detail incident
- [ ] buat halaman follow-up incident
- [ ] buat filter incident by site/severity/status/date

### Mobile
- [ ] buat form incident report
- [ ] buat upload bukti incident
- [ ] buat lihat histori incident sendiri

### QA / Testing
- [ ] test create incident
- [ ] test upload bukti
- [ ] test follow-up incident
- [ ] test close incident

---

## 4.4 Approval Workflow Basic

### Backend
- [ ] buat struktur approval status umum
- [ ] tambahkan approval attendance adjustment
- [ ] tambahkan approval leave
- [ ] tambahkan approval replacement
- [ ] tambahkan approval incident closure
- [ ] tambahkan approval payroll draft
- [ ] buat notification trigger saat approval dibutuhkan

### Frontend Web
- [ ] buat inbox approval sederhana
- [ ] buat halaman approval per modul

### Mobile
- [ ] tampilkan status approval request user

### QA / Testing
- [ ] test approval flow tiap modul dasar
- [ ] test rejection flow tiap modul dasar

---

## 4.5 Payroll Basic

### Backend
- [ ] buat migration tabel payroll_periods
- [ ] buat migration tabel payroll_components
- [ ] buat migration tabel payroll_employee_summaries
- [ ] buat migration tabel payroll_employee_component_values
- [ ] buat migration tabel payslips
- [ ] buat endpoint payroll periods CRUD
- [ ] buat endpoint process payroll
- [ ] buat endpoint payroll employee summary
- [ ] buat endpoint payroll adjustment component basic
- [ ] buat endpoint approve payroll employee
- [ ] buat endpoint approve payroll period
- [ ] buat endpoint payslips list/detail
- [ ] buat endpoint publish payslip
- [ ] hitung basic salary
- [ ] hitung tunjangan tetap
- [ ] hitung tunjangan kehadiran
- [ ] hitung lembur dasar
- [ ] hitung BPJS dasar
- [ ] hitung PPh21 dasar
- [ ] hitung potongan dasar
- [ ] hitung net salary

### Frontend Web
- [ ] buat halaman payroll period
- [ ] buat halaman proses payroll
- [ ] buat halaman review payroll employee
- [ ] buat halaman payroll approval
- [ ] buat halaman payslip list

### Mobile
- [ ] buat halaman lihat payslip basic

### QA / Testing
- [ ] test proses payroll 1 periode
- [ ] test payroll recalculate
- [ ] test publish payslip
- [ ] test perhitungan payroll basic sesuai sample

---

## 4.6 Notification & Escalation Basic

### Backend
- [ ] buat migration tabel system_notifications
- [ ] buat notification no check-in
- [ ] buat notification late check-in
- [ ] buat notification incident baru
- [ ] buat notification approval pending
- [ ] buat notification missed patrol basic

### Frontend Web
- [ ] buat notification center web

### Mobile
- [ ] tampilkan notification list basic

### QA / Testing
- [ ] test notification terkirim untuk trigger utama

---

## 4.7 Dashboard & Reporting Pro

### Backend
- [ ] buat endpoint laporan patrol
- [ ] buat endpoint laporan incident
- [ ] buat endpoint laporan replacement
- [ ] buat endpoint laporan payroll
- [ ] buat endpoint dashboard supervisor/ops

### Frontend Web
- [ ] buat supervisor dashboard
- [ ] tampilkan open incident
- [ ] tampilkan missed patrol
- [ ] tampilkan replacement pending
- [ ] tampilkan payroll pending approval
- [ ] buat halaman reporting pro

### QA / Testing
- [ ] test dashboard pro
- [ ] test export laporan pro

---

## 4.8 Release readiness HRIS Pro
- [ ] audit flow Basic + Pro end-to-end
- [ ] test flow absence → replacement → schedule update
- [ ] test flow patrol → incident → follow-up
- [ ] test flow attendance → payroll → payslip
- [ ] siapkan demo data HRIS Pro
- [ ] siapkan bug fixing sprint Pro
- [ ] siapkan release candidate HRIS Pro

---

# 5. PHASE 3 — HRIS ENTERPRISE

## Target phase
Menyelesaikan **HRIS Enterprise** sebagai platform kontrol operasional dan keuangan end-to-end.

## 5.1 Billing & Invoice Management

### Backend
- [ ] buat migration tabel billing_rules
- [ ] buat migration tabel invoices
- [ ] buat migration tabel invoice_items
- [ ] buat migration tabel client_payments
- [ ] buat endpoint billing rules CRUD
- [ ] buat endpoint generate invoice
- [ ] buat endpoint invoice list/detail/update
- [ ] buat endpoint issue invoice
- [ ] buat endpoint mark invoice sent
- [ ] buat endpoint input payment
- [ ] hitung subtotal invoice
- [ ] hitung tax amount
- [ ] hitung penalty amount basic
- [ ] hitung grand total
- [ ] validasi periode invoice tidak overlap

### Frontend Web
- [ ] buat halaman billing rules
- [ ] buat halaman invoice list
- [ ] buat halaman invoice detail
- [ ] buat halaman generate invoice
- [ ] buat halaman payment tracking
- [ ] buat aging piutang basic

### QA / Testing
- [ ] test generate invoice
- [ ] test input pembayaran
- [ ] test due date tracking
- [ ] test overlap billing ditolak

---

## 5.2 Advanced Approval Workflow

### Backend
- [ ] rancang approval matrix per modul
- [ ] implement maker-checker basic
- [ ] implement multi-level approval
- [ ] implement conditional approval basic
- [ ] implement escalation path basic

### Frontend Web
- [ ] buat halaman approval matrix
- [ ] buat monitoring approval berlapis

### QA / Testing
- [ ] test multi-level approval payroll
- [ ] test multi-level approval billing

---

## 5.3 Audit Log & Compliance

### Backend
- [ ] buat migration tabel audit_logs
- [ ] log create/update/delete entity penting
- [ ] log perubahan attendance
- [ ] log perubahan deployment
- [ ] log perubahan payroll
- [ ] log perubahan billing
- [ ] tambahkan created_by / updated_by pada tabel prioritas
- [ ] tambahkan soft delete support pada modul sensitif
- [ ] tambahkan version_no support pada modul prioritas

### Frontend Web
- [ ] buat halaman audit logs
- [ ] buat filter audit per modul/user/action/date

### QA / Testing
- [ ] test audit log tercatat untuk perubahan kritis
- [ ] test soft delete data sensitif

---

## 5.4 Analytics & Management Dashboard

### Backend
- [ ] buat endpoint finance summary
- [ ] buat endpoint site performance
- [ ] buat endpoint revenue per client
- [ ] buat endpoint margin per site
- [ ] buat endpoint attendance trend
- [ ] buat endpoint incident trend
- [ ] buat endpoint patrol compliance trend
- [ ] buat endpoint outstanding invoice insight

### Frontend Web
- [ ] buat management dashboard
- [ ] buat finance dashboard
- [ ] buat grafik revenue per client
- [ ] buat grafik margin per site
- [ ] buat trend attendance/incident/patrol

### QA / Testing
- [ ] test konsistensi angka analytics
- [ ] test filter analytics per periode/site/client

---

## 5.5 Multi Branch / Multi Region / Multi Company

### Backend
- [ ] refactor company scope support
- [ ] refactor branch scope support
- [ ] tambah regional grouping basic
- [ ] tambah site-scope access
- [ ] tambah branch-scope access
- [ ] validasi akses data berdasarkan scope

### Frontend Web
- [ ] buat filter multi-branch
- [ ] buat mapping regional/area
- [ ] buat UI pembatasan akses berdasarkan scope

### QA / Testing
- [ ] test user hanya melihat data sesuai scope

---

## 5.6 Enterprise Security & Access Control

### Backend
- [ ] granular permission per action
- [ ] site-scope policy enforcement
- [ ] branch-scope policy enforcement
- [ ] device restriction basic
- [ ] IP restriction basic
- [ ] SSO readiness design

### Frontend Web
- [ ] buat halaman permission advanced
- [ ] buat pengaturan security policy basic

### QA / Testing
- [ ] test permission granular
- [ ] test policy restriction

---

## 5.7 Client Portal Basic

### Backend
- [ ] buat auth terpisah atau portal access model
- [ ] buat endpoint portal invoice summary
- [ ] buat endpoint portal attendance summary
- [ ] buat endpoint portal incident summary
- [ ] buat endpoint portal SLA summary basic
- [ ] buat endpoint download laporan periodik

### Frontend Web / Portal
- [ ] buat halaman login client portal
- [ ] buat dashboard client portal
- [ ] buat halaman invoice portal
- [ ] buat halaman report portal

### QA / Testing
- [ ] test client hanya bisa lihat datanya sendiri

---

## 5.8 API & Integration Readiness

### Backend
- [ ] rapikan dokumentasi API publik/internal
- [ ] buat API token management basic
- [ ] buat webhook basic
- [ ] buat import/export template enterprise
- [ ] buat event log untuk integration basic

### QA / Testing
- [ ] test API token access
- [ ] test webhook trigger basic

---

## 5.9 Advanced Reporting

### Backend
- [ ] scheduled report generation basic
- [ ] report by client
- [ ] report by site
- [ ] report by period
- [ ] executive summary report basic

### Frontend Web
- [ ] buat halaman advanced reporting
- [ ] buat pengaturan schedule report

### QA / Testing
- [ ] test schedule report
- [ ] test export PDF/Excel enterprise

---

## 5.10 Release readiness HRIS Enterprise
- [ ] audit flow end-to-end operation → payroll → billing
- [ ] test flow contract → billing rules → invoice → payment
- [ ] test flow analytics dari data nyata
- [ ] test audit enterprise
- [ ] siapkan demo data enterprise
- [ ] siapkan bug fixing sprint Enterprise
- [ ] siapkan release candidate HRIS Enterprise

---

# 6. PHASE 4 — ADD-ON PRIORITAS TINGGI

## Target phase
Menambah mesin upsell tanpa merusak core tier.

## 6.1 Recruitment System

### Backend
- [ ] rancang entity recruitment
- [ ] buat manpower request basic
- [ ] buat candidate master
- [ ] buat screening status
- [ ] buat interview tracking
- [ ] buat offering/onboarding pipeline basic

### Frontend Web
- [ ] buat halaman candidate list
- [ ] buat halaman recruitment pipeline

### QA / Testing
- [ ] test flow kandidat sampai onboarding

---

## 6.2 Employee Loan / Dana Talangan

### Backend
- [ ] rancang entity employee loan
- [ ] buat pengajuan pinjaman
- [ ] buat approval pinjaman
- [ ] buat tenor & jadwal cicilan
- [ ] integrasikan potongan ke payroll
- [ ] buat histori pinjaman

### Frontend Web
- [ ] buat halaman loan request
- [ ] buat halaman approval loan
- [ ] buat halaman histori pinjaman

### Mobile
- [ ] buat form pengajuan dana talangan
- [ ] tampilkan status cicilan

### QA / Testing
- [ ] test loan approved masuk payroll deduction

---

## 6.3 Asset & Uniform Management

### Backend
- [ ] rancang entity asset & handover
- [ ] buat master asset
- [ ] buat assignment asset ke employee/site
- [ ] buat histori serah terima
- [ ] buat status asset

### Frontend Web
- [ ] buat halaman asset master
- [ ] buat halaman assignment asset
- [ ] buat halaman histori asset

### QA / Testing
- [ ] test assign & return asset

---

## 6.4 Training & Certification

### Backend
- [ ] buat master training
- [ ] buat training history
- [ ] buat certification tracking
- [ ] buat expiry reminder logic

### Frontend Web
- [ ] buat halaman training
- [ ] buat halaman certification tracking

### Mobile
- [ ] tampilkan sertifikasi user basic

### QA / Testing
- [ ] test reminder sertifikat habis

---

## 6.5 Reimbursement & Claim

### Backend
- [ ] buat entity reimbursement claim
- [ ] buat submit claim
- [ ] buat approval claim
- [ ] buat integrasi ke payroll/payable basic

### Frontend Web
- [ ] buat halaman claim
- [ ] buat approval claim

### Mobile
- [ ] buat submit claim basic

### QA / Testing
- [ ] test approval claim

---

## 6.6 Visitor / Logbook Digital

### Backend
- [ ] buat entity digital logbook
- [ ] buat visitor log
- [ ] buat vehicle log
- [ ] buat serah terima shift note
- [ ] buat daily site note

### Frontend Web
- [ ] buat halaman logbook site

### Mobile
- [ ] buat input logbook basic

### QA / Testing
- [ ] test input logbook dan visitor

---

## 6.7 Performance & Discipline

### Backend
- [ ] buat entity KPI guard
- [ ] buat entity pelanggaran
- [ ] buat warning letter basic
- [ ] buat reward/punishment basic

### Frontend Web
- [ ] buat halaman performance guard
- [ ] buat halaman disciplinary action

### QA / Testing
- [ ] test input pelanggaran

---

## 6.8 Notification Suite Advanced

### Backend
- [ ] tambahkan email notification
- [ ] tambahkan push notification abstraction
- [ ] siapkan WhatsApp notification readiness
- [ ] reminder shift
- [ ] reminder sertifikat habis
- [ ] alert invoice jatuh tempo

### QA / Testing
- [ ] test reminder dan alert advanced

---

# 7. PHASE 5 — ADVANCED ENTERPRISE ADD-ON

## 7.1 Payroll Advanced
- [ ] payroll formula custom
- [ ] payroll component template
- [ ] rapel
- [ ] THR
- [ ] bonus
- [ ] payroll simulation
- [ ] bank transfer export

## 7.2 Billing Advanced
- [ ] formula billing kompleks
- [ ] split billing
- [ ] penalty SLA billing
- [ ] multi-rate billing
- [ ] tax scenario
- [ ] custom invoice template

## 7.3 Patrol Advanced
- [ ] dynamic patrol schedule
- [ ] GPS checkpoint verification advanced
- [ ] photo proof patrol
- [ ] route compliance scoring
- [ ] real-time patrol dashboard

## 7.4 Incident Command Center
- [ ] escalation matrix
- [ ] incident SLA timer
- [ ] incident war room board
- [ ] response time tracking
- [ ] root cause & corrective action

## 7.5 SLA & Compliance Monitoring
- [ ] SLA matrix
- [ ] manpower compliance
- [ ] patrol compliance
- [ ] incident response compliance
- [ ] attendance compliance
- [ ] site scoring

## 7.6 Client Portal Advanced
- [ ] client dashboard advanced
- [ ] complaint/request channel
- [ ] kontrak & dokumen portal
- [ ] payment status detail
- [ ] incident & patrol summary

## 7.7 API & Integration Pack
- [ ] open API pack
- [ ] accounting integration readiness
- [ ] attendance device integration readiness
- [ ] import/export connector
- [ ] enterprise webhook expansion

---

# 8. CROSS-FUNCTION CHECKLIST

## 8.1 Security
- [ ] semua endpoint pakai auth
- [ ] semua endpoint sensitif pakai authorization
- [ ] sanitasi upload file
- [ ] rate limit login
- [ ] password hashing kuat
- [ ] audit untuk perubahan sensitif

## 8.2 Performance
- [ ] tambah index untuk query utama
- [ ] optimasi query attendance
- [ ] optimasi query schedule
- [ ] optimasi query payroll
- [ ] optimasi query billing
- [ ] cache untuk dashboard bila perlu

## 8.3 Quality assurance
- [ ] unit test service utama
- [ ] integration test API kritis
- [ ] end-to-end test flow utama
- [ ] regression test sebelum release tiap phase

## 8.4 DevOps
- [ ] staging environment stabil
- [ ] backup database strategy
- [ ] log monitoring
- [ ] error tracking
- [ ] release tagging
- [ ] rollback plan

## 8.5 Product readiness
- [ ] seed demo data per tier
- [ ] demo script sales per tier
- [ ] onboarding checklist customer Basic
- [ ] onboarding checklist customer Pro
- [ ] onboarding checklist customer Enterprise

---

# 9. URUTAN PRIORITAS PALING DISARANKAN

## Prioritas build level produk
- [ ] selesaikan HRIS Basic penuh terlebih dahulu
- [ ] stabilkan HRIS Basic sebelum masuk Pro
- [ ] selesaikan HRIS Pro sebagai paket revenue utama
- [ ] bangun HRIS Enterprise setelah flow Pro stabil
- [ ] kembangkan add-on setelah tier inti kokoh

## Prioritas build level teknis
- [ ] backend domain core dulu
- [ ] frontend admin core dulu
- [ ] mobile guard fokus jadwal + attendance dulu
- [ ] reporting dan dashboard setelah transaksi inti stabil
- [ ] analytics setelah data cukup matang

---

# 10. DEFINISI DONE PER TIER

## HRIS Basic dianggap selesai jika:
- [ ] employee master stabil
- [ ] client/contract/site/post stabil
- [ ] deployment stabil
- [ ] schedule stabil
- [ ] attendance stabil
- [ ] dashboard basic stabil
- [ ] flow end-to-end Basic lolos UAT

## HRIS Pro dianggap selesai jika:
- [ ] leave/replacement stabil
- [ ] patrol stabil
- [ ] incident stabil
- [ ] payroll basic stabil
- [ ] notification basic stabil
- [ ] flow Pro lolos UAT

## HRIS Enterprise dianggap selesai jika:
- [ ] billing stabil
- [ ] audit stabil
- [ ] analytics stabil
- [ ] multi-level approval stabil
- [ ] client portal basic stabil
- [ ] flow Enterprise lolos UAT

---

# 11. KESIMPULAN

Roadmap ini dibuat agar tim tidak sekadar membangun fitur, tetapi membangun produk yang siap dijual bertahap:

```text
Phase 1 = HRIS Basic
Phase 2 = HRIS Pro
Phase 3 = HRIS Enterprise
Phase 4 = Add-on Core
Phase 5 = Add-on Enterprise Advanced
```

Dengan format checklist ini, roadmap bisa langsung dipakai untuk:
- sprint planning
- pembagian task developer
- review progress founder/product owner
- persiapan milestone rilis
