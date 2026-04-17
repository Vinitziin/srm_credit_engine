import { useState } from "react";
import toast from "react-hot-toast";
import { extractErrorMessage } from "../api/client";
import { getTransaction } from "../api/transactions";
import { Money } from "../components/Money";
import { StatusBadge } from "../components/StatusBadge";
import { useCedentes } from "../hooks/useCedentes";
import { useCurrencies } from "../hooks/useCurrencies";
import { useStatements } from "../hooks/useStatements";
import { useUpdateTxStatus } from "../hooks/useTransactions";
import type { StatementFilters, StatementItem } from "../types/api";

const PAGE_SIZE = 20;

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("pt-BR");
}

export function StatementsPage() {
  const { data: cedentes } = useCedentes();
  const { data: currencies } = useCurrencies();
  const [filters, setFilters] = useState<StatementFilters>({
    page: 1,
    page_size: PAGE_SIZE,
  });
  const { data, isFetching, error } = useStatements(filters);
  const updateStatus = useUpdateTxStatus();

  const updateFilter = <K extends keyof StatementFilters>(
    key: K,
    value: StatementFilters[K],
  ) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const onRevert = async (item: StatementItem) => {
    try {
      const current = await getTransaction(item.id);
      await updateStatus.mutateAsync({
        id: item.id,
        status: "REVERSED",
        version: current.version,
      });
      toast.success("Transação revertida");
    } catch (err) {
      toast.error(extractErrorMessage(err, "Não foi possível reverter"));
    }
  };

  const totalPages = data
    ? Math.max(1, Math.ceil(data.total / data.page_size))
    : 1;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Extrato de liquidação</h2>

      <div className="grid grid-cols-2 gap-3 rounded-lg border border-gray-800 bg-gray-900 p-4 lg:grid-cols-5">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            De
          </label>
          <input
            type="date"
            value={filters.date_from ?? ""}
            onChange={(e) =>
              updateFilter("date_from", e.target.value || undefined)
            }
            className="w-full rounded bg-gray-800 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Até
          </label>
          <input
            type="date"
            value={filters.date_to ?? ""}
            onChange={(e) =>
              updateFilter("date_to", e.target.value || undefined)
            }
            className="w-full rounded bg-gray-800 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Cedente
          </label>
          <select
            value={filters.cedente_id ?? ""}
            onChange={(e) =>
              updateFilter("cedente_id", e.target.value || undefined)
            }
            className="w-full rounded bg-gray-800 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            {(cedentes ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Moeda pgto.
          </label>
          <select
            value={filters.currency_code ?? ""}
            onChange={(e) =>
              updateFilter("currency_code", e.target.value || undefined)
            }
            className="w-full rounded bg-gray-800 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Todas</option>
            {(currencies ?? []).map((c) => (
              <option key={c.id} value={c.code}>
                {c.code}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Status
          </label>
          <select
            value={filters.status ?? ""}
            onChange={(e) =>
              updateFilter("status", e.target.value || undefined)
            }
            className="w-full rounded bg-gray-800 px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            <option value="SETTLED">SETTLED</option>
            <option value="REVERSED">REVERSED</option>
          </select>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-400">
          {extractErrorMessage(error, "Erro ao carregar extrato")}
        </p>
      )}

      <div className="overflow-hidden rounded-lg border border-gray-800">
        <table className="w-full text-sm">
          <thead className="bg-gray-900 text-left text-xs uppercase text-gray-400">
            <tr>
              <th className="px-3 py-2">Data</th>
              <th className="px-3 py-2">Cedente</th>
              <th className="px-3 py-2">Tipo</th>
              <th className="px-3 py-2 text-right">Face</th>
              <th className="px-3 py-2 text-right">Presente</th>
              <th className="px-3 py-2">Moeda</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {(data?.items ?? []).map((item) => (
              <tr key={item.id} className="border-t border-gray-800">
                <td className="px-3 py-2 text-xs text-gray-400">
                  {formatDate(item.created_at)}
                </td>
                <td className="px-3 py-2">{item.cedente_name}</td>
                <td className="px-3 py-2 text-gray-300">
                  {item.receivable_type}
                </td>
                <td className="px-3 py-2 text-right">
                  <Money
                    value={item.face_value}
                    currency={item.currency_code}
                  />
                </td>
                <td className="px-3 py-2 text-right">
                  <Money
                    value={item.present_value}
                    currency={item.payment_currency_code}
                  />
                </td>
                <td className="px-3 py-2 text-xs">
                  {item.currency_code}→{item.payment_currency_code}
                </td>
                <td className="px-3 py-2">
                  <StatusBadge status={item.status} />
                </td>
                <td className="px-3 py-2 text-right">
                  {item.status === "SETTLED" && (
                    <button
                      onClick={() => onRevert(item)}
                      disabled={updateStatus.isPending}
                      className="rounded border border-amber-700 px-2 py-1 text-xs text-amber-300 hover:bg-amber-900/30 disabled:opacity-50"
                    >
                      Reverter
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {!isFetching && data?.items.length === 0 && (
              <tr>
                <td
                  colSpan={8}
                  className="px-3 py-6 text-center text-gray-500"
                >
                  Nenhuma transação encontrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-400">
        <span>
          {data
            ? `${data.total} transação(ões) · página ${data.page} de ${totalPages}`
            : "—"}
        </span>
        <div className="flex gap-2">
          <button
            disabled={!data || data.page <= 1}
            onClick={() =>
              setFilters((f) => ({ ...f, page: Math.max(1, f.page - 1) }))
            }
            className="rounded border border-gray-700 px-3 py-1 disabled:opacity-40"
          >
            Anterior
          </button>
          <button
            disabled={!data || data.page >= totalPages}
            onClick={() =>
              setFilters((f) => ({ ...f, page: f.page + 1 }))
            }
            className="rounded border border-gray-700 px-3 py-1 disabled:opacity-40"
          >
            Próxima
          </button>
        </div>
      </div>
    </div>
  );
}
