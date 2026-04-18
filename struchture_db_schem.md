# STRUCHTURE_DB-SCHEM.md

## Ringkasan
Dokumen ini berisi rancangan **struktur database/schema** untuk aplikasi **HRIS khusus perusahaan outsourcing security/satpam** yang sudah disesuaikan dengan strategi produk:

- **HRIS Basic**
- **HRIS Pro**
- **HRIS Enterprise**
- **Add-on Module**

Tujuan dokumen ini:
- menjadi pondasi backend development
- menyatukan struktur data dengan strategi tier produk
- memudahkan pembagian kerja coding per fase build
- menjaga agar roadmap, API, dan database tetap sinkron
- memudahkan monetisasi bertahap tanpa merusak struktur inti sistem

Dokumen ini disusun untuk sistem yang mendukung:
- multi-client
- multi-site
- multi-post
- deployment guard
- shift scheduling
- attendance lapangan
- patrol/guard tour
- incident reporting
- payroll
- billing klien
- audit trail
- add-on modular expansion

---

# 1. PRINSIP DESAIN DATABASE

Struktur database harus mampu menangani 4 lapisan besar secara bersamaan:

1. **HR Master**
2. **Operasional Site & Deployment**
3. **Attendance / Patrol / Incident**
4. **Payroll / Billing / Governance**

Prinsip yang dipakai:
- relasional dan konsisten
- modular per domain bisnis
- mudah di-scale
- mudah diaudit
- siap dipakai untuk web admin dan mobile guard
- mendukung build bertahap sesuai tier produk
- add-on tidak merusak schema inti

Database yang direkomendasikan:
- **PostgreSQL**

---

# 2. PRINSIP TIER PRODUK DALAM DATABASE

Database harus dibangun dengan konsep:

```text
Single Core Platform
+ Feature Flags / License Control
+ Modular Tables by Domain
```

Artinya:
- schema inti tetap satu
- perbedaan Basic / Pro / Enterprise terutama ditentukan oleh **fitur yang diaktifkan**, bukan membuat database terpisah
- add-on cukup menambah domain tabel baru atau mengaktifkan tabel yang sudah disiapkan

## 2.1 Core schema wajib ada sejak awal
Agar tidak bongkar pasang di tengah jalan, tabel inti untuk alur utama tetap disiapkan dari awal:

```text
Employee
→ Deployment
→ Schedule
→ Attendance
→ Payroll
→ Billing
```

Namun implementasi coding dan aktivasi UI/API bisa mengikuti tier.

## 2.2 Product control yang direkomendasikan
Untuk kontrol lisensi/paket, tambahkan layer konfigurasi produk:

### product_tiers
```sql
product_tiers
- id (pk)
- code                  -- BASIC / PRO / ENTERPRISE
- name
- description
- sort_order
- is_active
- created_at
- updated_at
```

### feature_modules
```sql
feature_modules
- id (pk)
- code                  -- PAYROLL_BASIC / BILLING_ADV / PATROL_BASIC dll
- name
- module_category       -- core / add_on / enterprise / integration
- default_tier_id (fk -> product_tiers.id)
- is_add_on
- is_active
- created_at
- updated_at
```

### company_subscriptions
```sql
company_subscriptions
- id (pk)
- company_id (fk -> companies.id)
- product_tier_id (fk -> product_tiers.id)
- start_date
- end_date
- subscription_status
- notes
- created_at
- updated_at
```

### company_feature_modules
```sql
company_feature_modules
- id (pk)
- company_subscription_id (fk -> company_subscriptions.id)
- feature_module_id (fk -> feature_modules.id)
- activation_type       -- included / add_on / trial / custom
- active_flag
- activated_at
- expired_at
- notes
- created_at
- updated_at
```

Dengan struktur ini, satu customer bisa:
- langganan **HRIS Basic**
- lalu membeli add-on **Recruitment**
- lalu upgrade ke **HRIS Pro**
- tanpa perubahan schema besar

---

# 3. DOMAIN DATA

Agar rapi, schema dibagi ke domain berikut:

- product_control
- organization
- master_hr
- recruitment
- client_contract
- site_operations
- workforce_operations
- attendance
- patrol
- incident
- leave_replacement
- payroll
- billing
- loan_finance
- training_compliance
- asset_logbook
- performance
- access_control
- audit
- integration

---

# 4. PEMETAAN DOMAIN KE TIER PRODUK

## 4.1 HRIS Basic
Domain utama yang aktif:
- product_control
- organization
- master_hr
- client_contract
- site_operations
- workforce_operations
- attendance
- access_control
- dashboard/reporting basic (turunan query/view)

## 4.2 HRIS Pro
Tambahan domain aktif:
- leave_replacement
- patrol
- incident
- payroll
- audit basic

## 4.3 HRIS Enterprise
Tambahan domain aktif:
- billing
- audit advanced
- integration
- client access / portal support
- analytics / reporting advanced

