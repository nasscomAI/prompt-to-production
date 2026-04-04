skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, priority, and reason based strictly on its text description.
    input: A single complaint record or text description.
    output: A dictionary containing four fields - `category`, `priority`, `reason`, and `flag`.
    error_handling: If the category cannot be determined from the description alone, it sets `flag` to `NEEDS_REVIEW` and uses `Other` as the category.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies `classify_complaint` to each row, and writes the classified results to an output CSV file.
    input: Two file paths - `input_path` (path to input CSV) and `output_path` (path to write output CSV).
    output: Generates and saves a new CSV file containing the classifications.
    error_handling: Continues processing if a bad row is encountered without crashing, flags null or invalid inputs, and ensures successful rows are still output.
