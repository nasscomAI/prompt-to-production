# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint description into a specific category and priority, providing a reason and a review flag.
    input: String (the complaint description).
    output: A dictionary/object containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the category is ambiguous, set `category` to Other and `flag` to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies the `classify_complaint` skill to each row, and writes the results to an output CSV file.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file.
    error_handling: Logs any rows that cannot be processed and ensures the output file is created with the correct schema.
