export const surfaceClass =
  "rounded-md border border-[color:var(--border)] bg-[color:var(--surface)] p-4 shadow-[0_10px_28px_rgba(29,47,35,0.06)]";

export const inputClass =
  "mt-1 w-full rounded-md border border-[color:var(--border)] bg-white px-3 py-2 text-sm text-[color:var(--foreground)] outline-none transition focus:border-[color:var(--accent)]";

export const labelClass = "text-sm font-medium text-[color:var(--foreground)]";

export const helperTextClass = "text-xs text-[color:var(--muted-foreground)]";

export const primaryButtonClass =
  "rounded-md bg-[color:var(--accent)] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[color:var(--accent-strong)] disabled:cursor-not-allowed disabled:opacity-60";

export const secondaryButtonClass =
  "rounded-md border border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-2 text-sm font-semibold text-[color:var(--foreground)] transition hover:bg-[color:var(--muted-surface)] disabled:cursor-not-allowed disabled:opacity-60";

export const dangerButtonClass =
  "rounded-md bg-[color:var(--danger)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60";

export const tableWrapperClass =
  "overflow-x-auto rounded-md border border-[color:var(--border)] bg-white";

export const tableClass = "min-w-full divide-y divide-[color:var(--border)] text-sm";

export const tableHeadClass =
  "bg-[color:var(--muted-surface)] px-3 py-2 text-left font-semibold text-[color:var(--muted-foreground)]";

export const tableCellClass =
  "px-3 py-3 align-top text-[color:var(--foreground)]";

export function badgeClass(
  tone: "neutral" | "success" | "warning" | "danger",
) {
  const toneMap = {
    neutral:
      "bg-[color:var(--muted-surface)] text-[color:var(--foreground)]",
    success: "bg-[color:var(--success)]/12 text-[color:var(--success)]",
    warning: "bg-[color:var(--warning)]/12 text-[color:var(--warning)]",
    danger: "bg-[color:var(--danger)]/12 text-[color:var(--danger)]",
  };

  return `inline-flex rounded-md px-2 py-1 text-xs font-semibold ${toneMap[tone]}`;
}
