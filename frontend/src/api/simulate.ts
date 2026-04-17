import { apiClient } from "./client";
import type { SimulateRequest, SimulateResponse } from "../types/api";

export async function simulate(
  payload: SimulateRequest,
): Promise<SimulateResponse> {
  const { data } = await apiClient.post<SimulateResponse>(
    "/api/v1/simulate",
    payload,
  );
  return data;
}
