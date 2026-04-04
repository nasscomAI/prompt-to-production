- name: load_dataset
  description: Reads the municipal budget CSV file, validates column integrity, and identifies all null 'actual_spend' entries to prevent silent data gaps.
  input: String representing the absolute path to 'ward_budget.csv'.
  output: List of Objects containing validated budget data, with null 'actual_spend' rows explicitly flagged for review.
  error_handling: Prevents 'Silent null handling' by identifying the 5 mandated null values (Shivajinagar, Warje, Kasba, Kothrud, Hadapsar) and extracting their 'notes' column justifications; raises a fatal error if the CSV is missing or malformed.

- name: compute_growth
  description: Performs granular MoM or YoY budget growth calculations for a specific ward and category while explicitly disclosing the mathematical formula used.
  input: Object containing 'ward' (String), 'category' (String), 'growth_type' ('MoM' or 'YoY' String), and the validated dataset.
  output: List of Objects representing a per-period growth table, each including the result and the specific formula applied.
  error_handling: Rejects any request for 'Wrong aggregation level' (e.g., cross-ward or cross-category analysis); fails if 'growth_type' is not provided ('Formula assumption'); skips calculation for null-flagged rows and inserts the corresponding 'notes' justification into the output instead.
