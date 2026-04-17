import { apiClient } from "./client";
import type { Transaction, TransactionCreate } from "../types/api";

export async function createTransaction(
  payload: TransactionCreate,
): Promise<Transaction> {
  const { data } = await apiClient.post<Transaction>(
    "/api/v1/transactions",
    payload,
  );
  return data;
}

export async function getTransaction(id: string): Promise<Transaction> {
  const { data } = await apiClient.get<Transaction>(
    `/api/v1/transactions/${id}`,
  );
  return data;
}

export async function updateTransactionStatus(
  id: string,
  status: string,
  version: number,
): Promise<Transaction> {
  const { data } = await apiClient.patch<Transaction>(
    `/api/v1/transactions/${id}/status`,
    { status, version },
  );
  return data;
}
