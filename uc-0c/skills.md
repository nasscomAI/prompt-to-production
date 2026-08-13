# skills.md — UC-0C Budget Growth Analyzer

## Skill 1: `load_dataset`
**Purpose**: Load the budget dataset, validate columns, and report null values.

**Input**: Path to the budget CSV file (e.g., `../data/budget/ward_budget.csv`).

**Output**: A cleaned DataFrame with null values flagged and reported.

**Rules**:
- Validate that all required columns are present.
- Report the count and rows of null `actual_spend` values.

---

## Skill 2: `compute_growth`
**Purpose**: Compute growth metrics for a specific ward and category.

**Input**:
- Cleaned dataset (output of `load_dataset`).
- Ward name (e.g., `"Ward 1 – Kasba"`).
- Category name (e.g., `"Roads & Pothole Repair"`).
- Growth type (e.g., `"MoM"`).

**Output**: A DataFrame with columns: `period`, `ward`, `category`, `actual_spend`, `growth_pct`, `formula`, and `flag`.

**Rules**:
- Compute growth only at the **per-ward per-category** level.
- Flag null values and explain why growth was not computed.
- Show the formula used for each row.