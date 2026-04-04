# skills.md

skills:
  - name: load_dataset
    description: Reads the financial CSV file, structurally validates the expected columns, and strictly reports the count of nulls along with their verbatim reasoning.
    input: A string representing the file path strictly leading to the targeted budget CSV dataset.
    output: The structured dataset object accompanied by a strict preemptive diagnostic report dictating all null rows utilizing their corresponding texts in the 'notes' column.
    error_handling: Throws an immediate structural error if core column dependencies (like ward, category, period, actual_spend) are absent from the dataset.

  - name: compute_growth
    description: Receives explicit granular parameters (ward + category + growth_type) to return per-period growth calculations showing transparent mathematical formulas.
    input: The validated dataset explicitly paired with string definitions for 'ward', 'category', and a strict methodology definition for 'growth_type'.
    output: A per-period breakdown table rendering calculated metrics concurrently presenting the exact baseline mathematical formula used alongside clearly flagged 'NULL' entries.
    error_handling: Automatically halts and enforces a refusal state if requested metrics imply organic multi-ward/multi-category aggregation, or if the exact growth architecture (e.g., MoM/YoY) is withheld rather than silently guessing variations.
