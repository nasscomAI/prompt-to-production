skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, priority, reason, and whether it requires review.
    input: A string containing the text of a single citizen complaint description.
    output: A dictionary or record with exactly four fields - category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: If the complaint description is completely unreadable or empty, output category "Other", priority "Low", reason "Missing description.", and flag "NEEDS_REVIEW". If the category is ambiguous, output the most likely category but set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file containing citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: An input file path (string) to a CSV of complaints, and an output file path (string) for the destination CSV.
    output: A saved CSV file containing the existing data plus the classified fields (category, priority, reason, flag).
    error_handling: If the input file is missing, halt execution and report FileNotFoundError. If a specific row is missing the description, output default values and continue processing.
