skills:
  - name: load_dataset
    description: Robustly reads a provided CSV file, validating required columns, reporting the total null count, and capturing rows containing missing `actual_spend` data before returning the validated dataset.
    input: File path to the `.csv` budget dataset.
    output: Structured list of dictionary rows representing the dataset, with metadata about null distributions.
    error_handling: Throws descriptive errors if required columns (`period`, `ward`, `category`, `actual_spend`, `notes`) are missing, or if file cannot be read.

  - name: compute_growth
    description: Filters dataset for explicitly provided `ward` and `category`, computes period-over-period `growth-type` (e.g., MoM), handles missing nulls accurately according to RICE, and attaches explicit formula derivations.
    input: Dataset (list of dicts), `ward`, `category`, and `growth_type`.
    output: Returns a processed list of dictionaries forming the final output table schema for CSV writing.
    error_handling: Refuses via exception if missing explicit arguments, computing aggregations, or encountering unhandled growth-types.
