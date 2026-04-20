type DataStateProps = {
  isLoading: boolean;
  error?: unknown;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
};

function resolveErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return "Terjadi error saat memuat data.";
}

export function DataState({
  isLoading,
  error,
  isEmpty,
  emptyMessage,
  children,
}: DataStateProps) {
  if (isLoading) {
    return (
      <div className="rounded-md border border-dashed border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-6 text-sm text-[color:var(--muted-foreground)]">
        Memuat data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-[color:var(--danger)]/30 bg-[color:var(--danger)]/8 px-4 py-6 text-sm text-[color:var(--danger)]">
        {resolveErrorMessage(error)}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="rounded-md border border-dashed border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-6 text-sm text-[color:var(--muted-foreground)]">
        {emptyMessage ?? "Belum ada data."}
      </div>
    );
  }

  return <>{children}</>;
}
