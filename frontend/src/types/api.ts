export interface Currency {
  id: string;
  code: string;
  name: string;
}

export interface ReceivableType {
  id: string;
  name: string;
  spread_rate: string;
}

export interface Cedente {
  id: string;
  name: string;
  document: string;
}

export interface CedenteCreate {
  name: string;
  document: string;
}

export interface SimulateRequest {
  face_value: string;
  base_rate: string;
  term_months: number;
  receivable_type: string;
  currency_code: string;
  payment_currency_code: string;
}

export interface SimulateResponse {
  face_value: string;
  present_value: string;
  base_rate: string;
  spread_applied: string;
  term_months: number;
  currency_code: string;
  payment_currency_code: string;
  exchange_rate_used: string | null;
  present_value_in_payment_currency: string;
}

export interface TransactionCreate extends SimulateRequest {
  cedente_id: string;
}

export interface Transaction {
  id: string;
  cedente_id: string;
  receivable_type_id: string;
  face_value: string;
  present_value: string;
  currency_id: string;
  payment_currency_id: string;
  exchange_rate_used: string | null;
  term_months: number;
  base_rate: string;
  spread_applied: string;
  status: string;
  version: number;
  created_at: string;
}

export interface StatementItem {
  id: string;
  created_at: string;
  cedente_name: string;
  cedente_document: string;
  receivable_type: string;
  face_value: string;
  present_value: string;
  currency_code: string;
  payment_currency_code: string;
  exchange_rate_used: string | null;
  status: string;
}

export interface StatementPage {
  page: number;
  page_size: number;
  total: number;
  items: StatementItem[];
}

export interface StatementFilters {
  date_from?: string;
  date_to?: string;
  cedente_id?: string;
  currency_code?: string;
  status?: string;
  page: number;
  page_size: number;
}
