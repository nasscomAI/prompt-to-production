# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Parses the dataset CSV, actively validates explicit columns, mathematically tallies all null actual_spends, and rigorously reports the precise rows affected by missing data alongside their accompanying notes.
    input: Filepath sequence referencing the input CSV file.
    output: A formally structured tabular collection mapping columns logically and emitting summary flags documenting the raw count of parsed null values.
    error_handling: Deliberately halts execution instead of assuming valid data if columns differ, or isolates missing records to ensure computations aren't processed on NaN values dynamically.

  - name: compute_growth
    description: Orchestrates per-ward and per-category level evaluations mathematically mapped by periods via a formal command-argument growth type (like MoM).
    input: Command arguments mapping strictly isolated limits: a specific ward, an explicit category, and the required growth formula logic.
    output: A generated analytical period table specifically detailing growth fluctuations mapped transparently against the raw baseline and including the mathematical formula string printed on every line.
    error_handling: Safely refuses to guess default parameters if `--growth-type` is completely missing or throws error boundaries around computations attempted over null periods.
