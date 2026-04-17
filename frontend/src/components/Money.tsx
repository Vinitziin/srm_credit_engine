interface MoneyProps {
  value: string | null | undefined;
  currency?: string;
}

export function Money({ value, currency }: MoneyProps) {
  if (value === null || value === undefined) return <span>—</span>;
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return <span>{value}</span>;

  if (currency) {
    try {
      return (
        <span>
          {new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }).format(numeric)}
        </span>
      );
    } catch {
      // Unknown currency code — fall through to plain number
    }
  }
  return (
    <span>
      {new Intl.NumberFormat("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
      }).format(numeric)}
      {currency ? ` ${currency}` : null}
    </span>
  );
}
