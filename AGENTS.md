# 🤖 AGENTS.md — HRIS-BPE AI DEVELOPMENT RULES

## 🎯 TUJUAN

Dokumen ini mendefinisikan aturan wajib untuk AI (Codex / Cursor / LLM lain) agar:

* tidak keluar dari arsitektur project
* tidak menggunakan stack di luar standar
* mengikuti roadmap development
* menghasilkan code yang konsisten & usable

---

# 🚨 PRIORITY RULE (PALING PENTING)

AI HARUS mengikuti urutan ini:

1. **BACA `TECH_STACK.md` (WAJIB)**
2. BACA roadmap (`roadmap_upgrade_refactor.md`)
3. IDENTIFIKASI phase aktif
4. BARU implement task

❌ Dilarang langsung coding tanpa memahami stack & phase

---

# 🧱 PROJECT CONTEXT

Project ini adalah:

```text
HRIS-BPE (Basic / Pro / Enterprise + Add-on)
```

Fokus:

* perusahaan outsourcing security/satpam
* mobile-first guard
* multi-site operation
* real-time attendance

---

# 🏗️ ARSITEKTUR WAJIB

```text
Frontend (Next.js)
Mobile (Flutter)
        ↓
Backend API (/api/v1 - FastAPI)
        ↓
PostgreSQL
```

---

# 🧰 TECH STACK (HARUS DIPATUHI)

## Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* JWT Auth

## Frontend

* Next.js (React)
* Tailwind CSS
* TanStack Query
* Zustand

## Mobile

* Flutter

## Database

* PostgreSQL

---

# 🚫 STACK YANG DILARANG

AI TIDAK BOLEH menggunakan:

* Vue
* Angular
* Laravel Blade
* jQuery
* Django Template
* random UI framework di luar stack

---

# 📍 PHASE AWARENESS

AI harus sadar phase:

## Current critical phase:

```text
PHASE_11_5_UI_BASIC
```

Fokus:

* UI Basic
* Demo ready
* Testable end-to-end

---

# 🎯 OBJECTIVE PHASE_11_5_UI_BASIC

AI harus membantu membangun:

```text
Employee → Deployment → Schedule → Attendance
```

Yang bisa:

* ditampilkan di UI
* diuji real
* dipakai demo

---

# 🧩 MODULE PRIORITY (WAJIB URUT)

1. Auth
2. Dashboard
3. Employee
4. Client & Site
5. Deployment
6. Schedule
7. Attendance
8. Mobile basic

❌ Jangan lompat ke:

* payroll
* patrol
* incident
* billing

---

# ⚙️ RULE IMPLEMENTASI

## 1. SELALU MAP KE API

Setiap UI:

* HARUS pakai endpoint `/api/v1/...`
* HARUS jelas endpointnya

---

## 2. HANDLE STATE

Setiap halaman WAJIB handle:

* loading
* error
* success

---

## 3. UI PRINCIPLE

* simple > complex
* functional > aesthetic
* usable > perfect

---

## 4. NAMING CONSISTENCY

Gunakan naming sesuai backend:

* employees
* deployments
* schedules
* attendance

❌ jangan bikin istilah baru

---

## 5. DATA FLOW WAJIB

AI harus selalu berpikir:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
```

---

# 📱 MOBILE RULE

Jika membuat mobile:

* wajib Flutter
* gunakan API yang sama
* fokus:

  * login
  * schedule
  * check-in/out

---

# 🔍 VALIDATION RULE

AI harus:

* warning jika endpoint belum ada
* warning jika flow tidak lengkap
* warning jika melanggar stack

---

# 🧾 OUTPUT FORMAT

Setiap jawaban HARUS:

1. Penjelasan singkat
2. Struktur folder (jika perlu)
3. Code
4. API yang dipakai
5. Keterkaitan dengan roadmap

---

# 🧠 BEHAVIOR

Jika:

* ❓ tidak jelas → tanya
* ❌ backend belum siap → beri warning
* ⚠️ desain tidak konsisten → perbaiki

---

# 🔥 GOAL AKHIR

Mencapai:

```text
UI-1 Basic:
- Demo ready
- Testable
- Real flow working
```

---

# 🚀 FUTURE PHASE (JANGAN DISENTUH SEKARANG)

* HRIS Pro
* HRIS Enterprise
* Add-on

---

# ⚠️ FINAL WARNING

Jika AI:

* tidak membaca TECH_STACK.md
* menggunakan stack lain
* melompat phase

→ output dianggap INVALID
