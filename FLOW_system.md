# FLOW_system.md

## Ringkasan

Dokumen ini menjelaskan **alur sistem (business flow & data flow)** untuk HRIS khusus perusahaan outsourcing security/satpam.

Versi ini sudah disesuaikan dengan:

* **HRIS Basic / Pro / Enterprise**
* **Add-on module**
* strategi build bertahap sesuai roadmap

---

# 1. FLOW GLOBAL SISTEM

Flow utama sistem tetap:

```text
Client Contract
→ Site & Post Setup
→ Recruitment / Onboarding
→ Deployment
→ Shift Scheduling
→ Attendance / Patrol / Incident
→ Payroll
→ Billing
→ Dashboard & Audit
```

Flow ini adalah backbone sistem dan **tidak boleh terputus**.

---

# 2. FLOW BERDASARKAN TIER PRODUK

## 2.1 HRIS BASIC FLOW

Flow yang tersedia di Basic:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Dashboard
```

### Modul yang terlibat:

* Employee & Guard Master
* Client & Contract Basic
* Site & Post
* Deployment
* Shift & Schedule
* Attendance
* Dashboard Basic

### Catatan:

* belum ada patrol
* belum ada incident
* belum ada payroll
* belum ada billing

---

## 2.2 HRIS PRO FLOW

Flow tambahan dari Basic:

```text
Attendance
→ Patrol
→ Incident
→ Replacement
→ Payroll
```

Flow lengkap Pro:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Patrol
→ Incident
→ Replacement
→ Payroll
→ Dashboard
```

### Modul tambahan:

* Patrol System
* Incident Management
* Leave & Replacement
* Approval Workflow
* Payroll Basic

---

## 2.3 HRIS ENTERPRISE FLOW

Flow tambahan dari Pro:

```text
Payroll
→ Billing
→ Analytics
→ Client Portal
```

Flow lengkap Enterprise:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Patrol
→ Incident
→ Payroll
→ Billing
→ Analytics
→ Dashboard
```

### Modul tambahan:

* Billing & Invoice
* Audit Log
* Advanced Approval
* Analytics Dashboard
* Client Portal
* API & Integration

---

# 3. FLOW PER MODUL (DETAIL)

## 3.1 Client & Contract

```text
Input client
→ Create contract
→ Set SLA
→ Set billing rule (Enterprise)
→ Activate contract
```

---

## 3.2 Site & Post

```text
Create site
→ Set geofence
→ Create post
→ Define manpower
→ Assign shift type
```

---

## 3.3 Recruitment & Onboarding (Add-on)

```text
Input candidate
→ Screening
→ Hiring
→ Create employee
→ Upload document
→ Ready for deployment
```

---

## 3.4 Deployment

```text
Select guard
→ Assign to site
→ Assign to post
→ Set position
→ Save deployment
```

Validasi:

* guard aktif
* tidak bentrok deployment

---

## 3.5 Shift Scheduling

```text
Select shift pattern
→ Generate schedule
→ Review supervisor
→ Publish schedule
```

Perubahan:

* shift swap
* replacement (Pro)

---

## 3.6 Attendance

```text
Guard check-in
→ GPS validation
→ Face validation (optional)
→ Save attendance
→ Guard check-out
→ Calculate working time
```

Exception:

```text
Manual adjustment
→ Supervisor approval
```

---

## 3.7 Patrol (PRO)

```text
Start patrol
→ Scan checkpoint
→ Save log
→ Validate sequence
→ Finish patrol
```

Output:

* patrol proof
* missed checkpoint detection

---

## 3.8 Incident (PRO)

```text
Create incident
→ Upload evidence
→ Set severity
→ Notify supervisor
→ Follow-up
→ Close incident
```

---

## 3.9 Replacement (PRO)

```text
No attendance detected
→ Trigger alert
→ Find standby guard
→ Assign replacement
→ Update schedule
```

---

## 3.10 Payroll (PRO)

```text
Collect attendance
+ deployment
+ shift

→ Calculate salary
→ Add allowance
→ Calculate overtime
→ Deduction (BPJS, tax)
→ Generate payroll
→ Approve payroll
→ Publish payslip
```

---

## 3.11 Billing (ENTERPRISE)

```text
Get contract
+ billing rules
+ attendance

→ Calculate manpower cost
→ Add overtime
→ Generate invoice
→ Send invoice
→ Track payment
```

---

## 3.12 Dashboard

```text
Attendance data
+ Incident data
+ Payroll data
+ Billing data

→ Generate dashboard
→ Display insight
```

---

# 4. FLOW DATA END-TO-END

## 4.1 Operasional → Payroll

```text
Schedule
→ Attendance
→ Payroll Calculation
→ Payslip
```

---

## 4.2 Operasional → Billing

```text
Deployment
→ Attendance
→ Billing Calculation
→ Invoice
```

---

# 5. FLOW ADD-ON

## 5.1 Employee Loan

```text
Request loan
→ Approval
→ Setup installment
→ Deduct payroll
```

---

## 5.2 Asset Management

```text
Assign asset
→ Use by guard
→ Return asset
→ Track history
```

---

## 5.3 Training & Certification

```text
Assign training
→ Complete training
→ Certification issued
→ Expiry monitoring
```

---

## 5.4 Performance & Discipline

```text
Evaluate guard
→ Record violation
→ Issue warning
→ Calculate score
```

---

## 5.5 SLA & Compliance

```text
Monitor attendance
+ patrol
+ incident

→ Calculate SLA
→ Generate score
→ Report to management/client
```

---

# 6. FLOW PER ROLE

## Guard

* lihat jadwal
* check-in/out
* patroli
* incident report

## Supervisor

* monitor attendance
* manage shift
* approve request

## HR

* kelola employee
* kontrak kerja

## Finance

* payroll
* billing

## Management

* dashboard
* analytics

---

# 7. FLOW KRITIS

## Guard tidak hadir

```text
No check-in
→ Alert
→ Replacement
→ Update schedule
```

---

## Incident critical

```text
Incident reported
→ Escalation
→ Action
→ Resolution
```

---

# 8. KESIMPULAN

Flow sistem ini memastikan:

```text
Operasional berjalan real-time
→ Data konsisten
→ Payroll akurat
→ Billing tepat
→ Insight tersedia
```

Dan dengan struktur tier:

```text
Basic → Operasional dasar
Pro → Kontrol lapangan
Enterprise → Kontrol bisnis & finance
```

Sistem ini adalah:

```text
Operational Control System
+ HRIS
+ Payroll Engine
+ Billing Engine
```
