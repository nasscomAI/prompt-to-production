# skills.md

skills:
  - name: classify_complaint
    description: Take a single complaint record and determine its category,
      priority, justification reason, and ambiguity flag.
    input: A dictionary (or row) with fields `complaint_id`, `date_raised`,
      `city`, `ward`, `location`, `description`, `reported_by`, `days_open`.
    output: A dictionary containing `category` (one of the ten allowed strings),
      `priority` (Urgent/Standard/Low), `reason` (one-sentence string quoting
      terms from the description), and `flag` (either `NEEDS_REVIEW` or an
      empty string).
    error_handling: If required input fields are missing or empty, the skill
      should raise an error or return a special error object indicating invalid
      input.

  - name: batch_classify
    description: Read an input CSV of complaints, apply `classify_complaint` to
      each row, and write an output CSV with category/priority attached.
    input: Two file paths (`input_path` and `output_path`) or equivalent
      handles; input CSV contains the complaint rows without `category` and
      `priority` columns.
    output: A CSV file written to `output_path` where each row has additional
      `category`, `priority`, `reason`, and `flag` columns.
    error_handling: If the input file cannot be read or a row cannot be
      classified (e.g. missing description), log the error, skip that row, or
      halt with an informative message depending on the calling context.
