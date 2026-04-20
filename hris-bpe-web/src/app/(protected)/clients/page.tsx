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
import { optionalText, requiredNumber } from "@/lib/forms";
import type { Client } from "@/lib/types";
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

type ClientFormValues = {
  company_id: string;
  code: string;
  name: string;
  contact_person_name: string;
  contact_person_phone: string;
  contact_person_email: string;
  industry_type: string;
  billing_address: string;
  tax_number: string;
  status: string;
};

type ClientEditFormValues = {
  code: string;
  name: string;
  contact_person_name: string;
  contact_person_phone: string;
  contact_person_email: string;
  industry_type: string;
  billing_address: string;
  tax_number: string;
  status: string;
};

type ContractFormValues = {
  client_id: string;
  contract_number: string;
  contract_title: string;
  start_date: string;
  end_date: string;
  contract_type: string;
  notes: string;
};

const clientFormDefaults: ClientFormValues = {
  company_id: "",
  code: "",
  name: "",
  contact_person_name: "",
  contact_person_phone: "",
  contact_person_email: "",
  industry_type: "",
  billing_address: "",
  tax_number: "",
  status: "ACTIVE",
};

const clientEditFormDefaults: ClientEditFormValues = {
  code: "",
  name: "",
  contact_person_name: "",
  contact_person_phone: "",
  contact_person_email: "",
  industry_type: "",
  billing_address: "",
  tax_number: "",
  status: "ACTIVE",
};

const contractFormDefaults: ContractFormValues = {
  client_id: "",
  contract_number: "",
  contract_title: "",
  start_date: todayInputValue(),
  end_date: addDaysInputValue(365),
  contract_type: "SERVICE",
  notes: "",
};

function toClientEditFormValues(client: Client): ClientEditFormValues {
  return {
    code: client.code,
    name: client.name,
    contact_person_name: client.contact_person_name ?? "",
    contact_person_phone: client.contact_person_phone ?? "",
    contact_person_email: client.contact_person_email ?? "",
    industry_type: client.industry_type ?? "",
    billing_address: client.billing_address ?? "",
    tax_number: client.tax_number ?? "",
    status: client.status,
  };
}

