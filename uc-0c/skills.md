skills:

## 1) name: load_dataset
  - description: Loads and validates the budget dataset and identifies null values.
  - input: File path to CSV dataset
  - output: Pandas DataFrame with validated columns
  - error_handling: Raises error if required columns are missing; prints null rows for visibility

## 2) name: compute_growth
  - description: Computes period-wise growth for a specific ward and category with formula transparency.
  - input: DataFrame, ward (string), category (string), growth_type (string)
  - output: DataFrame with period, actual_spend, growth, formula, and flag
  - error_handling: Skips null values, flags them, avoids invalid calculations, raises error if growth_type missing or unsupported
