"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { MetricCard } from "@/components/ui/metric-card";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import {
  surfaceClass,
  tableCellClass,
  tableClass,
  tableHeadClass,
  tableWrapperClass,
} from "@/lib/ui";
import { todayInputValue } from "@/lib/date";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardPage() {
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const today = todayInputValue();

  const summaryQuery = useQuery({
    queryKey: ["dashboard", "ops-summary"],
    queryFn: () => api.dashboard.opsSummary(accessToken!),
    enabled: Boolean(accessToken),
  });

  const attendanceReportQuery = useQuery({
    queryKey: ["dashboard", "attendance-report", today],
    queryFn: () =>
      api.dashboard.attendanceReport(accessToken!, {
        dateFrom: today,
        dateTo: today,
      }),
    enabled: Boolean(accessToken),
  });

  const metrics = useMemo(() => {
    if (!summaryQuery.data || !attendanceReportQuery.data) {
      return [];
    }

    return [
      {
        label: "Total employee",
        value: summaryQuery.data.employees_total,
        helper: "Cakupan employee sesuai scope user.",
      },
      {
        label: "Total client",
        value: summaryQuery.data.clients_total,
        helper: "Client aktif dalam scope operasional.",
      },
      {
        label: "Total site",
        value: summaryQuery.data.sites_total,
        helper: "Site yang masuk cakupan Basic saat ini.",
      },
      {
        label: "Active deployment",
        value: summaryQuery.data.active_deployments,
        helper: "Deployment aktif yang bisa dipakai schedule.",
      },
      {
        label: "Schedule hari ini",
        value: summaryQuery.data.schedules_today,
        helper: "Dipakai sebagai dasar monitoring attendance.",
      },
      {
        label: "Attendance hari ini",
        value: summaryQuery.data.attendance_today,
        helper: "Record attendance yang sudah tercatat hari ini.",
      },
      {
        label: "Present",
        value: summaryQuery.data.present_attendance,
        helper: "Guard yang check-in tepat waktu hari ini.",
      },
      {
        label: "Late",
        value: summaryQuery.data.late_attendance,
        helper: "Guard yang check-in terlambat hari ini.",
      },
      {
        label: "Absent",
        value: summaryQuery.data.absent_attendance,
        helper: "Schedule published/approved tanpa attendance record.",
      },
    ];
  }, [attendanceReportQuery.data, summaryQuery.data]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard Basic"
        description="Ringkasan Basic untuk employee, deployment, schedule, dan attendance hari ini."
      />

      <GapList
        items={[
          "Absent dihitung dari schedule PUBLISHED atau APPROVED yang belum memiliki attendance record pada hari yang sama.",
          "Status table tetap menampilkan status record attendance aktual, ditambah ABSENT sintetis bila ada schedule yang belum terisi.",
        ]}
      />

      <DataState
        isLoading={summaryQuery.isLoading || attendanceReportQuery.isLoading}
        error={summaryQuery.error ?? attendanceReportQuery.error}
        isEmpty={metrics.length === 0}
        emptyMessage="Ringkasan dashboard belum tersedia."
      >
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <MetricCard
              key={metric.label}
              label={metric.label}
              value={metric.value}
              helper={metric.helper}
            />
          ))}
        </section>

        {attendanceReportQuery.data ? (
          <section className="grid gap-4 xl:grid-cols-2">
            <div className={surfaceClass}>
              <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
                Validasi Attendance Hari Ini
              </h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-md bg-[color:var(--muted-surface)] px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    GPS Valid
                  </p>
                  <p className="mt-2 text-2xl font-semibold">
                    {formatNumber(attendanceReportQuery.data.gps_valid_total)}
                  </p>
                </div>
                <div className="rounded-md bg-[color:var(--muted-surface)] px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Geofence Valid
                  </p>
                  <p className="mt-2 text-2xl font-semibold">
                    {formatNumber(attendanceReportQuery.data.geofence_valid_total)}
                  </p>
                </div>
                <div className="rounded-md bg-[color:var(--muted-surface)] px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Face Valid
                  </p>
                  <p className="mt-2 text-2xl font-semibold">
                    {formatNumber(attendanceReportQuery.data.face_valid_total)}
                  </p>
                </div>
                <div className="rounded-md bg-[color:var(--muted-surface)] px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Overtime Minutes
                  </p>
                  <p className="mt-2 text-2xl font-semibold">
                    {formatNumber(attendanceReportQuery.data.total_overtime_minutes)}
                  </p>
                </div>
              </div>
            </div>

            <div className={surfaceClass}>
              <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
                Status Attendance Hari Ini
              </h2>
              <div className={`${tableWrapperClass} mt-4`}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Status</th>
                      <th className={tableHeadClass}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceReportQuery.data.by_status.map((item) => (
                      <tr key={item.key} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>{item.key}</td>
                        <td className={tableCellClass}>{formatNumber(item.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        ) : null}

        {attendanceReportQuery.data ? (
          <section className={surfaceClass}>
            <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
              Distribusi Attendance per Site
            </h2>
            <div className={`${tableWrapperClass} mt-4`}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Total Attendance</th>
                  </tr>
                </thead>
                <tbody>
                  {attendanceReportQuery.data.by_site.map((item) => (
                    <tr key={item.client_site_id} className="border-t border-[color:var(--border)]">
                      <td className={tableCellClass}>{item.site_name}</td>
                      <td className={tableCellClass}>{formatNumber(item.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}
      </DataState>
    </div>
  );
}
