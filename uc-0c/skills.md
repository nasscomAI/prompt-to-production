skills:
  - name: load_dataset
    description: >
      Reads a CSV budget file, validates columns, maps missing values natively, 
      and explicitly reports total null count including which specific rows contain them before proceeding.
    input: >
      Path to `.csv` dataset.
    output: >
      A structured dictionary of dataset records, alongside a metadata report summarizing detected anomalies (null values).
    error_handling: >
      If corrupted or unreachable, return a clear parse exception detailing why the frame could not load.

  - name: compute_growth
    description: >
      Evaluates growth figures strictly on an isolated Ward + Category subset, enforcing formula transparency and null preservation.
    input: >
      A subset of dataset records, a growth strategy parameter (e.g., 'MoM'), Ward constraint, and Category constraint.
    output: >
      A per-period list/table appending formula syntax and explicitly leaving nulls uncomputed.
    error_handling: >
      If Ward or Category covers multiple distinct values, actively refuse calculation.
      If a requested period references a null 'actual_spend', inject a flagged fallback string representing 
      the missing reason instead of silently dropping the calculation.
      If growth_type is missing, return a validation refusal error.
