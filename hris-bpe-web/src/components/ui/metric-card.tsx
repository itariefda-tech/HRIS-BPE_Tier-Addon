import { formatNumber } from "@/lib/format";
import { surfaceClass } from "@/lib/ui";

type MetricCardProps = {
  label: string;
  value: number;
  helper?: string;
};

export function MetricCard({ label, value, helper }: MetricCardProps) {
  return (
    <article className={`${surfaceClass} min-h-[124px]`}>
      <p className="text-sm text-[color:var(--muted-foreground)]">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-[color:var(--foreground)]">
        {formatNumber(value)}
      </p>
      {helper ? (
        <p className="mt-3 text-xs text-[color:var(--muted-foreground)]">
          {helper}
        </p>
      ) : null}
    </article>
  );
}
