import { apiClient } from "./client";
import type { Cedente, CedenteCreate } from "../types/api";

export async function listCedentes(): Promise<Cedente[]> {
  const { data } = await apiClient.get<Cedente[]>("/api/v1/cedentes");
  return data;
}

export async function createCedente(payload: CedenteCreate): Promise<Cedente> {
  const { data } = await apiClient.post<Cedente>("/api/v1/cedentes", payload);
  return data;
}