## 4.4 Add-on
Domain opsional:
- recruitment
- loan_finance
- training_compliance
- asset_logbook
- performance
- integration tambahan

---

# 5. ENTITY UTAMA

Entitas utama yang menjadi tulang punggung sistem:

- Company
- Branch
- Product Tier
- Feature Module
- Company Subscription
- User
- Role
- Permission
- Employee
- Guard Profile
- Employee Contract
- Client
- Client Contract
- Client Site
- Site Post
- Deployment
- Shift Type
- Shift Pattern
- Work Schedule
- Attendance Record
- Patrol Route
- Patrol Session
- Incident
- Leave Request
- Replacement Request
- Payroll Period
- Payroll Employee Summary
- Billing Rule
- Invoice
- Employee Loan
- Training Record
- Asset Assignment
- Performance Review
- Audit Log

---

# 6. STRUKTUR TABEL PER DOMAIN

# 6.1 product_control

## product_tiers
```sql
product_tiers
- id (pk)
- code
- name
- description
- sort_order
- is_active
- created_at
- updated_at
```

## feature_modules
```sql
feature_modules
- id (pk)
- code
- name
- module_category
- default_tier_id (fk -> product_tiers.id)
- is_add_on
- is_active
- created_at
- updated_at
```

## company_subscriptions
```sql
company_subscriptions
- id (pk)
- company_id (fk -> companies.id)
- product_tier_id (fk -> product_tiers.id)
- start_date
- end_date
- subscription_status
- notes
- created_at
- updated_at
```

## company_feature_modules
```sql
company_feature_modules
- id (pk)
- company_subscription_id (fk -> company_subscriptions.id)
- feature_module_id (fk -> feature_modules.id)
- activation_type
- active_flag
- activated_at
- expired_at
- notes
- created_at
- updated_at
```

---

# 6.2 organization

## companies
```sql
companies
- id (pk)
- code
- name
- legal_name
- tax_number
- address
- phone
- email
- status
- created_at
- updated_at
```

## company_groups
Opsional untuk enterprise multi-company.

```sql
company_groups
- id (pk)
- code
- name
- description
- created_at
- updated_at
```

## company_group_members
```sql
company_group_members
- id (pk)
- company_group_id (fk -> company_groups.id)
- company_id (fk -> companies.id)
- created_at
```

## branches
```sql
branches
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- address
- city
- province
- phone
- status
- created_at
- updated_at
```

## regions
Opsional untuk enterprise multi-region.

```sql
regions
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- parent_region_id (nullable fk -> regions.id)
- created_at
- updated_at
```

## departments
```sql
departments
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- description
- created_at
- updated_at
```

## positions
```sql
positions
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- category
- level_order
- description
- created_at
- updated_at
```

---

# 6.3 access_control

## users
```sql
users
- id (pk)
- employee_id (nullable fk -> employees.id)
- username
- email
- phone
- password_hash
- last_login_at
- is_active
- created_at
- updated_at
```

## roles
```sql
roles
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- description
- created_at
- updated_at
```

## permissions
```sql
permissions
- id (pk)
- code
- name
- module_name
- created_at
```

## role_permissions
```sql
role_permissions
- id (pk)
- role_id (fk -> roles.id)
- permission_id (fk -> permissions.id)
```

## user_roles
```sql
user_roles
- id (pk)
- user_id (fk -> users.id)
- role_id (fk -> roles.id)
```

## user_scope_access
Penting untuk enterprise site-scope / branch-scope.

```sql
user_scope_access
- id (pk)
- user_id (fk -> users.id)
- scope_type            -- company / branch / region / site
- scope_id
- created_at
```

---

# 6.4 master_hr

## employees
```sql
employees
- id (pk)
- employee_number
- company_id (fk -> companies.id)
- branch_id (fk -> branches.id)
- department_id (fk -> departments.id)
- position_id (fk -> positions.id)
- full_name
- nickname
- gender
- birth_place
- birth_date
- marital_status
- religion
- phone
- email
- address
- city
- province
- postal_code
- national_id_number
- tax_id_number
- bpjs_health_number
- bpjs_employment_number
- bank_name
- bank_account_number
- bank_account_name
- hire_date
- employment_status
- employee_status
- resign_date
- photo_path
- created_at
- updated_at
```

## employee_emergency_contacts
```sql
employee_emergency_contacts
- id (pk)
- employee_id (fk -> employees.id)
- name
- relationship
- phone
- address
- created_at
- updated_at
```

## employee_documents
```sql
employee_documents
- id (pk)
- employee_id (fk -> employees.id)
- document_type
- document_number
- issued_date
- expiry_date
- file_path
- verification_status
- notes
- created_at
- updated_at
```

## guard_profiles
```sql
guard_profiles
- id (pk)
- employee_id (fk -> employees.id, unique)
- guard_registration_number
- guard_level
- uniform_size
- shoe_size
- blood_type
- firearm_license_flag
- driving_license_type
- fitness_status
- blacklist_flag
- blacklist_reason
- created_at
- updated_at
```

