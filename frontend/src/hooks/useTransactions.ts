import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createTransaction,
  updateTransactionStatus,
} from "../api/transactions";
import type { TransactionCreate } from "../types/api";

export function useCreateTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: TransactionCreate) => createTransaction(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["statements"] });
    },
  });
}

export function useUpdateTxStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      status,
      version,
    }: {
      id: string;
      status: string;
      version: number;
    }) => updateTransactionStatus(id, status, version),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["statements"] });
    },
  });
}
