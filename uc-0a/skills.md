skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into one approved category, assigns the proper priority, and writes a brief evidence-based reason.
    input: A single complaint row containing at least a description field and any available metadata from the city CSV.
    output: A classification object with category, priority, reason, and optional flag values using the exact schema from the README.
    error_handling: If the complaint text is too ambiguous to assign a valid category with confidence, return flag=NEEDS_REVIEW and do not invent a category outside the allowed list.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to each complaint row, and writes the results to an output CSV.
    input: A CSV file path for a city dataset and an output CSV path.
    output: A CSV file with one row per complaint containing category, priority, reason, and flag values.
    error_handling: If a row is ambiguous or malformed, keep the row in the output with the exact evidence-based reason and set flag=NEEDS_REVIEW rather than silently guessing.
