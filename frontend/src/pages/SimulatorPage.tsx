import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Link, useNavigate } from "react-router-dom";
import { extractErrorMessage } from "../api/client";
import { Money } from "../components/Money";
import { useCedentes } from "../hooks/useCedentes";
import { useCurrencies, useReceivableTypes } from "../hooks/useCurrencies";
import { useSimulate } from "../hooks/useSimulate";
import { useCreateTransaction } from "../hooks/useTransactions";
import type { SimulateRequest, TransactionCreate } from "../types/api";

interface FormValues {
  cedente_id: string;
  receivable_type: string;
  face_value: string;
  base_rate: string;
  term_months: number;
  currency_code: string;
  payment_currency_code: string;
}

function useDebounced<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

function toSimulatePayload(v: FormValues): SimulateRequest | null {
  if (!v.receivable_type || !v.currency_code || !v.payment_currency_code) {
    return null;
  }
  const faceValue = Number(v.face_value);
  const baseRate = Number(v.base_rate);
  if (!Number.isFinite(faceValue) || faceValue <= 0) return null;
  if (!Number.isFinite(baseRate) || baseRate < 0) return null;
  if (v.term_months === undefined || v.term_months === null) return null;
  return {
    face_value: v.face_value,
    base_rate: v.base_rate,
    term_months: Number(v.term_months),
    receivable_type: v.receivable_type,
    currency_code: v.currency_code,
    payment_currency_code: v.payment_currency_code,
  };
}

export function SimulatorPage() {
  const navigate = useNavigate();
  const { data: cedentes } = useCedentes();
  const { data: currencies } = useCurrencies();
  const { data: types } = useReceivableTypes();
  const createTx = useCreateTransaction();

  const { register, handleSubmit, watch } = useForm<FormValues>({
    defaultValues: {
      cedente_id: "",
      receivable_type: "",
      face_value: "10000",
      base_rate: "0.01",
      term_months: 12,
      currency_code: "BRL",
      payment_currency_code: "BRL",
    },
  });

  const values = watch();
  const debounced = useDebounced(values, 400);
  const simulatePayload = useMemo(
    () => toSimulatePayload(debounced),
    [debounced],
  );
  const {
    data: simulation,
    isFetching,
    error: simulateError,
  } = useSimulate(simulatePayload);

  const onSubmit = async (v: FormValues) => {
    if (!v.cedente_id) {
      toast.error("Selecione um cedente");
      return;
    }
    const payload: TransactionCreate = {
      cedente_id: v.cedente_id,
      face_value: v.face_value,
      base_rate: v.base_rate,
      term_months: Number(v.term_months),
      receivable_type: v.receivable_type,
      currency_code: v.currency_code,
      payment_currency_code: v.payment_currency_code,
    };
    try {
      const tx = await createTx.mutateAsync(payload);
      toast.success(`Liquidado: ${tx.id.slice(0, 8)}…`);
      navigate("/statements");
    } catch (err) {
      toast.error(extractErrorMessage(err, "Erro ao liquidar"));
    }
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="col-span-3 space-y-4 rounded-lg border border-gray-800 bg-gray-900 p-6"
      >
        <h2 className="text-xl font-semibold">Dados do recebível</h2>

        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Cedente
          </label>
          <select
            {...register("cedente_id")}
            className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">— Selecione —</option>
            {(cedentes ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.document})
              </option>
            ))}
          </select>
          {(cedentes ?? []).length === 0 && (
            <p className="mt-1 text-xs text-amber-400">
              Nenhum cedente cadastrado.{" "}
              <Link to="/cedentes" className="underline">
                Cadastrar agora
              </Link>
            </p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-gray-400">
            Tipo de recebível
          </label>
          <select
            {...register("receivable_type")}
            className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">— Selecione —</option>
            {(types ?? []).map((t) => (
              <option key={t.id} value={t.name}>
                {t.name} (spread {Number(t.spread_rate) * 100}% a.m.)
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Valor de face
            </label>
            <input
              type="text"
              inputMode="decimal"
              {...register("face_value")}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Taxa base (a.m.)
            </label>
            <input
              type="text"
              inputMode="decimal"
              {...register("base_rate")}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Prazo (meses)
            </label>
            <input
              type="number"
              min={0}
              {...register("term_months", { valueAsNumber: true })}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div />
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Moeda do título
            </label>
            <select
              {...register("currency_code")}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {(currencies ?? []).map((c) => (
                <option key={c.id} value={c.code}>
                  {c.code} — {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Moeda de pagamento
            </label>
            <select
              {...register("payment_currency_code")}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {(currencies ?? []).map((c) => (
                <option key={c.id} value={c.code}>
                  {c.code} — {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={createTx.isPending}
          className="w-full rounded bg-indigo-600 py-2 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50"
        >
          {createTx.isPending ? "Liquidando…" : "Liquidar"}
        </button>
      </form>

      <aside className="col-span-2 space-y-3 rounded-lg border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">Simulação</h2>
        {isFetching && (
          <p className="text-xs text-gray-500">Calculando…</p>
        )}
        {simulateError && (
          <p className="text-xs text-red-400">
            {extractErrorMessage(simulateError, "Erro ao simular")}
          </p>
        )}
        {!simulation && !simulateError && (
          <p className="text-xs text-gray-500">
            Preencha os dados para ver o valor presente.
          </p>
        )}
        {simulation && (
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-400">Valor de face</dt>
              <dd>
                <Money
                  value={simulation.face_value}
                  currency={simulation.currency_code}
                />
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Spread aplicado</dt>
              <dd>{(Number(simulation.spread_applied) * 100).toFixed(2)}%</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Valor presente</dt>
              <dd className="font-medium text-emerald-300">
                <Money
                  value={simulation.present_value}
                  currency={simulation.currency_code}
                />
              </dd>
            </div>
            {simulation.exchange_rate_used && (
              <div className="flex justify-between">
                <dt className="text-gray-400">
                  Câmbio {simulation.currency_code}→
                  {simulation.payment_currency_code}
                </dt>
                <dd>{simulation.exchange_rate_used}</dd>
              </div>
            )}
            <div className="flex justify-between border-t border-gray-800 pt-3">
              <dt className="text-gray-400">Líquido na moeda de pgto.</dt>
              <dd className="text-lg font-bold text-indigo-300">
                <Money
                  value={simulation.present_value_in_payment_currency}
                  currency={simulation.payment_currency_code}
                />
              </dd>
            </div>
          </dl>
        )}
      </aside>
    </div>
  );
}
