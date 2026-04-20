function parseDate(value: string) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }
  return new Date(value);
}

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(parseDate(value));
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parseDate(value));
}

export function formatNumber(value: number | null | undefined) {
  return new Intl.NumberFormat("id-ID").format(value ?? 0);
}

export function fallbackText(value: string | null | undefined) {
  return value && value.trim().length > 0 ? value : "-";
}
