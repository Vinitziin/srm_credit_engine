import { apiClient } from "./client";
import type { StatementFilters, StatementPage } from "../types/api";

export async function listStatements(
  filters: StatementFilters,
): Promise<StatementPage> {
  const params: Record<string, string | number> = {
    page: filters.page,
    page_size: filters.page_size,
  };
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.cedente_id) params.cedente_id = filters.cedente_id;
  if (filters.currency_code) params.currency_code = filters.currency_code;
  if (filters.status) params.status = filters.status;

  const { data } = await apiClient.get<StatementPage>(
    "/api/v1/reports/statements",
    { params },
  );
  return data;
}
