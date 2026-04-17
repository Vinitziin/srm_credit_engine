import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { useCedentes, useCreateCedente } from "../hooks/useCedentes";
import { extractErrorMessage } from "../api/client";
import type { CedenteCreate } from "../types/api";

export function CedentesPage() {
  const { data: cedentes, isLoading } = useCedentes();
  const createMutation = useCreateCedente();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CedenteCreate>();

  const onSubmit = async (values: CedenteCreate) => {
    try {
      await createMutation.mutateAsync(values);
      toast.success("Cedente cadastrado");
      reset();
    } catch (err) {
      toast.error(extractErrorMessage(err, "Erro ao cadastrar cedente"));
    }
  };

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-xl font-semibold">Novo cedente</h2>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="grid max-w-xl grid-cols-2 gap-4 rounded-lg border border-gray-800 bg-gray-900 p-6"
        >
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Razão social
            </label>
            <input
              {...register("name", { required: "Obrigatório", minLength: 1 })}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {errors.name && (
              <p className="mt-1 text-xs text-red-400">{errors.name.message}</p>
            )}
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-400">
              CNPJ
            </label>
            <input
              {...register("document", {
                required: "Obrigatório",
                minLength: { value: 11, message: "Mínimo 11 caracteres" },
                maxLength: { value: 18, message: "Máximo 18 caracteres" },
              })}
              className="w-full rounded bg-gray-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="12345678000190"
            />
            {errors.document && (
              <p className="mt-1 text-xs text-red-400">
                {errors.document.message}
              </p>
            )}
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="col-span-2 rounded bg-indigo-600 py-2 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50"
          >
            Cadastrar
          </button>
        </form>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Cedentes cadastrados</h2>
        {isLoading ? (
          <p className="text-sm text-gray-400">Carregando…</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-left text-xs uppercase text-gray-400">
                <tr>
                  <th className="px-4 py-2">Razão social</th>
                  <th className="px-4 py-2">CNPJ</th>
                </tr>
              </thead>
              <tbody>
                {(cedentes ?? []).map((c) => (
                  <tr key={c.id} className="border-t border-gray-800">
                    <td className="px-4 py-2">{c.name}</td>
                    <td className="px-4 py-2 font-mono text-xs">
                      {c.document}
                    </td>
                  </tr>
                ))}
                {cedentes?.length === 0 && (
                  <tr>
                    <td
                      colSpan={2}
                      className="px-4 py-6 text-center text-gray-500"
                    >
                      Nenhum cedente cadastrado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
