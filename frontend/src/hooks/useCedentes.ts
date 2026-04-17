import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createCedente, listCedentes } from "../api/cedentes";
import type { CedenteCreate } from "../types/api";

export function useCedentes() {
  return useQuery({
    queryKey: ["cedentes"],
    queryFn: listCedentes,
  });
}

export function useCreateCedente() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CedenteCreate) => createCedente(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cedentes"] });
    },
  });
}
