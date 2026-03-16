# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports the count and specific rows containing null 'actual_spend' values.
    input: File path string to the CSV dataset.
    output: A list of dictionaries representing the rows, along with a warning log of all rows with null actual_spend and their notes.
    error_handling: Return refusal/error if the file is missing or if mandatory columns are not present.

  - name: compute_growth
    description: Takes the dataset, ward, category, and growth_type to compute the per-period growth table safely, documenting formulas and handling nulls.
    input: Dataset list, ward string, category string, and growth_type string.
    output: A structured table (list of dicts or CSV string) containing Period, Actual Spend, Formula Used, and the computed Growth percentage or a flagged error.
    error_handling: Refuse execution if growth_type is missing/invalid. Refuse execution if ward or category is "Any" or unspecified (to prevent unauthorized aggregation). Flag computations as NULL with the provided note if math involves a null row.
