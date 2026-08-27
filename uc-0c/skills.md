
# Skills

## load_dataset

### Description
Load and validate the ward-level budget dataset with full structural and null awareness.

### Inputs
- file_path (string): Path to CSV file

### Validation Rules
- CSV must contain the following columns:
  - period
  - ward
  - category
  - budgeted_amount
  - actual_spend
  - notes
- period must follow YYYY-MM format
- budgeted_amount must be present in all rows

### Behaviour
- Read dataset from disk
- Verify schema and expected dimensions
- Identify every row where `actual_spend` is NULL
- Report:
  - Total row count
  - List of wards
  - List of categories
  - Count of null actual_spend rows
  - Exact row identifiers (period, ward, category) with nulls
  - Corresponding notes explanations

### Output
- Validated dataset object
- Structured report describing all detected nulls

---

## compute_growth

### Description
Compute growth metrics safely for a **single ward and single category**.

### Inputs
- dataset (validated output of load_dataset)
- ward (string)
- category (string)
- growth_type (string: MoM or YoY)

### Preconditions
- Ward must exist in dataset
- Category must exist in dataset
- growth_type must be explicitly provided
- Dataset must already have been null-audited

### Behaviour
- Filter data strictly to the specified ward + category
- Sort periods chronologically
- For each period:
  - If actual_spend is NULL:
    - Mark row as FLAGGED
    - Include null reason from notes
    - Do not compute growth
  - Else:
    - Compute growth according to growth_type
    - Attach explicit formula string to result

### Formula Disclosure
Every computed value must include its formula, e.g.:
- MoM: `(Actual_t − Actual_(t−1)) / Actual_(t−1)`
- YoY: `(Actual_t − Actual_(t−12)) / Actual_(t−12)`

### Output
A table where each row contains:
- Period
- Ward
- Category
- Actual Spend (₹ lakh or NULL)
- Growth Value or FLAGGED
- Formula Used or Flag Reason

### Refusal Conditions
- Aggregate growth requested
- growth_type missing
- ward or category unspecified
- Attempt to compute across null rows without flagging
