# Agent Enforcement Rules — UC-0C (Number That Looks Right)

These rules enforce correct, transparent, and non-misleading computation of growth metrics on the civic budget dataset.

---

## 1. Aggregation Control

- The system MUST operate on exactly one `ward` and one `category`.
- The system MUST NOT aggregate across multiple wards or categories under any condition.
- If input implies combined analysis (e.g., "overall", "all wards"), the system MUST REFUSE with an explicit error.

---

## 2. Null Handling

- The system MUST detect all null values in `actual_spend` BEFORE computation.
- The system MUST NOT compute growth if:
  - current value is null
  - previous value is null
- All null rows MUST:
  - be included in output
  - be flagged using `null_flag = TRUE`
  - include null reason from `notes` column
- Silent skipping of null rows is strictly prohibited.

---

## 3. Input Validation

- The following inputs are REQUIRED:
  - `ward`
  - `category`
  - `growth_type`
- The system MUST REFUSE if:
  - any input is missing
  - inputs are ambiguous (e.g., "overall", "all", "any category")
- Validation MUST occur before any dataset processing.

---

## 4. Growth Type Enforcement

- Only the following values are allowed:
  - `MoM`
  - `YoY`
- If `growth_type` is not provided or invalid → the system MUST REFUSE.
- The system MUST NOT assume or default to any growth type.

---

## 5. Output Requirements

- Output MUST be a per-period table (no aggregation).
- Each row MUST include:
  - period
  - ward
  - category
  - actual_spend
  - previous_spend
  - growth_percentage
  - formula_used
  - null_flag
- Each computed row MUST include the exact formula used.

---

## 6. No Silent Behavior

- The system MUST NOT:
  - silently skip null values
  - make hidden assumptions
  - fabricate or infer missing data
- All decisions MUST be explicit and traceable in output.

---

## 7. Error Handling

- All invalid scenarios MUST:
  - raise clear, explicit error messages
  - stop execution safely
- The system MUST fail clearly rather than produce misleading or partial output.

---