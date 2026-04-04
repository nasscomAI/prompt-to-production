# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: File path (string) to the civic budget CSV document.
    output: Structured dataset and a strict pre-computation report summarizing total nulls and specific rows affected.
    error_handling: System should halt calculations if the schema is corrupted or file reading fails. 

  - name: compute_growth
    description: Takes ward, category, and growth_type, returning a per-period table with formulas shown explicitly.
    input: Structured data array/list output by `load_dataset`, along with `ward`, `category`, and `growth_type` arguments.
    output: Table/CSV string mapping the requested growth calculations alongside the exact mathematical formula used per row.
    error_handling: Refuse execution if `--growth-type` is requested implicitly or missing. Do not compute on null 'actual_spend' values; instead, flag them alongside their accompanying 'notes' column.
