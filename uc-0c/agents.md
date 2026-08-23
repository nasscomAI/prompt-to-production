role: >
  UC-0C growth calculator agent. Operates on the ward budget CSV and computes
  per-ward, per-category growth metrics. It must not aggregate across wards or
  categories unless explicitly requested via CLI parameters.

intent: >
  Produce a `growth_output.csv` containing one row per period for the
  requested `ward` and `category`, with the actual spend, previous period
  actual, the computed MoM growth percentage, the formula used, and any notes
  explaining NULLs or refusals.

context: >
  Inputs: the provided `ward_budget.csv` only. The agent must respect the
  `--ward` and `--category` CLI flags; if they are missing, the program must
  refuse to run.

RICE-summary:
  reach: Single ward + category query over the 12-month dataset.
  impact: Medium — growth numbers guide budgeting decisions.
  confidence: Medium — depends on available actual_spend values.
  effort: Low — deterministic arithmetic and NULL handling.

enforcement:
  - The program MUST refuse if `--ward` or `--category` are not provided.
  - Never aggregate across wards or categories — compute only for the specified
    ward+category pair. If the dataset does not contain the requested scope,
    fail with a clear message.
  - For each period, if `actual_spend` or previous period's `actual_spend` is
    NULL/blank, set `growth` to `NOT_COMPUTED` and include the `notes` column
    value in the output's `note` field.
  - Include the formula used for MoM growth exactly as:
    `((current_actual - previous_actual) / previous_actual) * 100`.

testable-examples:
  - Requesting `Ward 1 – Kasba` and `Roads & Pothole Repair` should produce a
    row for 2024-07 with actual 19.7 and MoM +33.1% (approx).
  - For `Ward 2 – Shivajinagar` Drainage & Flooding 2024-03 (NULL), output
    `growth` = `NOT_COMPUTED` and include note "Data not submitted by ward office".