## guard_certifications
```sql
guard_certifications
- id (pk)
- employee_id (fk -> employees.id)
- certification_type
- certificate_number
- issued_by
- issue_date
- expiry_date
- file_path
- status
- created_at
- updated_at
```

## employee_contracts
```sql
employee_contracts
- id (pk)
- employee_id (fk -> employees.id)
- contract_number
- contract_type
- start_date
- end_date
- salary_type
- basic_salary
- allowance_fixed
- notes
- status
- created_at
- updated_at
```

---

# 6.5 recruitment (ADD-ON)

## candidates
```sql
candidates
- id (pk)
- company_id (fk -> companies.id)
- full_name
- phone
- email
- source_channel
- current_city
- last_education
- status
- notes
- created_at
- updated_at
```

## recruitment_requests
```sql
recruitment_requests
- id (pk)
- company_id (fk -> companies.id)
- branch_id (fk -> branches.id)
- requested_position_id (fk -> positions.id)
- requested_headcount
- needed_for_site_id (nullable fk -> client_sites.id)
- request_status
- requested_by
- approved_by
- created_at
- updated_at
```

## candidate_applications
```sql
candidate_applications
- id (pk)
- candidate_id (fk -> candidates.id)
- recruitment_request_id (fk -> recruitment_requests.id)
- application_stage
- screening_result
- interview_result
- medical_check_result
- background_check_result
- final_status
- created_at
- updated_at
```

## candidate_documents
```sql
candidate_documents
- id (pk)
- candidate_id (fk -> candidates.id)
- document_type
- file_path
- verification_status
- created_at
- updated_at
```

---

# 6.6 client_contract

## clients
```sql
clients
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- industry_type
- contact_person_name
- contact_person_phone
- contact_person_email
- billing_address
- tax_number
- status
- created_at
- updated_at
```

## client_contracts
```sql
client_contracts
- id (pk)
- client_id (fk -> clients.id)
- contract_number
- contract_title
- start_date
- end_date
- contract_type
- currency
- tax_included_flag
- payment_term_days
- sla_description
- status
- notes
- created_at
- updated_at
```

## client_contract_files
```sql
client_contract_files
- id (pk)
- client_contract_id (fk -> client_contracts.id)
- file_name
- file_path
- file_type
- uploaded_by
- uploaded_at
```

---

# 6.7 site_operations

## client_sites
```sql
client_sites
- id (pk)
- client_id (fk -> clients.id)
- client_contract_id (fk -> client_contracts.id)
- branch_id (fk -> branches.id)
- region_id (nullable fk -> regions.id)
- code
- name
- address
- city
- province
- latitude
- longitude
- geofence_radius_meter
- site_type
- operational_status
- start_service_date
- end_service_date
- created_at
- updated_at
```

## site_posts
```sql
site_posts
- id (pk)
- client_site_id (fk -> client_sites.id)
- code
- name
- area_name
- risk_level
- checkpoint_required_flag
- active_flag
- created_at
- updated_at
```

## site_manpower_requirements
```sql
site_manpower_requirements
- id (pk)
- client_site_id (fk -> client_sites.id)
- site_post_id (fk -> site_posts.id)
- position_id (fk -> positions.id)
- shift_type_id (fk -> shift_types.id)
- required_headcount
- minimum_grade
- effective_start_date
- effective_end_date
- created_at
- updated_at
```

## site_sla_rules
Opsional, penting untuk enterprise / add-on SLA.

```sql
site_sla_rules
- id (pk)
- client_contract_id (fk -> client_contracts.id)
- client_site_id (fk -> client_sites.id)
- sla_code
- sla_name
- measurement_type
- target_value
- penalty_rule_json
- active_flag
- created_at
- updated_at
```

---

# 6.8 workforce_operations

## employee_deployments
```sql
employee_deployments
- id (pk)
- employee_id (fk -> employees.id)
- client_id (fk -> clients.id)
- client_contract_id (fk -> client_contracts.id)
- client_site_id (fk -> client_sites.id)
- site_post_id (fk -> site_posts.id)
- position_id (fk -> positions.id)
- start_date
- end_date
- deployment_status
- source_type
- notes
- created_at
- updated_at
```

## deployment_histories
```sql
deployment_histories
- id (pk)
- employee_deployment_id (fk -> employee_deployments.id)
- action_type
- old_client_site_id
- new_client_site_id
- old_site_post_id
- new_site_post_id
- action_date
- remarks
- created_by
- created_at
```

## standby_pools
```sql
standby_pools
- id (pk)
- branch_id (fk -> branches.id)
- employee_id (fk -> employees.id)
- availability_status
- available_from
- available_until
- remarks
- created_at
- updated_at
```

