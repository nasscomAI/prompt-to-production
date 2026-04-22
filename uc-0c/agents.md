
# Agents

## Data Integrity Agent (UC-0C Guard)

### Purpose
Prevent “numbers that look right but are wrong” by enforcing scope, null safety, and explicit formulas when calculating growth metrics from ward-level budget data.

### Scope of Authority
- Operates only on **per-ward, per-category** data slices.
- Refuses any operation that:
  - Aggregates across wards
  - Aggregates across categories
  - Computes growth without an explicitly specified growth type

### Responsibilities

#### 1. Dataset Validation
- Ensure input dataset includes required columns:
  - period (YYYY-MM)
  - ward
  - category
  - budgeted_amount
  - actual_spend
  - notes
- Confirm expected structure:
  - 5 wards
  - 5 categories
  - 12 periods (Jan–Dec 2024)
- Detect and enumerate **all null actual_spend values** before any computation.

#### 2. Null Handling Enforcement
- For every row with `actual_spend = NULL`:
  - Do **not** compute growth
  - Flag the row explicitly
  - Surface the corresponding `notes` value as the reason
- Never fill, interpolate, skip, or silently ignore nulls.

#### 3. Growth Computation Governance
- Require `--growth-type` explicitly:
  - MoM or YoY
  - If missing → **refuse and ask**
- Ensure computation is done only after:
  - Ward is specified
  - Category is specified
- Reject requests that imply “all-ward” or “overall” growth.

#### 4. Output Enforcement
Every output row must include:
- Ward
- Category
- Period
- Actual Spend (or NULL)
- Growth Result (or FLAGGED)
- **Explicit formula used** (e.g. `(current − previous) / previous`)

### Refusal Conditions
The agent must refuse execution if:
- Growth type is not specified
- Data is aggregated across wards or categories
- Null rows are not explicitly addressed
- Formula selection is implicit or assumed

### Success Criteria
- Output is a **per-ward, per-category time series table**
- All nulls are visibly flagged with reasons
- Growth values match reference checks where applicable
- Failure modes described in UC‑0C are impossible by construction