export default function ClientsPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [clientSuccess, setClientSuccess] = useState<string | null>(null);
  const [contractSuccess, setContractSuccess] = useState<string | null>(null);
  const [clientUpdateSuccess, setClientUpdateSuccess] = useState<string | null>(null);
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);

  const clientForm = useForm<ClientFormValues>({
    defaultValues: clientFormDefaults,
  });
  const clientEditForm = useForm<ClientEditFormValues>({
    defaultValues: clientEditFormDefaults,
  });
  const contractForm = useForm<ContractFormValues>({
    defaultValues: contractFormDefaults,
  });

  const companiesQuery = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.organization.listCompanies(accessToken!),
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

  const effectiveSelectedClientId = useMemo(() => {
    const clients = clientsQuery.data ?? [];
    if (clients.length === 0) {
      return null;
    }

    if (selectedClientId !== null) {
      const selectedStillVisible = clients.some((client) => client.id === selectedClientId);
      if (selectedStillVisible) {
        return selectedClientId;
      }
    }

    return clients[0].id;
  }, [clientsQuery.data, selectedClientId]);

  const clientDetailQuery = useQuery({
    queryKey: ["client-detail", effectiveSelectedClientId],
    queryFn: () => api.clientContract.getClientDetail(accessToken!, effectiveSelectedClientId!),
    enabled: Boolean(accessToken) && effectiveSelectedClientId !== null,
  });

  const createClientMutation = useMutation({
    mutationFn: (values: ClientFormValues) =>
      api.clientContract.createClient(accessToken!, {
        company_id: requiredNumber(values.company_id),
        code: values.code.trim(),
        name: values.name.trim(),
        contact_person_name: optionalText(values.contact_person_name),
        contact_person_phone: optionalText(values.contact_person_phone),
        contact_person_email: optionalText(values.contact_person_email),
        industry_type: optionalText(values.industry_type),
        billing_address: optionalText(values.billing_address),
        tax_number: optionalText(values.tax_number),
        status: values.status.trim(),
      }),
    onSuccess: (client) => {
      setClientSuccess("Client berhasil dibuat.");
      setClientUpdateSuccess(null);
      clientForm.reset(clientFormDefaults);
      contractForm.setValue("client_id", String(client.id));
      setSelectedClientId(client.id);
      queryClient.setQueryData(["client-detail", client.id], client);
      queryClient.invalidateQueries({ queryKey: ["clients"] });
    },
  });

  const updateClientMutation = useMutation({
    mutationFn: (values: ClientEditFormValues) =>
      api.clientContract.updateClient(accessToken!, effectiveSelectedClientId!, {
        code: values.code.trim(),
        name: values.name.trim(),
        contact_person_name: optionalText(values.contact_person_name),
        contact_person_phone: optionalText(values.contact_person_phone),
        contact_person_email: optionalText(values.contact_person_email),
        industry_type: optionalText(values.industry_type),
        billing_address: optionalText(values.billing_address),
        tax_number: optionalText(values.tax_number),
        status: values.status.trim(),
      }),
    onSuccess: (client) => {
      setClientUpdateSuccess("Client berhasil diperbarui.");
      queryClient.setQueryData(["client-detail", client.id], client);
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      clientEditForm.reset(toClientEditFormValues(client));
    },
  });

  const createContractMutation = useMutation({
    mutationFn: (values: ContractFormValues) =>
      api.clientContract.createContract(accessToken!, {
        client_id: requiredNumber(values.client_id),
        contract_number: values.contract_number.trim(),
        contract_title: values.contract_title.trim(),
        start_date: values.start_date,
        end_date: values.end_date,
        contract_type: optionalText(values.contract_type),
        notes: optionalText(values.notes),
      }),
    onSuccess: () => {
      setContractSuccess("Contract berhasil dibuat.");
      contractForm.reset({
        ...contractFormDefaults,
        client_id: effectiveSelectedClientId ? String(effectiveSelectedClientId) : "",
      });
      queryClient.invalidateQueries({ queryKey: ["contracts"] });
    },
  });

  useEffect(() => {
    if (!clientDetailQuery.data) {
      return;
    }

    clientEditForm.reset(toClientEditFormValues(clientDetailQuery.data));
    contractForm.setValue("client_id", String(clientDetailQuery.data.id));
  }, [clientDetailQuery.data, clientEditForm, contractForm]);

  const companyNameById = useMemo(
    () => new Map((companiesQuery.data ?? []).map((item) => [item.id, item.name])),
    [companiesQuery.data],
  );
  const selectedClient = clientDetailQuery.data ?? null;
  const selectedClientContracts = useMemo(
    () =>
      (contractsQuery.data ?? []).filter((contract) => contract.client_id === effectiveSelectedClientId),
    [contractsQuery.data, effectiveSelectedClientId],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Client & Contract"
        description="Kelola client dan contract Basic sebagai fondasi site dan deployment."
      />

      <GapList
        items={[
          "Detail dan update client sudah memakai endpoint /api/v1/client-contract/clients/{client_id}.",
          "Contract masih fokus pada list dan create. Endpoint update contract belum tersedia.",
          "Filter server-side untuk client dan contract belum tersedia.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Create Client</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={clientForm.handleSubmit((values) => createClientMutation.mutate(values))}
          >
            <div>
              <label className={labelClass}>Company</label>
              <select className={inputClass} {...clientForm.register("company_id", { required: true })}>
                <option value="">Pilih company</option>
                {(companiesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select className={inputClass} {...clientForm.register("status", { required: true })}>
                <option value="ACTIVE">ACTIVE</option>
                <option value="NON_ACTIVE">NON_ACTIVE</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Code</label>
              <input className={inputClass} {...clientForm.register("code", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Industry Type</label>
              <input className={inputClass} {...clientForm.register("industry_type")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Client Name</label>
              <input className={inputClass} {...clientForm.register("name", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Contact Person</label>
              <input className={inputClass} {...clientForm.register("contact_person_name")} />
            </div>
            <div>
              <label className={labelClass}>Contact Phone</label>
              <input className={inputClass} {...clientForm.register("contact_person_phone")} />
            </div>
            <div>
              <label className={labelClass}>Contact Email</label>
              <input
                className={inputClass}
                type="email"
                {...clientForm.register("contact_person_email")}
              />
            </div>
            <div>
              <label className={labelClass}>Tax Number</label>
              <input className={inputClass} {...clientForm.register("tax_number")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Billing Address</label>
              <textarea
                className={`${inputClass} min-h-24`}
                {...clientForm.register("billing_address")}
              />
            </div>

            {clientSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {clientSuccess}
              </div>
            ) : null}
            {createClientMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createClientMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createClientMutation.isPending}
              >
                {createClientMutation.isPending ? "Menyimpan..." : "Simpan client"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => clientForm.reset(clientFormDefaults)}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Create Contract</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={contractForm.handleSubmit((values) => createContractMutation.mutate(values))}
          >
            <div className="md:col-span-2">
              <label className={labelClass}>Client</label>
              <select className={inputClass} {...contractForm.register("client_id", { required: true })}>
                <option value="">Pilih client</option>
                {(clientsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Contract Number</label>
              <input
                className={inputClass}
                {...contractForm.register("contract_number", { required: true })}
              />
            </div>
            <div>
              <label className={labelClass}>Contract Type</label>
              <input className={inputClass} {...contractForm.register("contract_type")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Contract Title</label>
              <input
                className={inputClass}
                {...contractForm.register("contract_title", { required: true })}
              />
            </div>
            <div>
              <label className={labelClass}>Start Date</label>
              <input
                className={inputClass}
                type="date"
                {...contractForm.register("start_date", { required: true })}
              />
            </div>
            <div>
              <label className={labelClass}>End Date</label>
              <input className={inputClass} type="date" {...contractForm.register("end_date")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Notes</label>
              <input className={inputClass} {...contractForm.register("notes")} />
            </div>

            {contractSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {contractSuccess}
              </div>
            ) : null}
            {createContractMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createContractMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createContractMutation.isPending}
              >
                {createContractMutation.isPending ? "Menyimpan..." : "Simpan contract"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() =>
                  contractForm.reset({
                    ...contractFormDefaults,
                    client_id: effectiveSelectedClientId ? String(effectiveSelectedClientId) : "",
                  })
                }
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Daftar Client</h2>
          <div className="mt-4">
            <DataState
              isLoading={clientsQuery.isLoading}
              error={clientsQuery.error}
              isEmpty={(clientsQuery.data ?? []).length === 0}
              emptyMessage="Belum ada client."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Client</th>
                      <th className={tableHeadClass}>Status</th>
                      <th className={tableHeadClass}>Contact</th>
                      <th className={tableHeadClass}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(clientsQuery.data ?? []).map((item) => {
                      const isSelected = item.id === effectiveSelectedClientId;
                      return (
                        <tr
                          key={item.id}
                          className={`border-t border-[color:var(--border)] ${
                            isSelected ? "bg-[color:var(--muted-surface)]" : ""
                          }`}
                        >
                          <td className={tableCellClass}>
                            <div className="font-semibold">{item.name}</div>
                            <div className="text-xs text-[color:var(--muted-foreground)]">
                              {item.code}
                            </div>
                          </td>
                          <td className={tableCellClass}>{item.status}</td>
                          <td className={tableCellClass}>
                            {fallbackText(item.contact_person_name)} -{" "}
                            {fallbackText(item.contact_person_phone)}
                          </td>
                          <td className={tableCellClass}>
                            <button
                              type="button"
                              className={secondaryButtonClass}
                              onClick={() => {
                                setSelectedClientId(item.id);
                                setClientUpdateSuccess(null);
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

        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Daftar Contract</h2>
          <div className="mt-4">
            <DataState
              isLoading={contractsQuery.isLoading}
              error={contractsQuery.error}
              isEmpty={(contractsQuery.data ?? []).length === 0}
              emptyMessage="Belum ada contract."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Contract</th>
                      <th className={tableHeadClass}>Type</th>
                      <th className={tableHeadClass}>Period</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(contractsQuery.data ?? []).map((item) => (
                      <tr key={item.id} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>
                          <div className="font-semibold">{item.contract_title}</div>
                          <div className="text-xs text-[color:var(--muted-foreground)]">
                            {item.contract_number}
                          </div>
                        </td>
                        <td className={tableCellClass}>{fallbackText(item.contract_type)}</td>
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
        </div>
      </section>

      <section className={surfaceClass}>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Detail dan Update Client</h2>
            <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
              Detail client memakai API khusus agar edit data client tidak lagi berhenti di create.
            </p>
          </div>
          {selectedClient ? (
            <p className="text-sm text-[color:var(--muted-foreground)]">Client ID: {selectedClient.id}</p>
          ) : null}
        </div>

        <div className="mt-4">
          <DataState
            isLoading={Boolean(effectiveSelectedClientId) && clientDetailQuery.isLoading}
            error={clientDetailQuery.error}
            isEmpty={!effectiveSelectedClientId}
            emptyMessage="Pilih client dari tabel untuk melihat detail dan update."
          >
            {selectedClient ? (
              <div className="grid gap-8 xl:grid-cols-[0.95fr_1.05fr]">
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Client
                    </p>
                    <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                      {selectedClient.name}
                    </p>
                    <p className="mt-1 text-[color:var(--muted-foreground)]">
                      {selectedClient.code} - {companyNameById.get(selectedClient.company_id) ?? "-"}
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Status
                      </p>
                      <p className="mt-1">{selectedClient.status}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Industry
                      </p>
                      <p className="mt-1">{fallbackText(selectedClient.industry_type)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Contact Person
                      </p>
                      <p className="mt-1">{fallbackText(selectedClient.contact_person_name)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Contact Phone
                      </p>
                      <p className="mt-1">{fallbackText(selectedClient.contact_person_phone)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Contact Email
                      </p>
                      <p className="mt-1">{fallbackText(selectedClient.contact_person_email)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Tax Number
                      </p>
                      <p className="mt-1">{fallbackText(selectedClient.tax_number)}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Billing Address
                    </p>
                    <p className="mt-1">{fallbackText(selectedClient.billing_address)}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Contract Terkait
                    </p>
                    {selectedClientContracts.length > 0 ? (
                      <div className="mt-2 space-y-2">
                        {selectedClientContracts.map((contract) => (
                          <div
                            key={contract.id}
                            className="rounded-md border border-[color:var(--border)] px-3 py-2"
                          >
                            <div className="font-semibold text-[color:var(--foreground)]">
                              {contract.contract_title}
                            </div>
                            <div className="mt-1 text-[color:var(--muted-foreground)]">
                              {contract.contract_number} - {formatDate(contract.start_date)} sampai{" "}
                              {formatDate(contract.end_date)}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-1">Belum ada contract untuk client ini.</p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                      Audit
                    </p>
                    <p className="mt-1">Dibuat: {formatDateTime(selectedClient.created_at)}</p>
                    <p className="mt-1">Diperbarui: {formatDateTime(selectedClient.updated_at)}</p>
                  </div>
                </div>

                <form
                  className="grid gap-4 md:grid-cols-2"
                  onSubmit={clientEditForm.handleSubmit((values) => updateClientMutation.mutate(values))}
                >
                  <div>
                    <label className={labelClass}>Status</label>
                    <select className={inputClass} {...clientEditForm.register("status", { required: true })}>
                      <option value="ACTIVE">ACTIVE</option>
                      <option value="NON_ACTIVE">NON_ACTIVE</option>
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Industry Type</label>
                    <input className={inputClass} {...clientEditForm.register("industry_type")} />
                  </div>
                  <div>
                    <label className={labelClass}>Code</label>
                    <input className={inputClass} {...clientEditForm.register("code", { required: true })} />
                  </div>
                  <div>
                    <label className={labelClass}>Client Name</label>
                    <input className={inputClass} {...clientEditForm.register("name", { required: true })} />
                  </div>
                  <div>
                    <label className={labelClass}>Contact Person</label>
                    <input className={inputClass} {...clientEditForm.register("contact_person_name")} />
                  </div>
                  <div>
                    <label className={labelClass}>Contact Phone</label>
                    <input className={inputClass} {...clientEditForm.register("contact_person_phone")} />
                  </div>
                  <div>
                    <label className={labelClass}>Contact Email</label>
                    <input
                      className={inputClass}
                      type="email"
                      {...clientEditForm.register("contact_person_email")}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Tax Number</label>
                    <input className={inputClass} {...clientEditForm.register("tax_number")} />
                  </div>
                  <div className="md:col-span-2">
                    <label className={labelClass}>Billing Address</label>
                    <textarea
                      className={`${inputClass} min-h-24`}
                      {...clientEditForm.register("billing_address")}
                    />
                  </div>

                  {clientUpdateSuccess ? (
                    <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                      {clientUpdateSuccess}
                    </div>
                  ) : null}
                  {updateClientMutation.error ? (
                    <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                      {updateClientMutation.error.message}
                    </div>
                  ) : null}
                  <div className="flex gap-2 md:col-span-2">
                    <button
                      type="submit"
                      className={primaryButtonClass}
                      disabled={updateClientMutation.isPending}
                    >
                      {updateClientMutation.isPending ? "Menyimpan..." : "Update client"}
                    </button>
                    <button
                      type="button"
                      className={secondaryButtonClass}
                      onClick={() =>
                        selectedClient
                          ? clientEditForm.reset(toClientEditFormValues(selectedClient))
                          : clientEditForm.reset(clientEditFormDefaults)
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
