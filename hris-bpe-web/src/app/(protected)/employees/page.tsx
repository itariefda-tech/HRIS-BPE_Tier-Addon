"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDate, formatDateTime } from "@/lib/format";
import { optionalNumber, optionalText, requiredNumber } from "@/lib/forms";
import type { Employee } from "@/lib/types";
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

type EmployeeCreateFormValues = {
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

type EmployeeEditFormValues = {
  branch_id: string;
  department_id: string;
  position_id: string;
  employee_number: string;
  full_name: string;
  nik: string;
  email: string;
  phone: string;
  address: string;
  gender: string;
  marital_status: string;
  hire_date: string;
  employment_status: string;
  employee_status: string;
  resign_date: string;
  photo_path: string;
};

const createFormDefaults: EmployeeCreateFormValues = {
  company_id: "",
  branch_id: "",
  department_id: "",
  position_id: "",
  employee_number: "",
  full_name: "",
  email: "",
  phone: "",
  employment_status: "PERMANENT",
};

const editFormDefaults: EmployeeEditFormValues = {
  branch_id: "",
  department_id: "",
  position_id: "",
  employee_number: "",
  full_name: "",
  nik: "",
  email: "",
  phone: "",
  address: "",
  gender: "",
  marital_status: "",
  hire_date: "",
  employment_status: "",
  employee_status: "ACTIVE",
  resign_date: "",
  photo_path: "",
};

function toEditFormValues(employee: Employee): EmployeeEditFormValues {
  return {
    branch_id: String(employee.branch_id),
    department_id: employee.department_id ? String(employee.department_id) : "",
    position_id: employee.position_id ? String(employee.position_id) : "",
    employee_number: employee.employee_number,
    full_name: employee.full_name,
    nik: employee.nik ?? "",
    email: employee.email ?? "",
    phone: employee.phone ?? "",
    address: employee.address ?? "",
    gender: employee.gender ?? "",
    marital_status: employee.marital_status ?? "",
    hire_date: employee.hire_date ?? "",
    employment_status: employee.employment_status ?? "",
    employee_status: employee.employee_status,
    resign_date: employee.resign_date ?? "",
    photo_path: employee.photo_path ?? "",
  };
}

function filteredEmployeesFromData(
  employees: Employee[],
  branchFilter: string,
  statusFilter: string,
  positionFilter: string,
) {
  return employees.filter((employee) => {
    const branchMatches = branchFilter ? String(employee.branch_id) === branchFilter : true;
    const statusMatches = statusFilter ? employee.employee_status === statusFilter : true;
    const positionMatches = positionFilter
      ? String(employee.position_id ?? "") === positionFilter
      : true;
    return branchMatches && statusMatches && positionMatches;
  });
}

function filteredEmployeeSelection(
  employees: Employee[],
  selectedEmployeeId: number | null,
) {
  if (employees.length === 0) {
    return null;
  }

  if (selectedEmployeeId !== null) {
    const selectedEmployeeStillVisible = employees.some(
      (employee) => employee.id === selectedEmployeeId,
    );
    if (selectedEmployeeStillVisible) {
      return selectedEmployeeId;
    }
  }

  return employees[0].id;
}

export default function EmployeesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [createSuccessMessage, setCreateSuccessMessage] = useState<string | null>(null);
  const [updateSuccessMessage, setUpdateSuccessMessage] = useState<string | null>(null);
  const [branchFilter, setBranchFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [positionFilter, setPositionFilter] = useState("");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);

  const createForm = useForm<EmployeeCreateFormValues>({
    defaultValues: createFormDefaults,
  });
  const editForm = useForm<EmployeeEditFormValues>({
    defaultValues: editFormDefaults,
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
  const effectiveSelectedEmployeeId = filteredEmployeeSelection(
    filteredEmployeesFromData(employeesQuery.data ?? [], branchFilter, statusFilter, positionFilter),
    selectedEmployeeId,
  );
  const employeeDetailQuery = useQuery({
    queryKey: ["employee-detail", effectiveSelectedEmployeeId],
    queryFn: () => api.masterHr.getEmployeeDetail(accessToken!, effectiveSelectedEmployeeId!),
    enabled: Boolean(accessToken) && effectiveSelectedEmployeeId !== null,
  });

  const createEmployeeMutation = useMutation({
    mutationFn: (values: EmployeeCreateFormValues) =>
      api.masterHr.createEmployee(accessToken!, {
        company_id: requiredNumber(values.company_id),
        branch_id: requiredNumber(values.branch_id),
        department_id: optionalNumber(values.department_id),
        position_id: optionalNumber(values.position_id),
        employee_number: values.employee_number.trim(),
        full_name: values.full_name.trim(),
        email: optionalText(values.email),
        phone: optionalText(values.phone),
        employment_status: optionalText(values.employment_status),
      }),
    onSuccess: (employee) => {
      setCreateSuccessMessage("Employee berhasil dibuat.");
      setUpdateSuccessMessage(null);
      setBranchFilter("");
      setStatusFilter("");
      setPositionFilter("");
      createForm.reset(createFormDefaults);
      setSelectedEmployeeId(employee.id);
      queryClient.setQueryData(["employee-detail", employee.id], employee);
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });

  const updateEmployeeMutation = useMutation({
    mutationFn: (values: EmployeeEditFormValues) =>
      api.masterHr.updateEmployee(accessToken!, effectiveSelectedEmployeeId!, {
        branch_id: requiredNumber(values.branch_id),
        department_id: optionalNumber(values.department_id),
        position_id: optionalNumber(values.position_id),
        employee_number: values.employee_number.trim(),
        full_name: values.full_name.trim(),
        nik: optionalText(values.nik),
        email: optionalText(values.email),
        phone: optionalText(values.phone),
        address: optionalText(values.address),
        gender: optionalText(values.gender),
        marital_status: optionalText(values.marital_status),
        hire_date: optionalText(values.hire_date),
        employment_status: optionalText(values.employment_status),
        employee_status: values.employee_status.trim(),
        resign_date: optionalText(values.resign_date),
        photo_path: optionalText(values.photo_path),
      }),
    onSuccess: (employee) => {
      setUpdateSuccessMessage("Employee berhasil diperbarui.");
      queryClient.setQueryData(["employee-detail", employee.id], employee);
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      editForm.reset(toEditFormValues(employee));
    },
  });

  const companyNameById = useMemo(
    () => new Map((companiesQuery.data ?? []).map((item) => [item.id, item.name])),
    [companiesQuery.data],
  );
  const branchNameById = useMemo(
    () => new Map((branchesQuery.data ?? []).map((item) => [item.id, item.name])),
    [branchesQuery.data],
  );
  const departmentNameById = useMemo(
    () => new Map((departmentsQuery.data ?? []).map((item) => [item.id, item.name])),
    [departmentsQuery.data],
  );
  const positionNameById = useMemo(
    () => new Map((positionsQuery.data ?? []).map((item) => [item.id, item.name])),
    [positionsQuery.data],
  );

  const filteredEmployees = useMemo(
    () =>
      filteredEmployeesFromData(
        employeesQuery.data ?? [],
        branchFilter,
        statusFilter,
        positionFilter,
      ),
    [branchFilter, employeesQuery.data, positionFilter, statusFilter],
  );

  useEffect(() => {
    if (!employeeDetailQuery.data) {
      return;
    }

    editForm.reset(toEditFormValues(employeeDetailQuery.data));
  }, [editForm, employeeDetailQuery.data]);

  const selectedEmployee = employeeDetailQuery.data ?? null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employee"
        description="Kelola employee untuk fondasi operasional Basic, termasuk detail dan update."
      />

      <GapList
        items={[
          "Detail dan update employee sudah memakai endpoint /api/v1/master-hr/employees/{employee_id}.",
          "Perubahan company belum tersedia pada kontrak update employee saat ini.",
          "Filter branch, status, dan position masih berjalan client-side.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-[1.05fr_1.45fr]">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
            Create Employee
          </h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={createForm.handleSubmit((values) => createEmployeeMutation.mutate(values))}
          >
            <div>
              <label className={labelClass}>Company</label>
              <select
                className={inputClass}
                {...createForm.register("company_id", { required: true })}
              >
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
              <select
                className={inputClass}
                {...createForm.register("branch_id", { required: true })}
              >
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
              <select className={inputClass} {...createForm.register("department_id")}>
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
              <select className={inputClass} {...createForm.register("position_id")}>
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
              <input
                className={inputClass}
                {...createForm.register("employee_number", { required: true })}
              />
            </div>
            <div>
              <label className={labelClass}>Full Name</label>
              <input
                className={inputClass}
                {...createForm.register("full_name", { required: true })}
              />
            </div>
            <div>
              <label className={labelClass}>Email</label>
              <input className={inputClass} type="email" {...createForm.register("email")} />
            </div>
            <div>
              <label className={labelClass}>Phone</label>
              <input className={inputClass} {...createForm.register("phone")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Employment Status</label>
              <input className={inputClass} {...createForm.register("employment_status")} />
            </div>

            {createSuccessMessage ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {createSuccessMessage}
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
                onClick={() => createForm.reset(createFormDefaults)}
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
                      <th className={tableHeadClass}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.map((employee) => {
                      const isSelected = employee.id === effectiveSelectedEmployeeId;
                      return (
                        <tr
                          key={employee.id}
                          className={`border-t border-[color:var(--border)] ${
                            isSelected ? "bg-[color:var(--muted-surface)]" : ""
                          }`}
                        >
                          <td className={tableCellClass}>
                            <div className="font-semibold">{employee.full_name}</div>
                            <div className="text-xs text-[color:var(--muted-foreground)]">
                              {employee.employee_number} - {fallbackText(employee.email)}
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
                          <td className={tableCellClass}>
                            <button
                              type="button"
                              className={secondaryButtonClass}
                              onClick={() => {
                                setSelectedEmployeeId(employee.id);
                                setUpdateSuccessMessage(null);
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
        </div>
      </section>

      <section className={surfaceClass}>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
              Detail dan Update Employee
            </h2>
            <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
              Panel ini memakai detail employee dari API agar edit tidak lagi bergantung pada data
              list saja.
            </p>
          </div>
          {selectedEmployee ? (
            <p className="text-sm text-[color:var(--muted-foreground)]">
              Employee ID: {selectedEmployee.id}
            </p>
          ) : null}
        </div>

        <div className="mt-4">
          <DataState
            isLoading={Boolean(effectiveSelectedEmployeeId) && employeeDetailQuery.isLoading}
            error={employeeDetailQuery.error}
            isEmpty={!effectiveSelectedEmployeeId}
            emptyMessage="Pilih employee dari tabel untuk melihat detail dan edit."
          >
            {selectedEmployee ? (
              <div className="grid gap-8 xl:grid-cols-[0.9fr_1.1fr]">
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Employee
                    </p>
                    <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                      {selectedEmployee.full_name}
                    </p>
                    <p className="mt-1 text-[color:var(--muted-foreground)]">
                      {selectedEmployee.employee_number} - {fallbackText(selectedEmployee.email)}
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Company
                      </p>
                      <p className="mt-1">
                        {companyNameById.get(selectedEmployee.company_id) ?? "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Branch
                      </p>
                      <p className="mt-1">
                        {branchNameById.get(selectedEmployee.branch_id) ?? "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Department
                      </p>
                      <p className="mt-1">
                        {departmentNameById.get(selectedEmployee.department_id ?? -1) ?? "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Position
                      </p>
                      <p className="mt-1">
                        {positionNameById.get(selectedEmployee.position_id ?? -1) ?? "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Employee Status
                      </p>
                      <p className="mt-1">{selectedEmployee.employee_status}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Employment Status
                      </p>
                      <p className="mt-1">{fallbackText(selectedEmployee.employment_status)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Hire Date
                      </p>
                      <p className="mt-1">{formatDate(selectedEmployee.hire_date)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Resign Date
                      </p>
                      <p className="mt-1">{formatDate(selectedEmployee.resign_date)}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Contact
                    </p>
                    <p className="mt-1">{fallbackText(selectedEmployee.phone)}</p>
                    <p className="mt-1">{fallbackText(selectedEmployee.address)}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Audit
                    </p>
                    <p className="mt-1">Dibuat: {formatDateTime(selectedEmployee.created_at)}</p>
                    <p className="mt-1">
                      Diperbarui: {formatDateTime(selectedEmployee.updated_at)}
                    </p>
                  </div>
                </div>

                <form
                  className="grid gap-4 md:grid-cols-2"
                  onSubmit={editForm.handleSubmit((values) => updateEmployeeMutation.mutate(values))}
                >
                  <div>
                    <label className={labelClass}>Branch</label>
                    <select
                      className={inputClass}
                      {...editForm.register("branch_id", { required: true })}
                    >
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
                    <select className={inputClass} {...editForm.register("department_id")}>
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
                    <select className={inputClass} {...editForm.register("position_id")}>
                      <option value="">Tanpa position</option>
                      {(positionsQuery.data ?? []).map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Employee Status</label>
                    <select
                      className={inputClass}
                      {...editForm.register("employee_status", { required: true })}
                    >
                      <option value="ACTIVE">ACTIVE</option>
                      <option value="NON_ACTIVE">NON_ACTIVE</option>
                      <option value="RESIGNED">RESIGNED</option>
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Employee Number</label>
                    <input
                      className={inputClass}
                      {...editForm.register("employee_number", { required: true })}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Full Name</label>
                    <input
                      className={inputClass}
                      {...editForm.register("full_name", { required: true })}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>NIK</label>
                    <input className={inputClass} {...editForm.register("nik")} />
                  </div>
                  <div>
                    <label className={labelClass}>Email</label>
                    <input className={inputClass} type="email" {...editForm.register("email")} />
                  </div>
                  <div>
                    <label className={labelClass}>Phone</label>
                    <input className={inputClass} {...editForm.register("phone")} />
                  </div>
                  <div>
                    <label className={labelClass}>Gender</label>
                    <input className={inputClass} {...editForm.register("gender")} />
                  </div>
                  <div>
                    <label className={labelClass}>Marital Status</label>
                    <input className={inputClass} {...editForm.register("marital_status")} />
                  </div>
                  <div>
                    <label className={labelClass}>Hire Date</label>
                    <input className={inputClass} type="date" {...editForm.register("hire_date")} />
                  </div>
                  <div>
                    <label className={labelClass}>Employment Status</label>
                    <input className={inputClass} {...editForm.register("employment_status")} />
                  </div>
                  <div>
                    <label className={labelClass}>Resign Date</label>
                    <input className={inputClass} type="date" {...editForm.register("resign_date")} />
                  </div>
                  <div className="md:col-span-2">
                    <label className={labelClass}>Address</label>
                    <textarea
                      className={`${inputClass} min-h-24`}
                      {...editForm.register("address")}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className={labelClass}>Photo Path</label>
                    <input className={inputClass} {...editForm.register("photo_path")} />
                  </div>

                  {updateSuccessMessage ? (
                    <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                      {updateSuccessMessage}
                    </div>
                  ) : null}

                  {updateEmployeeMutation.error ? (
                    <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                      {updateEmployeeMutation.error.message}
                    </div>
                  ) : null}

                  <div className="flex flex-wrap gap-2 md:col-span-2">
                    <button
                      type="submit"
                      className={primaryButtonClass}
                      disabled={updateEmployeeMutation.isPending}
                    >
                      {updateEmployeeMutation.isPending ? "Menyimpan..." : "Update employee"}
                    </button>
                    <button
                      type="button"
                      className={secondaryButtonClass}
                      onClick={() =>
                        selectedEmployee
                          ? editForm.reset(toEditFormValues(selectedEmployee))
                          : editForm.reset(editFormDefaults)
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
