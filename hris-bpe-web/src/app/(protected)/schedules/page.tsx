"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { addDaysInputValue, todayInputValue } from "@/lib/date";
import { fallbackText, formatDate, formatDateTime } from "@/lib/format";
import {
  optionalNumber,
  optionalText,
  requiredNumber,
  selectedValuesToNumbers,
} from "@/lib/forms";
import type { WorkSchedule } from "@/lib/types";
import {
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

type ShiftTypeFormValues = {
  company_id: string;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
  tolerance_late_minutes: string;
};

type GenerateScheduleFormValues = {
  employee_deployment_ids: string[];
  shift_type_id: string;
  date_from: string;
  date_to: string;
};

type ScheduleEditFormValues = {
  shift_type_id: string;
  scheduled_date: string;
  scheduled_start_datetime: string;
  scheduled_end_datetime: string;
  replacement_for_schedule_id: string;
};

const shiftTypeFormDefaults: ShiftTypeFormValues = {
  company_id: "",
  code: "",
  name: "",
  start_time: "08:00",
  end_time: "17:00",
  tolerance_late_minutes: "15",
};

const generateScheduleFormDefaults: GenerateScheduleFormValues = {
  employee_deployment_ids: [],
  shift_type_id: "",
  date_from: todayInputValue(),
  date_to: addDaysInputValue(6),
};

const scheduleEditFormDefaults: ScheduleEditFormValues = {
  shift_type_id: "",
  scheduled_date: "",
  scheduled_start_datetime: "",
  scheduled_end_datetime: "",
  replacement_for_schedule_id: "",
};

function toDateTimeLocalValue(value: string | null) {
  if (!value) {
    return "";
  }

  return value.slice(0, 16);
}

function toScheduleEditFormValues(schedule: WorkSchedule): ScheduleEditFormValues {
  return {
    shift_type_id: String(schedule.shift_type_id),
    scheduled_date: schedule.scheduled_date,
    scheduled_start_datetime: toDateTimeLocalValue(schedule.scheduled_start_datetime),
    scheduled_end_datetime: toDateTimeLocalValue(schedule.scheduled_end_datetime),
    replacement_for_schedule_id: schedule.replacement_for_schedule_id
      ? String(schedule.replacement_for_schedule_id)
      : "",
  };
}

export default function SchedulesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [shiftTypeSuccess, setShiftTypeSuccess] = useState<string | null>(null);
  const [generateSuccess, setGenerateSuccess] = useState<string | null>(null);
  const [updateSuccess, setUpdateSuccess] = useState<string | null>(null);
  const [siteFilter, setSiteFilter] = useState("");
  const [postFilter, setPostFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [selectedScheduleId, setSelectedScheduleId] = useState<number | null>(null);

  const shiftTypeForm = useForm<ShiftTypeFormValues>({
    defaultValues: shiftTypeFormDefaults,
  });
  const generateForm = useForm<GenerateScheduleFormValues>({
    defaultValues: generateScheduleFormDefaults,
  });
  const scheduleEditForm = useForm<ScheduleEditFormValues>({
    defaultValues: scheduleEditFormDefaults,
  });

  const companiesQuery = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.organization.listCompanies(accessToken!),
    enabled: Boolean(accessToken),
  });
  const employeesQuery = useQuery({
    queryKey: ["employees"],
    queryFn: () => api.masterHr.listEmployees(accessToken!),
    enabled: Boolean(accessToken),
  });
  const deploymentsQuery = useQuery({
    queryKey: ["deployments"],
    queryFn: () => api.workforceOperations.listDeployments(accessToken!),
    enabled: Boolean(accessToken),
  });
  const shiftTypesQuery = useQuery({
    queryKey: ["shift-types"],
    queryFn: () => api.workforceOperations.listShiftTypes(accessToken!),
    enabled: Boolean(accessToken),
  });
  const schedulesQuery = useQuery({
    queryKey: ["schedules"],
    queryFn: () => api.workforceOperations.listWorkSchedules(accessToken!),
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

  const siteNameById = useMemo(
    () => new Map((sitesQuery.data ?? []).map((item) => [item.id, item.name])),
    [sitesQuery.data],
  );
  const postNameById = useMemo(
    () => new Map((postsQuery.data ?? []).map((item) => [item.id, item.name])),
    [postsQuery.data],
  );
  const shiftTypeNameById = useMemo(
    () => new Map((shiftTypesQuery.data ?? []).map((item) => [item.id, item.name])),
    [shiftTypesQuery.data],
  );
  const employeeNameById = useMemo(
    () => new Map((employeesQuery.data ?? []).map((item) => [item.id, item.full_name])),
    [employeesQuery.data],
  );
  const deploymentById = useMemo(
    () => new Map((deploymentsQuery.data ?? []).map((item) => [item.id, item])),
    [deploymentsQuery.data],
  );

  const filteredSchedules = useMemo(() => {
    return (schedulesQuery.data ?? []).filter((item) => {
      const siteMatches = siteFilter ? String(item.client_site_id) === siteFilter : true;
      const postMatches = postFilter ? String(item.site_post_id ?? "") === postFilter : true;
      const dateMatches = dateFilter ? item.scheduled_date === dateFilter : true;
      return siteMatches && postMatches && dateMatches;
    });
  }, [dateFilter, postFilter, schedulesQuery.data, siteFilter]);

  const effectiveSelectedScheduleId = useMemo(() => {
    if (filteredSchedules.length === 0) {
      return null;
    }

    if (selectedScheduleId !== null) {
      const selectedStillVisible = filteredSchedules.some(
        (schedule) => schedule.id === selectedScheduleId,
      );
      if (selectedStillVisible) {
        return selectedScheduleId;
      }
    }

    return filteredSchedules[0].id;
  }, [filteredSchedules, selectedScheduleId]);

  const scheduleDetailQuery = useQuery({
    queryKey: ["schedule-detail", effectiveSelectedScheduleId],
    queryFn: () =>
      api.workforceOperations.getWorkScheduleDetail(
        accessToken!,
        effectiveSelectedScheduleId!,
      ),
    enabled: Boolean(accessToken) && effectiveSelectedScheduleId !== null,
  });

  const createShiftTypeMutation = useMutation({
    mutationFn: (values: ShiftTypeFormValues) =>
      api.workforceOperations.createShiftType(accessToken!, {
        company_id: requiredNumber(values.company_id),
        code: values.code.trim(),
        name: values.name.trim(),
        start_time: values.start_time,
        end_time: values.end_time,
        tolerance_late_minutes: Number(values.tolerance_late_minutes),
      }),
    onSuccess: () => {
      setShiftTypeSuccess("Shift type berhasil dibuat.");
      shiftTypeForm.reset(shiftTypeFormDefaults);
      queryClient.invalidateQueries({ queryKey: ["shift-types"] });
    },
  });

  const generateScheduleMutation = useMutation({
    mutationFn: (values: GenerateScheduleFormValues) =>
      api.workforceOperations.generateWorkSchedules(accessToken!, {
        employee_deployment_ids: selectedValuesToNumbers(values.employee_deployment_ids),
        shift_type_id: requiredNumber(values.shift_type_id),
        date_from: values.date_from,
        date_to: values.date_to,
      }),
    onSuccess: () => {
      setGenerateSuccess("Bulk schedule berhasil dibuat.");
      generateForm.reset(generateScheduleFormDefaults);
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });

  const updateScheduleMutation = useMutation({
    mutationFn: (values: ScheduleEditFormValues) =>
      api.workforceOperations.updateWorkSchedule(accessToken!, effectiveSelectedScheduleId!, {
        shift_type_id: requiredNumber(values.shift_type_id),
        scheduled_date: values.scheduled_date,
        scheduled_start_datetime: optionalText(values.scheduled_start_datetime),
        scheduled_end_datetime: optionalText(values.scheduled_end_datetime),
        replacement_for_schedule_id: optionalNumber(values.replacement_for_schedule_id),
      }),
    onSuccess: (schedule) => {
      setUpdateSuccess("Schedule berhasil diperbarui.");
      queryClient.setQueryData(["schedule-detail", schedule.id], schedule);
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
      scheduleEditForm.reset(toScheduleEditFormValues(schedule));
    },
  });

  const publishScheduleMutation = useMutation({
    mutationFn: (scheduleId: number) =>
      api.workforceOperations.publishWorkSchedule(accessToken!, scheduleId),
    onSuccess: (schedule) => {
      queryClient.setQueryData(["schedule-detail", schedule.id], schedule);
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });

  useEffect(() => {
    if (!scheduleDetailQuery.data) {
      return;
    }

    scheduleEditForm.reset(toScheduleEditFormValues(scheduleDetailQuery.data));
  }, [scheduleDetailQuery.data, scheduleEditForm]);

  const selectedSchedule = scheduleDetailQuery.data ?? null;
  const selectedDeployment = selectedSchedule
    ? deploymentById.get(selectedSchedule.employee_deployment_id) ?? null
    : null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Schedule"
        description="Siapkan shift type, generate work schedule, publish, lalu update detail schedule operasional."
      />

      <GapList
        items={[
          "Detail dan update schedule sudah memakai endpoint /api/v1/workforce-operations/work-schedules/{schedule_id}.",
          "Belum ada calendar view pada iterasi ini.",
          "Endpoint /api/v1/my/schedules sudah ada di backend, tetapi UI mobile guard belum disambungkan.",
          "Filter site, post, dan date masih client-side.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Create Shift Type</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={shiftTypeForm.handleSubmit((values) => createShiftTypeMutation.mutate(values))}
          >
            <div className="md:col-span-2">
              <label className={labelClass}>Company</label>
              <select className={inputClass} {...shiftTypeForm.register("company_id", { required: true })}>
                <option value="">Pilih company</option>
                {(companiesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Code</label>
              <input className={inputClass} {...shiftTypeForm.register("code", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Name</label>
              <input className={inputClass} {...shiftTypeForm.register("name", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Start Time</label>
              <input className={inputClass} type="time" {...shiftTypeForm.register("start_time", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>End Time</label>
              <input className={inputClass} type="time" {...shiftTypeForm.register("end_time", { required: true })} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Tolerance Late Minutes</label>
              <input className={inputClass} type="number" {...shiftTypeForm.register("tolerance_late_minutes")} />
            </div>

            {shiftTypeSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {shiftTypeSuccess}
              </div>
            ) : null}
            {createShiftTypeMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createShiftTypeMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createShiftTypeMutation.isPending}
              >
                {createShiftTypeMutation.isPending ? "Menyimpan..." : "Simpan shift type"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => shiftTypeForm.reset(shiftTypeFormDefaults)}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Generate Schedule</h2>
          <form
            className="mt-4 grid gap-4"
            onSubmit={generateForm.handleSubmit((values) =>
              generateScheduleMutation.mutate(values),
            )}
          >
            <div>
              <label className={labelClass}>Deployment Aktif</label>
              <select
                multiple
                className={`${inputClass} min-h-40`}
                {...generateForm.register("employee_deployment_ids")}
              >
                {(deploymentsQuery.data ?? [])
                  .filter((item) => item.deployment_status === "ACTIVE")
                  .map((item) => (
                    <option key={item.id} value={item.id}>
                      #{item.id} - {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                    </option>
                  ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Shift Type</label>
              <select className={inputClass} {...generateForm.register("shift_type_id", { required: true })}>
                <option value="">Pilih shift type</option>
                {(shiftTypesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} ({item.start_time} - {item.end_time})
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className={labelClass}>Date From</label>
                <input className={inputClass} type="date" {...generateForm.register("date_from", { required: true })} />
              </div>
              <div>
                <label className={labelClass}>Date To</label>
                <input className={inputClass} type="date" {...generateForm.register("date_to", { required: true })} />
              </div>
            </div>

            {generateSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                {generateSuccess}
              </div>
            ) : null}
            {generateScheduleMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                {generateScheduleMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={generateScheduleMutation.isPending}
              >
                {generateScheduleMutation.isPending ? "Memproses..." : "Generate schedule"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => generateForm.reset(generateScheduleFormDefaults)}
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </section>

      <section className={surfaceClass}>
        <div className="grid gap-4 md:grid-cols-3">
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
            <label className={labelClass}>Filter Post</label>
            <select
              className={inputClass}
              value={postFilter}
              onChange={(event) => setPostFilter(event.target.value)}
            >
              <option value="">Semua post</option>
              {(postsQuery.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Filter Date</label>
            <input
              className={inputClass}
              type="date"
              value={dateFilter}
              onChange={(event) => setDateFilter(event.target.value)}
            />
          </div>
        </div>

        <div className="mt-4">
          <DataState
            isLoading={
              schedulesQuery.isLoading ||
              shiftTypesQuery.isLoading ||
              sitesQuery.isLoading ||
              postsQuery.isLoading ||
              employeesQuery.isLoading ||
              deploymentsQuery.isLoading
            }
            error={
              schedulesQuery.error ??
              shiftTypesQuery.error ??
              sitesQuery.error ??
              postsQuery.error ??
              employeesQuery.error ??
              deploymentsQuery.error
            }
            isEmpty={filteredSchedules.length === 0}
            emptyMessage="Belum ada schedule yang cocok dengan filter."
          >
            <div className={tableWrapperClass}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Date</th>
                    <th className={tableHeadClass}>Employee</th>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Post</th>
                    <th className={tableHeadClass}>Shift</th>
                    <th className={tableHeadClass}>Status</th>
                    <th className={tableHeadClass}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSchedules.map((item) => {
                    const isSelected = item.id === effectiveSelectedScheduleId;
                    return (
                      <tr
                        key={item.id}
                        className={`border-t border-[color:var(--border)] ${
                          isSelected ? "bg-[color:var(--muted-surface)]" : ""
                        }`}
                      >
                        <td className={tableCellClass}>{formatDate(item.scheduled_date)}</td>
                        <td className={tableCellClass}>
                          {employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`}
                        </td>
                        <td className={tableCellClass}>
                          {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                        </td>
                        <td className={tableCellClass}>
                          {postNameById.get(item.site_post_id ?? -1) ?? "-"}
                        </td>
                        <td className={tableCellClass}>
                          {shiftTypeNameById.get(item.shift_type_id) ?? `Shift ${item.shift_type_id}`}
                        </td>
                        <td className={tableCellClass}>{item.schedule_status}</td>
                        <td className={tableCellClass}>
                          <div className="flex flex-wrap gap-2">
                            <button
                              type="button"
                              className={secondaryButtonClass}
                              onClick={() => {
                                setSelectedScheduleId(item.id);
                                setUpdateSuccess(null);
                              }}
                            >
                              {isSelected ? "Dipilih" : "Detail"}
                            </button>
                            {item.schedule_status === "DRAFT" ? (
                              <button
                                type="button"
                                className={secondaryButtonClass}
                                disabled={publishScheduleMutation.isPending}
                                onClick={() => publishScheduleMutation.mutate(item.id)}
                              >
                                Publish
                              </button>
                            ) : null}
                          </div>
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
            <h2 className="text-lg font-semibold">Detail dan Update Schedule</h2>
            <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
              Panel ini memakai detail schedule dari API agar perubahan shift dan window kerja tidak
              lagi bergantung pada data list saja.
            </p>
          </div>
          {selectedSchedule ? (
            <p className="text-sm text-[color:var(--muted-foreground)]">
              Schedule ID: {selectedSchedule.id}
            </p>
          ) : null}
        </div>

        <div className="mt-4">
          <DataState
            isLoading={Boolean(effectiveSelectedScheduleId) && scheduleDetailQuery.isLoading}
            error={scheduleDetailQuery.error}
            isEmpty={!effectiveSelectedScheduleId}
            emptyMessage="Pilih schedule dari tabel untuk melihat detail dan update."
          >
            {selectedSchedule ? (
              <div className="grid gap-8 xl:grid-cols-[0.95fr_1.05fr]">
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Schedule
                    </p>
                    <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                      {employeeNameById.get(selectedSchedule.employee_id) ??
                        `Employee ${selectedSchedule.employee_id}`}
                    </p>
                    <p className="mt-1 text-[color:var(--muted-foreground)]">
                      Deployment #{selectedSchedule.employee_deployment_id}
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Site
                      </p>
                      <p className="mt-1">
                        {siteNameById.get(selectedSchedule.client_site_id) ??
                          `Site ${selectedSchedule.client_site_id}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Post
                      </p>
                      <p className="mt-1">
                        {postNameById.get(selectedSchedule.site_post_id ?? -1) ?? "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Shift
                      </p>
                      <p className="mt-1">
                        {shiftTypeNameById.get(selectedSchedule.shift_type_id) ??
                          `Shift ${selectedSchedule.shift_type_id}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Status
                      </p>
                      <p className="mt-1">{selectedSchedule.schedule_status}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Scheduled Date
                      </p>
                      <p className="mt-1">{formatDate(selectedSchedule.scheduled_date)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Replacement Schedule
                      </p>
                      <p className="mt-1">
                        {selectedSchedule.replacement_for_schedule_id
                          ? `#${selectedSchedule.replacement_for_schedule_id}`
                          : "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Start Window
                      </p>
                      <p className="mt-1">
                        {formatDateTime(selectedSchedule.scheduled_start_datetime)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        End Window
                      </p>
                      <p className="mt-1">
                        {formatDateTime(selectedSchedule.scheduled_end_datetime)}
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Deployment Context
                    </p>
                    {selectedDeployment ? (
                      <div className="mt-2 rounded-md border border-[color:var(--border)] px-3 py-3">
                        <p>
                          Client site:{" "}
                          {siteNameById.get(selectedDeployment.client_site_id) ??
                            `Site ${selectedDeployment.client_site_id}`}
                        </p>
                        <p className="mt-1">
                          Position:{" "}
                          {fallbackText(
                            selectedDeployment.position_id
                              ? `#${selectedDeployment.position_id}`
                              : null,
                          )}
                        </p>
                        <p className="mt-1">
                          Deployment status: {selectedDeployment.deployment_status}
                        </p>
                      </div>
                    ) : (
                      <p className="mt-1">Detail deployment belum tersedia di cache list.</p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Audit
                    </p>
                    <p className="mt-1">Dibuat: {formatDateTime(selectedSchedule.created_at)}</p>
                    <p className="mt-1">
                      Diperbarui: {formatDateTime(selectedSchedule.updated_at)}
                    </p>
                  </div>
                </div>

                <form
                  className="grid gap-4 md:grid-cols-2"
                  onSubmit={scheduleEditForm.handleSubmit((values) =>
                    updateScheduleMutation.mutate(values),
                  )}
                >
                  <div className="md:col-span-2">
                    <label className={labelClass}>Shift Type</label>
                    <select
                      className={inputClass}
                      {...scheduleEditForm.register("shift_type_id", { required: true })}
                    >
                      <option value="">Pilih shift type</option>
                      {(shiftTypesQuery.data ?? []).map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name} ({item.start_time} - {item.end_time})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Scheduled Date</label>
                    <input
                      className={inputClass}
                      type="date"
                      {...scheduleEditForm.register("scheduled_date", { required: true })}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Replacement Schedule</label>
                    <select className={inputClass} {...scheduleEditForm.register("replacement_for_schedule_id")}>
                      <option value="">Tanpa replacement</option>
                      {(schedulesQuery.data ?? [])
                        .filter((item) => item.id !== selectedSchedule.id)
                        .map((item) => (
                          <option key={item.id} value={item.id}>
                            #{item.id} -{" "}
                            {employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`} -{" "}
                            {formatDate(item.scheduled_date)}
                          </option>
                        ))}
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Scheduled Start</label>
                    <input
                      className={inputClass}
                      type="datetime-local"
                      {...scheduleEditForm.register("scheduled_start_datetime")}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Scheduled End</label>
                    <input
                      className={inputClass}
                      type="datetime-local"
                      {...scheduleEditForm.register("scheduled_end_datetime")}
                    />
                  </div>

                  {updateSuccess ? (
                    <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                      {updateSuccess}
                    </div>
                  ) : null}
                  {updateScheduleMutation.error ? (
                    <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                      {updateScheduleMutation.error.message}
                    </div>
                  ) : null}
                  <div className="flex gap-2 md:col-span-2">
                    <button
                      type="submit"
                      className={primaryButtonClass}
                      disabled={updateScheduleMutation.isPending}
                    >
                      {updateScheduleMutation.isPending ? "Menyimpan..." : "Update schedule"}
                    </button>
                    <button
                      type="button"
                      className={secondaryButtonClass}
                      onClick={() =>
                        selectedSchedule
                          ? scheduleEditForm.reset(toScheduleEditFormValues(selectedSchedule))
                          : scheduleEditForm.reset(scheduleEditFormDefaults)
                      }
                    >
                      Reset perubahan
                    </button>
                  </div>
                </form>
              </div>
            ) : null}
          </DataState>
        </div>
      </section>
    </div>
  );
}
