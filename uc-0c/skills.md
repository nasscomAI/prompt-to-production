# skills.md

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate required columns, and identify NULL values before analysis.
    input:
      type: CSV
      format: ward_budget.csv
    output:
      type: validated_dataset
      format: In-memory table with validation report
    error_handling: >
      Refuse processing if required columns are missing, the file is unreadable,
      or NULL rows cannot be identified. Report all NULL rows and their notes.

  - name: compute_growth
    description: Compute growth for one ward and one category using the requested growth type.
    input:
      type: validated_dataset
      format: Single ward, single category, growth_type
    output:
      type: CSV
      format: Per-period growth table including formula and status
    error_handling: >
      Refuse requests without a growth type or those spanning multiple wards or
      categories. Mark rows with NULL values as NOT COMPUTED instead of guessing.