## shift_types
```sql
shift_types
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- start_time
- end_time
- cross_day_flag
- break_minutes
- tolerance_late_minutes
- overtime_after_minutes
- created_at
- updated_at
```

## shift_patterns
```sql
shift_patterns
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- pattern_type
- cycle_days
- description
- created_at
- updated_at
```

## shift_pattern_details
```sql
shift_pattern_details
- id (pk)
- shift_pattern_id (fk -> shift_patterns.id)
- day_order
- shift_type_id (fk -> shift_types.id)
- is_day_off
- created_at
```

## work_schedules
```sql
work_schedules
- id (pk)
- employee_id (fk -> employees.id)
- employee_deployment_id (fk -> employee_deployments.id)
- client_site_id (fk -> client_sites.id)
- site_post_id (fk -> site_posts.id)
- shift_type_id (fk -> shift_types.id)
- scheduled_date
- scheduled_start_datetime
- scheduled_end_datetime
- schedule_status
- replacement_for_schedule_id
- generated_by
- approved_by
- created_at
- updated_at
```

## shift_change_requests
```sql
shift_change_requests
- id (pk)
- work_schedule_id (fk -> work_schedules.id)
- requested_by_employee_id
- target_employee_id
- reason
- request_status
- approved_by
- approved_at
- created_at
- updated_at
```

---

# 6.9 attendance

## attendance_records
```sql
attendance_records
- id (pk)
- employee_id (fk -> employees.id)
- work_schedule_id (fk -> work_schedules.id)
- client_site_id (fk -> client_sites.id)
- site_post_id (fk -> site_posts.id)
- attendance_date
- check_in_datetime
- check_out_datetime
- check_in_latitude
- check_in_longitude
- check_out_latitude
- check_out_longitude
- check_in_photo_path
- check_out_photo_path
- check_in_method
- check_out_method
- gps_valid_flag
- face_valid_flag
- geofence_valid_flag
- attendance_status
- minutes_late
- working_minutes
- overtime_minutes
- remarks
- created_at
- updated_at
```

## attendance_exceptions
```sql
attendance_exceptions
- id (pk)
- attendance_record_id (fk -> attendance_records.id)
- exception_type
- description
- resolution_status
- resolved_by
- resolved_at
- created_at
- updated_at
```

## attendance_manual_adjustments
```sql
attendance_manual_adjustments
- id (pk)
- attendance_record_id (fk -> attendance_records.id)
- old_check_in_datetime
- new_check_in_datetime
- old_check_out_datetime
- new_check_out_datetime
- reason
- approved_by
- created_by
- created_at
```

## attendance_device_bindings
Opsional untuk enterprise security control.

```sql
attendance_device_bindings
- id (pk)
- employee_id (fk -> employees.id)
- device_id
- device_name
- device_platform
- active_flag
- bound_at
- unbound_at
```

---

# 6.10 leave_replacement

## leave_types
```sql
leave_types
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- paid_flag
- requires_approval_flag
- created_at
- updated_at
```

## leave_requests
```sql
leave_requests
- id (pk)
- employee_id (fk -> employees.id)
- leave_type_id (fk -> leave_types.id)
- start_date
- end_date
- total_days
- reason
- request_status
- approved_by
- approved_at
- created_at
- updated_at
```

## replacement_requests
```sql
replacement_requests
- id (pk)
- work_schedule_id (fk -> work_schedules.id)
- request_type
- requested_by
- reason
- replacement_employee_id
- request_status
- approved_by
- approved_at
- created_at
- updated_at
```

---

# 6.11 patrol

## patrol_routes
```sql
patrol_routes
- id (pk)
- client_site_id (fk -> client_sites.id)
- code
- name
- estimated_minutes
- active_flag
- created_at
- updated_at
```

## patrol_checkpoints
```sql
patrol_checkpoints
- id (pk)
- patrol_route_id (fk -> patrol_routes.id)
- client_site_id (fk -> client_sites.id)
- checkpoint_code
- checkpoint_name
- sequence_no
- latitude
- longitude
- qr_code_value
- nfc_code_value
- required_flag
- created_at
- updated_at
```

## patrol_sessions
```sql
patrol_sessions
- id (pk)
- employee_id (fk -> employees.id)
- work_schedule_id (fk -> work_schedules.id)
- patrol_route_id (fk -> patrol_routes.id)
- start_datetime
- end_datetime
- session_status
- created_at
- updated_at
```

## patrol_logs
```sql
patrol_logs
- id (pk)
- patrol_session_id (fk -> patrol_sessions.id)
- patrol_checkpoint_id (fk -> patrol_checkpoints.id)
- scanned_at
- latitude
- longitude
- scan_method
- photo_path
- notes
- created_at
```

## patrol_missed_events
Untuk Patrol Advanced / analytics.

```sql
patrol_missed_events
- id (pk)
- patrol_session_id (fk -> patrol_sessions.id)
- patrol_checkpoint_id (fk -> patrol_checkpoints.id)
- missed_type
- expected_at
- detected_at
- status
- created_at
```

