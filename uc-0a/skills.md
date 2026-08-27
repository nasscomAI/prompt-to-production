skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description to determine its proper classification.
    input: A single string or data row containing the citizen's complaint description.
    output: A structured object returning precisely four fields - category, priority, reason, and flag.
    error_handling: If input is missing or completely unparseable, assigns category "Other", low priority, and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, applies classify_complaint iteratively per row, and writes all results to an output CSV.
    input: Filepath to the input CSV file and filepath for the intended output CSV file.
    output: A new CSV file generated at the output filepath containing original data unified with the classification columns.
    error_handling: Handles missing input files with clear error messages. For individual failed rows, continues processing but assigns them the "NEEDS_REVIEW" flag and "Other" category.
