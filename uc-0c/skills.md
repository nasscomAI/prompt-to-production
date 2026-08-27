# Budget Analysis Skills

- `load_dataset(file_path: str) -> list`: Loads the CSV budget data, validates the presence of required columns (period, ward, category, budgeted_amount, actual_spend), and identifies/reports the count and locations of null `actual_spend` values.
- `compute_growth(data: list, ward: str, category: str, growth_type: str) -> list`: Performs period-over-period growth calculations based on the specified `growth_type` (e.g., 'MoM'). It returns a table including the original data, the calculated growth, and the formula used. It explicitly flags null rows with the reason from the notes column.
