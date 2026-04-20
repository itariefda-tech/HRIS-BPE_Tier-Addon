"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { DataState } from "@/components/ui/data-state";
import { GapList } from "@/components/ui/gap-list";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { fallbackText, formatDateTime } from "@/lib/format";
import { optionalNumber, optionalText, requiredNumber } from "@/lib/forms";
import type { ClientSite, SitePost } from "@/lib/types";
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
  latitude: string;
  longitude: string;
  radius_meters: string;
  status: string;
};

type SiteEditFormValues = {
  code: string;
  name: string;
  city: string;
  province: string;
  address: string;
  latitude: string;
  longitude: string;
  radius_meters: string;
  status: string;
};

type PostFormValues = {
  client_site_id: string;
  code: string;
  name: string;
  description: string;
  active_flag: string;
};

type PostEditFormValues = {
  code: string;
  name: string;
  description: string;
  active_flag: string;
};

const siteFormDefaults: SiteFormValues = {
  client_id: "",
  code: "",
  name: "",
  city: "",
  province: "",
  address: "",
  latitude: "",
  longitude: "",
  radius_meters: "150",
  status: "ACTIVE",
};

const siteEditFormDefaults: SiteEditFormValues = {
  code: "",
  name: "",
  city: "",
  province: "",
  address: "",
  latitude: "",
  longitude: "",
  radius_meters: "",
  status: "ACTIVE",
};

const postFormDefaults: PostFormValues = {
  client_site_id: "",
  code: "",
  name: "",
  description: "",
  active_flag: "true",
};

const postEditFormDefaults: PostEditFormValues = {
  code: "",
  name: "",
  description: "",
  active_flag: "true",
};

function optionalDecimalNumber(value: string) {
  const trimmed = value.trim();
  return trimmed.length > 0 ? Number(trimmed) : null;
}

function toSiteEditFormValues(site: ClientSite): SiteEditFormValues {
  return {
    code: site.code,
    name: site.name,
    city: site.city ?? "",
    province: site.province ?? "",
    address: site.address ?? "",
    latitude: site.latitude ?? "",
    longitude: site.longitude ?? "",
    radius_meters: site.radius_meters !== null ? String(site.radius_meters) : "",
    status: site.status,
  };
}

function toPostEditFormValues(post: SitePost): PostEditFormValues {
  return {
    code: post.code,
    name: post.name,
    description: post.description ?? "",
    active_flag: String(post.active_flag),
  };
}

