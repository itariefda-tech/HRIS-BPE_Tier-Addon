import { surfaceClass } from "@/lib/ui";

type GapListProps = {
  title?: string;
  items: string[];
};

export function GapList({ title = "Gap backend saat ini", items }: GapListProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className={`${surfaceClass} border-[color:var(--warning)]/35 bg-[color:var(--warning)]/8`}>
      <h2 className="text-sm font-semibold text-[color:var(--foreground)]">
        {title}
      </h2>
      <ul className="mt-3 space-y-2 text-sm text-[color:var(--foreground)]">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1 h-1.5 w-1.5 rounded-full bg-[color:var(--warning)]" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
