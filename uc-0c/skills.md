skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, and reports the total null count and exact row identifiers of any null actual_spend values before returning the dataset.
    input:
      type: file_path
      format: String path to a CSV file expected to contain columns — period (YYYY-MM), ward (string), category (string), budgeted_amount (float), actual_spend (float or blank), notes (string)
    output:
      type: structured_report
      format: Object containing (1) validated dataframe of all rows, (2) null_count integer, (3) null_rows list of objects each with period, ward, category, and notes explaining the null reason
    error_handling:
      missing_file: Raise a FileNotFoundError with the attempted path; do not proceed.
      missing_columns: Raise a ValidationError listing every absent column; do not return partial data.
      wrong_column_types: Report the column name and observed type, flag the anomaly, and halt before returning data.
      no_nulls_found: Return null_count of 0 and an empty null_rows list; do not silently omit the null report section.
      ambiguous_path: Refuse to guess; return an error asking the caller to supply an explicit, unambiguous file path.

  - name: compute_growth
    description: Accepts an explicit ward, category, and growth_type, then returns a per-period table showing each period's actual_spend, the computed growth value, and the exact formula applied, while refusing to aggregate across wards or categories and flagging every null row instead of computing a value for it.
    input:
      type: parameters
      format: Object with three required fields — ward (string, must match one of the 5 known ward names exactly), category (string, must match one of the 5 known category names exactly), growth_type (enum: MoM | YoY); all three fields are mandatory
    output:
      type: table
      format: CSV-compatible row set with columns — period, ward, category, actual_spend, growth_value, formula, null_flag (boolean), null_reason (string from notes column when null_flag is true, empty otherwise)
    error_handling:
      missing_growth_type: Refuse to compute; return an error message asking the caller to explicitly specify MoM or YoY — never default or guess.
      null_actual_spend: Do not compute a growth value for that period; set null_flag to true and populate null_reason from the notes column; continue processing non-null rows.
      aggregation_requested: Refuse the request entirely and return an explicit error stating that cross-ward or cross-category aggregation is not permitted unless explicitly instructed by a qualified operator.
      unrecognized_ward_or_category: Refuse to proceed; return an error listing the unrecognized value and the set of valid options — do not fuzzy-match silently.
      single_number_output_attempted: Treat as an aggregation violation; refuse and return the same cross-aggregation error.