export default function SitesPage() {
  const queryClient = useQueryClient();
  const accessToken = useAuthStore((state) => state.session?.access_token);
  const [siteSuccess, setSiteSuccess] = useState<string | null>(null);
  const [postSuccess, setPostSuccess] = useState<string | null>(null);
  const [siteUpdateSuccess, setSiteUpdateSuccess] = useState<string | null>(null);
  const [postUpdateSuccess, setPostUpdateSuccess] = useState<string | null>(null);
  const [selectedSiteId, setSelectedSiteId] = useState<number | null>(null);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);

  const siteForm = useForm<SiteFormValues>({
    defaultValues: siteFormDefaults,
  });
  const siteEditForm = useForm<SiteEditFormValues>({
    defaultValues: siteEditFormDefaults,
  });
  const postForm = useForm<PostFormValues>({
    defaultValues: postFormDefaults,
  });
  const postEditForm = useForm<PostEditFormValues>({
    defaultValues: postEditFormDefaults,
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

  const effectiveSelectedSiteId = useMemo(() => {
    const sites = sitesQuery.data ?? [];
    if (sites.length === 0) {
      return null;
    }

    if (selectedSiteId !== null) {
      const selectedStillVisible = sites.some((site) => site.id === selectedSiteId);
      if (selectedStillVisible) {
        return selectedSiteId;
      }
    }

    return sites[0].id;
  }, [selectedSiteId, sitesQuery.data]);

  const effectiveSelectedPostId = useMemo(() => {
    const posts = postsQuery.data ?? [];
    if (posts.length === 0) {
      return null;
    }

    if (selectedPostId !== null) {
      const selectedStillVisible = posts.some((post) => post.id === selectedPostId);
      if (selectedStillVisible) {
        return selectedPostId;
      }
    }

    return posts[0].id;
  }, [postsQuery.data, selectedPostId]);

  const siteDetailQuery = useQuery({
    queryKey: ["site-detail", effectiveSelectedSiteId],
    queryFn: () => api.siteOperations.getSiteDetail(accessToken!, effectiveSelectedSiteId!),
    enabled: Boolean(accessToken) && effectiveSelectedSiteId !== null,
  });
  const postDetailQuery = useQuery({
    queryKey: ["post-detail", effectiveSelectedPostId],
    queryFn: () => api.siteOperations.getPostDetail(accessToken!, effectiveSelectedPostId!),
    enabled: Boolean(accessToken) && effectiveSelectedPostId !== null,
  });

  const createSiteMutation = useMutation({
    mutationFn: (values: SiteFormValues) =>
      api.siteOperations.createSite(accessToken!, {
        client_id: requiredNumber(values.client_id),
        code: values.code.trim(),
        name: values.name.trim(),
        city: optionalText(values.city),
        province: optionalText(values.province),
        address: optionalText(values.address),
        latitude: optionalDecimalNumber(values.latitude),
        longitude: optionalDecimalNumber(values.longitude),
        radius_meters: optionalNumber(values.radius_meters),
        status: values.status.trim(),
      }),
    onSuccess: (site) => {
      setSiteSuccess("Site berhasil dibuat.");
      setSiteUpdateSuccess(null);
      siteForm.reset(siteFormDefaults);
      setSelectedSiteId(site.id);
      queryClient.setQueryData(["site-detail", site.id], site);
      queryClient.invalidateQueries({ queryKey: ["sites"] });
    },
  });

  const updateSiteMutation = useMutation({
    mutationFn: (values: SiteEditFormValues) =>
      api.siteOperations.updateSite(accessToken!, effectiveSelectedSiteId!, {
        code: values.code.trim(),
        name: values.name.trim(),
        city: optionalText(values.city),
        province: optionalText(values.province),
        address: optionalText(values.address),
        latitude: optionalDecimalNumber(values.latitude),
        longitude: optionalDecimalNumber(values.longitude),
        radius_meters: optionalNumber(values.radius_meters),
        status: values.status.trim(),
      }),
    onSuccess: (site) => {
      setSiteUpdateSuccess("Site berhasil diperbarui.");
      queryClient.setQueryData(["site-detail", site.id], site);
      queryClient.invalidateQueries({ queryKey: ["sites"] });
      siteEditForm.reset(toSiteEditFormValues(site));
    },
  });

  const createPostMutation = useMutation({
    mutationFn: (values: PostFormValues) =>
      api.siteOperations.createPost(accessToken!, {
        client_site_id: requiredNumber(values.client_site_id),
        code: values.code.trim(),
        name: values.name.trim(),
        description: optionalText(values.description),
        active_flag: values.active_flag === "true",
      }),
    onSuccess: (post) => {
      setPostSuccess("Site post berhasil dibuat.");
      setPostUpdateSuccess(null);
      postForm.reset({
        ...postFormDefaults,
        client_site_id: String(post.client_site_id),
      });
      setSelectedPostId(post.id);
      queryClient.setQueryData(["post-detail", post.id], post);
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });

  const updatePostMutation = useMutation({
    mutationFn: (values: PostEditFormValues) =>
      api.siteOperations.updatePost(accessToken!, effectiveSelectedPostId!, {
        code: values.code.trim(),
        name: values.name.trim(),
        description: optionalText(values.description),
        active_flag: values.active_flag === "true",
      }),
    onSuccess: (post) => {
      setPostUpdateSuccess("Site post berhasil diperbarui.");
      queryClient.setQueryData(["post-detail", post.id], post);
      queryClient.invalidateQueries({ queryKey: ["posts"] });
      postEditForm.reset(toPostEditFormValues(post));
    },
  });

  useEffect(() => {
    if (!siteDetailQuery.data) {
      return;
    }

    siteEditForm.reset(toSiteEditFormValues(siteDetailQuery.data));
  }, [siteDetailQuery.data, siteEditForm]);

  useEffect(() => {
    if (!postDetailQuery.data) {
      return;
    }

    postEditForm.reset(toPostEditFormValues(postDetailQuery.data));
  }, [postDetailQuery.data, postEditForm]);

  const clientNameById = useMemo(
    () => new Map((clientsQuery.data ?? []).map((item) => [item.id, item.name])),
    [clientsQuery.data],
  );
  const siteNameById = useMemo(
    () => new Map((sitesQuery.data ?? []).map((item) => [item.id, item.name])),
    [sitesQuery.data],
  );
  const selectedSite = siteDetailQuery.data ?? null;
  const selectedPost = postDetailQuery.data ?? null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Site & Post"
        description="Kelola site dan site post untuk jalur deployment dan attendance."
      />

      <GapList
        items={[
          "Detail dan update site sudah memakai endpoint /api/v1/site-operations/sites/{site_id}.",
          "Detail dan update post sudah memakai endpoint /api/v1/site-operations/posts/{post_id}.",
          "Filter server-side untuk site dan post belum tersedia.",
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
              <label className={labelClass}>Latitude</label>
              <input className={inputClass} {...siteForm.register("latitude")} />
            </div>
            <div>
              <label className={labelClass}>Longitude</label>
              <input className={inputClass} {...siteForm.register("longitude")} />
            </div>
            <div>
              <label className={labelClass}>Radius Meters</label>
              <input className={inputClass} type="number" {...siteForm.register("radius_meters")} />
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select className={inputClass} {...siteForm.register("status", { required: true })}>
                <option value="ACTIVE">ACTIVE</option>
                <option value="NON_ACTIVE">NON_ACTIVE</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Address</label>
              <textarea className={`${inputClass} min-h-24`} {...siteForm.register("address")} />
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
                onClick={() => siteForm.reset(siteFormDefaults)}
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
              <textarea className={`${inputClass} min-h-24`} {...postForm.register("description")} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>Active Flag</label>
              <select className={inputClass} {...postForm.register("active_flag", { required: true })}>
                <option value="true">TRUE</option>
                <option value="false">FALSE</option>
              </select>
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
                onClick={() => postForm.reset(postFormDefaults)}
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
              isLoading={sitesQuery.isLoading || clientsQuery.isLoading}
              error={sitesQuery.error ?? clientsQuery.error}
              isEmpty={(sitesQuery.data ?? []).length === 0}
              emptyMessage="Belum ada site."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Site</th>
                      <th className={tableHeadClass}>Client</th>
                      <th className={tableHeadClass}>Location</th>
                      <th className={tableHeadClass}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(sitesQuery.data ?? []).map((item) => {
                      const isSelected = item.id === effectiveSelectedSiteId;
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
                          <td className={tableCellClass}>
                            {clientNameById.get(item.client_id) ?? `Client ${item.client_id}`}
                          </td>
                          <td className={tableCellClass}>
                            {fallbackText(item.city)} - {fallbackText(item.province)}
                          </td>
                          <td className={tableCellClass}>
                            <button
                              type="button"
                              className={secondaryButtonClass}
                              onClick={() => {
                                setSelectedSiteId(item.id);
                                setSiteUpdateSuccess(null);
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
          <h2 className="text-lg font-semibold">Daftar Site Post</h2>
          <div className="mt-4">
            <DataState
              isLoading={postsQuery.isLoading || sitesQuery.isLoading}
              error={postsQuery.error ?? sitesQuery.error}
              isEmpty={(postsQuery.data ?? []).length === 0}
              emptyMessage="Belum ada site post."
            >
              <div className={tableWrapperClass}>
                <table className={tableClass}>
                  <thead>
                    <tr>
                      <th className={tableHeadClass}>Post</th>
                      <th className={tableHeadClass}>Site</th>
                      <th className={tableHeadClass}>Status</th>
                      <th className={tableHeadClass}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(postsQuery.data ?? []).map((item) => {
                      const isSelected = item.id === effectiveSelectedPostId;
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
                          <td className={tableCellClass}>
                            {siteNameById.get(item.client_site_id) ?? `Site ${item.client_site_id}`}
                          </td>
                          <td className={tableCellClass}>
                            {item.active_flag ? "ACTIVE" : "INACTIVE"}
                          </td>
                          <td className={tableCellClass}>
                            <button
                              type="button"
                              className={secondaryButtonClass}
                              onClick={() => {
                                setSelectedPostId(item.id);
                                setPostUpdateSuccess(null);
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

      <section className="grid gap-6 xl:grid-cols-2">
        <div className={surfaceClass}>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Detail dan Update Site</h2>
            {selectedSite ? (
              <p className="text-sm text-[color:var(--muted-foreground)]">Site ID: {selectedSite.id}</p>
            ) : null}
          </div>

          <div className="mt-4">
            <DataState
              isLoading={Boolean(effectiveSelectedSiteId) && siteDetailQuery.isLoading}
              error={siteDetailQuery.error}
              isEmpty={!effectiveSelectedSiteId}
              emptyMessage="Pilih site dari tabel untuk melihat detail dan update."
            >
              {selectedSite ? (
                <div className="space-y-6">
                  <div className="space-y-4 text-sm">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Site
                      </p>
                      <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                        {selectedSite.name}
                      </p>
                      <p className="mt-1 text-[color:var(--muted-foreground)]">
                        {selectedSite.code} -{" "}
                        {clientNameById.get(selectedSite.client_id) ?? `Client ${selectedSite.client_id}`}
                      </p>
                    </div>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Status
                        </p>
                        <p className="mt-1">{selectedSite.status}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Radius
                        </p>
                        <p className="mt-1">{selectedSite.radius_meters ?? "-"}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          City
                        </p>
                        <p className="mt-1">{fallbackText(selectedSite.city)}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Province
                        </p>
                        <p className="mt-1">{fallbackText(selectedSite.province)}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Latitude
                        </p>
                        <p className="mt-1">{fallbackText(selectedSite.latitude)}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Longitude
                        </p>
                        <p className="mt-1">{fallbackText(selectedSite.longitude)}</p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Address
                      </p>
                      <p className="mt-1">{fallbackText(selectedSite.address)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Audit
                      </p>
                      <p className="mt-1">Dibuat: {formatDateTime(selectedSite.created_at)}</p>
                      <p className="mt-1">Diperbarui: {formatDateTime(selectedSite.updated_at)}</p>
                    </div>
                  </div>

                  <form
                    className="grid gap-4 md:grid-cols-2"
                    onSubmit={siteEditForm.handleSubmit((values) => updateSiteMutation.mutate(values))}
                  >
                    <div>
                      <label className={labelClass}>Code</label>
                      <input className={inputClass} {...siteEditForm.register("code", { required: true })} />
                    </div>
                    <div>
                      <label className={labelClass}>Site Name</label>
                      <input className={inputClass} {...siteEditForm.register("name", { required: true })} />
                    </div>
                    <div>
                      <label className={labelClass}>City</label>
                      <input className={inputClass} {...siteEditForm.register("city")} />
                    </div>
                    <div>
                      <label className={labelClass}>Province</label>
                      <input className={inputClass} {...siteEditForm.register("province")} />
                    </div>
                    <div>
                      <label className={labelClass}>Latitude</label>
                      <input className={inputClass} {...siteEditForm.register("latitude")} />
                    </div>
                    <div>
                      <label className={labelClass}>Longitude</label>
                      <input className={inputClass} {...siteEditForm.register("longitude")} />
                    </div>
                    <div>
                      <label className={labelClass}>Radius Meters</label>
                      <input className={inputClass} type="number" {...siteEditForm.register("radius_meters")} />
                    </div>
                    <div>
                      <label className={labelClass}>Status</label>
                      <select className={inputClass} {...siteEditForm.register("status", { required: true })}>
                        <option value="ACTIVE">ACTIVE</option>
                        <option value="NON_ACTIVE">NON_ACTIVE</option>
                      </select>
                    </div>
                    <div className="md:col-span-2">
                      <label className={labelClass}>Address</label>
                      <textarea className={`${inputClass} min-h-24`} {...siteEditForm.register("address")} />
                    </div>

                    {siteUpdateSuccess ? (
                      <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)] md:col-span-2">
                        {siteUpdateSuccess}
                      </div>
                    ) : null}
                    {updateSiteMutation.error ? (
                      <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)] md:col-span-2">
                        {updateSiteMutation.error.message}
                      </div>
                    ) : null}
                    <div className="flex gap-2 md:col-span-2">
                      <button
                        type="submit"
                        className={primaryButtonClass}
                        disabled={updateSiteMutation.isPending}
                      >
                        {updateSiteMutation.isPending ? "Menyimpan..." : "Update site"}
                      </button>
                      <button
                        type="button"
                        className={secondaryButtonClass}
                        onClick={() =>
                          selectedSite
                            ? siteEditForm.reset(toSiteEditFormValues(selectedSite))
                            : siteEditForm.reset(siteEditFormDefaults)
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
        </div>

        <div className={surfaceClass}>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Detail dan Update Site Post</h2>
            {selectedPost ? (
              <p className="text-sm text-[color:var(--muted-foreground)]">Post ID: {selectedPost.id}</p>
            ) : null}
          </div>

          <div className="mt-4">
            <DataState
              isLoading={Boolean(effectiveSelectedPostId) && postDetailQuery.isLoading}
              error={postDetailQuery.error}
              isEmpty={!effectiveSelectedPostId}
              emptyMessage="Pilih site post dari tabel untuk melihat detail dan update."
            >
              {selectedPost ? (
                <div className="space-y-6">
                  <div className="space-y-4 text-sm">
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Site Post
                      </p>
                      <p className="mt-1 text-lg font-semibold text-[color:var(--foreground)]">
                        {selectedPost.name}
                      </p>
                      <p className="mt-1 text-[color:var(--muted-foreground)]">
                        {selectedPost.code} -{" "}
                        {siteNameById.get(selectedPost.client_site_id) ?? `Site ${selectedPost.client_site_id}`}
                      </p>
                    </div>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                          Active Flag
                        </p>
                        <p className="mt-1">{selectedPost.active_flag ? "TRUE" : "FALSE"}</p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Description
                      </p>
                      <p className="mt-1">{fallbackText(selectedPost.description)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                        Audit
                      </p>
                      <p className="mt-1">Dibuat: {formatDateTime(selectedPost.created_at)}</p>
                      <p className="mt-1">Diperbarui: {formatDateTime(selectedPost.updated_at)}</p>
                    </div>
                  </div>

                  <form
                    className="grid gap-4"
                    onSubmit={postEditForm.handleSubmit((values) => updatePostMutation.mutate(values))}
                  >
                    <div>
                      <label className={labelClass}>Code</label>
                      <input className={inputClass} {...postEditForm.register("code", { required: true })} />
                    </div>
                    <div>
                      <label className={labelClass}>Post Name</label>
                      <input className={inputClass} {...postEditForm.register("name", { required: true })} />
                    </div>
                    <div>
                      <label className={labelClass}>Active Flag</label>
                      <select className={inputClass} {...postEditForm.register("active_flag", { required: true })}>
                        <option value="true">TRUE</option>
                        <option value="false">FALSE</option>
                      </select>
                    </div>
                    <div>
                      <label className={labelClass}>Description</label>
                      <textarea className={`${inputClass} min-h-24`} {...postEditForm.register("description")} />
                    </div>

                    {postUpdateSuccess ? (
                      <div className="rounded-md bg-[color:var(--success)]/10 px-3 py-2 text-sm text-[color:var(--success)]">
                        {postUpdateSuccess}
                      </div>
                    ) : null}
                    {updatePostMutation.error ? (
                      <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                        {updatePostMutation.error.message}
                      </div>
                    ) : null}
                    <div className="flex gap-2">
                      <button
                        type="submit"
                        className={primaryButtonClass}
                        disabled={updatePostMutation.isPending}
                      >
                        {updatePostMutation.isPending ? "Menyimpan..." : "Update site post"}
                      </button>
                      <button
                        type="button"
                        className={secondaryButtonClass}
                        onClick={() =>
                          selectedPost
                            ? postEditForm.reset(toPostEditFormValues(selectedPost))
                            : postEditForm.reset(postEditFormDefaults)
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
        </div>
      </section>
    </div>
  );
}
