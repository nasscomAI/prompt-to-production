# Skills for UC-0C

## `load_dataset`
- **Purpose**: Reads CSV, validates columns, reports null count, and identifies specific null rows before returning the dataset.
- **Constraints**: Warns on nulls, extracts notes explaining them.

## `compute_growth`
- **Purpose**: Takes a specific ward, category, and growth_type to calculate growth. Output is a per-period table.
- **Constraints**: Shows formula used. Avoids aggregate calculations. Halts if parameters are missing or general ("Any").
