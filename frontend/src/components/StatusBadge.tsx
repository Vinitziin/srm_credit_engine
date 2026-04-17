interface StatusBadgeProps {
  status: string;
}

const COLORS: Record<string, string> = {
  SETTLED: "bg-emerald-900/50 text-emerald-300 border-emerald-700",
  REVERSED: "bg-amber-900/50 text-amber-300 border-amber-700",
  PENDING: "bg-sky-900/50 text-sky-300 border-sky-700",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const cls = COLORS[status] ?? "bg-gray-800 text-gray-300 border-gray-700";
  return (
    <span
      className={`inline-block rounded border px-2 py-0.5 text-xs font-medium ${cls}`}
    >
      {status}
    </span>
  );
}
