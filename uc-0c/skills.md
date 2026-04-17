skills:
  - name: load_dataset
    description: Reads the raw CSV budget data, structurally validating columns while producing a preliminary log locating and counting deliberate null occurrence rows.
    input: The filesystem path string pointing to the targeted `.csv` source.
    output: Returns parsed dictionary rows mapped alongside a system report summarizing any null `actual_spend` observations.
    error_handling: Return a rigid error if required dataset headers are corrupted or entirely absent.

  - name: compute_growth
    description: Restricts calculation dynamically to single paired ward/category parameters mapping the designated growth period sequentially per row (with displayed formula logic).
    input: Parameters containing explicit `ward`, `category`, and verified `growth_type`.
    output: Returns a structured per-period analytical table retaining contextual records and flagged formulas safely attached to the values.
    error_handling: Systematically stops analysis natively refusing response if `growth_type` was omitted or an aggregation query violated single-ward resolution.
