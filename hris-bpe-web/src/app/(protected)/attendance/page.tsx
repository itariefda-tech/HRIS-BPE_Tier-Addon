"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDate, formatDateTime } from "@/lib/format";
import {
  badgeClass,
  inputClass,
  labelClass,
  secondaryButtonClass,
  surfaceClass,
  tableCellClass,
  tableClass,
  tableHeadClass,
  tableWrapperClass,
} from "@/lib/ui";
import { useAuthStore } from "@/store/auth-store";

export default function AttendancePage() {
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [dateFilter, setDateFilter] = useState("");
  const [siteFilter, setSiteFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedRecordId, setSelectedRecordId] = useState<number | null>(null);

  const attendanceQuery = useQuery({
    queryKey: ["attendance-records"],
    queryFn: () => api.attendance.listRecords(accessToken!),
    enabled: Boolean(accessToken),
  });
  const sitesQuery = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.siteOperations.listSites(accessToken!),
    enabled: Boolean(accessToken),
  });
  const employeesQuery = useQuery({
    queryKey: ["employees"],
    queryFn: () => api.masterHr.listEmployees(accessToken!),
    enabled: Boolean(accessToken),
  });

  const siteNameById = useMemo(
    () => new Map((sitesQuery.data ?? []).map((item) => [item.id, item.name])),
    [sitesQuery.data],
  );
  const employeeNameById = useMemo(
    () => new Map((employeesQuery.data ?? []).map((item) => [item.id, item.full_name])),
    [employeesQuery.data],
  );

  const filteredRecords = useMemo(() => {
    return (attendanceQuery.data ?? []).filter((item) => {
      const dateMatches = dateFilter ? item.attendance_date === dateFilter : true;
      const siteMatches = siteFilter ? String(item.client_site_id) === siteFilter : true;
      const statusMatches = statusFilter ? item.attendance_status === statusFilter : true;
      return dateMatches && siteMatches && statusMatches;
    });
  }, [attendanceQuery.data, dateFilter, siteFilter, statusFilter]);

  const selectedRecord =
    filteredRecords.find((item) => item.id === selectedRecordId) ?? filteredRecords[0] ?? null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Attendance"
        description="Monitoring attendance, flag validasi, dan detail sederhana dari record yang sudah ada."
      />

      <GapList
        items={[
          "Belum ada endpoint detail attendance khusus. Panel detail memakai data dari list record.",
          "Status absent final masih menunggu kontrak backend yang lebih jelas.",
          "Filter tanggal, site, dan status masih client-side.",
        ]}
      />

      <section className={surfaceClass}>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className={labelClass}>Filter Date</label>
            <input
              className={inputClass}
              type="date"
              value={dateFilter}
              onChange={(event) => setDateFilter(event.target.value)}
            />
          </div>
          <div>
            <label className={labelClass}>Filter Site</label>
            <select
              className={inputClass}
              value={siteFilter}
              onChange={(event) => setSiteFilter(event.target.value)}
            >
              <option value="">Semua site</option>
              {(sitesQuery.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Filter Status</label>
            <select
              className={inputClass}
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="">Semua status</option>
              <option value="PRESENT">PRESENT</option>
              <option value="LATE">LATE</option>
              <option value="COMPLETED">COMPLETED</option>
            </select>
          </div>
        </div>

        <div className="mt-4 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
          <DataState
            isLoading={
              attendanceQuery.isLoading || sitesQuery.isLoading || employeesQuery.isLoading
            }
            error={attendanceQuery.error ?? sitesQuery.error ?? employeesQuery.error}
            isEmpty={filteredRecords.length === 0}
            emptyMessage="Belum ada attendance record yang cocok dengan filter."
          >
            <div className={tableWrapperClass}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Employee</th>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Date</th>
                    <th className={tableHeadClass}>Status</th>
                    <th className={tableHeadClass}>Flags</th>
                    <th className={tableHeadClass}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((item) => (
                    <tr key={item.id} className="border-t border-[color:var(--border)]">
                      <td className={tableCellClass}>
                        {employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                      </td>
                      <td className={tableCellClass}>{formatDate(item.attendance_date)}</td>
                      <td className={tableCellClass}>{item.attendance_status}</td>
                      <td className={tableCellClass}>
                        <div className="flex flex-wrap gap-1">
                          <span className={badgeClass(item.gps_valid_flag ? "success" : "danger")}>
                            GPS
                          </span>
                          <span
                            className={badgeClass(
                              item.geofence_valid_flag ? "success" : "warning",
                            )}
                          >
                            Geofence
                          </span>
                          <span className={badgeClass(item.face_valid_flag ? "success" : "warning")}>
                            Face
                          </span>
                        </div>
                      </td>
                      <td className={tableCellClass}>
                        <button
                          type="button"
                          className={secondaryButtonClass}
                          onClick={() => setSelectedRecordId(item.id)}
                        >
                          Detail
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DataState>

          <div className={surfaceClass}>
            <h2 className="text-lg font-semibold">Detail Attendance</h2>
            {selectedRecord ? (
              <div className="mt-4 space-y-4 text-sm">
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Employee
                  </p>
                  <p className="mt-1 font-semibold">
                    {employeeNameById.get(selectedRecord.employee_id) ??
                      `Employee ${selectedRecord.employee_id}`}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Site
                  </p>
                  <p className="mt-1">
                    {siteNameById.get(selectedRecord.client_site_id) ??
                      `Site ${selectedRecord.client_site_id}`}
                  </p>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check In
                    </p>
                    <p className="mt-1">{formatDateTime(selectedRecord.check_in_datetime)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check Out
                    </p>
                    <p className="mt-1">{formatDateTime(selectedRecord.check_out_datetime)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check In Method
                    </p>
                    <p className="mt-1">{fallbackText(selectedRecord.check_in_method)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check Out Method
                    </p>
                    <p className="mt-1">{fallbackText(selectedRecord.check_out_method)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check In Coordinate
                    </p>
                    <p className="mt-1">
                      {fallbackText(selectedRecord.check_in_latitude)} /{" "}
                      {fallbackText(selectedRecord.check_in_longitude)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Check Out Coordinate
                    </p>
                    <p className="mt-1">
                      {fallbackText(selectedRecord.check_out_latitude)} /{" "}
                      {fallbackText(selectedRecord.check_out_longitude)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Minutes Late
                    </p>
                    <p className="mt-1">{selectedRecord.minutes_late}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Working Minutes
                    </p>
                    <p className="mt-1">{selectedRecord.working_minutes}</p>
                  </div>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                    Remarks
                  </p>
                  <p className="mt-1">{fallbackText(selectedRecord.remarks)}</p>
                </div>
              </div>
            ) : (
              <p className="mt-4 text-sm text-[color:var(--muted-foreground)]">
                Pilih record attendance dari tabel untuk melihat detail.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
