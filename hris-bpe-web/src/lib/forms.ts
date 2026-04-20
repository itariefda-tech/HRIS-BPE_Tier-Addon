export function requiredNumber(value: string) {
  return Number(value);
}

export function optionalNumber(value: string) {
  return value.trim().length > 0 ? Number(value) : null;
}

export function optionalText(value: string) {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

export function selectedValuesToNumbers(values: string[]) {
  return values
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value) && value > 0);
}
