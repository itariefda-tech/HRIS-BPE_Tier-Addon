export type UiLanguage = "id" | "en";

type MessageKey =
  | "app.name"
  | "auth.title"
  | "auth.subtitle"
  | "auth.identifier"
  | "auth.password"
  | "auth.submit"
  | "auth.demo"
  | "nav.dashboard"
  | "nav.employees"
  | "nav.clients"
  | "nav.sites"
  | "nav.deployments"
  | "nav.schedules"
  | "nav.attendance"
  | "layout.profile"
  | "layout.logout";

const messages: Record<UiLanguage, Record<MessageKey, string>> = {
  id: {
    "app.name": "HRIS BPE Web",
    "auth.title": "Masuk ke operasi Basic",
    "auth.subtitle": "Fokus pada alur employee, deployment, schedule, dan attendance.",
    "auth.identifier": "Email atau username",
    "auth.password": "Password",
    "auth.submit": "Masuk",
    "auth.demo": "Akun seed demo tersedia untuk owner, supervisor, dan guard.",
    "nav.dashboard": "Dashboard",
    "nav.employees": "Employee",
    "nav.clients": "Client",
    "nav.sites": "Site & Post",
    "nav.deployments": "Deployment",
    "nav.schedules": "Schedule",
    "nav.attendance": "Attendance",
    "layout.profile": "Profil",
    "layout.logout": "Keluar",
  },
  en: {
    "app.name": "HRIS BPE Web",
    "auth.title": "Sign in to Basic operations",
    "auth.subtitle": "Focus on employee, deployment, schedule, and attendance flow.",
    "auth.identifier": "Email or username",
    "auth.password": "Password",
    "auth.submit": "Sign in",
    "auth.demo": "Seed demo accounts are available for owner, supervisor, and guard.",
    "nav.dashboard": "Dashboard",
    "nav.employees": "Employees",
    "nav.clients": "Clients",
    "nav.sites": "Sites & Posts",
    "nav.deployments": "Deployments",
    "nav.schedules": "Schedules",
    "nav.attendance": "Attendance",
    "layout.profile": "Profile",
    "layout.logout": "Logout",
  },
};

export function t(language: UiLanguage, key: MessageKey) {
  return messages[language][key] ?? messages.id[key];
}
