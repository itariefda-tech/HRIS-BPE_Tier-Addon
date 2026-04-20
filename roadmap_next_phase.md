# Roadmap Lanjutan (Setelah HRIS Basic Selesai)
## HRIS-BPE: Pro → Enterprise → UI → Add-on

---

# 🎯 KONDISI AWAL (PRASYARAT)

Sebelum masuk fase ini, pastikan:

- [ ] Flow Basic stabil:
  - Employee → Deployment → Schedule → Attendance
- [ ] Data konsisten (tidak ada data liar)
- [ ] API /api/v1 stabil
- [ ] RBAC berjalan
- [ ] Migration & seed rapi
- [ ] End-to-end test Basic lulus

---

# 🚀 PHASE 10 — HRIS PRO (OPERATIONAL CONTROL)

## 10.1 Leave & Replacement
- [ ] Implement leave_types
- [ ] Implement leave_requests
- [ ] Implement approval leave
- [ ] Implement replacement_requests
- [ ] Implement standby_pool
- [ ] Auto update schedule jika replacement disetujui
- [ ] Validasi bentrok dan availability guard

## 10.2 Patrol System
- [ ] patrol_routes
- [ ] patrol_checkpoints
- [ ] patrol_sessions
- [ ] patrol_logs
- [ ] Flow start → scan → finish
- [ ] Sequence validation
- [ ] Missed checkpoint detection

## 10.3 Incident Management
- [ ] incident_categories
- [ ] incidents
- [ ] Upload evidence
- [ ] Follow-up tracking
- [ ] Close incident
- [ ] Notification ke supervisor

## 10.4 Approval Workflow
- [ ] Approval leave
- [ ] Approval replacement
- [ ] Approval attendance adjustment
- [ ] Approval incident closure
- [ ] Approval payroll draft

## 10.5 Payroll Basic
- [ ] payroll_periods
- [ ] payroll_components
- [ ] payroll_employee_summary
- [ ] Hitung salary, allowance, overtime
- [ ] Deduction (BPJS, PPh21 basic)
- [ ] Generate & publish payslip

## 10.6 Notification System
- [ ] No check-in alert
- [ ] Late alert
- [ ] Incident alert
- [ ] Approval notification
- [ ] Missed patrol alert

## 10.7 Dashboard Pro
- [ ] Open incident
- [ ] Missed patrol
- [ ] Replacement pending
- [ ] Payroll pending approval

---

# 🏢 PHASE 11 — HRIS ENTERPRISE

## 11.1 Billing & Invoice
- [ ] billing_rules
- [ ] invoice generation (attendance + deployment + contract)
- [ ] invoice_items
- [ ] payment tracking
- [ ] tax & penalty calculation

## 11.2 Advanced Approval
- [ ] Multi-level approval
- [ ] Maker-checker
- [ ] Escalation path

## 11.3 Audit Log
- [ ] audit_logs
- [ ] change tracking
- [ ] created_by / updated_by
- [ ] soft delete

## 11.4 Analytics
- [ ] revenue per client
- [ ] margin per site
- [ ] attendance trend
- [ ] incident trend
- [ ] patrol compliance
- [ ] outstanding invoice

## 11.5 Multi Branch
- [ ] branch scope
- [ ] site scope
- [ ] region grouping
- [ ] multi-company support

## 11.6 Client Portal
- [ ] client login
- [ ] invoice view
- [ ] attendance summary
- [ ] incident summary
- [ ] SLA summary

## 11.7 Integration
- [ ] API token
- [ ] webhook
- [ ] import/export
- [ ] integration logs

---

# 🎨 PHASE 12 — UI/UX

## Web Admin
- [ ] dashboard admin
- [ ] employee UI
- [ ] deployment UI
- [ ] schedule UI
- [ ] attendance UI
- [ ] payroll UI
- [ ] billing UI

## Mobile Guard
- [ ] login
- [ ] my schedule
- [ ] check-in/out
- [ ] patrol
- [ ] incident
- [ ] payslip

## Client Portal UI
- [ ] dashboard
- [ ] invoice UI
- [ ] report UI

## UI/UX Dual Language
- [ ] implement i18n (ID / EN)
- [ ] move all UI text to translation keys
- [ ] language switcher
- [ ] persist user language
- [ ] fallback language

## UI/UX Multi Theme
- [ ] setup theme tokens (CSS variables)
- [ ] create 5 themes
- [ ] theme switcher
- [ ] persist theme
- [ ] apply across all UI

## UX Improvement
- [ ] simplify flow
- [ ] reduce click
- [ ] improve performance
- [ ] mobile usability
- [ ] ensure layout consistency across languages
- [ ] ensure readability across themes
- [ ] test mobile & web responsiveness

---

# 🔌 PHASE 13 — ADD-ON

## Recruitment
- [ ] candidate system
- [ ] recruitment pipeline

## Employee Loan
- [ ] loan request
- [ ] payroll deduction

## Asset
- [ ] assignment
- [ ] tracking

## Training
- [ ] training record
- [ ] expiry reminder

## Performance
- [ ] KPI guard
- [ ] discipline tracking

---

# 🏁 FINAL

- [ ] HRIS Pro release
- [ ] HRIS Enterprise release
- [ ] UI polishing
- [ ] Add-on expansion

---

# 🧭 STRATEGI AKHIR

HRIS Basic → stabilkan core  
HRIS Pro → best seller  
HRIS Enterprise → high margin  
Add-on → upsell engine  
UI → usability & experience
