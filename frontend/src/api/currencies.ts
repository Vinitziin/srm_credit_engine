import { apiClient } from "./client";
import type { Currency, ReceivableType } from "../types/api";

export async function listCurrencies(): Promise<Currency[]> {
  const { data } = await apiClient.get<Currency[]>("/api/v1/currencies");
  return data;
}

export async function listReceivableTypes(): Promise<ReceivableType[]> {
  const { data } = await apiClient.get<ReceivableType[]>(
    "/api/v1/receivable-types",
  );
  return data;
}
