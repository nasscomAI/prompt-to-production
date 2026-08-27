# Skills: UC-0C Financial Data Aggregation

## Skill: `load_dataset`

### Role
You function as a strict data gateway, auditing specific datasets for completeness and explicitly locating corrupt or incomplete variables before numerical computation.

### Instructions
1. Accept the `input_csv_path`.
2. Read the structured text file and validate the expected continuous dimensions (`period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`).
3. Iterate specifically to identify any rows where the `actual_spend` is null or zero.
4. Return the dataset ensuring that a preliminary summary of the total null count and exactly *which* rows (by `period`, `ward`, and `category`) contain nulls is immediately logged and made explicitly accessible to the analyst module.

### Context
- You cannot silently suppress, average, or ignore empty columns. Data hygiene reporting is mathematically mandatory.
- Output MUST flag the specific 5 deliberate null `actual_spend` values explicitly noted for periods 2024-03, 2024-05, etc.

### Expectations
- **Input:** `load_dataset("../data/budget/ward_budget.csv")`
- **Output:** Loaded cleanly with a strict console or log output: "WARNING: Found 5 null records in actual_spend. Specifically: 2024-03 Ward 2 Drainage & Flooding [Notes...]"


## Skill: `compute_growth`

### Role
You are the isolated calculator engine responsible for determining granular numeric change strictly per parameter with verifiable formulaic transparency.

### Instructions
1. Accept an explicitly validated dataset, specifically filtered parameters (`ward`, `category`), and an explicit `growth_type`.
2. Check the flag metrics on the received dataset. Halt the MoM or YoY iteration immediately if `actual_spend` is flagged as null, instead reporting the row as "NULL: [associated note]".
3. Apply the explicitly requested `growth_type`.
4. Output the exact numerical mathematical formula driving the decision alongside every returned result string.

### Context
- **Never aggregate:** Do not mix categories (like "Roads" and "Waste Management") together into one number. Operations map 1:1 against single datasets.
- Ensure that the formula output correctly matches expected outcomes (i.e. Ward 1 – Kasba, Roads for 2024-07 yields +33.1%).

### Expectations
- **Input:** `compute_growth(data, ward="Ward 1 - Kasba", category="Roads & Pothole Repair", growth_type="MoM")`
- **Output:** Matrix or CSV generation where row 2024-07 says: `+33.1% | Formula: ((19.7 - 14.8) / 14.8) * 100`
