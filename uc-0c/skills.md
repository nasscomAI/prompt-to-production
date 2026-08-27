skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, and flags rows with null or missing actual spend values.
    input: File path to the dataset.
    output: A structured dataset, along with a report detailing the count of null values and the specific rows and reasons containing them based on the notes column.
    error_handling: Throws an error if required columns are missing or if the file cannot be read. Ensures null rows are properly documented before returning data.

  - name: compute_growth
    description: Calculates precise growth metrics (e.g., MoM) for a specific ward and category, refusing to extrapolate or assume missing values.
    input: Target ward name, target category name, and the specific growth type to calculate (e.g., MoM).
    output: A per-period table showing calculated growth along with the explicitly stated mathematical formula used for each row's calculation.
    error_handling: Refuses calculation across aggregated wards/categories. Refuses calculation if growth type is not explicitly specified. Refuses to compute values for null rows, instead flagging them.
