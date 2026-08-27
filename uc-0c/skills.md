# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count along with which rows contain nulls before returning.
    input: File path to the budget CSV document.
    output: A structured dataset mapping rows with warnings for any null `actual_spend` values.
    error_handling: Return a critical warning detailing the null reasons from the notes column if nulls are found.

  - name: compute_growth
    description: Takes ward, category, and growth_type to return a per-period calculation table.
    input: Requested ward string, category string, and growth type (e.g., MoM).
    output: A per-period table showing the growth result alongside the exact formula used.
    error_handling: Refuse to compute (throw error) if growth_type is missing or if aggregating across wards/categories is requested.
