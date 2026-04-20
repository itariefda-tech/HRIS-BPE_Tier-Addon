"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { addDaysInputValue, todayInputValue } from "@/lib/date";
import { fallbackText, formatDate, formatDateTime } from "@/lib/format";
import { requiredNumber, selectedValuesToNumbers } from "@/lib/forms";
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

export default function SchedulesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [shiftTypeSuccess, setShiftTypeSuccess] = useState<string | null>(null);
  const [generateSuccess, setGenerateSuccess] = useState<string | null>(null);
  const [siteFilter, setSiteFilter] = useState("");
  const [postFilter, setPostFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const shiftTypeForm = useForm<ShiftTypeFormValues>({
    defaultValues: {
      company_id: "",
      code: "",
      name: "",
      start_time: "08:00",
      end_time: "17:00",
      tolerance_late_minutes: "15",
    },
  });
  const generateForm = useForm<GenerateScheduleFormValues>({
    defaultValues: {
      employee_deployment_ids: [],
      shift_type_id: "",
      date_from: todayInputValue(),
      date_to: addDaysInputValue(6),
    },
  });

  const companiesQuery = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.organization.listCompanies(accessToken!),
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

  const filteredSchedules = useMemo(() => {
    return (schedulesQuery.data ?? []).filter((item) => {
      const siteMatches = siteFilter ? String(item.client_site_id) === siteFilter : true;
      const postMatches = postFilter ? String(item.site_post_id ?? "") === postFilter : true;
      const dateMatches = dateFilter ? item.scheduled_date === dateFilter : true;
      return siteMatches && postMatches && dateMatches;
    });
  }, [dateFilter, postFilter, schedulesQuery.data, siteFilter]);

  const createShiftTypeMutation = useMutation({
    mutationFn: (values: ShiftTypeFormValues) =>
      api.workforceOperations.createShiftType(accessToken!, {
        company_id: requiredNumber(values.company_id),
        code: values.code,
        name: values.name,
        start_time: values.start_time,
        end_time: values.end_time,
        tolerance_late_minutes: Number(values.tolerance_late_minutes),
      }),
    onSuccess: () => {
      setShiftTypeSuccess("Shift type berhasil dibuat.");
      shiftTypeForm.reset({
        company_id: "",
        code: "",
        name: "",
        start_time: "08:00",
        end_time: "17:00",
        tolerance_late_minutes: "15",
      });
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
      generateForm.reset({
        employee_deployment_ids: [],
        shift_type_id: "",
        date_from: todayInputValue(),
        date_to: addDaysInputValue(6),
      });
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });

  const publishScheduleMutation = useMutation({
    mutationFn: (scheduleId: number) =>
      api.workforceOperations.publishWorkSchedule(accessToken!, scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Schedule"
        description="Siapkan shift type, generate work schedule, lalu publish untuk flow operasional."
      />

      <GapList
        items={[
          "Belum ada calendar view pada iterasi ini.",
          "Belum ada endpoint detail schedule khusus dan filter server-side by site/post/date.",
          "Roadmap mobile masih butuh endpoint `my schedules` yang belum tersedia di backend.",
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
                onClick={() => shiftTypeForm.reset()}
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
                      #{item.id} · {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
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
                onClick={() => generateForm.reset()}
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
              postsQuery.isLoading
            }
            error={
              schedulesQuery.error ??
              shiftTypesQuery.error ??
              sitesQuery.error ??
              postsQuery.error
            }
            isEmpty={filteredSchedules.length === 0}
            emptyMessage="Belum ada schedule yang cocok dengan filter."
          >
            <div className={tableWrapperClass}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Date</th>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Post</th>
                    <th className={tableHeadClass}>Shift</th>
                    <th className={tableHeadClass}>Window</th>
                    <th className={tableHeadClass}>Status</th>
                    <th className={tableHeadClass}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSchedules.map((item) => (
                    <tr key={item.id} className="border-t border-[color:var(--border)]">
                      <td className={tableCellClass}>{formatDate(item.scheduled_date)}</td>
                      <td className={tableCellClass}>
                        {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {postNameById.get(item.site_post_id ?? -1) ?? "-"}
                      </td>
                      <td className={tableCellClass}>
                        {shiftTypeNameById.get(item.shift_type_id) ?? `Shift ${item.shift_type_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {formatDateTime(item.scheduled_start_datetime)}
                        <br />
                        {formatDateTime(item.scheduled_end_datetime)}
                      </td>
                      <td className={tableCellClass}>{item.schedule_status}</td>
                      <td className={tableCellClass}>
                        {item.schedule_status === "DRAFT" ? (
                          <button
                            type="button"
                            className={secondaryButtonClass}
                            disabled={publishScheduleMutation.isPending}
                            onClick={() => publishScheduleMutation.mutate(item.id)}
                          >
                            Publish
                          </button>
                        ) : (
                          fallbackText(item.schedule_status)
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DataState>
        </div>
      </section>
    </div>
  );
}
