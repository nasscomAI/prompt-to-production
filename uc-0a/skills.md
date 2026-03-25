# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and outputs its category, priority, and reason according to the classification schema.
    input: String containing the complaint description.
    output: A structured object with keys: category, priority, reason, flag.
    error_handling: Returns "Other" for category and sets flag: NEEDS_REVIEW if description is ambiguous or unclassifiable.

  - name: batch_classify
    description: Processes an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: File paths for input and output CSVs.
    output: A CSV file containing original data and new classification columns.
    error_handling: Aborts with clear error if input file is missing or contains malformed data.