---

# 6.12 incident

## incident_categories
```sql
incident_categories
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- severity_default
- created_at
- updated_at
```

## incidents
```sql
incidents
- id (pk)
- incident_number
- client_site_id (fk -> client_sites.id)
- site_post_id (fk -> site_posts.id)
- employee_id (fk -> employees.id)
- work_schedule_id (fk -> work_schedules.id)
- incident_category_id (fk -> incident_categories.id)
- reported_at
- occurred_at
- severity_level
- title
- description
- action_taken
- escalation_status
- incident_status
- resolved_at
- resolved_by
- created_at
- updated_at
```

## incident_files
```sql
incident_files
- id (pk)
- incident_id (fk -> incidents.id)
- file_type
- file_path
- uploaded_by
- uploaded_at
```

## incident_follow_ups
```sql
incident_follow_ups
- id (pk)
- incident_id (fk -> incidents.id)
- follow_up_datetime
- note
- follow_up_by
- status_after_follow_up
- created_at
```

## incident_escalations
Untuk Incident Command Center / enterprise.

```sql
incident_escalations
- id (pk)
- incident_id (fk -> incidents.id)
- escalation_level
- escalated_to_user_id
- escalated_at
- acknowledged_at
- closed_at
- escalation_status
- created_at
```

---

# 6.13 payroll

## payroll_periods
```sql
payroll_periods
- id (pk)
- company_id (fk -> companies.id)
- code
- start_date
- end_date
- payment_date
- status
- created_at
- updated_at
```

## payroll_components
```sql
payroll_components
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- component_type
- calculation_method
- taxable_flag
- active_flag
- created_at
- updated_at
```

## payroll_employee_summaries
```sql
payroll_employee_summaries
- id (pk)
- payroll_period_id (fk -> payroll_periods.id)
- employee_id (fk -> employees.id)
- employee_deployment_id (fk -> employee_deployments.id)
- basic_salary
- fixed_allowance
- attendance_allowance
- overtime_amount
- night_shift_allowance
- site_allowance
- risk_allowance
- gross_salary
- bpjs_health_deduction
- bpjs_employment_deduction
- tax_pph21
- loan_deduction
- penalty_deduction
- other_deduction
- net_salary
- payroll_status
- created_at
- updated_at
```

## payroll_employee_component_values
```sql
payroll_employee_component_values
- id (pk)
- payroll_employee_summary_id (fk -> payroll_employee_summaries.id)
- payroll_component_id (fk -> payroll_components.id)
- amount
- calculation_notes
- created_at
```

## payslips
```sql
payslips
- id (pk)
- payroll_employee_summary_id (fk -> payroll_employee_summaries.id)
- payslip_number
- generated_at
- file_path
- published_flag
- published_at
```

## payroll_adjustments
Untuk Payroll Advanced.

```sql
payroll_adjustments
- id (pk)
- payroll_employee_summary_id (fk -> payroll_employee_summaries.id)
- adjustment_type
- amount
- reason
- effective_period_id
- approved_by
- created_at
```

---

# 6.14 billing

## billing_rules
```sql
billing_rules
- id (pk)
- client_contract_id (fk -> client_contracts.id)
- client_site_id (fk -> client_sites.id)
- billing_type
- rate_amount
- overtime_rate_amount
- night_shift_rate_amount
- holiday_rate_amount
- penalty_rule_json
- effective_start_date
- effective_end_date
- created_at
- updated_at
```

## invoices
```sql
invoices
- id (pk)
- client_id (fk -> clients.id)
- client_contract_id (fk -> client_contracts.id)
- client_site_id (fk -> client_sites.id)
- invoice_number
- invoice_date
- billing_period_start
- billing_period_end
- subtotal_amount
- tax_amount
- penalty_amount
- grand_total
- due_date
- invoice_status
- notes
- created_at
- updated_at
```

## invoice_items
```sql
invoice_items
- id (pk)
- invoice_id (fk -> invoices.id)
- item_type
- description
- quantity
- unit_price
- amount
- reference_type
- reference_id
- created_at
```

## client_payments
```sql
client_payments
- id (pk)
- invoice_id (fk -> invoices.id)
- payment_date
- payment_amount
- payment_method
- reference_number
- notes
- created_at
```

## invoice_approvals
Untuk enterprise billing governance.

```sql
invoice_approvals
- id (pk)
- invoice_id (fk -> invoices.id)
- approval_level
- approver_user_id
- approval_status
- approved_at
- notes
- created_at
```

---

# 6.15 loan_finance (ADD-ON)

## employee_loans
```sql
employee_loans
- id (pk)
- employee_id (fk -> employees.id)
- loan_number
- loan_type
- principal_amount
- approved_amount
- installment_count
- installment_amount
- start_period_date
- end_period_date
- loan_status
- requested_by
- approved_by
- created_at
- updated_at
```

