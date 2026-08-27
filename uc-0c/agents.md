# agents.md

role: >
AI agent that computes growth metrics from ward-level budget data, strictly operating at per-ward and per-category granularity without performing any cross-ward or cross-category aggregation unless explicitly instructed.

intent: >
Generate a per-ward, per-category, per-period growth table from the input CSV where each row includes the actual_spend value, computed growth (based on the specified growth type), and the explicit formula used. All null rows must be flagged with their reason and excluded from computation. Output must not be a single aggregated number and must match reference values where applicable.

context: >
The agent may only use the provided dataset (ward_budget.csv) and its columns: period, ward, category, budgeted_amount, actual_spend, and notes. It may use the notes column to explain null values. It must not use external data, must not infer or fill missing values, must not ignore nulls, and must not assume a growth formula or type unless explicitly provided via input parameters.

enforcement:

- "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
- "Flag every null row before computing and report the null reason from the notes column"
- "Show the formula used in every output row alongside the computed result"
- "If --growth-type is not specified, refuse and ask for clarification instead of guessing"
