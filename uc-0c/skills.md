# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path to the dataset CSV file (string)
    output: Validated dataset table, and a report detailing count and reason for null rows
    error_handling: Halts if required columns are missing, or warns if unreadable format

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Ward (string), Category (string), and Growth Type (string, e.g. MoM)
    output: A per-period table displaying actual spend, calculated growth, and the formula used
    error_handling: Refuses to calculate if growth-type missing, or marks row as flagged if actual_spend is null