## employee_loan_installments
```sql
employee_loan_installments
- id (pk)
- employee_loan_id (fk -> employee_loans.id)
- installment_no
- due_period_date
- principal_amount
- paid_amount
- deduction_payroll_summary_id (nullable fk -> payroll_employee_summaries.id)
- installment_status
- created_at
- updated_at
```

---

# 6.16 training_compliance (ADD-ON)

## trainings
```sql
trainings
- id (pk)
- company_id (fk -> companies.id)
- code
- name
- training_type
- validity_months
- mandatory_flag
- created_at
- updated_at
```

## employee_training_records
```sql
employee_training_records
- id (pk)
- employee_id (fk -> employees.id)
- training_id (fk -> trainings.id)
- completed_at
- expiry_date
- result_status
- certificate_file_path
- created_at
- updated_at
```

## training_matrix_rules
```sql
training_matrix_rules
- id (pk)
- client_site_id (fk -> client_sites.id)
- site_post_id (nullable fk -> site_posts.id)
- required_training_id (fk -> trainings.id)
- mandatory_flag
- created_at
- updated_at
```

---

# 6.17 asset_logbook (ADD-ON)

## assets
```sql
assets
- id (pk)
- company_id (fk -> companies.id)
- asset_code
- asset_name
- asset_category
- serial_number
- purchase_date
- asset_status
- current_branch_id
- created_at
- updated_at
```

## asset_assignments
```sql
asset_assignments
- id (pk)
- asset_id (fk -> assets.id)
- assigned_to_employee_id (nullable fk -> employees.id)
- assigned_to_site_id (nullable fk -> client_sites.id)
- assigned_at
- returned_at
- condition_out
- condition_in
- notes
- created_at
- updated_at
```

## digital_logbooks
```sql
digital_logbooks
- id (pk)
- client_site_id (fk -> client_sites.id)
- site_post_id (nullable fk -> site_posts.id)
- work_schedule_id (nullable fk -> work_schedules.id)
- logbook_type
- title
- note
- created_by_employee_id
- created_at
- updated_at
```

## visitor_logs
```sql
visitor_logs
- id (pk)
- client_site_id (fk -> client_sites.id)
- site_post_id (nullable fk -> site_posts.id)
- visitor_name
- identity_number
- vehicle_number
- purpose
- check_in_at
- check_out_at
- recorded_by_employee_id
- created_at
- updated_at
```

---

# 6.18 performance (ADD-ON)

## performance_reviews
```sql
performance_reviews
- id (pk)
- employee_id (fk -> employees.id)
- review_period_start
- review_period_end
- reviewer_employee_id
- score_total
- result_level
- notes
- created_at
- updated_at
```

## performance_review_items
```sql
performance_review_items
- id (pk)
- performance_review_id (fk -> performance_reviews.id)
- indicator_code
- indicator_name
- score
- notes
- created_at
```

## disciplinary_actions
```sql
disciplinary_actions
- id (pk)
- employee_id (fk -> employees.id)
- action_type
- action_date
- reason
- severity_level
- related_incident_id (nullable fk -> incidents.id)
- document_file_path
- created_at
- updated_at
```

---

# 6.19 integration / enterprise support

## webhooks
```sql
webhooks
- id (pk)
- company_id (fk -> companies.id)
- webhook_name
- target_url
- secret_key
- event_code
- active_flag
- created_at
- updated_at
```

## integration_logs
```sql
integration_logs
- id (pk)
- company_id (fk -> companies.id)
- integration_type
- event_code
- request_payload_json
- response_payload_json
- status
- processed_at
- created_at
```

## client_portal_users
```sql
client_portal_users
- id (pk)
- client_id (fk -> clients.id)
- name
- email
- phone
- password_hash
- is_active
- last_login_at
- created_at
- updated_at
```

---

# 6.20 audit

## audit_logs
```sql
audit_logs
- id (pk)
- user_id (fk -> users.id)
- module_name
- entity_name
- entity_id
- action_type
- old_values_json
- new_values_json
- ip_address
- user_agent
- created_at
```

## approval_logs
```sql
approval_logs
- id (pk)
- module_name
- reference_id
- approval_level
- approver_user_id
- action_type
- notes
- created_at
```

## system_notifications
```sql
system_notifications
- id (pk)
- user_id (fk -> users.id)
- title
- message
- notification_type
- reference_type
- reference_id
- read_at
- created_at
```

---

# 7. RELASI INTI ANTAR TABEL

## 7.1 Relasi produk dan lisensi

```text
companies
└── company_subscriptions
    └── product_tiers
    └── company_feature_modules
        └── feature_modules
```

## 7.2 Relasi organisasi

```text
companies
└── branches
└── departments
└── positions
└── roles
└── employees
```

## 7.3 Relasi client dan site

```text
clients
└── client_contracts
    └── client_contract_files
    └── billing_rules
    └── site_sla_rules
    └── client_sites
        └── site_posts
        └── site_manpower_requirements
        └── patrol_routes
            └── patrol_checkpoints
```

