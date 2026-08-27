# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its restricted category, priority level, justifiable reason, and whether it requires human review.
    input: A single string representing the raw complaint description.
    output: A dictionary/object with four string fields (category, priority, reason, flag).
    error_handling: If the complaint text is completely unintelligible, ambiguous, or lacks context, it sets the category to 'Other', leaves priority as 'Standard' or 'Low', and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, iterates over each row applying classify_complaint, and writes the classified dataset to an output CSV.
    input: File paths for the input CSV file containing unclassified complaints and the target output CSV file.
    output: A completed CSV file containing the original rows appended with the newly classified columns.
    error_handling: If the input file is missing or if there is a parsing error, it should raise a clear exception. If an individual row fails during classification, it should catch the error, assign a 'NEEDS_REVIEW' flag for that row, and continue processing the remaining rows securely.
