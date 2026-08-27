skills:
  - name: Budget Data Reading
    description: Reads the ward budget dataset from the budget directory.
    input: CSV file path (string)
    output: List of rows from the dataset
    error_handling: Returns empty list if the dataset cannot be opened.

  - name: Budget Aggregation
    description: Groups budget values by ward and category.
    input: Dataset rows
    output: Aggregated totals per ward and category
    error_handling: Skips rows with missing or invalid numeric values.

  - name: Growth Calculation
    description: Calculates growth values based on aggregated budget data.
    input: Aggregated ward-category totals
    output: Growth results written to CSV format
    error_handling: Produces no result if required columns are missing.
