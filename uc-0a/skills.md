# Skills for UC-0A

## `classify_complaint`
- **Input**: A dictionary representing one complaint row.
- **Output**: A dictionary with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.
- **Purpose**: Applies strict RICE enforcement rules to prevent severity blindness and taxonomy drift.

## `batch_classify`
- **Input**: `input_path` (CSV), `output_path` (CSV).
- **Output**: Writes the results out.
- **Purpose**: Processes the whole file safely, catching exceptions per row to avoid crashes.
