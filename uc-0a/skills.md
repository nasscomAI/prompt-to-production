skills:
  - name: classify_complaint
    description: Classifies one civic complaint row into the UC-0A taxonomy.
    input: A dictionary representing one CSV row; description is the required evidence field.
    output: A dictionary with category, priority, reason, and flag keys using only allowed schema values.
    error_handling: Missing or unclassifiable descriptions return category Other, non-urgent priority, a reason citing the missing evidence condition, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the classified CSV.
    input: Input CSV path and output CSV path.
    output: A CSV containing all original non-classification columns plus category, priority, reason, and flag.
    error_handling: Invalid CSV structure stops with a clear error; ambiguous rows are retained and marked NEEDS_REVIEW instead of guessed confidently.
