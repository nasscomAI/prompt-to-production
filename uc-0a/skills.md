classify_complaint
    - Input: A single text string (citizen complaint description).
    - Processing: Evaluates text against the allowed 10-category taxonomy. Checks for the 9 strict severity keywords. Evaluates ambiguity.
    - Output: A dictionary containing `category`, `priority`, `reason`, and `flag`.

batch_classify
    - Input: Path to an input CSV file containing 15 rows of raw complaints.
    - Processing: Iterates through each row, applies `classify_complaint`, and structures the data.
    - Output: Writes a structured CSV file to the `uc-0a/` directory.