# breakdown_modul.md

## Ringkasan
Dokumen ini menjabarkan **breakdown modul produk** untuk aplikasi HRIS khusus perusahaan outsourcing security/satpam dengan model paket:

- **HRIS Basic**
- **HRIS Pro**
- **HRIS Enterprise**
- **Add-on Module**

Tujuan dokumen ini:
- menjadi acuan packaging produk
- membantu prioritas development per tier
- menjaga agar produk tetap utuh secara bisnis
- memudahkan strategi pricing, upsell, dan roadmap implementasi

---

# 1. PRINSIP PENYUSUNAN PAKET

Produk ini tidak diposisikan sebagai HRIS umum, tetapi sebagai:

```text
HR Core + Operational Control + Payroll Engine + Billing Engine
```

Karena itu, pembagian paket tidak boleh memutus alur bisnis utama.

## Alur inti yang harus dijaga

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Patrol / Incident
→ Payroll
→ Billing
→ Dashboard
```

Prinsip packaging:
1. **Basic harus usable**, bukan sekadar demo.
2. **Pro harus menjadi paket operasional paling laku**.
3. **Enterprise harus unggul di kontrol, integrasi, audit, dan analytics**.
4. **Add-on dipakai untuk monetisasi bertahap**, bukan untuk membuat sistem inti menjadi kosong.

---

# 2. STRATEGI TIER PRODUK

## 2.1 HRIS Basic
Posisi:
- untuk perusahaan kecil–menengah
- baru migrasi dari Excel / WhatsApp / sistem manual
- butuh digitalisasi inti operasional dan HR dasar

## 2.2 HRIS Pro
Posisi:
- untuk perusahaan outsourcing security yang sudah aktif operasional di banyak site
- butuh kontrol lapangan lebih kuat
- butuh payroll yang mulai rapi dan tidak manual penuh

## 2.3 HRIS Enterprise
Posisi:
- untuk perusahaan besar / multi-cabang / multi-area / multi-klien
- butuh governance, finance control, integrasi, dan analytics mendalam

## 2.4 Add-on
Posisi:
- modul tambahan yang bisa dibeli bertahap
- dipakai untuk upsell tanpa harus upgrade total paket
- cocok untuk kebutuhan spesifik atau tahap ekspansi bisnis

---

# 3. DAFTAR MODUL UTAMA PRODUK

Modul besar sistem:

1. Organization & Multi Branch
2. User, Role & Permission
3. Employee & Guard Master
4. Recruitment & Onboarding
5. Employee Document & Legal
6. Client Management
7. Contract Management
8. Site & Post Management
9. Manpower Planning
10. Deployment Management
11. Shift & Schedule Management
12. Attendance Management
13. Leave, Permission & Replacement
14. Patrol / Guard Tour
15. Incident Control & Report
16. Payroll
17. Billing & Invoice
18. Employee Loan / Dana Talangan
19. Asset & Uniform Management
20. Training & Certification
21. Performance & Discipline
22. Dashboard & Reporting
23. Notification & Escalation
24. Audit Log & Compliance
25. Client Portal
26. API & Integration

---

# 4. BREAKDOWN MODUL PER TIER

# 4.1 HRIS BASIC

## Tujuan paket
Memberikan pondasi HR dan operasional dasar yang sudah cukup dipakai harian.

## Modul yang termasuk

### 1. Organization & Branch Basic
Fungsi:
- company profile
- branch/cabang
- data struktur organisasi sederhana

Fitur inti:
- master company
- master branch
- status aktif/nonaktif

---

### 2. User, Role & Permission Basic
Fungsi:
- mengatur akun login dasar
- membatasi akses berdasarkan peran utama

Fitur inti:
- login/logout
- user management
- role standar
- permission sederhana berbasis modul

Role minimum:
- super admin
- HR admin
- ops admin
- supervisor
- finance admin
- guard

---

### 3. Employee & Guard Master
Fungsi:
- menyimpan data induk seluruh karyawan dan satpam

Fitur inti:
- employee master
- guard profile
- data identitas
- status kerja
- nomor induk karyawan
- data kontak darurat

---

### 4. Employee Document & Legal Basic
Fungsi:
- menyimpan dokumen dasar karyawan

Fitur inti:
- upload KTP
- upload BPJS
- upload NPWP
- upload kontrak kerja
- masa berlaku dokumen dasar

---

### 5. Client Management Basic
Fungsi:
- mengelola data klien

Fitur inti:
- master client
- contact person
- status client
- alamat penagihan dasar

---

### 6. Contract Management Basic
Fungsi:
- mencatat kontrak layanan utama

Fitur inti:
- nomor kontrak
- periode kontrak
- jenis kontrak
- status kontrak
- upload file kontrak

---

### 7. Site & Post Management
Fungsi:
- membentuk struktur operasional lapangan

Fitur inti:
- data site
- data post/pos jaga
- alamat site
- geofence sederhana
- status operasional site

---

### 8. Manpower Planning Basic
Fungsi:
- menentukan kebutuhan personel sederhana per site/post

Fitur inti:
- kebutuhan headcount
- mapping post ke shift dasar
- kebutuhan posisi dasar

---

### 9. Deployment Management
Fungsi:
- menempatkan guard ke site dan post tertentu

Fitur inti:
- assign guard ke site
- assign guard ke post
- start/end deployment
- status deployment
- histori deployment sederhana

---

### 10. Shift Type & Schedule Basic
Fungsi:
- membuat dan mempublikasikan jadwal kerja

Fitur inti:
- master shift type
- jadwal manual
- generate jadwal sederhana
- publish jadwal
- lihat jadwal guard

---

### 11. Attendance Basic
Fungsi:
- mencatat kehadiran dasar lapangan

Fitur inti:
- check-in/check-out
- GPS attendance basic
- geofence validation basic
- foto check-in/check-out
- daftar hadir
- telat / hadir / tidak hadir
- adjustment manual sederhana

---

### 12. Dashboard Basic
Fungsi:
- memberikan visibilitas operasional inti

Fitur inti:
- active site
- scheduled guard
- present guard
- late guard
- absent guard

---

### 13. Reporting Basic
Fungsi:
- export laporan dasar

Fitur inti:
- laporan employee
- laporan deployment
- laporan jadwal
- laporan attendance

---

## Nilai jual HRIS Basic
Cocok untuk user yang ingin keluar dari cara kerja manual, tapi belum butuh payroll kompleks, patroli canggih, dan billing otomatis.

## Batasan HRIS Basic
Belum fokus pada:
- patrol system penuh
- incident management lengkap
- payroll engine
- billing engine
- audit enterprise
- integrasi eksternal

---

# 4.2 HRIS PRO

## Tujuan paket
Menjadi paket operasional lengkap untuk perusahaan outsourcing security yang ingin kontrol lapangan lebih ketat.

## Semua modul Basic termasuk, ditambah:

### 1. Leave, Permission & Replacement
Fungsi:
- mengelola izin, cuti, dan pengganti personel

Fitur inti:
- leave request
- izin tidak masuk
- replacement request
- standby pool
- approval replacement
- update jadwal akibat pengganti

---

### 2. Patrol / Guard Tour Basic
Fungsi:
- memastikan patroli lapangan benar-benar dilakukan

Fitur inti:
- patrol route
- checkpoint
- patrol session
- scan QR / NFC basic
- log patroli
- missed checkpoint detection basic

---

### 3. Incident Control & Report
Fungsi:
- mencatat dan mengelola kejadian di lapangan

Fitur inti:
- incident report
- kategori incident
- severity level
- upload bukti foto/file
- follow-up incident
- close incident
- histori incident

---

### 4. Approval Workflow Basic
Fungsi:
- mengontrol perubahan penting

Fitur inti:
- approval attendance adjustment
- approval leave
- approval replacement
- approval incident closure
- approval payroll draft

---

### 5. Payroll Basic
Fungsi:
- menghitung gaji berdasarkan data operasional

Fitur inti:
- payroll period
- komponen gaji dasar
- basic salary
- tunjangan tetap
- tunjangan kehadiran
- lembur dasar
- potongan dasar
- BPJS dasar
- PPh21 dasar
- payroll approval
- payslip publish

---

### 6. Reporting Pro
Fungsi:
- menyediakan laporan operasional yang lebih detail

Fitur inti:
- laporan attendance detail
- laporan incident
- laporan patrol
- laporan replacement
- laporan payroll
- export Excel/PDF dasar

---

### 7. Notification & Escalation Basic
Fungsi:
- memberi alert untuk kejadian penting

Fitur inti:
- no check-in alert
- late check-in alert
- incident alert
- approval notification
- missed patrol alert basic

---

### 8. Supervisor & Ops Dashboard
Fungsi:
- memperkuat kontrol operasional harian

Fitur inti:
- site yang kekurangan personel
- open incident
- missed patrol
- replacement pending
- payroll pending approval

---

## Nilai jual HRIS Pro
Ini adalah paket yang paling logis menjadi **best seller**, karena user sudah mendapatkan:
- HR dasar
- operasional site
- patroli
- incident
- replacement
- payroll dasar

## Batasan HRIS Pro
Belum fokus penuh pada:
- billing otomatis lengkap
- analytics profitability
- multi-level approval kompleks
- audit detail enterprise
- client portal
- integrasi enterprise

---

# 4.3 HRIS ENTERPRISE

## Tujuan paket
Memberikan kontrol penuh untuk perusahaan besar dengan kebutuhan governance, finance, analytics, dan integrasi.

## Semua modul Pro termasuk, ditambah:

### 1. Billing & Invoice Management
Fungsi:
- mengubah data kontrak dan operasional menjadi tagihan ke klien

Fitur inti:
- billing rules
- invoice generation
- invoice items
- overtime billing
- holiday billing
- payment tracking
- due date tracking
- aging piutang dasar

---

### 2. Advanced Approval Workflow
Fungsi:
- mendukung approval berlapis dan governance yang lebih ketat

Fitur inti:
- multi-level approval
- maker-checker
- conditional approval
- escalation path
- approval matrix per modul

---

### 3. Audit Log & Compliance
Fungsi:
- memastikan semua perubahan penting dapat ditelusuri

Fitur inti:
- audit log detail
- histori perubahan data sensitif
- created_by / updated_by
- soft delete support
- versioning support
- tracking perubahan payroll, billing, attendance, deployment

---

### 4. Analytics & Management Dashboard
Fungsi:
- membantu owner/direksi melihat performa bisnis dan operasional

Fitur inti:
- revenue per client
- margin per site
- profitability per kontrak
- attendance trend
- incident trend
- patrol compliance trend
- payroll cost insight
- outstanding invoice insight

---

### 5. Multi Branch / Multi Region / Multi Company Support
Fungsi:
- mendukung struktur organisasi yang lebih kompleks

Fitur inti:
- hierarchy cabang
- area/regional grouping
- multi company group
- policy per branch/region
- akses berbasis scope area/site

---

### 6. Enterprise Security & Access Control
Fungsi:
- meningkatkan keamanan penggunaan sistem

Fitur inti:
- granular permission
- site-scope access
- branch-scope access
- optional SSO readiness
- device restriction basic
- IP restriction basic

---

### 7. Client Portal
Fungsi:
- memberi akses terbatas untuk klien

Fitur inti:
- lihat invoice
- lihat attendance summary
- lihat incident report
- lihat SLA summary
- download laporan periodik

---

### 8. API & Integration Readiness
Fungsi:
- memungkinkan koneksi dengan sistem lain

Fitur inti:
- API access
- webhook basic
- integration endpoint
- export/import template enterprise

---

### 9. Advanced Reporting
Fungsi:
- reporting formal untuk operasional dan manajemen

Fitur inti:
- scheduled report
- report by client
- report by site
- report by period
- executive summary report
- KPI summary

---

## Nilai jual HRIS Enterprise
Paket ini cocok untuk perusahaan yang ingin menjadikan sistem sebagai pusat kontrol operasi dan keuangan, bukan sekadar aplikasi absensi atau HR.

---

# 5. ADD-ON MODULE

Add-on disusun agar customer bisa upgrade bertahap tanpa wajib langsung pindah tier penuh.

# 5.1 Recruitment System

## Fungsi
Mengelola proses rekrutmen dari kandidat sampai siap onboarding.

## Fitur
- manpower request
- lowongan kerja
- database kandidat
- screening administrasi
- interview tracking
- medical check tracking
- background check
- offering & onboarding pipeline

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.2 Employee Loan / Dana Talangan

## Fungsi
Mengelola pinjaman atau dana talangan karyawan yang dipotong dari payroll.

## Fitur
- pengajuan pinjaman
- approval pinjaman
- nominal & tenor
- jadwal cicilan
- potong payroll otomatis
- histori pinjaman
- status pelunasan

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.3 Billing Advanced

## Fungsi
Memperdalam billing untuk kebutuhan kontrak dan penagihan yang lebih kompleks.

## Fitur
- formula billing kompleks
- penalty SLA billing
- split billing
- multi-rate billing
- invoice approval
- tax scenario
- custom invoice template

## Cocok untuk
- Pro
- Enterprise

---

# 5.4 Payroll Advanced

## Fungsi
Menambah fleksibilitas payroll untuk organisasi besar.

## Fitur
- payroll formula custom
- payroll component template
- rapel
- THR
- bonus
- payroll simulation
- approval berlapis
- bank transfer export

## Cocok untuk
- Pro
- Enterprise

---

# 5.5 Patrol Advanced

## Fungsi
Meningkatkan kualitas kontrol patroli lapangan.

## Fitur
- dynamic patrol schedule
- missed patrol analytics
- real-time patrol dashboard
- GPS checkpoint verification
- photo proof patrol
- route compliance scoring

## Cocok untuk
- Pro
- Enterprise

---

# 5.6 Incident Command Center

## Fungsi
Meningkatkan penanganan insiden yang lebih terstruktur.

## Fitur
- escalation matrix
- incident SLA timer
- incident war room board
- incident category severity matrix
- response time tracking
- root cause & corrective action

## Cocok untuk
- Pro
- Enterprise

---

# 5.7 Reimbursement & Claim

## Fungsi
Mengelola klaim biaya operasional atau personal yang sah.

## Fitur
- klaim transport
- klaim operasional lapangan
- upload bukti
- approval claim
- integrasi ke payroll/payable

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.8 Training & Certification

## Fungsi
Mengelola pelatihan dan sertifikasi personel security.

## Fitur
- master training
- training history
- sertifikasi satpam
- masa berlaku sertifikat
- reminder expiry
- training matrix per site/risk

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.9 Asset & Uniform Management

## Fungsi
Mengelola perlengkapan kerja guard.

## Fitur
- seragam
- HT/radio
- tongkat
- senter
- kartu identitas
- serah terima asset
- histori asset per employee/site

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.10 Visitor / Logbook Digital

## Fungsi
Menggantikan buku mutasi/manual logbook.

## Fitur
- buku mutasi digital
- tamu masuk/keluar
- kendaraan masuk/keluar
- serah terima shift
- catatan kejadian harian

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.11 Performance & Discipline

## Fungsi
Mengelola penilaian dan disiplin guard.

## Fitur
- KPI guard
- penilaian supervisor
- pelanggaran
- warning letter
- reward/punishment
- ranking guard/site

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.12 Notification Suite Advanced

## Fungsi
Meningkatkan komunikasi sistem.

## Fitur
- push notification
- email notification
- WhatsApp notification readiness
- reminder shift
- reminder sertifikat habis
- alert invoice jatuh tempo

## Cocok untuk
- Basic
- Pro
- Enterprise

---

# 5.13 SLA & Compliance Monitoring

## Fungsi
Mengukur kualitas layanan terhadap kontrak dan operasional.

## Fitur
- SLA matrix
- manpower compliance
- patrol compliance
- incident response compliance
- attendance compliance
- site scoring

## Cocok untuk
- Pro
- Enterprise

---

# 5.14 Client Portal Advanced

## Fungsi
Menambah pengalaman digital bagi klien.

## Fitur
- client dashboard
- laporan bulanan
- complaint/request channel
- dokumen kontrak
- invoice & payment status
- incident & patrol summary

## Cocok untuk
- Enterprise

---

# 5.15 API & Integration Pack

## Fungsi
Membuka sistem ke software dan perangkat lain.

## Fitur
- open API
- webhook
- accounting integration readiness
- attendance device integration readiness
- import/export connector

## Cocok untuk
- Enterprise

---

# 6. MATRIX PEMBAGIAN MODUL

## 6.1 Modul utama per tier

| Modul | Basic | Pro | Enterprise |
|---|---|---|---|
| Organization & Branch | Ya | Ya | Ya |
| User, Role & Permission | Ya | Ya | Ya |
| Employee & Guard Master | Ya | Ya | Ya |
| Employee Document | Ya | Ya | Ya |
| Client Management | Ya | Ya | Ya |
| Contract Management | Ya | Ya | Ya |
| Site & Post Management | Ya | Ya | Ya |
| Manpower Planning | Ya | Ya | Ya |
| Deployment | Ya | Ya | Ya |
| Shift & Schedule | Ya | Ya | Ya |
| Attendance | Ya | Ya | Ya |
| Leave & Replacement | - | Ya | Ya |
| Patrol | - | Ya | Ya |
| Incident | - | Ya | Ya |
| Payroll | - | Ya | Ya |
| Billing & Invoice | - | - | Ya |
| Dashboard | Basic | Pro | Advanced |
| Reporting | Basic | Pro | Advanced |
| Audit Log | - | Basic | Advanced |
| Client Portal | - | - | Ya |
| API & Integration | - | - | Ya |

---

## 6.2 Add-on availability

| Add-on | Basic | Pro | Enterprise |
|---|---|---|---|
| Recruitment System | Ya | Ya | Ya |
| Employee Loan / Dana Talangan | Ya | Ya | Ya |
| Reimbursement & Claim | Ya | Ya | Ya |
| Training & Certification | Ya | Ya | Ya |
| Asset & Uniform Management | Ya | Ya | Ya |
| Visitor / Logbook Digital | Ya | Ya | Ya |
| Performance & Discipline | Ya | Ya | Ya |
| Notification Suite Advanced | Ya | Ya | Ya |
| Payroll Advanced | - | Ya | Ya |
| Billing Advanced | - | Ya | Ya |
| Patrol Advanced | - | Ya | Ya |
| Incident Command Center | - | Ya | Ya |
| SLA & Compliance | - | Ya | Ya |
| Client Portal Advanced | - | - | Ya |
| API & Integration Pack | - | - | Ya |

---

# 7. STRATEGI UPSELL YANG DIREKOMENDASIKAN

## Dari Basic ke Pro
Trigger upsell:
- user mulai butuh patroli
- user mulai mencatat incident secara formal
- user mulai kesulitan mengelola pengganti
- user ingin payroll tidak manual

## Dari Pro ke Enterprise
Trigger upsell:
- user mulai ingin billing otomatis
- user butuh dashboard owner/direksi
- user butuh audit trail ketat
- user butuh multi-level approval
- user butuh akses client portal
- user butuh integrasi sistem lain

## Dari tier ke add-on
Trigger upsell:
- rekrutmen makin besar
- banyak pinjaman karyawan
- kebutuhan asset/uniform mulai kompleks
- kontrak SLA klien makin ketat
- klien minta portal laporan

---

# 8. REKOMENDASI PRODUK KOMERSIAL

## HRIS Basic
Narasi jual:

```text
Digitalisasi inti HR dan operasional security untuk perusahaan yang baru naik kelas dari sistem manual.
```

## HRIS Pro
Narasi jual:

```text
Paket operasional lengkap untuk mengontrol guard, patroli, incident, replacement, dan payroll dalam satu sistem.
```

## HRIS Enterprise
Narasi jual:

```text
Platform kontrol operasional dan keuangan end-to-end untuk perusahaan outsourcing security skala besar.
```

---

# 9. REKOMENDASI PRIORITAS BUILD

## Phase 1
- HRIS Basic penuh
- fondasi akses, employee, client, site, deployment, schedule, attendance, dashboard basic

## Phase 2
- HRIS Pro inti
- leave & replacement
- patrol
- incident
- payroll basic
- reporting pro

## Phase 3
- HRIS Enterprise inti
- billing
- audit
- analytics
- multi-level approval
- client portal basic

## Phase 4
- add-on prioritas tinggi
- recruitment
- dana talangan
- asset & uniform
- training & certification
- notification suite

## Phase 5
- add-on enterprise lanjutan
- SLA & compliance
- integration pack
- advanced payroll/billing
- client portal advanced

---

# 10. KESIMPULAN

Struktur modul ini dirancang agar:
- **Basic** cukup kuat untuk dipakai harian
- **Pro** menjadi paket operasional paling menarik dan paling laku
- **Enterprise** menjadi paket premium dengan kontrol, finance, audit, dan analytics yang kuat
- **Add-on** menjadi mesin upsell bertahap yang adil untuk pembuat dan fleksibel untuk customer

Ringkasnya:

```text
HRIS Basic
= HR Core + Operasional Dasar

HRIS Pro
= Basic + Patrol + Incident + Replacement + Payroll

HRIS Enterprise
= Pro + Billing + Audit + Analytics + Portal + Integration
```

Dengan pembagian ini, produk tetap utuh secara bisnis, mudah dikembangkan secara teknis, dan jelas secara komersial.
