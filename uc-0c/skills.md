skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, counts nulls, and returns rows with null metadata.
    input:
      type: object
      format: "{ input_csv_path: string }"
    output:
      type: object
      format: "{ rows: Array<object>, null_count: integer, null_rows: Array<object> }"
    error_handling: >
      If the input file is missing or unreadable, raise an error; if required columns are missing, terminate with a clear validation message; if null rows are present, include them in `null_rows` with their notes.

  - name: compute_growth
    description: Takes ward, category, and growth type, then computes a per-period growth table while preserving null rows and citing the calculation formula.
    input:
      type: object
      format: "{ rows: Array<object>, ward: string, category: string, growth_type: string }"
    output:
      type: object
      format: "{ results: Array<{ period: string, actual_spend: string, growth: string, formula: string, notes: string }> }"
    error_handling: >
      If `ward`, `category`, or `growth_type` is missing, refuse and indicate the required parameter; if the selected ward/category contains null rows, flag them and include the `notes` reason; if the dataset is empty for the selection, return an empty results list with an explanatory message.
