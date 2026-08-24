# Skills for UC-0C
- `load_dataset`: Reads CSV, validates columns, reports null count and which rows before returning.
- `compute_growth`: Computes growth correctly per period for a given ward and category without unauthorized aggregation. Flags nulls and includes the explicit formula used in the output. Refuses to guess the growth type if omitted.
