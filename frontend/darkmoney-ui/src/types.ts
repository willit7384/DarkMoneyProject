// ===== Core domain types for DarkMoneyProject =====

// ---------- Organizations ----------
export interface Organization {
  ein: string
  name: string
  city?: string | null
  state?: string | null
  ruling_year?: number | null
  ntee_code?: string | null
}

// ---------- IRS Filings (990 / 990-PF) ----------
export interface Filing {
  ein: string
  organization: string
  tax_year: number
  form_type: "990" | "990EZ" | "990PF" | string
  total_revenue?: number | null
  admin_expense?: number | null
  source_file?: string
}

// ---------- Grants ----------
export interface Grant {
  source_ein: string
  source_org: string
  target_org: string
  amount: number
  tax_year: number
  purpose?: string | null
}

// ---------- Officers / Directors ----------
export interface Officer {
  ein: string
  organization: string
  name: string
  title?: string | null
  compensation?: number | null
  tax_year: number
}

// ---------- Graph edges (for network viz later) ----------
export interface GrantEdge {
  source: string
  target: string
  weight: number
  year: number
  purpose?: string | null
}