## 7.4 Relasi employee dan operasi

```text
employees
└── employee_documents
└── guard_profiles
└── guard_certifications
└── employee_contracts
└── employee_deployments
    └── work_schedules
        └── attendance_records
        └── patrol_sessions
            └── patrol_logs
        └── incidents
        └── replacement_requests
```

## 7.5 Relasi payroll

```text
payroll_periods
└── payroll_employee_summaries
    └── payroll_employee_component_values
    └── payslips
    └── payroll_adjustments
```

## 7.6 Relasi billing

```text
invoices
└── invoice_items
└── client_payments
└── invoice_approvals
```

## 7.7 Relasi add-on

```text
employees
└── employee_loans
└── employee_training_records
└── asset_assignments
└── performance_reviews
└── disciplinary_actions
```

---

# 8. FLOW DATA ANTAR DOMAIN

## 8.1 Dari HR ke Operasional

```text
employees
→ guard_profiles
→ employee_contracts
→ employee_deployments
→ work_schedules
```

## 8.2 Dari Operasional ke Attendance

```text
work_schedules
→ attendance_records
→ attendance_exceptions / attendance_manual_adjustments
```

## 8.3 Dari Operasional ke Patrol & Incident

```text
work_schedules
→ patrol_sessions
→ patrol_logs

work_schedules
→ incidents
→ incident_follow_ups
```

## 8.4 Dari Operasional ke Payroll

```text
employee_deployments
+ work_schedules
+ attendance_records
→ payroll_employee_summaries
→ payslips
```

## 8.5 Dari Operasional ke Billing

```text
client_contracts
+ billing_rules
+ employee_deployments
+ attendance_records
→ invoices
→ invoice_items
```

## 8.6 Dari Add-on Loan ke Payroll

```text
employee_loans
→ employee_loan_installments
→ payroll_employee_summaries.loan_deduction
```

## 8.7 Dari Training ke Compliance

```text
trainings
+ employee_training_records
+ training_matrix_rules
→ training compliance monitoring
```

---

# 9. PEMBAGIAN PRIORITAS TABEL PER TIER

# 9.1 Tabel wajib untuk HRIS BASIC

## Product control
- product_tiers
- feature_modules
- company_subscriptions
- company_feature_modules

## Organization & access
- companies
- branches
- departments
- positions
- users
- roles
- permissions
- role_permissions
- user_roles

## HR core
- employees
- employee_emergency_contacts
- employee_documents
- guard_profiles
- guard_certifications
- employee_contracts

## Client & operations
- clients
- client_contracts
- client_contract_files
- client_sites
- site_posts
- site_manpower_requirements
- employee_deployments
- deployment_histories
- shift_types
- shift_patterns
- shift_pattern_details
- work_schedules
- shift_change_requests

## Attendance
- attendance_records
- attendance_exceptions
- attendance_manual_adjustments

---

# 9.2 Tabel tambahan untuk HRIS PRO

- standby_pools
- leave_types
- leave_requests
- replacement_requests
- patrol_routes
- patrol_checkpoints
- patrol_sessions
- patrol_logs
- patrol_missed_events
- incident_categories
- incidents
- incident_files
- incident_follow_ups
- incident_escalations
- payroll_periods
- payroll_components
- payroll_employee_summaries
- payroll_employee_component_values
- payslips
- payroll_adjustments
- audit_logs
- approval_logs
- system_notifications

---

# 9.3 Tabel tambahan untuk HRIS ENTERPRISE

- company_groups
- company_group_members
- regions
- user_scope_access
- site_sla_rules
- attendance_device_bindings
- billing_rules
- invoices
- invoice_items
- client_payments
- invoice_approvals
- webhooks
- integration_logs
- client_portal_users

---

# 9.4 Tabel add-on

## Recruitment System
- candidates
- recruitment_requests
- candidate_applications
- candidate_documents

## Employee Loan / Dana Talangan
- employee_loans
- employee_loan_installments

## Training & Certification
- trainings
- employee_training_records
- training_matrix_rules

## Asset & Uniform / Visitor Logbook
- assets
- asset_assignments
- digital_logbooks
- visitor_logs

## Performance & Discipline
- performance_reviews
- performance_review_items
- disciplinary_actions

---

# 10. INDEX YANG DIREKOMENDASIKAN

## employees
- `(company_id, employee_status)`
- `(branch_id, employee_status)`
- `(employee_number)` unique

## employee_deployments
- `(employee_id, deployment_status)`
- `(client_site_id, deployment_status)`
- `(client_contract_id, deployment_status)`

## work_schedules
- `(employee_id, scheduled_date)`
- `(client_site_id, scheduled_date)`
- `(site_post_id, scheduled_date)`
- `(employee_deployment_id, scheduled_date)`

