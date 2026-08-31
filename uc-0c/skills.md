# Skills

## load_dataset

**Purpose**: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows with their reasons from the notes column before returning filtered data.

**Input**: CSV file path (expected: `../data/budget/ward_budget.csv`)

**Behavior**:
1. Read CSV with columns: period, ward, category, budgeted_amount, actual_spend, notes
2. Validate all 6 columns exist
3. Identify all rows where actual_spend is null/blank
4. Report null count and list each null row with: period, ward, category, and notes (the reason)
5. Return the full DataFrame for downstream filtering

**Output**: DataFrame with all rows; null report printed to stdout before return

**Refusal**: If required columns missing, refuse and list missing columns.

---

## compute_growth

**Purpose**: Computes per-period growth (MoM or YoY) for a single ward + category combination. Returns a per-period table with the formula shown in every output row.

**Input**:
- DataFrame from load_dataset
- ward: string (exact match, e.g., "Ward 1 – Kasba")
- category: string (exact match, e.g., "Roads & Pothole Repair")
- growth_type: "MoM" or "YoY" (must be explicitly provided)

**Behavior**:
1. Filter DataFrame to exact ward + category match
2. Sort by period ascending
3. Flag any null actual_spend rows in this subset — report period and notes reason; do NOT compute growth for these rows
4. For each non-null row with a valid prior period (MoM: previous month; YoY: same month prior year):
   - Compute growth: (current - prior) / prior * 100
   - Output row with: period, actual_spend, growth_pct, formula
   - Formula format: `((current - prior) / prior) * 100 = X.X%`
5. First period (no prior) outputs: period, actual_spend, growth_pct: "N/A (baseline)", formula: "N/A — baseline period"

**Output**: Per-period table (CSV rows) with columns: period, actual_spend, growth_pct, formula

**Refusal**: 
- If growth_type not provided — refuse and ask, never guess
- If ward/category not found in data — refuse and list available values