"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { todayInputValue } from "@/lib/date";
import { formatDate } from "@/lib/format";
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

type DeploymentFormValues = {
  employee_id: string;
  client_id: string;
  client_contract_id: string;
  client_site_id: string;
  site_post_id: string;
  position_id: string;
  start_date: string;
  notes: string;
};

type EndDeploymentFormValues = {
  deployment_id: string;
  end_date: string;
  notes: string;
};

export default function DeploymentsPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [createSuccess, setCreateSuccess] = useState<string | null>(null);
  const [endSuccess, setEndSuccess] = useState<string | null>(null);
  const [clientFilter, setClientFilter] = useState("");
  const [siteFilter, setSiteFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const deploymentForm = useForm<DeploymentFormValues>({
    defaultValues: {
      employee_id: "",
      client_id: "",
      client_contract_id: "",
      client_site_id: "",
      site_post_id: "",
      position_id: "",
      start_date: todayInputValue(),
      notes: "",
    },
  });
  const endForm = useForm<EndDeploymentFormValues>({
    defaultValues: {
      deployment_id: "",
      end_date: todayInputValue(),
      notes: "",
    },
  });

  const employeesQuery = useQuery({
    queryKey: ["employees"],
    queryFn: () => api.masterHr.listEmployees(accessToken!),
    enabled: Boolean(accessToken),
  });
  const clientsQuery = useQuery({
    queryKey: ["clients"],
    queryFn: () => api.clientContract.listClients(accessToken!),
    enabled: Boolean(accessToken),
  });
  const contractsQuery = useQuery({
    queryKey: ["contracts"],
    queryFn: () => api.clientContract.listContracts(accessToken!),
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
  const positionsQuery = useQuery({
    queryKey: ["positions"],
    queryFn: () => api.organization.listPositions(accessToken!),
    enabled: Boolean(accessToken),
  });
  const deploymentsQuery = useQuery({
    queryKey: ["deployments"],
    queryFn: () => api.workforceOperations.listDeployments(accessToken!),
    enabled: Boolean(accessToken),
  });

  const employeeNameById = useMemo(
    () => new Map((employeesQuery.data ?? []).map((item) => [item.id, item.full_name])),
    [employeesQuery.data],
  );
  const clientNameById = useMemo(
    () => new Map((clientsQuery.data ?? []).map((item) => [item.id, item.name])),
    [clientsQuery.data],
  );
  const siteNameById = useMemo(
    () => new Map((sitesQuery.data ?? []).map((item) => [item.id, item.name])),
    [sitesQuery.data],
  );
  const postNameById = useMemo(
    () => new Map((postsQuery.data ?? []).map((item) => [item.id, item.name])),
    [postsQuery.data],
  );
  const positionNameById = useMemo(
    () => new Map((positionsQuery.data ?? []).map((item) => [item.id, item.name])),
    [positionsQuery.data],
  );

  const filteredDeployments = useMemo(() => {
    return (deploymentsQuery.data ?? []).filter((item) => {
      const clientMatches = clientFilter ? String(item.client_id) === clientFilter : true;
      const siteMatches = siteFilter ? String(item.client_site_id) === siteFilter : true;
      const statusMatches = statusFilter ? item.deployment_status === statusFilter : true;
      return clientMatches && siteMatches && statusMatches;
    });
  }, [clientFilter, deploymentsQuery.data, siteFilter, statusFilter]);

  const createDeploymentMutation = useMutation({
    mutationFn: (values: DeploymentFormValues) =>
      api.workforceOperations.createDeployment(accessToken!, {
        employee_id: requiredNumber(values.employee_id),
        client_id: requiredNumber(values.client_id),
        client_contract_id: requiredNumber(values.client_contract_id),
        client_site_id: requiredNumber(values.client_site_id),
        site_post_id: optionalNumber(values.site_post_id),
        position_id: optionalNumber(values.position_id),
        start_date: values.start_date,
        notes: optionalText(values.notes),
      }),
    onSuccess: () => {
      setCreateSuccess("Deployment berhasil dibuat.");
      deploymentForm.reset({
        employee_id: "",
        client_id: "",
        client_contract_id: "",
        client_site_id: "",
        site_post_id: "",
        position_id: "",
        start_date: todayInputValue(),
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["deployments"] });
    },
  });

  const endDeploymentMutation = useMutation({
    mutationFn: (values: EndDeploymentFormValues) =>
      api.workforceOperations.endDeployment(
        accessToken!,
        requiredNumber(values.deployment_id),
        {
          end_date: values.end_date,
          notes: optionalText(values.notes),
        },
      ),
    onSuccess: () => {
      setEndSuccess("Deployment berhasil diakhiri.");
      endForm.reset({
        deployment_id: "",
        end_date: todayInputValue(),
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["deployments"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Deployment"
        description="Assign guard ke site, lihat deployment aktif, dan akhiri deployment."
      />

      <GapList
        items={[
          "Belum ada endpoint detail deployment khusus dan update deployment.",
          "Filter site, client, dan status masih berjalan client-side.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Assign Deployment</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={deploymentForm.handleSubmit((values) =>
              createDeploymentMutation.mutate(values),
            )}
          >
            <div>
              <label className={labelClass}>Employee</label>
              <select className={inputClass} {...deploymentForm.register("employee_id", { required: true })}>
                <option value="">Pilih employee</option>
                {(employeesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.full_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Client</label>
              <select className={inputClass} {...deploymentForm.register("client_id", { required: true })}>
                <option value="">Pilih client</option>
                {(clientsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Contract</label>
              <select className={inputClass} {...deploymentForm.register("client_contract_id", { required: true })}>
                <option value="">Pilih contract</option>
                {(contractsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.contract_number}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Site</label>
              <select className={inputClass} {...deploymentForm.register("client_site_id", { required: true })}>
                <option value="">Pilih site</option>
                {(sitesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Site Post</label>
              <select className={inputClass} {...deploymentForm.register("site_post_id")}>
                <option value="">Tanpa post</option>
                {(postsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Position</label>
              <select className={inputClass} {...deploymentForm.register("position_id")}>
                <option value="">Tanpa position</option>
                {(positionsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Start Date</label>
              <input className={inputClass} type="date" {...deploymentForm.register("start_date", { required: true })} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Notes</label>
              <input className={inputClass} {...deploymentForm.register("notes")} />
            </div>
            {createSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {createSuccess}
              </div>
            ) : null}
            {createDeploymentMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createDeploymentMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createDeploymentMutation.isPending}
              >
                {createDeploymentMutation.isPending ? "Menyimpan..." : "Assign deployment"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => deploymentForm.reset()}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">End Deployment</h2>
          <form
            className="mt-4 grid gap-4"
            onSubmit={endForm.handleSubmit((values) => endDeploymentMutation.mutate(values))}
          >
            <div>
              <label className={labelClass}>Deployment Aktif</label>
              <select className={inputClass} {...endForm.register("deployment_id", { required: true })}>
                <option value="">Pilih deployment</option>
                {(deploymentsQuery.data ?? [])
                  .filter((item) => item.deployment_status === "ACTIVE")
                  .map((item) => (
                    <option key={item.id} value={item.id}>
                      {(employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`) +
                        " · " +
                        (siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`)}
                    </option>
                  ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>End Date</label>
              <input className={inputClass} type="date" {...endForm.register("end_date", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Notes</label>
              <input className={inputClass} {...endForm.register("notes")} />
            </div>
            {endSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                {endSuccess}
              </div>
            ) : null}
            {endDeploymentMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                {endDeploymentMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={endDeploymentMutation.isPending}
              >
                {endDeploymentMutation.isPending ? "Memproses..." : "Akhiri deployment"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => endForm.reset()}
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
            <label className={labelClass}>Filter Client</label>
            <select
              className={inputClass}
              value={clientFilter}
              onChange={(event) => setClientFilter(event.target.value)}
            >
              <option value="">Semua client</option>
              {(clientsQuery.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
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
              <option value="ACTIVE">ACTIVE</option>
              <option value="ENDED">ENDED</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <DataState
            isLoading={
              deploymentsQuery.isLoading ||
              employeesQuery.isLoading ||
              clientsQuery.isLoading ||
              sitesQuery.isLoading
            }
            error={
              deploymentsQuery.error ??
              employeesQuery.error ??
              clientsQuery.error ??
              sitesQuery.error
            }
            isEmpty={filteredDeployments.length === 0}
            emptyMessage="Belum ada deployment yang cocok dengan filter."
          >
            <div className={tableWrapperClass}>
              <table className={tableClass}>
                <thead>
                  <tr>
                    <th className={tableHeadClass}>Employee</th>
                    <th className={tableHeadClass}>Client</th>
                    <th className={tableHeadClass}>Site</th>
                    <th className={tableHeadClass}>Post</th>
                    <th className={tableHeadClass}>Position</th>
                    <th className={tableHeadClass}>Status</th>
                    <th className={tableHeadClass}>Period</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDeployments.map((item) => (
                    <tr key={item.id} className="border-t border-[color:var(--border)]">
                      <td className={tableCellClass}>
                        {employeeNameById.get(item.employee_id) ?? `Employee ${item.employee_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {clientNameById.get(item.client_id) ?? `Client ${item.client_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                      </td>
                      <td className={tableCellClass}>
                        {postNameById.get(item.site_post_id ?? -1) ?? "-"}
                      </td>
                      <td className={tableCellClass}>
                        {positionNameById.get(item.position_id ?? -1) ?? "-"}
                      </td>
                      <td className={tableCellClass}>{item.deployment_status}</td>
                      <td className={tableCellClass}>
                        {formatDate(item.start_date)} - {formatDate(item.end_date)}
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
