# skills.md

skills:
  - name: classify_complaint
    description: Parses a single citizen complaint description and returns a precise classification based on predefined rules.
    input: Dictionary/JSON containing the complaint row with fields like description, location, etc.
    output: A dictionary containing the keys category, priority, reason, and flag.
    error_handling: Refuses classification on completely opaque input by falling back to category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a CSV of multiple complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: String path to the input CSV file and string path to the output CSV file.
    output: A boolean indicating success, and writes a newly formatted CSV file to the output path.
    error_handling: Skips heavily malformed rows without crashing, ensuring all valid rows are processed and written to the output file.
