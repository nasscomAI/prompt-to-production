# Budget Growth Skills

- `load_dataset`
  - Input: path to CSV file.
  - Output: validates columns, reports null count and identifies which rows have nulls before returning the data.
- `compute_growth`
  - Input: dataset, ward, category, growth_type.
  - Output: per-period table showing actual spend, computed growth, and the formula used. If scope is not single ward/category, it refuses.
