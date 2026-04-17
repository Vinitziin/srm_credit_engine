import { useQuery } from "@tanstack/react-query";
import { simulate } from "../api/simulate";
import type { SimulateRequest } from "../types/api";

export function useSimulate(payload: SimulateRequest | null) {
  return useQuery({
    queryKey: ["simulate", payload],
    queryFn: () => simulate(payload!),
    enabled: payload !== null,
    retry: false,
    staleTime: 0,
  });
}
