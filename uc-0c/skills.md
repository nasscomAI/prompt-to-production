# skills.md

skills:
  - name: load_dataset
    description: Parses and validates the structural integrity of the input CSV budget data before usage.
    input: CSV filepath.
    output: A validated, loaded dataset array or dictionary, along with a tally and report of all 'null' or defective rows inherently present.
    error_handling: Halts if headers are mangled. Discovers and reports the exact count of nulls in actual_spend without crashing.

  - name: compute_growth
    description: Executes the mathematical generation of a per-period aggregated growth table, provided isolated scopes are targeted.
    input: Validated dataset rows filtered expressly by `ward`, `category`, and the target `growth_type`.
    output: Per-period tabular data displaying `period`, `actual_spend`, `growth`, and critically, the `formula` alongside explanatory `notes`.
    error_handling: Refuses calculation mathematically if ward/category/growth_type are omitted, missing, or cross-polluted across different sectors.
