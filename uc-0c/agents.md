# agents.md — UC-0C Operational Guardrails

## Purpose
Ensure growth analysis is computed at the correct granularity and never hides data-quality issues or formula assumptions.

## Scope
- Input dataset: `../data/budget/ward_budget.csv`
- Output dataset: `growth_output.csv`
- Allowed analysis unit: **per-ward + per-category + per-period**

## Hard Enforcement Rules (MUST)
1. **No unintended aggregation**
   - Never aggregate across wards or categories unless explicitly instructed.
   - If a prompt asks for one overall growth number across all wards/categories, **refuse** and request explicit approval for aggregation.

2. **Null-first handling before computation**
   - Detect and report all rows where `actual_spend` is null before growth calculations.
   - For each null row, include: `period`, `ward`, `category`, and `notes` (null reason).
   - Do **not** compute growth for rows where current or required comparison value is null.

3. **Formula transparency on every output row**
   - Every computed row must include the formula string used (not just the numeric result).
   - Example MoM formula:
     - `((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100`

4. **No growth-type guessing**
   - If `--growth-type` is not provided, **refuse** and ask the user to specify it.
   - Never default silently to MoM, YoY, or any other type.

## Required Refusal Messages
Use clear, actionable refusals:

- Missing growth type:
  - `Refused: --growth-type is required. Please specify a growth type (e.g., MoM or YoY).`

- Unsafe aggregation request:
  - `Refused: Aggregating across wards/categories is disabled by UC-0C guardrails unless you explicitly authorize that aggregation scope.`

## Output Requirements
For each row in output table/file:
- `period`
- `ward`
- `category`
- `actual_spend`
- `growth_type`
- `formula`
- `growth_percent`
- `status` (`computed` | `flagged_null` | `not_computed`)
- `reason` (required when status != `computed`)

## Validation Checklist Before Returning Results
- Confirm results are filtered to exactly one `ward` and one `category` unless explicitly instructed otherwise.
- Confirm all null rows in scope are flagged with `notes` reason.
- Confirm every computed row includes `formula`.
- Confirm `--growth-type` was provided explicitly.

## Known UC-0C Reference Checks
- `Ward 1 – Kasba` + `Roads & Pothole Repair` + `2024-07` MoM should be approximately `+33.1%`.
- `Ward 1 – Kasba` + `Roads & Pothole Repair` + `2024-10` MoM should be approximately `-34.8%`.
- `Ward 2 – Shivajinagar` + `Drainage & Flooding` + `2024-03` must be flagged null.
- `Ward 4 – Warje` + `Roads & Pothole Repair` + `2024-07` must be flagged null.

## Naive Prompt Trap (must not happen)
For prompts like `Calculate growth from the data.`:
- Do not return a single all-ward/all-category number.
- Do not ignore nulls.
- Do not choose formula/growth-type implicitly.

## Commit Message Convention
`UC-0C Fix [failure mode]: [why it failed] → [what you changed]`
