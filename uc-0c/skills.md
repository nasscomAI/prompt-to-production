skills:
  - name: load_dataset
    description: Reads the CSV, validates columns, and immediately reports any null actual_spends found before returning data.
    input: File path to the budget CSV.
    output: A validated list of dictionaries representing budget rows.
    error_handling: Throws an explicit error if critical columns are missing or unreadable.

  - name: compute_growth
    description: Takes specific ward and category filters, computes period-over-period growth, safely handles null breaks, and produces an explicit calculation table.
    input: Validated dataset rows, ward string, category string, growth type string.
    output: A structured table containing growth results, explicit formulas, and explicit null flags.
    error_handling: Refuses to execute if ward, category, or growth_type are undefined or "All".
