# 🧱 TECH_STACK.md — HRIS-BPE

## 🎯 Tujuan

Dokumen ini menetapkan standar teknologi untuk pengembangan HRIS-BPE agar:

* konsisten antar tim (backend, frontend, mobile)
* tidak gonta-ganti stack di tengah jalan
* mempercepat development
* siap scale ke Enterprise

---

# 1. ARSITEKTUR UMUM

```text
Web Admin (Frontend)
+ Mobile App (Guard)
        ↓
   REST API (/api/v1)
        ↓
     Backend Service
        ↓
     PostgreSQL Database
```

---

# 2. BACKEND

## ✅ Stack yang dipilih

* Language: **Python**
* Framework: **FastAPI**
* ORM: **SQLAlchemy**
* Migration: **Alembic**
* Validation: **Pydantic**
* Authentication: **JWT (Bearer Token)**
* API Style: **REST API (/api/v1)**

## 🎯 Alasan

* cepat dikembangkan (startup-friendly)
* performa tinggi untuk API
* cocok untuk mobile + web
* mudah scaling ke microservice

---

# 3. DATABASE

## ✅ Stack

* DBMS: **PostgreSQL**
* ORM: SQLAlchemy
* Migration: Alembic

## 📌 Prinsip

* single database (tidak dipisah per tier)
* gunakan feature flag untuk kontrol Basic / Pro / Enterprise
* relasi kuat antar domain (deployment → attendance → payroll → billing)

---

# 4. FRONTEND WEB (ADMIN)

## ✅ Stack yang dipilih

* Framework: **Next.js (React)**
* Styling: **Tailwind CSS**
* UI Components: **ShadCN UI / Headless UI**
* State Management: **Zustand**
* Data Fetching: **TanStack Query (React Query)**
* Form Handling: **React Hook Form**

## 🎯 Alasan

* cepat build dashboard admin
* modular & scalable
* banyak template siap pakai
* cocok untuk internal system (non-SEO)

---

# 5. MOBILE APP (GUARD)

## ✅ Stack yang dipilih

* Framework: **Flutter**

## 🎯 Alasan

* performa tinggi untuk GPS & kamera
* cocok untuk:

  * check-in/out
  * patroli
  * upload foto
* satu codebase Android & iOS

---

# 6. AUTHENTICATION FLOW

```text
User login
→ Backend generate JWT
→ Token disimpan di Web/Mobile
→ Setiap request pakai Authorization Bearer Token
```

---

# 7. FILE STORAGE

## ✅ Phase awal

* Local storage (development)

## ✅ Production

* **S3-compatible storage**

  * MinIO (self-hosted)
  * AWS S3 (cloud)

## Digunakan untuk:

* foto attendance
* dokumen employee
* bukti incident

---

# 8. NOTIFICATION (PHASE PRO+)

## Phase Basic

* database notification sederhana

## Phase lanjut

* Firebase Cloud Messaging (push notification)
* WhatsApp Gateway (opsional)

---

# 9. DEVOPS (BASIC)

## Repository

* GitHub

## Environment

* development
* staging
* production

## Optional (next phase)

* Docker
* CI/CD pipeline

---

# 10. STRUKTUR REPOSITORY

```text
/hris-bpe-backend
/hris-bpe-web
/hris-bpe-mobile
```

---

# 11. VERSIONING

## API

* `/api/v1`

## Git

* main (production)
* develop (integration)
* feature/* (development)

---

# 12. STANDAR KOMUNIKASI DATA

## Request

```json
{
  "field": "value"
}
```

## Response

```json
{
  "success": true,
  "message": "OK",
  "data": {},
  "meta": {}
}
```

## Error

```json
{
  "success": false,
  "message": "Validation error",
  "errors": {}
}
```

---

# 13. PRINSIP PENTING

* ❌ Jangan ganti stack di tengah jalan
* ❌ Jangan over-engineering di awal
* ✅ Fokus ke delivery (UI + flow hidup)
* ✅ Backend harus stabil sebelum scaling
* ✅ Mobile-first untuk guard

---

# 14. KESIMPULAN

Stack yang digunakan:

```text
Backend  : FastAPI (Python)
Frontend : Next.js (React)
Mobile   : Flutter
Database : PostgreSQL
```

Arsitektur ini dipilih karena:

* cepat untuk build
* cukup kuat untuk enterprise
* cocok untuk HRIS outsourcing security
* mendukung mobile-first operation

---

# 🚀 NEXT STEP

Setelah file ini dibuat:

1. Lock stack (jangan diubah lagi)
2. Lanjut ke:

   * PHASE 11.5 UI-1 (Web Admin + Mobile Basic)
   * Implementasi API → UI
   * Testing end-to-end flow

---
