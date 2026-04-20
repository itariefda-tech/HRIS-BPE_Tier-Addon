"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText } from "@/lib/format";
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

type SiteFormValues = {
  client_id: string;
  code: string;
  name: string;
  city: string;
  province: string;
  address: string;
  radius_meters: string;
};

type PostFormValues = {
  client_site_id: string;
  code: string;
  name: string;
  description: string;
};

export default function SitesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [siteSuccess, setSiteSuccess] = useState<string | null>(null);
  const [postSuccess, setPostSuccess] = useState<string | null>(null);
  const siteForm = useForm<SiteFormValues>({
    defaultValues: {
      client_id: "",
      code: "",
      name: "",
      city: "",
      province: "",
      address: "",
      radius_meters: "150",
    },
  });
  const postForm = useForm<PostFormValues>({
    defaultValues: {
      client_site_id: "",
      code: "",
      name: "",
      description: "",
    },
  });

  const clientsQuery = useQuery({
    queryKey: ["clients"],
    queryFn: () => api.clientContract.listClients(accessToken!),
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

  const createSiteMutation = useMutation({
    mutationFn: (values: SiteFormValues) =>
      api.siteOperations.createSite(accessToken!, {
        client_id: requiredNumber(values.client_id),
        code: values.code,
        name: values.name,
        city: optionalText(values.city),
        province: optionalText(values.province),
        address: optionalText(values.address),
        radius_meters: optionalNumber(values.radius_meters),
      }),
    onSuccess: () => {
      setSiteSuccess("Site berhasil dibuat.");
      siteForm.reset({
        client_id: "",
        code: "",
        name: "",
        city: "",
        province: "",
        address: "",
        radius_meters: "150",
      });
      queryClient.invalidateQueries({ queryKey: ["sites"] });
    },
  });

  const createPostMutation = useMutation({
    mutationFn: (values: PostFormValues) =>
      api.siteOperations.createPost(accessToken!, {
        client_site_id: requiredNumber(values.client_site_id),
        code: values.code,
        name: values.name,
        description: optionalText(values.description),
      }),
    onSuccess: () => {
      setPostSuccess("Site post berhasil dibuat.");
      postForm.reset({
        client_site_id: "",
        code: "",
        name: "",
        description: "",
      });
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Site & Post"
        description="Kelola site dan site post untuk jalur deployment dan attendance."
      />

      <GapList
        items={[
          "Belum ada endpoint detail site khusus dan update site/post.",
          "Filter site dan post masih berbasis list client-side.",
        ]}
      />

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Create Site</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={siteForm.handleSubmit((values) => createSiteMutation.mutate(values))}
          >
            <div className="md:col-span-2">
              <label className={labelClass}>Client</label>
              <select className={inputClass} {...siteForm.register("client_id", { required: true })}>
                <option value="">Pilih client</option>
                {(clientsQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Code</label>
              <input className={inputClass} {...siteForm.register("code", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Site Name</label>
              <input className={inputClass} {...siteForm.register("name", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>City</label>
              <input className={inputClass} {...siteForm.register("city")} />
            </div>
            <div>
              <label className={labelClass}>Province</label>
              <input className={inputClass} {...siteForm.register("province")} />
            </div>
            <div>
              <label className={labelClass}>Radius Meters</label>
              <input className={inputClass} type="number" {...siteForm.register("radius_meters")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Address</label>
              <input className={inputClass} {...siteForm.register("address")} />
            </div>
            {siteSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {siteSuccess}
              </div>
            ) : null}
            {createSiteMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createSiteMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createSiteMutation.isPending}
              >
                {createSiteMutation.isPending ? "Menyimpan..." : "Simpan site"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => siteForm.reset()}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Create Site Post</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={postForm.handleSubmit((values) => createPostMutation.mutate(values))}
          >
            <div className="md:col-span-2">
              <label className={labelClass}>Site</label>
              <select className={inputClass} {...postForm.register("client_site_id", { required: true })}>
                <option value="">Pilih site</option>
                {(sitesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Code</label>
              <input className={inputClass} {...postForm.register("code", { required: true })} />
            </div>
            <div>
              <label className={labelClass}>Post Name</label>
              <input className={inputClass} {...postForm.register("name", { required: true })} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Description</label>
              <input className={inputClass} {...postForm.register("description")} />
            </div>
            {postSuccess ? (
              <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                {postSuccess}
              </div>
            ) : null}
            {createPostMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                {createPostMutation.error.message}
              </div>
            ) : null}
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                className={primaryButtonClass}
                disabled={createPostMutation.isPending}
              >
                {createPostMutation.isPending ? "Menyimpan..." : "Simpan site post"}
              </button>
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={() => postForm.reset()}
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <h2 className="text-lg font-semibold">Daftar Site</h2>
          <div className="mt-4">
            <DataState
              isLoading={sitesQuery.isLoading}
              error={sitesQuery.error}
              isEmpty={(sitesQuery.data ?? []).length === 0}
              emptyMessage="Belum ada site."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Site</th>
                      <th className={tableHeadClass}>Location</th>
                      <th className={tableHeadClass}>Radius</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(sitesQuery.data ?? []).map((item) => (
                      <tr key={item.id} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>
                          <div className="font-semibold">{item.name}</div>
                          <div className="text-xs text-[color:var(--muted-foreground)]">
                            {item.code}
                          </div>
                        </td>
                        <td className={tableCellClass}>
                          {fallbackText(item.city)}, {fallbackText(item.province)}
                        </td>
                        <td className={tableCellClass}>
                          {item.radius_meters ?? "-"}
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
          <h2 className="text-lg font-semibold">Daftar Site Post</h2>
          <div className="mt-4">
            <DataState
              isLoading={postsQuery.isLoading}
              error={postsQuery.error}
              isEmpty={(postsQuery.data ?? []).length === 0}
              emptyMessage="Belum ada site post."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Post</th>
                      <th className={tableHeadClass}>Site ID</th>
                      <th className={tableHeadClass}>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(postsQuery.data ?? []).map((item) => (
                      <tr key={item.id} className="border-t border-[color:var(--border)]">
                        <td className={tableCellClass}>
                          <div className="font-semibold">{item.name}</div>
                          <div className="text-xs text-[color:var(--muted-foreground)]">
                            {item.code}
                          </div>
                        </td>
                        <td className={tableCellClass}>{item.client_site_id}</td>
                        <td className={tableCellClass}>{fallbackText(item.description)}</td>
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
