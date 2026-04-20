"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDate } from "@/lib/format";
import { optionalText, requiredNumber } from "@/lib/forms";
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
import { addDaysInputValue, todayInputValue } from "@/lib/date";
import { useAuthStore } from "@/store/auth-store";

type ClientFormValues = {
  company_id: string;
  code: string;
  name: string;
  contact_person_name: string;
  contact_person_phone: string;
  industry_type: string;
  billing_address: string;
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

export default function ClientsPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [clientSuccess, setClientSuccess] = useState<string | null>(null);
  const [contractSuccess, setContractSuccess] = useState<string | null>(null);
  const clientForm = useForm<ClientFormValues>({
    defaultValues: {
      company_id: "",
      code: "",
      name: "",
      contact_person_name: "",
      contact_person_phone: "",
      industry_type: "",
      billing_address: "",
    },
  });
  const contractForm = useForm<ContractFormValues>({
    defaultValues: {
      client_id: "",
      contract_number: "",
      contract_title: "",
      start_date: todayInputValue(),
      end_date: addDaysInputValue(365),
      contract_type: "SERVICE",
      notes: "",
    },
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

  const createClientMutation = useMutation({
    mutationFn: (values: ClientFormValues) =>
      api.clientContract.createClient(accessToken!, {
        company_id: requiredNumber(values.company_id),
        code: values.code,
        name: values.name,
        contact_person_name: optionalText(values.contact_person_name),
        contact_person_phone: optionalText(values.contact_person_phone),
        industry_type: optionalText(values.industry_type),
        billing_address: optionalText(values.billing_address),
      }),
    onSuccess: () => {
      setClientSuccess("Client berhasil dibuat.");
      clientForm.reset();
      queryClient.invalidateQueries({ queryKey: ["clients"] });
    },
  });

  const createContractMutation = useMutation({
    mutationFn: (values: ContractFormValues) =>
      api.clientContract.createContract(accessToken!, {
        client_id: requiredNumber(values.client_id),
        contract_number: values.contract_number,
        contract_title: values.contract_title,
        start_date: values.start_date,
        end_date: values.end_date,
        contract_type: optionalText(values.contract_type),
        notes: optionalText(values.notes),
      }),
    onSuccess: () => {
      setContractSuccess("Contract berhasil dibuat.");
      contractForm.reset({
        client_id: "",
        contract_number: "",
        contract_title: "",
        start_date: todayInputValue(),
        end_date: addDaysInputValue(365),
        contract_type: "SERVICE",
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["contracts"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Client & Contract"
        description="Kelola client dan contract Basic sebagai fondasi site dan deployment."
      />

      <GapList
        items={[
          "Belum ada endpoint detail client khusus dan update client.",
          "Belum ada filter server-side untuk client maupun contract.",
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
              <label className={labelClass}>Code</label>
              <input className={inputClass} {...clientForm.register("code", { required: true })} />
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
              <label className={labelClass}>Industry Type</label>
              <input className={inputClass} {...clientForm.register("industry_type")} />
            </div>
            <div>
              <label className={labelClass}>Billing Address</label>
              <input className={inputClass} {...clientForm.register("billing_address")} />
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
                onClick={() => clientForm.reset()}
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
              <input className={inputClass} {...contractForm.register("contract_number", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Contract Type</label>
              <input className={inputClass} {...contractForm.register("contract_type")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Contract Title</label>
              <input className={inputClass} {...contractForm.register("contract_title", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Start Date</label>
              <input className={inputClass} type="date" {...contractForm.register("start_date", { required: true })} />
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
                onClick={() => contractForm.reset()}
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
                    </tr>
                  </thead>
                  <tbody>
                    {(clientsQuery.data ?? []).map((item) => (
                      <tr key={item.id} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>
                          <div className="font-semibold">{item.name}</div>
                          <div className="text-xs text-[color:var(--muted-foreground)]">
                            {item.code}
                          </div>
                        </td>
                        <td className={tableCellClass}>{item.status}</td>
                        <td className={tableCellClass}>
                          {fallbackText(item.contact_person_name)} ·{" "}
                          {fallbackText(item.contact_person_phone)}
                        </td>
                      </tr>
                    ))}
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
    </div>
  );
}
