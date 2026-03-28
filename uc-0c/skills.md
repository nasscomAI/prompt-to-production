# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: csv_reader
    description: Reads budget data from CSV file.
    input: CSV file path.
    output: List of rows.
    error_handling: Shows error if file not found.

  - name: data_processing
    description: Processes numeric data to calculate totals.
    input: Budget data rows.
    output: Calculated values.
    error_handling: Skips invalid rows.

  - name: csv_writer
    description: Writes processed data into CSV file.
    input: Processed data.
    output: Output CSV file.
    error_handling: Shows error if writing fails.