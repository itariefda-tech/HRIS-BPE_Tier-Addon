"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDate } from "@/lib/format";
import { optionalNumber, optionalText, requiredNumber } from "@/lib/forms";
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

type EmployeeFormValues = {
  company_id: string;
  branch_id: string;
  department_id: string;
  position_id: string;
  employee_number: string;
  full_name: string;
  email: string;
  phone: string;
  employment_status: string;
};

export default function EmployeesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [branchFilter, setBranchFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [positionFilter, setPositionFilter] = useState("");
  const form = useForm<EmployeeFormValues>({
    defaultValues: {
      company_id: "",
      branch_id: "",
      department_id: "",
      position_id: "",
      employee_number: "",
      full_name: "",
      email: "",
      phone: "",
      employment_status: "PERMANENT",
    },
  });

  const companiesQuery = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.organization.listCompanies(accessToken!),
    enabled: Boolean(accessToken),
  });
  const branchesQuery = useQuery({
    queryKey: ["branches"],
    queryFn: () => api.organization.listBranches(accessToken!),
    enabled: Boolean(accessToken),
  });
  const departmentsQuery = useQuery({
    queryKey: ["departments"],
    queryFn: () => api.organization.listDepartments(accessToken!),
    enabled: Boolean(accessToken),
  });
  const positionsQuery = useQuery({
    queryKey: ["positions"],
    queryFn: () => api.organization.listPositions(accessToken!),
    enabled: Boolean(accessToken),
  });
  const employeesQuery = useQuery({
    queryKey: ["employees"],
    queryFn: () => api.masterHr.listEmployees(accessToken!),
    enabled: Boolean(accessToken),
  });

  const createEmployeeMutation = useMutation({
    mutationFn: (values: EmployeeFormValues) =>
      api.masterHr.createEmployee(accessToken!, {
        company_id: requiredNumber(values.company_id),
        branch_id: requiredNumber(values.branch_id),
        department_id: optionalNumber(values.department_id),
        position_id: optionalNumber(values.position_id),
        employee_number: values.employee_number,
        full_name: values.full_name,
        email: optionalText(values.email),
        phone: optionalText(values.phone),
        employment_status: optionalText(values.employment_status),
      }),
    onSuccess: () => {
      setSuccessMessage("Employee berhasil dibuat.");
      form.reset({
        company_id: "",
        branch_id: "",
        department_id: "",
        position_id: "",
        employee_number: "",
        full_name: "",
        email: "",
        phone: "",
        employment_status: "PERMANENT",
      });
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });

  const branchNameById = useMemo(
    () => new Map((branchesQuery.data ?? []).map((item) => [item.id, item.name])),
    [branchesQuery.data],
  );
  const positionNameById = useMemo(
    () => new Map((positionsQuery.data ?? []).map((item) => [item.id, item.name])),
    [positionsQuery.data],
  );

  const filteredEmployees = useMemo(() => {
    return (employeesQuery.data ?? []).filter((employee) => {
      const branchMatches = branchFilter
        ? String(employee.branch_id) === branchFilter
        : true;
      const statusMatches = statusFilter
        ? employee.employee_status === statusFilter
        : true;
      const positionMatches = positionFilter
        ? String(employee.position_id ?? "") === positionFilter
        : true;
      return branchMatches && statusMatches && positionMatches;
    });
  }, [branchFilter, employeesQuery.data, positionFilter, statusFilter]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employee"
        description="List dan create employee untuk fondasi operasional Basic."
      />

      <GapList
        items={[
          "Belum ada endpoint detail employee khusus. UI saat ini fokus pada list dan create.",
          "Belum ada endpoint update employee, jadi edit masih ditahan.",
          "Filter branch, status, dan position masih berjalan client-side.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-[1.1fr_1.4fr]">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
            Create Employee
          </h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={form.handleSubmit((values) => createEmployeeMutation.mutate(values))}
          >
            <div>
              <label className={labelClass}>Company</label>
              <select className={inputClass} {...form.register("company_id", { required: true })}>
                <option value="">Pilih company</option>
                {(companiesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Branch</label>
              <select className={inputClass} {...form.register("branch_id", { required: true })}>
                <option value="">Pilih branch</option>
                {(branchesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Department</label>
              <select className={inputClass} {...form.register("department_id")}>
                <option value="">Tanpa department</option>
                {(departmentsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Position</label>
              <select className={inputClass} {...form.register("position_id")}>
                <option value="">Tanpa position</option>
                {(positionsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Employee Number</label>
              <input className={inputClass} {...form.register("employee_number", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Full Name</label>
              <input className={inputClass} {...form.register("full_name", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Email</label>
              <input className={inputClass} type="email" {...form.register("email")} />
            </div>
            <div>
              <label className={labelClass}>Phone</label>
              <input className={inputClass} {...form.register("phone")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Employment Status</label>
              <input className={inputClass} {...form.register("employment_status")} />
            </div>

            {successMessage ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {successMessage}
              </div>
            ) : null}

            {createEmployeeMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createEmployeeMutation.error.message}
              </div>
            ) : null}

            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createEmployeeMutation.isPending}
              >
                {createEmployeeMutation.isPending ? "Menyimpan..." : "Simpan employee"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => form.reset()}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className={surfaceClass}>
          <div className="flex flex-col gap-4 md:flex-row md:items-end">
            <div className="flex-1">
              <label className={labelClass}>Filter Branch</label>
              <select
                className={inputClass}
                value={branchFilter}
                onChange={(event) => setBranchFilter(event.target.value)}
              >
                <option value="">Semua branch</option>
                {(branchesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className={labelClass}>Filter Status</label>
              <select
                className={inputClass}
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                <option value="">Semua status</option>
                <option value="ACTIVE">ACTIVE</option>
                <option value="NON_ACTIVE">NON_ACTIVE</option>
                <option value="RESIGNED">RESIGNED</option>
              </select>
            </div>
            <div className="flex-1">
              <label className={labelClass}>Filter Position</label>
              <select
                className={inputClass}
                value={positionFilter}
                onChange={(event) => setPositionFilter(event.target.value)}
              >
                <option value="">Semua position</option>
                {(positionsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <DataState
              isLoading={
                employeesQuery.isLoading ||
                branchesQuery.isLoading ||
                positionsQuery.isLoading
              }
              error={
                employeesQuery.error ??
                branchesQuery.error ??
                positionsQuery.error
              }
              isEmpty={filteredEmployees.length === 0}
              emptyMessage="Belum ada employee yang cocok dengan filter."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Employee</th>
                      <th className={tableHeadClass}>Branch</th>
                      <th className={tableHeadClass}>Position</th>
                      <th className={tableHeadClass}>Status</th>
                      <th className={tableHeadClass}>Employment</th>
                      <th className={tableHeadClass}>Hire Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.map((employee) => (
                      <tr key={employee.id} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>
                          <div className="font-semibold">{employee.full_name}</div>
                          <div className="text-xs text-[color:var(--muted-foreground)]">
                            {employee.employee_number} · {fallbackText(employee.email)}
                          </div>
                        </td>
                        <td className={tableCellClass}>
                          {branchNameById.get(employee.branch_id) ?? "-"}
                        </td>
                        <td className={tableCellClass}>
                          {positionNameById.get(employee.position_id ?? -1) ?? "-"}
                        </td>
                        <td className={tableCellClass}>{employee.employee_status}</td>
                        <td className={tableCellClass}>
                          {fallbackText(employee.employment_status)}
                        </td>
                        <td className={tableCellClass}>{formatDate(employee.hire_date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </DataState>
          </div>
        </div>
      </section>
    </div>
  );
}
