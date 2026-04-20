export function todayInputValue() {
  const now = new Date();
  const localTime = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localTime.toISOString().slice(0, 10);
}

export function addDaysInputValue(days: number) {
  const now = new Date();
  now.setDate(now.getDate() + days);
  const localTime = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localTime.toISOString().slice(0, 10);
}
