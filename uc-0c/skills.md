skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates the presence of required columns, and reports the null count and specific rows before returning the data.
    input: File path to the .csv budget file.
    output: A structured object containing the dataset and metadata about which rows contain NULL actual_spend values.
    error_handling: Throws an exception if the file is inaccessible or missing required columns like 'ward', 'category', or 'actual_spend'.

  - name: compute_growth
    description: Takes a specifically requested ward, category, and growth_type, and calculates the per-period budget growth.
    input: The dataset object, target ward, target category, and the defined growth type.
    output: A tabular result listing the growth calculation with the applied explicit formula shown per period.
    error_handling: Refuses to compute and returns an explicit warning if the ward/category request attempts combining data, if the growth_type is missing, or if actual_spends are null (in which case it outputs the note instead of a number).
