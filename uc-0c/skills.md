# skills.md

skills:
  - name: load_dataset
    description: Integrates the source structured CSV payload, rigorously verifies expected schema columns, and transparently traps missing target variables before releasing data downstream.
    input: String file path pointing natively to the target budget CSV file.
    output: A cleansed and loaded structural data object representing the table, alongside an immediate structural anomaly report listing exactly which rows contained nulls and their justifications.
    error_handling: Actively combats silent filtering by capturing rows possessing deliberate null variables within `actual_spend` and forcing explicit inclusion of the metadata from the internal `notes` column prior to returning.

  - name: compute_growth
    description: Deploys exact period-over-period financial variance calculus targeting narrowly requested category blocks strictly within stated ward boundaries.
    input: Cleansed output structure from load_dataset along with specific isolated runtime mapping parameters (`ward`, `category`, and mandatory `growth_type`).
    output: A formatted tabular structure tracking each period's differential, structurally appending the explicitly declared mathematical formula (e.g. "Formula: MoM") to the output schema.
    error_handling: Triggers an immediate operational rejection ("REFUSE") if generalized across disparate wards or categories without explicit commands, or if an undefined missing `growth_type` is encountered.
