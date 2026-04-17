import { useQuery } from "@tanstack/react-query";
import { listCurrencies, listReceivableTypes } from "../api/currencies";

export function useCurrencies() {
  return useQuery({
    queryKey: ["currencies"],
    queryFn: listCurrencies,
    staleTime: 1000 * 60 * 5,
  });
}

export function useReceivableTypes() {
  return useQuery({
    queryKey: ["receivable-types"],
    queryFn: listReceivableTypes,
    staleTime: 1000 * 60 * 5,
  });
}
