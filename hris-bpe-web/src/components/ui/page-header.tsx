type PageHeaderProps = {
  title: string;
  description: string;
  actions?: React.ReactNode;
};

export function PageHeader({
  title,
  description,
  actions,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-3 border-b border-[color:var(--border)] pb-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[color:var(--foreground)]">
          {title}
        </h1>
        <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
          {description}
        </p>
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}
