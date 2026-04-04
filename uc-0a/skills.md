# skills.md

skills:
  - name: classify_complaint
    description: Analyzes and classifies a single raw citizen complaint into predefined strict categorical assignments and severity-based priorities.
    input: A dictionary (`dict`) representing a single row from the CSV containing the unstructured citizen complaint `description`.
    output: A dictionary (`dict`) with exactly the keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: Refuses to confidently classify ambiguous inputs or empty descriptions by setting the category to 'Other' and definitively injecting 'NEEDS_REVIEW' into the flag column.

  - name: batch_classify
    description: Reads an entire input CSV of raw complaints, orchestrates the `classify_complaint` skill across every row, and writes the results to an output CSV.
    input: Two strings (`str`). `input_path`: the path to the raw data CSV. `output_path`: the destination path for the categorized results CSV.
    output: None (writes the classified data out to the specified file path).
    error_handling: Gracefully handles malformed rows or read/write exceptions without completely crashing the batch process. Flags deeply failed rows with an error note under the 'flag' field to ensure output continuity.
