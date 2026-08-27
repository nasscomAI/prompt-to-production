skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a specific category, assigns a priority, provides a cited reason, and sets a review flag if ambiguous.
    input: A single dictionary or JSON object representing one complaint row (e.g., from a CSV).
    output: A dictionary containing the keys `category` (string), `priority` (string), `reason` (string), and `flag` (string: NEEDS_REVIEW or blank).
    error_handling: If the input is completely unparseable or irrelevant, return category 'Other' and set flag to 'NEEDS_REVIEW'. Do not throw unhandled exceptions.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to a new output CSV file.
    input: Two strings representing the file paths `input_path` (source CSV) and `output_path` (destination CSV).
    output: Writes a new CSV file to the `output_path` with the added classification columns. Returns nothing or a success status.
    error_handling: Must flag nulls or bad rows, and must not crash on bad rows. It must produce an output file even if some rows fail, logging or flagging the failures as 'NEEDS_REVIEW'.