## attendance_records
- `(employee_id, attendance_date)`
- `(work_schedule_id)`
- `(client_site_id, attendance_date)`

## patrol_logs
- `(patrol_session_id, scanned_at)`
- `(patrol_checkpoint_id, scanned_at)`

## incidents
- `(client_site_id, incident_status)`
- `(reported_at)`
- `(severity_level, incident_status)`

## payroll_employee_summaries
- `(payroll_period_id, employee_id)`

## invoices
- `(client_id, invoice_status)`
- `(billing_period_start, billing_period_end)`
- `(due_date, invoice_status)`

## employee_loans
- `(employee_id, loan_status)`

---

# 11. FIELD UMUM YANG DISARANKAN

Sebagian besar tabel sebaiknya memiliki field standar berikut:

```sql
- created_at
- updated_at
```

Untuk tabel penting, sangat direkomendasikan menambah:

```sql
- created_by
- updated_by
- deleted_at
- deleted_by
- version_no
```

Field tambahan ini berguna untuk:
- audit trail
- soft delete
- optimistic locking
- histori perubahan yang lebih rapi

Tabel yang paling layak memakai field lengkap ini:
- employees
- employee_contracts
- client_contracts
- client_sites
- employee_deployments
- work_schedules
- attendance_manual_adjustments
- incidents
- payroll_employee_summaries
- invoices
- employee_loans

---

# 12. CATATAN DESAIN PENTING

## 12.1 Jangan pisahkan database per tier
Tier produk tidak perlu database berbeda.

Yang lebih tepat:
- satu schema utama
- feature diaktifkan berdasarkan subscription / feature module

## 12.2 Deployment adalah pusat relasi operasional
Tabel `employee_deployments` adalah pusat utama karena menghubungkan:
- employee
- client
- contract
- site
- post
- position

## 12.3 Work schedule adalah pusat aktivitas harian
Tabel `work_schedules` menjadi referensi utama untuk:
- attendance
- patrol
- incident
- replacement

## 12.4 Payroll dan billing tidak boleh berdiri sendiri
Payroll dan billing wajib menarik data dari operasi nyata, bukan input manual terpisah.

## 12.5 Add-on harus tetap menempel ke core
Contoh:
- loan menempel ke payroll
- training menempel ke employee dan site compliance
- asset menempel ke employee/site
- performance menempel ke employee dan incident/attendance bila perlu

---

# 13. REKOMENDASI MIGRATION BUILD ORDER

## Phase 1 — Basic foundation
1. product_control
2. organization
3. access_control
4. master_hr
5. client_contract
6. site_operations
7. workforce_operations
8. attendance

## Phase 2 — Pro foundation
9. leave_replacement
10. patrol
11. incident
12. payroll
13. audit

## Phase 3 — Enterprise foundation
14. billing
15. enterprise scope & portal support
16. integration

## Phase 4 — Add-on domain
17. recruitment
18. loan_finance
19. training_compliance
20. asset_logbook
21. performance

---

# 14. CONTOH ALUR IMPLEMENTASI DATA

## Saat guard baru diterima
```text
employees
→ guard_profiles
→ guard_certifications
→ employee_contracts
```

## Saat guard ditempatkan
```text
employee_deployments
→ deployment_histories
```

## Saat jadwal dibuat
```text
work_schedules
```

## Saat guard hadir
```text
attendance_records
→ attendance_exceptions (jika ada)
```

## Saat patroli
```text
patrol_sessions
→ patrol_logs
```

## Saat insiden terjadi
```text
incidents
→ incident_files
→ incident_follow_ups
→ incident_escalations
```

## Saat payroll diproses
```text
payroll_periods
→ payroll_employee_summaries
→ payroll_employee_component_values
→ payslips
```

## Saat invoice dibuat
```text
invoices
→ invoice_items
→ client_payments
→ invoice_approvals
```

## Saat pinjaman karyawan aktif
```text
employee_loans
→ employee_loan_installments
→ payroll deduction
```

---

# 15. KESIMPULAN

Schema database ini dirancang agar sistem dapat berkembang menjadi:
- **HRIS Basic** untuk operasional inti
- **HRIS Pro** untuk kontrol lapangan dan payroll
- **HRIS Enterprise** untuk billing, governance, analytics, dan integrasi
- **Add-on platform** untuk monetisasi bertahap

Ringkasnya, struktur inti sistem dapat dibaca seperti ini:

```text
Product Tier / Feature Module
→ Employee
→ Deployment
→ Schedule
→ Attendance / Patrol / Incident
→ Payroll
→ Billing
→ Audit / Integration
```

Dengan pondasi ini, tim development bisa membagi pekerjaan ke area:
- backend API
- admin web
- mobile app
- payroll module
- billing module
- add-on module
- reporting & dashboard
- enterprise integration

Dokumen ini sekarang sudah sinkron dengan:
- positioning produk
- breakdown modul
- roadmap tier-based
- API design tier-based
