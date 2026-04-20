export type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, unknown> | null;
  errors?: Record<string, unknown> | null;
};

export type AuthUser = {
  id: number;
  employee_id: number | null;
  username: string;
  email: string;
  phone: string | null;
  preferred_language: "id" | "en";
  preferred_theme: "theme_1" | "theme_2" | "theme_3" | "theme_4" | "theme_5";
  is_active: boolean;
  last_login_at: string | null;
  role_codes: string[];
  permission_codes: string[];
  company_ids: number[];
  company_scope_ids: number[];
  branch_scope_ids: number[];
  site_scope_ids: number[];
  has_explicit_scope: boolean;
};

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  session_id: string;
  access_token_expires_at: string;
  refresh_token_expires_at: string;
  user: AuthUser;
};

export type Company = {
  id: number;
  code: string;
  name: string;
  legal_name: string | null;
  status: string;
  default_language: "id" | "en" | null;
  default_theme:
    | "theme_1"
    | "theme_2"
    | "theme_3"
    | "theme_4"
    | "theme_5"
    | null;
};

export type Branch = {
  id: number;
  company_id: number;
  code: string;
  name: string;
  city: string | null;
  province: string | null;
  status: string;
};

export type Department = {
  id: number;
  company_id: number;
  code: string;
  name: string;
  description: string | null;
};

export type Position = {
  id: number;
  company_id: number;
  code: string;
  name: string;
  category: string | null;
  level_order: number;
};

export type Employee = {
  id: number;
  company_id: number;
  branch_id: number;
  department_id: number | null;
  position_id: number | null;
  employee_number: string;
  full_name: string;
  nik: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  gender: string | null;
  marital_status: string | null;
  hire_date: string | null;
  employment_status: string | null;
  employee_status: string;
  resign_date: string | null;
  photo_path: string | null;
  created_at: string;
  updated_at: string;
};

export type Client = {
  id: number;
  company_id: number;
  code: string;
  name: string;
  industry_type: string | null;
  contact_person_name: string | null;
  contact_person_phone: string | null;
  contact_person_email: string | null;
  billing_address: string | null;
  tax_number: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type ClientContract = {
  id: number;
  client_id: number;
  contract_number: string;
  contract_title: string;
  start_date: string;
  end_date: string | null;
  contract_type: string | null;
  currency: string;
  tax_included_flag: boolean;
  payment_term_days: number;
  sla_description: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ClientSite = {
  id: number;
  client_id: number;
  code: string;
  name: string;
  address: string | null;
  city: string | null;
  province: string | null;
  latitude: string | null;
  longitude: string | null;
  radius_meters: number | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type SitePost = {
  id: number;
  client_site_id: number;
  code: string;
  name: string;
  description: string | null;
  active_flag: boolean;
  created_at: string;
  updated_at: string;
};

export type EmployeeDeployment = {
  id: number;
  employee_id: number;
  client_id: number;
  client_contract_id: number;
  client_site_id: number;
  site_post_id: number | null;
  position_id: number | null;
  start_date: string;
  end_date: string | null;
  deployment_status: string;
  source_type: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ShiftType = {
  id: number;
  company_id: number;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
  cross_day_flag: boolean;
  break_minutes: number;
  tolerance_late_minutes: number;
  overtime_after_minutes: number;
  created_at: string;
  updated_at: string;
};

export type WorkSchedule = {
  id: number;
  employee_id: number;
  employee_deployment_id: number;
  client_site_id: number;
  site_post_id: number | null;
  shift_type_id: number;
  scheduled_date: string;
  scheduled_start_datetime: string;
  scheduled_end_datetime: string;
  schedule_status: string;
  replacement_for_schedule_id: number | null;
  generated_by: number | null;
  approved_by: number | null;
  created_at: string;
  updated_at: string;
};

export type AttendanceRecord = {
  id: number;
  employee_id: number;
  work_schedule_id: number;
  client_site_id: number;
  site_post_id: number | null;
  attendance_date: string;
  check_in_datetime: string | null;
  check_out_datetime: string | null;
  check_in_latitude: string | null;
  check_in_longitude: string | null;
  check_out_latitude: string | null;
  check_out_longitude: string | null;
  check_in_photo_path: string | null;
  check_out_photo_path: string | null;
  check_in_method: string | null;
  check_out_method: string | null;
  gps_valid_flag: boolean;
  face_valid_flag: boolean;
  geofence_valid_flag: boolean;
  attendance_status: string;
  minutes_late: number;
  working_minutes: number;
  overtime_minutes: number;
  remarks: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardOpsSummary = {
  employees_total: number;
  clients_total: number;
  sites_total: number;
  active_deployments: number;
  schedules_today: number;
  attendance_today: number;
};

export type DashboardGroupedCount = {
  key: string;
  total: number;
};

export type DashboardSiteCount = {
  client_site_id: number;
  site_name: string;
  total: number;
};

export type DashboardAttendanceReport = {
  date_from: string;
  date_to: string;
  total_attendance: number;
  present_attendance: number;
  late_attendance: number;
  completed_attendance: number;
  gps_valid_total: number;
  geofence_valid_total: number;
  face_valid_total: number;
  total_working_minutes: number;
  total_overtime_minutes: number;
  by_status: DashboardGroupedCount[];
  by_site: DashboardSiteCount[];
};
