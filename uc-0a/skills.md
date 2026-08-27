# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, reason, priority, and flag.
    input: A single citizen complaint description string.
    output: A structured record containing category, priority, reason, and flag strings.
    error_handling: Flags the complaint as "NEEDS_REVIEW" and categorizes as "Other" if ambiguous or invalid.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Filepath to an input CSV containing city complaints.
    output: Filepath to an output CSV containing the original data appended with the classification results.
    error_handling: Continues processing remaining rows and relies on classify_complaint to handle and flag row-level issues.
