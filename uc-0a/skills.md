# skills.md
  
skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, assigns a priority, provides a reason, and sets a review flag.
    input: A single citizen complaint row (text description).
    output: A structured record containing the category, priority, reason, and flag.
    error_handling: If the input is ambiguous or unclear, assigns category "Other" and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Filepath to the input CSV file.
    output: A new CSV file containing the original data appended with category, priority, reason, and flag.
    error_handling: Logs an error if the input CSV is missing or unreadable, and skips malformed rows while continuing to process the rest of the file.
