# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint text into one of the predefined categories, determine its priority, and provide a text-based reason with a flag if ambiguous.
    input: Dictionary containing a single complaint row (e.g., {"description": "...", "location": "..."})
    output: Dictionary containing {"category": string, "priority": string, "reason": string, "flag": string}
    error_handling: If category is completely ambiguous or not matching any keywords, it returns "Other" as category and "NEEDS_REVIEW" as flag, defaulting priority to Low or Standard.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill per row, and writes the results to an output CSV.
    input: Path to an input CSV file and path to an output CSV file.
    output: A CSV file written to disk, and prints a success message to the console.
    error_handling: Handles malformed rows by trying to extract description or skipping row without crashing. Logs an error for bad rows but continues processing the batch.
