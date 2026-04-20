"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDate, formatDateTime } from "@/lib/format";
import {
  badgeClass,
  inputClass,
  labelClass,
  primaryButtonClass,
  secondaryButtonClass,
  surfaceClass,
  tableCellClass,
  tableClass,
  tableHeadClass,
  tableWrapperClass,
} from "@/lib/ui";
import { useAuthStore } from "@/store/auth-store";

type AdjustmentFormValues = {
  new_check_in_datetime: string;
  new_check_out_datetime: string;
  reason: string;
};

type ExceptionFormValues = {
  exception_type: string;
  description: string;
};

const adjustmentFormDefaults: AdjustmentFormValues = {
  new_check_in_datetime: "",
  new_check_out_datetime: "",
  reason: "",
};

const exceptionFormDefaults: ExceptionFormValues = {
  exception_type: "GPS_REVIEW",
  description: "",
};

function exceptionStatusTone(status: string) {
  if (status === "RESOLVED") {
    return "success";
  }
  if (status === "REJECTED") {
    return "danger";
  }
  return "warning";
}

export default function AttendancePage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const permissionCodes = useAuthStore(
    (state) => state.session?.user.permission_codes ?? [],
  );
  const canManageAttendance = permissionCodes.includes("attendance.manage");
  const canWriteAttendance =
    canManageAttendance || permissionCodes.includes("attendance.self_service");

  const [dateFilter, setDateFilter] = useState("");
  const [siteFilter, setSiteFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedRecordId, setSelectedRecordId] = useState<number | null>(null);
  const [adjustmentSuccess, setAdjustmentSuccess] = useState<string | null>(null);
  const [exceptionSuccess, setExceptionSuccess] = useState<string | null>(null);
  const [resolveSuccess, setResolveSuccess] = useState<string | null>(null);

  const adjustmentForm = useForm<AdjustmentFormValues>({
    defaultValues: adjustmentFormDefaults,
  });
  const exceptionForm = useForm<ExceptionFormValues>({
    defaultValues: exceptionFormDefaults,
  });

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
  const postsQuery = useQuery({
    queryKey: ["posts"],
    queryFn: () => api.siteOperations.listPosts(accessToken!),
    enabled: Boolean(accessToken),
  });
  const employeesQuery = useQuery({
    queryKey: ["employees"],
    queryFn: () => api.masterHr.listEmployees(accessToken!),
    enabled: Boolean(accessToken),
  });
  const manualAdjustmentsQuery = useQuery({
    queryKey: ["attendance-manual-adjustments"],
    queryFn: () => api.attendance.listManualAdjustments(accessToken!),
    enabled: Boolean(accessToken),
  });
  const exceptionsQuery = useQuery({
    queryKey: ["attendance-exceptions"],
    queryFn: () => api.attendance.listExceptions(accessToken!),
    enabled: Boolean(accessToken),
  });

  const siteNameById = useMemo(
    () => new Map((sitesQuery.data ?? []).map((item) => [item.id, item.name])),
    [sitesQuery.data],
  );
  const postNameById = useMemo(
    () => new Map((postsQuery.data ?? []).map((item) => [item.id, item.name])),
    [postsQuery.data],
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

  const effectiveSelectedRecordId = useMemo(() => {
    if (filteredRecords.length === 0) {
      return null;
    }

    if (selectedRecordId !== null) {
      const selectedStillVisible = filteredRecords.some(
        (item) => item.id === selectedRecordId,
      );
      if (selectedStillVisible) {
        return selectedRecordId;
      }
    }

    return filteredRecords[0].id;
  }, [filteredRecords, selectedRecordId]);

  const attendanceDetailQuery = useQuery({
    queryKey: ["attendance-record-detail", effectiveSelectedRecordId],
    queryFn: () =>
      api.attendance.getRecordDetail(accessToken!, effectiveSelectedRecordId!),
    enabled: Boolean(accessToken) && effectiveSelectedRecordId !== null,
  });

  const selectedRecord = attendanceDetailQuery.data ?? null;

  const selectedAdjustments = useMemo(() => {
    if (!selectedRecord) {
      return [];
    }

    return (manualAdjustmentsQuery.data ?? []).filter(
      (item) => item.attendance_record_id === selectedRecord.id,
    );
  }, [manualAdjustmentsQuery.data, selectedRecord]);

  const selectedExceptions = useMemo(() => {
    if (!selectedRecord) {
      return [];
    }

    return (exceptionsQuery.data ?? []).filter(
      (item) => item.attendance_record_id === selectedRecord.id,
    );
  }, [exceptionsQuery.data, selectedRecord]);

  const openExceptions = selectedExceptions.filter(
    (item) => item.resolution_status === "OPEN",
  );

  const manualAdjustmentMutation = useMutation({
    mutationFn: (values: AdjustmentFormValues) =>
      api.attendance.createManualAdjustment(accessToken!, {
        attendance_record_id: effectiveSelectedRecordId!,
        new_check_in_datetime: values.new_check_in_datetime || null,
        new_check_out_datetime: values.new_check_out_datetime || null,
        reason: values.reason.trim(),
      }),
    onSuccess: (adjustment) => {
      setAdjustmentSuccess("Manual adjustment berhasil disimpan.");
      setResolveSuccess(null);
      adjustmentForm.reset(adjustmentFormDefaults);
      queryClient.invalidateQueries({ queryKey: ["attendance-records"] });
      queryClient.invalidateQueries({
        queryKey: ["attendance-record-detail", adjustment.attendance_record_id],
      });
      queryClient.invalidateQueries({ queryKey: ["attendance-manual-adjustments"] });
    },
  });

  const createExceptionMutation = useMutation({
    mutationFn: (values: ExceptionFormValues) =>
      api.attendance.createException(accessToken!, {
        attendance_record_id: effectiveSelectedRecordId!,
        exception_type: values.exception_type.trim().toUpperCase(),
        description: values.description.trim(),
      }),
    onSuccess: () => {
      setExceptionSuccess("Attendance exception berhasil dibuat.");
      setResolveSuccess(null);
      exceptionForm.reset(exceptionFormDefaults);
      queryClient.invalidateQueries({ queryKey: ["attendance-exceptions"] });
    },
  });

  const resolveExceptionMutation = useMutation({
    mutationFn: (payload: { exceptionId: number; resolutionStatus: "RESOLVED" | "REJECTED" }) =>
      api.attendance.resolveException(accessToken!, payload.exceptionId, {
        resolution_status: payload.resolutionStatus,
      }),
    onSuccess: (exception) => {
      setResolveSuccess(
        exception.resolution_status === "RESOLVED"
          ? "Exception berhasil diselesaikan."
          : "Exception berhasil ditolak.",
      );
      queryClient.invalidateQueries({ queryKey: ["attendance-exceptions"] });
    },
  });

  function resetActionFeedback() {
    setAdjustmentSuccess(null);
    setExceptionSuccess(null);
    setResolveSuccess(null);
  }

  useEffect(() => {
    adjustmentForm.reset(adjustmentFormDefaults);
    exceptionForm.reset(exceptionFormDefaults);
  }, [adjustmentForm, exceptionForm, selectedRecord?.id]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Attendance"
        description="Monitoring attendance, lihat detail record dari endpoint khusus, lalu proses manual adjustment dan exception bila diperlukan."
      />

      <GapList
        items={[
          "Detail attendance sekarang memakai endpoint /api/v1/attendance/records/{attendance_record_id}.",
          "Manual adjustment dan exception attendance sudah memakai endpoint backend khusus.",
          "Absent final sekarang dihitung dari schedule PUBLISHED atau APPROVED yang belum memiliki attendance record, jadi tidak muncul sebagai baris attendance record tersendiri.",
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
              onChange={(event) => {
                resetActionFeedback();
                setDateFilter(event.target.value);
              }}
            />
          </div>
          <div>
            <label className={labelClass}>Filter Site</label>
            <select
              className={inputClass}
              value={siteFilter}
              onChange={(event) => {
                resetActionFeedback();
                setSiteFilter(event.target.value);
              }}
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
              onChange={(event) => {
                resetActionFeedback();
                setStatusFilter(event.target.value);
              }}
            >
              <option value="">Semua status</option>
              <option value="PRESENT">PRESENT</option>
              <option value="LATE">LATE</option>
              <option value="COMPLETED">COMPLETED</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <DataState
            isLoading={
              attendanceQuery.isLoading ||
              sitesQuery.isLoading ||
              postsQuery.isLoading ||
              employeesQuery.isLoading
            }
            error={
              attendanceQuery.error ??
              sitesQuery.error ??
              postsQuery.error ??
              employeesQuery.error
            }
            isEmpty={filteredRecords.length === 0}
            emptyMessage="Belum ada attendance record yang cocok dengan filter."
          >
            <div className={tableWrapperClass}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Employee</th>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Post</th>
                    <th className={tableHeadClass}>Date</th>
                    <th className={tableHeadClass}>Status</th>
                    <th className={tableHeadClass}>Flags</th>
                    <th className={tableHeadClass}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((item) => {
                    const isSelected = item.id === effectiveSelectedRecordId;

                    return (
                      <tr
                        key={item.id}
                        className={`border-t border-[color:var(--border)] ${
                          isSelected ? "bg-[color:var(--muted-surface)]" : ""
                        }`}
                      >
                        <td className={tableCellClass}>
                          {employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`}
                        </td>
                        <td className={tableCellClass}>
                          {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                        </td>
                        <td className={tableCellClass}>
                          {postNameById.get(item.site_post_id ?? -1) ?? "-"}
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
                            onClick={() => {
                              resetActionFeedback();
                              setSelectedRecordId(item.id);
                            }}
                          >
                            {isSelected ? "Dipilih" : "Detail"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </DataState>
        </div>
      </section>

      <section className={surfaceClass}>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Detail dan Tindak Lanjut Attendance</h2>
            <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
              Panel ini mengambil detail record langsung dari API, lalu menampilkan riwayat
              adjustment dan exception yang terkait.
            </p>
          </div>
          {selectedRecord ? (
            <p className="text-sm text-[color:var(--muted-foreground)]">
              Attendance ID: {selectedRecord.id}
            </p>
          ) : null}
        </div>

        <div className="mt-4">
          <DataState
            isLoading={Boolean(effectiveSelectedRecordId) && attendanceDetailQuery.isLoading}
            error={attendanceDetailQuery.error}
            isEmpty={!effectiveSelectedRecordId}
            emptyMessage="Pilih attendance record dari tabel untuk melihat detail."
          >
            {selectedRecord ? (
              <div className="grid gap-8 xl:grid-cols-[0.95fr_1.05fr]">
                <div className="space-y-6 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Attendance
                    </p>
                    <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                      {employeeNameById.get(selectedRecord.employee_id) ??
                        `Employee ${selectedRecord.employee_id}`}
                    </p>
                    <p className="mt-1 text-[color:var(--muted-foreground)]">
                      {siteNameById.get(selectedRecord.client_site_id) ??
                        `Site ${selectedRecord.client_site_id}`}
                      {selectedRecord.site_post_id
                        ? ` / ${postNameById.get(selectedRecord.site_post_id) ?? `Post ${selectedRecord.site_post_id}`}`
                        : ""}
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Work Schedule
                      </p>
                      <p className="mt-1">#{selectedRecord.work_schedule_id}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Attendance Date
                      </p>
                      <p className="mt-1">{formatDate(selectedRecord.attendance_date)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Status
                      </p>
                      <p className="mt-1">{selectedRecord.attendance_status}</p>
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
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Overtime Minutes
                      </p>
                      <p className="mt-1">{selectedRecord.overtime_minutes}</p>
                    </div>
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
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Validation Flags
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className={badgeClass(selectedRecord.gps_valid_flag ? "success" : "danger")}>
                        GPS {selectedRecord.gps_valid_flag ? "Valid" : "Invalid"}
                      </span>
                      <span
                        className={badgeClass(
                          selectedRecord.geofence_valid_flag ? "success" : "warning",
                        )}
                      >
                        Geofence {selectedRecord.geofence_valid_flag ? "Valid" : "Review"}
                      </span>
                      <span className={badgeClass(selectedRecord.face_valid_flag ? "success" : "warning")}>
                        Face {selectedRecord.face_valid_flag ? "Valid" : "Review"}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Media dan Remarks
                    </p>
                    <p className="mt-2">
                      Check-in photo: {fallbackText(selectedRecord.check_in_photo_path)}
                    </p>
                    <p className="mt-1">
                      Check-out photo: {fallbackText(selectedRecord.check_out_photo_path)}
                    </p>
                    <p className="mt-1">Remarks: {fallbackText(selectedRecord.remarks)}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Manual Adjustment History
                    </p>
                    {manualAdjustmentsQuery.isLoading ? (
                      <p className="mt-2 text-[color:var(--muted-foreground)]">
                        Memuat riwayat adjustment...
                      </p>
                    ) : manualAdjustmentsQuery.error ? (
                      <p className="mt-2 text-[color:var(--danger)]">
                        {manualAdjustmentsQuery.error.message}
                      </p>
                    ) : selectedAdjustments.length > 0 ? (
                      <div className="mt-2 space-y-3">
                        {selectedAdjustments.map((item) => (
                          <div
                            key={item.id}
                            className="rounded-md border border-[color:var(--border)] px-3 py-3"
                          >
                            <p className="font-medium">Adjustment #{item.id}</p>
                            <p className="mt-1">
                              Check-in: {formatDateTime(item.old_check_in_datetime)} to{" "}
                              {formatDateTime(item.new_check_in_datetime)}
                            </p>
                            <p className="mt-1">
                              Check-out: {formatDateTime(item.old_check_out_datetime)} to{" "}
                              {formatDateTime(item.new_check_out_datetime)}
                            </p>
                            <p className="mt-1">Reason: {item.reason}</p>
                            <p className="mt-1 text-[color:var(--muted-foreground)]">
                              Dibuat {formatDateTime(item.created_at)}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-2 text-[color:var(--muted-foreground)]">
                        Belum ada manual adjustment untuk record ini.
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Attendance Exceptions
                    </p>
                    {exceptionsQuery.isLoading ? (
                      <p className="mt-2 text-[color:var(--muted-foreground)]">
                        Memuat exception attendance...
                      </p>
                    ) : exceptionsQuery.error ? (
                      <p className="mt-2 text-[color:var(--danger)]">
                        {exceptionsQuery.error.message}
                      </p>
                    ) : selectedExceptions.length > 0 ? (
                      <div className="mt-2 space-y-3">
                        {selectedExceptions.map((item) => (
                          <div
                            key={item.id}
                            className="rounded-md border border-[color:var(--border)] px-3 py-3"
                          >
                            <div className="flex flex-wrap items-center gap-2">
                              <p className="font-medium">{item.exception_type}</p>
                              <span className={badgeClass(exceptionStatusTone(item.resolution_status))}>
                                {item.resolution_status}
                              </span>
                            </div>
                            <p className="mt-1">{item.description}</p>
                            <p className="mt-1 text-[color:var(--muted-foreground)]">
                              Dibuat {formatDateTime(item.created_at)}
                            </p>
                            {item.resolved_at ? (
                              <p className="mt-1 text-[color:var(--muted-foreground)]">
                                Diproses {formatDateTime(item.resolved_at)}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-2 text-[color:var(--muted-foreground)]">
                        Belum ada exception untuk record ini.
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Audit
                    </p>
                    <p className="mt-1">Dibuat: {formatDateTime(selectedRecord.created_at)}</p>
                    <p className="mt-1">
                      Diperbarui: {formatDateTime(selectedRecord.updated_at)}
                    </p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="rounded-md border border-[color:var(--border)] px-4 py-4">
                    <h3 className="text-base font-semibold">Manual Adjustment</h3>
                    <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
                      Gunakan saat waktu check-in atau check-out perlu dikoreksi.
                    </p>

                    {canManageAttendance ? (
                      <form
                        className="mt-4 grid gap-4"
                        onSubmit={adjustmentForm.handleSubmit((values) =>
                          manualAdjustmentMutation.mutate(values),
                        )}
                      >
                        <div>
                          <label className={labelClass}>New Check In</label>
                          <input
                            className={inputClass}
                            type="datetime-local"
                            {...adjustmentForm.register("new_check_in_datetime")}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>New Check Out</label>
                          <input
                            className={inputClass}
                            type="datetime-local"
                            {...adjustmentForm.register("new_check_out_datetime")}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Reason</label>
                          <textarea
                            className={`${inputClass} min-h-24`}
                            {...adjustmentForm.register("reason", { required: true })}
                          />
                        </div>

                        {adjustmentSuccess ? (
                          <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                            {adjustmentSuccess}
                          </div>
                        ) : null}
                        {manualAdjustmentMutation.error ? (
                          <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                            {manualAdjustmentMutation.error.message}
                          </div>
                        ) : null}
                        <div className="flex gap-2">
                          <button
                            type="submit"
                            className={primaryButtonClass}
                            disabled={manualAdjustmentMutation.isPending}
                          >
                            {manualAdjustmentMutation.isPending
                              ? "Menyimpan..."
                              : "Simpan adjustment"}
                          </button>
                          <button
                            type="button"
                            className={secondaryButtonClass}
                            onClick={() => adjustmentForm.reset(adjustmentFormDefaults)}
                          >
                            Reset
                          </button>
                        </div>
                      </form>
                    ) : (
                      <p className="mt-4 text-sm text-[color:var(--muted-foreground)]">
                        User ini belum punya permission `attendance.manage`.
                      </p>
                    )}
                  </div>

                  <div className="rounded-md border border-[color:var(--border)] px-4 py-4">
                    <h3 className="text-base font-semibold">Buat Attendance Exception</h3>
                    <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
                      Catat exception operasional seperti GPS review, face review, atau check-out
                      missing.
                    </p>

                    {canWriteAttendance ? (
                      <form
                        className="mt-4 grid gap-4"
                        onSubmit={exceptionForm.handleSubmit((values) =>
                          createExceptionMutation.mutate(values),
                        )}
                      >
                        <div>
                          <label className={labelClass}>Exception Type</label>
                          <input
                            className={inputClass}
                            placeholder="GPS_REVIEW"
                            {...exceptionForm.register("exception_type", { required: true })}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Description</label>
                          <textarea
                            className={`${inputClass} min-h-24`}
                            {...exceptionForm.register("description", { required: true })}
                          />
                        </div>

                        {exceptionSuccess ? (
                          <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                            {exceptionSuccess}
                          </div>
                        ) : null}
                        {createExceptionMutation.error ? (
                          <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                            {createExceptionMutation.error.message}
                          </div>
                        ) : null}
                        <div className="flex gap-2">
                          <button
                            type="submit"
                            className={primaryButtonClass}
                            disabled={createExceptionMutation.isPending}
                          >
                            {createExceptionMutation.isPending
                              ? "Menyimpan..."
                              : "Simpan exception"}
                          </button>
                          <button
                            type="button"
                            className={secondaryButtonClass}
                            onClick={() => exceptionForm.reset(exceptionFormDefaults)}
                          >
                            Reset
                          </button>
                        </div>
                      </form>
                    ) : (
                      <p className="mt-4 text-sm text-[color:var(--muted-foreground)]">
                        User ini belum punya permission untuk membuat exception attendance.
                      </p>
                    )}
                  </div>

                  {canManageAttendance ? (
                    <div className="rounded-md border border-[color:var(--border)] px-4 py-4">
                      <h3 className="text-base font-semibold">Proses Exception</h3>
                      <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
                        Resolve atau reject exception yang masih terbuka untuk record terpilih.
                      </p>

                      {resolveSuccess ? (
                        <div className="mt-4 rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                          {resolveSuccess}
                        </div>
                      ) : null}
                      {resolveExceptionMutation.error ? (
                        <div className="mt-4 rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                          {resolveExceptionMutation.error.message}
                        </div>
                      ) : null}

                      {openExceptions.length > 0 ? (
                        <div className="mt-4 space-y-3">
                          {openExceptions.map((item) => (
                            <div
                              key={item.id}
                              className="rounded-md border border-[color:var(--border)] px-3 py-3"
                            >
                              <p className="font-medium">{item.exception_type}</p>
                              <p className="mt-1 text-sm">{item.description}</p>
                              <div className="mt-3 flex flex-wrap gap-2">
                                <button
                                  type="button"
                                  className={primaryButtonClass}
                                  disabled={resolveExceptionMutation.isPending}
                                  onClick={() =>
                                    resolveExceptionMutation.mutate({
                                      exceptionId: item.id,
                                      resolutionStatus: "RESOLVED",
                                    })
                                  }
                                >
                                  Resolve
                                </button>
                                <button
                                  type="button"
                                  className={secondaryButtonClass}
                                  disabled={resolveExceptionMutation.isPending}
                                  onClick={() =>
                                    resolveExceptionMutation.mutate({
                                      exceptionId: item.id,
                                      resolutionStatus: "REJECTED",
                                    })
                                  }
                                >
                                  Reject
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-4 text-sm text-[color:var(--muted-foreground)]">
                          Tidak ada exception OPEN untuk record ini.
                        </p>
                      )}
                    </div>
                  ) : null}
                </div>
              </div>
            ) : null}
          </DataState>
        </div>
      </section>
    </div>
  );
}
