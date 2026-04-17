import { useQuery } from "@tanstack/react-query";
import { listStatements } from "../api/statements";
import type { StatementFilters } from "../types/api";

export function useStatements(filters: StatementFilters) {
  return useQuery({
    queryKey: ["statements", filters],
    queryFn: () => listStatements(filters),
    placeholderData: (previous) => previous,
  });
}
